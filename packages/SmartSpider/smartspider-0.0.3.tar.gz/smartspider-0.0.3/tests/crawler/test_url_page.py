import pytest
from SmartSpider import Url, Page

@pytest.mark.parametrize("invalid_url", ["ftp://example.com", "example.com", ""])
def test_url_invalid_raises(invalid_url):
    with pytest.raises(ValueError):
        Url(invalid_url)

def test_url_addition():
    base = Url("https://example.com/")
    combined = base + "about"
    assert combined.href == "https://example.com/about"

def test_page_url_initialization():
    p = Page("https://example.com", "<html></html>")
    assert p.url == "https://example.com"
    assert p.domain == "example.com"
