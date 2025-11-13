from typing import Callable, Any

from ..models import *
from .core import href_scrape_fn

class Scraper:
    def __init__(self,page:Page|None=None, scrape_fn:Callable = href_scrape_fn):
        self.page = page
        self.scrape_fn = scrape_fn

    def __call__(self, *args, **kwargs):
        if not self.scrape_fn:
            raise ValueError("No scraping function provided.")
        assert self.page is not None, "Scraper has no page to scrape."
        arguments = (self.page,) + args
        return self.scrape_fn(*arguments)
                
    def step(self,page:Page):
        self.page = page