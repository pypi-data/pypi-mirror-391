from typing import Callable, Optional
from dataclasses import dataclass, field
import heapq

from ...models import *

@dataclass
class CrawlQueue:
    queue:list[CrawlTask] = field(default_factory=list)
    urls_in_queue:set[Url] = field(default_factory=set)
    visited:set[Url] = field(default_factory=set)
    max_depth:int = -1
    priority:Callable[[Url,int],float] = field(default_factory=lambda: (lambda url, depth: depth))

    def _rebuild_heap(self):
        for i, task in enumerate(self.queue):
            self.queue[i] = CrawlTask(self.priority[task.url,task.depth],task.url,task.depth)
            heapq.heapify(self.queue)
    
    def set_priority(self, fn:Callable[[Url,int],float]):
        self.priority = fn
        self._rebuild_heap()

    def add_url(self, url:Url, depth: int):
        if url not in self.visited and url not in self.urls_in_queue:
            if self.max_depth > -1 and self.max_depth < depth:
                return
            
            heapq.heappush(self.queue,CrawlTask(self.priority(url,depth),url,depth))
            
            self.urls_in_queue.add(url)

    def next_link(self) ->Optional[tuple[Url,int]]:
        if not self.queue:
            return None
        
        task = heapq.heappop(self.queue)
        
        self.urls_in_queue.remove(task.url)
        self.visited.add(task.url)
        
        return task.url, task.depth

    def add_new_links(self, links:list[Url], depth:int):
        for link in links:
            self.add_url(link, depth+1)

