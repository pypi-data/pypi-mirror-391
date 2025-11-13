import pytest

def test_first_time_page_is_new(change_detector, sample_page):
    assert change_detector.has_changed(sample_page) is True

def test_page_change_detection(change_detector, sample_page, changed_page):
    change_detector.has_changed(sample_page)  # store initial hash
    assert change_detector.has_changed(changed_page) is True

def test_page_no_change_detection(change_detector, sample_page):
    change_detector.has_changed(sample_page)
    assert change_detector.has_changed(sample_page) is False
