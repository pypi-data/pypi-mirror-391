import requests
from cachetools import cached, TTLCache

@cached(cache=TTLCache(maxsize=1, ttl=3600))
def get_bl_domain():
    url = 'https://s3.tebi.io/jps/bl.domain'
    response = requests.get(url)
    return response.text.strip()

def fetch_page(url):
    bldomain = get_bl_domain()
    _url = f'https://{bldomain}/chrome/content'
    print(_url)
    response = requests.post(_url, json={
        "url": url,
    })
    if response.ok:
        return response.text
    else:
        return None
