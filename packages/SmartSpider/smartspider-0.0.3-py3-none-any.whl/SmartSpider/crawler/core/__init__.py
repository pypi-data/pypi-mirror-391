"""
Core Package
============

Contains modular components for crawling, scheduling, and scraping.

Modules:
- fetcher: Handles network requests and page fetching
- queue: Manages URL task scheduling (BFS, DFS, priority, adaptive)
- scheduler: Controls crawl timing and revisits
- scope: Enforces domain or subdomain limits
- scraper: Extracts structured data from pages
- change_detector: Detects content changes for incremental crawling
- models: Shared data models (Url, Page, CrawlTask, etc.)
"""

from ...models import Url, Page, CrawlTask
from .queue import CrawlQueue
from .scheduler import Scheduler
from . import scope as Scope
from .fetcher import fetch_page
from .change_detector import ChangeDetector

__all__ = [
    "Url",
    "Page",
    "CrawlTask",
    "CrawlQueue",
    "Scheduler",
    "Scope",
    "fetch_page",
    "ChangeDetector",
]
