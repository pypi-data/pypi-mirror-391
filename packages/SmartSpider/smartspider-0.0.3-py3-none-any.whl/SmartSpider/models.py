from urllib.parse import urlparse, urljoin
from dataclasses import dataclass, field
class Url:
    def __init__(self, url: str):
        if not (url.startswith("http://") or url.startswith("https://")):
            raise ValueError(f"Invalid URL: {url}")
        self._url = url
        self._domain = urlparse(url).netloc

    def __add__(self,other):
        if isinstance(other,str):
            return Url(urljoin(self._url, other))
        else:
            return Url(urljoin(self._url, other.href))

    @property
    def href(self):
        return self._url

    @property
    def domain(self):
        return self._domain

    def __str__(self):
        return self._url

    def __repr__(self):
        return f"<URL url={self._url} domain={self._domain}>"

    def __eq__(self, other):
        return isinstance(other, Url) and self._url == other._url

    def __hash__(self):
        return hash(self._url)

@dataclass
class Page:
    _url:Url|str = field(default_factory=str)
    html:str = field(default_factory=str)

    def __post_init__(self):
        if isinstance(self._url,str):
            self._url = Url(self._url)
    
    @property
    def url(self):
        return self._url.href
    
    @property
    def domain(self):
        return self._url.domain
    
@dataclass(order=True)
class CrawlTask:
    priority:float
    url:Url = field(compare=False)
    depth:int = field(compare=False)