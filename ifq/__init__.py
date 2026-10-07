import logging
import os
import tempfile
from datetime import date
from pathlib import Path
from urllib.parse import urljoin

import requests
from lxml import html

IFQ_LOGIN_URL = "https://shop.ilfattoquotidiano.it/login/"
IFQ_EDITION_LOOKUP_URL = (
    "https://www.ilfattoquotidiano.it/ilfattoquotidiano/getByDate/edizione/"
)
IFQ_MIN_CONTENT_LENGTH = 8_000_000


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

        with requests.Session() as session:

            resp = session.get(IFQ_LOGIN_URL)
            resp.raise_for_status()
            tree = html.fromstring(resp.text)
            nonce = tree.xpath('//input[@id="woocommerce-login-nonce"]/@value')
            if not nonce:
                raise LoginError("Cannot find login form on IFQ login page")
            login_payload["woocommerce-login-nonce"] = nonce[0]

            #
            # do the actual login on the website
            #
            resp = session.post(IFQ_LOGIN_URL, data=login_payload)
            resp.raise_for_status()

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

            self.logger.info(f"looking up IFQ issue for {pub_date}")
            resp = session.get(
                IFQ_EDITION_LOOKUP_URL + pub_date.strftime("%Y-%m-%d")
            )
            resp.raise_for_status()
            edition_url = resp.json().get("url")
            if not edition_url:
                raise IssueNotAvailableError(
                    f"No issue available for {pub_date:%Y-%m-%d}"
                )

            resp = session.get(edition_url)
            resp.raise_for_status()
            tree = html.fromstring(resp.text)
            download_links = tree.xpath(
                '//*[@data-edition-action="download"]/@data-href'
            )
            if not download_links:
                raise DownloadError(
                    f"PDF download link not available for {pub_date:%Y-%m-%d}; "
                    "check your subscription"
                )

            resp = session.get(
                urljoin(edition_url, download_links[0]), stream=True
            )

            self.logger.debug(f"status code: {resp.status_code}")
            self.logger.debug(f"content length: {len(resp.content)}")

            if resp.status_code != 200:
                raise IssueNotAvailableError(
                    f"expected status code 200, got ${resp.status_code}"
                )

            content_type = resp.headers.get("Content-Type", "")
            if content_type.split(";", 1)[0].strip() != "application/pdf":
                raise DownloadError(
                    f"expected 'application/pdf', got '{content_type}'"
                )

            if len(resp.content) < IFQ_MIN_CONTENT_LENGTH:
                raise DownloadError(
                    f"expected at least {IFQ_MIN_CONTENT_LENGTH} bytes, "
                    f"got {len(resp.content)}"
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
