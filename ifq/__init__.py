import logging
import os
import tempfile
from datetime import date
from pathlib import Path

import requests
from lxml import html

IFQ_LOGIN_URL = "https://shop.ilfattoquotidiano.it/login/"
IFQ_ARCHIVE_URL = "https://shop.ilfattoquotidiano.it/archivio-edizioni/"
IFQ_MIN_CONTENT_LENGTH = 9000000


class Scraper:
    """Scrape the IFQ website to download PDF files.

    This class require a valid paid subscription to the newspaper.
    """

    def __init__(self, username: str, password: str):
        self.logger = logging.getLogger(__name__)
        self.username = username
        self.password = password

    def download_pdf(
        self, pub_date: date, output_dir: Path = Path.cwd()
    ) -> Path:
        """Download a IFQ issues from the website archive.

        Scrape and download the issue published at the give pub_date and
        return path to the temp file on the local filesystem.
        """

        # prepare the payloads
        login_payload = dict(
            username=self.username,
            password=self.password,
            _wp_http_referer="/login/",
            redirect="/login/",
            login="Accedi",
        )

        edition_payload = dict(
            edition_date=pub_date.strftime("%d/%m/%Y"),
            _wp_http_referer="/abbonati/",
        )

        with requests.Session() as session:

            resp = session.get(IFQ_LOGIN_URL)
            tree = html.fromstring(resp.text)
            nonce = tree.xpath('//input[@id="woocommerce-login-nonce"]')
            login_payload["woocommerce-login-nonce"] = nonce[0].value

            #
            # do the actual login on the website
            #
            resp = session.post(IFQ_LOGIN_URL, data=login_payload)

            #
            # Check if the login was successful
            #
            # Lookup if the `wordpress_logged_in` cookie has been set,
            # see https://wordpress.org/support/article/cookies/
            # for more details.
            #
            logged_in_cookies = [
                key
                for key in session.cookies.keys()
                if "wordpress_logged_in" in key
            ]
            if len(logged_in_cookies) < 1:
                self.logger.error("login failed")
                raise LoginError("Cannot login")

            self.logger.info("getting archive page")
            # open the archive page and get the nonce
            resp = session.get(IFQ_ARCHIVE_URL)

            tree = html.fromstring(resp.text)
            nonce = tree.xpath('//input[@name="edition_date_nonce"]')
            edition_date_nonce = nonce[0].value

            edition_payload["edition_date_nonce"] = edition_date_nonce

            self.logger.info(f"getting IFQ opening issue for ${pub_date}")

            # download the actual issues
            resp = session.post(
                IFQ_ARCHIVE_URL, data=edition_payload, stream=True
            )

            self.logger.debug(f"status code: {resp.status_code}")
            self.logger.debug(f"headers: {resp.headers}")
            self.logger.debug(f"content length: {len(resp.content)}")

            if resp.status_code != 200:
                raise IssueNotAvailableError(
                    f"expected status code 200, got ${resp.status_code}"
                )

            if resp.headers["Content-Type"] != "application/pdf":
                raise DownloadError(
                    f"expected 'application/pdf', got '{resp.headers['Content-Type']}'"
                )

            if len(resp.content) < IFQ_MIN_CONTENT_LENGTH:
                raise DownloadError(
                    f"expected at least {IFQ_MIN_CONTENT_LENGTH} bytes, got {len(resp.content)}"
                )

            self.logger.debug("copying the PDF bytes into a temporary file")

            # create a temporary file to store the PDF bytes
            file = tempfile.NamedTemporaryFile(delete=False)

            with file as f:
                for chunk in resp.iter_content(chunk_size=1024):
                    # filter out keep-alive new chunks
                    if chunk:
                        f.write(chunk)
                        f.flush()

            # rename the file to the output directory if specified
            output_file = os.path.join(
                output_dir, pub_date.strftime("%Y-%m-%d") + ".pdf"
            )
            os.rename(file.name, output_file)

            self.logger.info(f"PDF file available at ${output_file}")

            return output_file


class IssueNotAvailableError(Exception):
    pass


class LoginError(Exception):
    pass


class DownloadError(Exception):
    pass
