import pytest
from SmartSpider import CrawlQueue
from SmartSpider import Url

def test_add_and_next_link():
    q = CrawlQueue()
    url = Url("https://example.com")
    q.add_url(url, 0)
    result = q.next_link()
    assert result == (url, 0)
    assert url in q.visited

def test_max_depth_prevents_add():
    q = CrawlQueue(max_depth=1)
    url = Url("https://example.com")
    q.add_url(url, 2)
    assert not q.queue

def test_priority_function_changes_order():
    q = CrawlQueue()
    q.set_priority(lambda url, depth: -depth)
    q.add_url(Url("https://a.com"), 1)
    q.add_url(Url("https://b.com"), 2)
    u, d = q.next_link()
    assert d == 2  # higher depth = higher priority
