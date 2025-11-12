from base64 import urlsafe_b64decode
import pytest
from .link_maker import LinkMaker


@pytest.mark.parametrize(
    "site_url,page_url,expected",
    [
        ("http://site.test", "/example", "http://site.test/example"),
        ("http://site.test/", "/example", "http://site.test/example"),
        ("http://site.test/path/", "/example", "http://site.test/example"),
    ],
)
def test_link_maker_page_url(site_url, page_url, expected):
    base_url = "http://base.test/example/"

    link_maker = LinkMaker(base_url=base_url, site_url=site_url)

    result = link_maker.ap_object(page_url)

    assert result.startswith(base_url)

    end = result.removeprefix(base_url + "pages/")
    decoded = urlsafe_b64decode(end.encode()).decode()

    assert decoded == expected
