import logging
import tempfile
import requests

from datetime import date
from lxml import html

IFQ_LOGIN_URL = 'https://shop.ilfattoquotidiano.it/login/'
IFQ_ARCHIVE_URL = 'https://shop.ilfattoquotidiano.it/archivio-edizioni/'


class Scraper:
    """Scrape the IFQ website to download PDF files.

    This class require a valid paid subscription to the newspaper.
    """

    def __init__(self, username: str, password: str):
        self.logger = logging.getLogger(__name__)
        self.username = username
        self.password = password

    def download_pdf(self, pub_date: date) -> str:
        """Download a IFQ issues from the website archive.

        Scrape and download the issue published at the give pub_date and
        return path to the temp file on the local filesystem.
        """

        with requests.Session() as session:

            #
            # 1) First thing first, let's get the login page.
            #
            login_payload = dict(
                username=self.username,
                password=self.password,
                _wp_http_referer='/login/',
                redirect='/login/',
                login='Accedi')

            resp = session.get(IFQ_LOGIN_URL)
            tree = html.fromstring(resp.text)
            nonce = tree.xpath('//input[@id="woocommerce-login-nonce"]')
            login_payload['woocommerce-login-nonce'] = nonce[0].value

            #
            # 2) Now we can do the actual login on the website
            #
            resp = session.post(IFQ_LOGIN_URL, data=login_payload)

            #
            # 3) Check if the login was successful
            #
            # Lookup if the `wordpress_logged_in` cookie has been set,
            # see https://wordpress.org/support/article/cookies/
            # for more details.
            #
            logged_in_cookies = [
                key for key in session.cookies.keys()
                if 'wordpress_logged_in' in key
            ]

            if not logged_in_cookies:
                self.logger.error('login failed')
                raise LoginFailed("Cannot login")

            #
            # 4) Visit the issues archive page
            #
            self.logger.info('getting archive page')
            resp = session.get(IFQ_ARCHIVE_URL)

            # we need the `nonce` from this page
            tree = html.fromstring(resp.text)
            nonce = tree.xpath('//input[@name="edition_date_nonce"]')
            edition_date_nonce = nonce[0].value

            #
            # 5) Download the PDF file from the archive
            #
            edition_payload = dict(
                edition_date=pub_date.strftime('%d/%m/%Y'),
                _wp_http_referer='/abbonati/')
            edition_payload['edition_date_nonce'] = edition_date_nonce

            self.logger.info(f'getting IFQ opening issue for ${pub_date}')

            resp = session.post(IFQ_ARCHIVE_URL,
                                data=edition_payload,
                                stream=True)

            if resp.status_code != 200:
                self.logger.error(f'status code ${resp.status_code}')
                raise IssueNotAvailable()

            #
            # 6) Final step, now copy the PDF bytes into a temporary file.
            #
            self.logger.info(f'copying the PDF bytes into a temporary file')
            file = tempfile.NamedTemporaryFile(delete=False)

            with file as f:
                for chunk in resp.iter_content(chunk_size=1024):
                    # filter out keep-alive new chunks
                    if chunk:
                        f.write(chunk)
                        f.flush()

            self.logger.info(f'PDF file available at ${file.name}')
            return file.name


class IssueNotAvailable(Exception):
    pass


class LoginFailed(Exception):
    pass
