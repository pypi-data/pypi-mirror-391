from SmartSpider import Scheduler

def test_once_mode_always_true(sample_page):
    s = Scheduler(mode="once")
    assert s.process(sample_page) is True

def test_incremental_mode_with_change_detector(change_detector, sample_page):
    s = Scheduler(mode="incremental", detector=change_detector)
    assert s.process(sample_page) is True
    # unchanged page should be False
    assert s.process(sample_page) is False

def test_should_crawl_respects_interval(monkeypatch):
    s = Scheduler(mode="incremental", revisit_interval=10)
    url = "https://example.com"
    s.last_crawled[url] = 1000
    monkeypatch.setattr("time.time", lambda: 1005)
    assert s.should_crawl(url) is False
    monkeypatch.setattr("time.time", lambda: 1011)
    assert s.should_crawl(url) is True
