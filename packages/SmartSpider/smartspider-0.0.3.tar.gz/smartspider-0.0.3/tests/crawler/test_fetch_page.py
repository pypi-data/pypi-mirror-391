import pytest
import requests
from SmartSpider import fetch_page
from SmartSpider import Page, Url

def test_fetch_page_success(monkeypatch):
    class MockResponse:
        text = "<html>ok</html>"
        def raise_for_status(self): pass
    monkeypatch.setattr(requests, "get", lambda url: MockResponse())
    page = fetch_page(Url("https://example.com"))
    assert isinstance(page, Page)
    assert page.html == "<html>ok</html>"

def test_fetch_page_failure(monkeypatch):
    def mock_get(url): raise requests.RequestException("fail")
    monkeypatch.setattr(requests, "get", mock_get)
    page = fetch_page(Url("https://example.com"))
    assert page is None
