from datetime import date
from unittest.mock import Mock

import pytest
import requests
from click.testing import CliRunner

from ifq import DownloadError, IssueNotAvailableError, LoginError, Scraper
from ifq.cli import cli


def test_version():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert result.output.startswith("cli, version ")


LOGIN_URL = "https://shop.ilfattoquotidiano.it/login/"
LOOKUP_URL = (
    "https://www.ilfattoquotidiano.it/ilfattoquotidiano/"
    "getByDate/edizione/2026-10-07"
)
EDITION_URL = (
    "https://www.ilfattoquotidiano.it/in-edicola/edizione/"
    "mercoledi-7-ottobre-2026/"
)
DOWNLOAD_URL = (
    "https://www.ilfattoquotidiano.it/ilfattoquotidiano/"
    "edition/8529818/download"
)
PUB_DATE = date(2026, 10, 7)


def response(
    text="<html></html>", json_data=None, content=b"", content_type="text/html"
):
    result = Mock()
    result.text = text
    result.json.return_value = json_data
    result.status_code = 200
    result.headers = {"Content-Type": content_type}
    result.content = content
    result.iter_content.return_value = [content]
    return result


@pytest.fixture
def session(monkeypatch):
    session = Mock()
    session.__enter__ = Mock(return_value=session)
    session.__exit__ = Mock(return_value=False)
    session.cookies = {"wordpress_logged_in_test": "authenticated"}
    monkeypatch.setattr("ifq.requests.Session", Mock(return_value=session))
    return session


def prepare_download(session, pdf):
    session.get.side_effect = [
        response('<input id="woocommerce-login-nonce" value="login-nonce">'),
        response(json_data={"url": EDITION_URL, "id": "8529818"}),
        # The current site uses data-href, not the PDF viewer's href.
        response(
            '<a href="/in-edicola/sfoglia-pdf/?file=viewer" '
            'data-edition-action="download" '
            'data-href="/ilfattoquotidiano/edition/8529818/download">'
            "Scarica PDF</a>"
        ),
        pdf,
    ]


def test_download_uses_current_edition_interface(session, tmp_path):
    content = b"%PDF-1.7\n" + b"x" * 8_000_000
    prepare_download(
        session, response(content=content, content_type="application/pdf")
    )

    output = Scraper("user", "password").download_pdf(PUB_DATE, tmp_path)

    assert str(output) == str(tmp_path / "2026-10-07.pdf")
    assert (tmp_path / "2026-10-07.pdf").read_bytes() == content
    assert [call.args[0] for call in session.get.call_args_list] == [
        LOGIN_URL,
        LOOKUP_URL,
        EDITION_URL,
        DOWNLOAD_URL,
    ]
    assert session.get.call_args.kwargs["stream"] is True
    session.post.assert_called_once()
    assert (
        session.post.call_args.kwargs["data"]["woocommerce-login-nonce"]
        == "login-nonce"
    )


def test_missing_login_form_has_clear_error(session, tmp_path):
    session.get.return_value = response("<html>Login unavailable</html>")

    with pytest.raises(LoginError, match="login form"):
        Scraper("user", "password").download_pdf(PUB_DATE, tmp_path)

    session.post.assert_not_called()


def test_invalid_credentials(session, tmp_path):
    session.get.return_value = response(
        '<input id="woocommerce-login-nonce" value="login-nonce">'
    )
    session.cookies = {}

    with pytest.raises(LoginError, match="Cannot login"):
        Scraper("user", "password").download_pdf(PUB_DATE, tmp_path)


def test_unavailable_issue(session, tmp_path):
    session.get.side_effect = [
        response('<input id="woocommerce-login-nonce" value="login-nonce">'),
        response(json_data={}),
    ]

    with pytest.raises(IssueNotAvailableError, match="2026-10-07"):
        Scraper("user", "password").download_pdf(PUB_DATE, tmp_path)

    assert not list(tmp_path.iterdir())


def test_missing_download_link(session, tmp_path):
    session.get.side_effect = [
        response('<input id="woocommerce-login-nonce" value="login-nonce">'),
        response(json_data={"url": EDITION_URL}),
        response(
            '<a href="#" data-edition-action="download" '
            'data-show-paywall="true">Scarica PDF</a>'
        ),
    ]

    with pytest.raises(DownloadError, match="PDF download link"):
        Scraper("user", "password").download_pdf(PUB_DATE, tmp_path)

    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize(
    "pdf, message",
    [
        (response(content_type="text/html"), "application/pdf"),
        (
            response(content=b"%PDF-small", content_type="application/pdf"),
            "at least",
        ),
    ],
)
def test_invalid_pdf_is_not_saved(session, tmp_path, pdf, message):
    prepare_download(session, pdf)

    with pytest.raises(DownloadError, match=message):
        Scraper("user", "password").download_pdf(PUB_DATE, tmp_path)

    assert not list(tmp_path.iterdir())


def test_lookup_http_error(session, tmp_path):
    lookup = response()
    lookup.raise_for_status.side_effect = requests.HTTPError("503 unavailable")
    session.get.side_effect = [
        response('<input id="woocommerce-login-nonce" value="login-nonce">'),
        lookup,
    ]

    with pytest.raises(requests.HTTPError, match="503"):
        Scraper("user", "password").download_pdf(PUB_DATE, tmp_path)
