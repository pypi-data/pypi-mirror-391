from ...models import *

class Scope:
    def __call__(self, url: Url) -> bool:
        raise NotImplementedError


class SiteWide(Scope):
    def __init__(self, root_url: str):
        self.root_domain = Url(root_url).domain

    def __call__(self, url: Url) -> bool:
        domain = url.domain
        return domain == self.root_domain or domain.endswith("." + self.root_domain)


class MultiDomain(Scope):
    def __init__(self, allowed_domains: list[str]):
        self.allowed_domains = set(allowed_domains)

    def __call__(self, url: Url) -> bool:
        domain = url.domain
        return any(domain == d or domain.endswith("." + d) for d in self.allowed_domains)

class Unrestricted(Scope):
    def __call__(self, url: Url) -> bool:
        return True
