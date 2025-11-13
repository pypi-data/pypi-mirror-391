"""
Crawler Package
===============

High-level entrypoint for the web crawler system.

This package combines modular components from `core` to provide:
- Priority-based, adaptive crawling (BFS, DFS, priority)
- Incremental and continuous scheduling
- Domain and subdomain scope control
- Optional content change detection
"""

from .crawler import Crawler
from .core import (
    CrawlQueue,
    Scheduler,
    Scope,
    ChangeDetector,
    fetch_page
)

__all__ = [
    "Crawler",
    "CrawlQueue",
    "Scheduler",
    "Scope",
    "CrawlerScraper",
    "ChangeDetector",
    "fetch_page",
]
