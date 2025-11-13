from SmartSpider import Url
from SmartSpider import Scope

def test_sitewide_scope():
    scope = Scope.SiteWide("https://example.com")
    assert scope(Url("https://example.com/page"))
    assert not scope(Url("https://other.com"))

def test_multidomain_scope():
    scope = Scope.MultiDomain(["example.com", "test.org"])
    assert scope(Url("https://test.org"))
    assert not scope(Url("https://google.com"))

def test_unrestricted_scope():
    scope = Scope.Unrestricted()
    assert scope(Url("https://anywhere.com"))
