from typing import Optional
import time

from ...models import Page, Url
from .change_detector import ChangeDetector

class Scheduler:
    def __init__(self,mode:str = "once", revisit_interval:int = 3600, 
                 detector:Optional[ChangeDetector] = None):
        
        assert mode in ("once", "incremental", "continuous")
        
        self.mode = mode
        self.revisit_interval = revisit_interval
        self.last_crawled:dict[Url,float] = {}
        self.detector = detector if mode in ("incremental", "continuous") and detector else None

    def process(self,page:Page) -> bool:
        self.last_crawled[page.url] = time.time()

        if self.mode == "once":
            return True
        
        if self.detector:
            return self.detector.has_changed(page)

        return True

    def should_crawl(self, url:Url):
        if self.mode == "once":
            return url in self.last_crawled
        
        last = self.last_crawled.get(url, time.time())
        return (time.time() - last) >= self.revisit_interval