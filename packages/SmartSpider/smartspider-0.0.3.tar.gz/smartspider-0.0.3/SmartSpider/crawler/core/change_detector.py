from dataclasses import dataclass,field
import hashlib

from ...models import Page

@dataclass
class ChangeDetector:
    page_hashes:dict[str,str] = field(default_factory=dict)
    
    def has_changed(self,page:Page):
        new_hash = hashlib.md5(page.html.encode("utf-8")).hexdigest()
        old_hash = self.page_hashes.get(page.url)
        self.page_hashes[page.url] = new_hash
        return old_hash is None or old_hash != new_hash