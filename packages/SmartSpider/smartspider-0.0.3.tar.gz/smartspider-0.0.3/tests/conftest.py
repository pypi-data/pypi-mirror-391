import pytest
from SmartSpider.core import Page, Url, ChangeDetector

@pytest.fixture
def sample_url():
    return Url("https://example.com")

@pytest.fixture
def sample_page(sample_url):
    return Page(sample_url, "<html>Hello</html>")

@pytest.fixture
def changed_page(sample_url):
    return Page(sample_url, "<html>Changed</html>")

@pytest.fixture
def change_detector():
    return ChangeDetector()
