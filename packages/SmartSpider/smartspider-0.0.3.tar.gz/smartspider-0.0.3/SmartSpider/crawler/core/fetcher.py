import requests
from requests.exceptions import RequestException

from typing import Optional

from ...models import Page,Url
def fetch_page(url:Url) -> Optional[Page]: 
    try:       
        r = requests.get(url.href)
        
        r.raise_for_status()

        return Page(url,r.text)
    except RequestException as e:
        return None