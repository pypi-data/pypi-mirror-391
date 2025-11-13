import time
import random

import requests
from cachetools import cached, LRUCache

@cached(LRUCache(maxsize=1))
def gethttpclient():
    httpclient = requests.session()
    httpclient.timeout = (10, 120)
    return httpclient

def fetch_get(url, headers={
                'Content-Type': 'application/json'
            }, error_sleep = 2.0, max_error_cnt = 1000, timeout = (10, 60),
            proxies = None,proxylist = []):
    if max_error_cnt < 0:
        return None
    remain_proxylist = []
    if not proxies and proxylist:
        proxies = random.choice(proxylist)
        print(proxies)
        remain_proxylist = [item for item in proxylist if item != proxies]
    result = None
    try:
        status_code = 200
        with requests.get(url, 
                        headers = headers, 
                        timeout = timeout,
                        proxies = proxies) as response:
            status_code = response.status_code
            if status_code == 200 or status_code == 201:
                result = response.json()
            elif status_code == 404:
                print("404")
                return None
            elif status_code == 429:
                print(f"rate limit retry: {max_error_cnt}")
        if status_code == 429:
            time.sleep(error_sleep)
            if max_error_cnt < 10:
                error_sleep = error_sleep / 1.2
            return fetch_get(url, headers, max_error_cnt = max_error_cnt-1, error_sleep=error_sleep, proxies=proxies, proxylist=remain_proxylist)
    except requests.exceptions.ReadTimeout:
        print("timeout retry")
        time.sleep(error_sleep)
        if max_error_cnt < 10:
            error_sleep = error_sleep / 1.2
        return fetch_get(url, headers, max_error_cnt = max_error_cnt-1, error_sleep=error_sleep, proxies=proxies, proxylist=remain_proxylist)
    except requests.exceptions.ConnectionError as e:
        print("connection error retry", repr(e))
        time.sleep(error_sleep)
        if max_error_cnt < 10:
            error_sleep = error_sleep / 1.2
        return fetch_get(url, headers, max_error_cnt = max_error_cnt-1, error_sleep=error_sleep, proxies = proxies, proxylist=remain_proxylist)
    return result

def fetch_post(url, payload = {} , headers={
        'Content-Type': 'application/json'
    }, error_sleep = 2.0, max_error_cnt = 5, timeout=(10, 60)):
    if max_error_cnt <= 0:
        return None
    result = None
    try:
        with requests.post(url, 
                        json=payload,
                        headers=headers, 
                        timeout=timeout) as response:
            if response.status_code == 200 or response.status_code == 201:
                result = response.json()
            elif response.status_code == 404:
                print("404")
                return None
            elif response.status_code == 429:
                print("rate limit retry")
                time.sleep(error_sleep)
                return fetch_post(url, payload, headers, max_error_cnt=max_error_cnt-1)
            else:
                print(response.text, response.status_code)
    except requests.exceptions.ReadTimeout:
        print("timeout retry")
        time.sleep(error_sleep)
        return fetch_post(url,payload, headers, max_error_cnt=max_error_cnt-1)
    except requests.exceptions.ConnectionError:
        print("connection error retry")
        time.sleep(error_sleep)
        return fetch_post(url,payload, headers, max_error_cnt=max_error_cnt-1)
    return result

DEFAULT_HEADERS = {
    'Accept': '*/*',
    'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'DNT': '1',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'cross-site',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; ) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.61 Chrome/126.0.6478.61 Not/A)Brand/8  Safari/537.36',
    'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

def fetch_get_raw(url, timeout=None, headers=DEFAULT_HEADERS):
    httpclient = gethttpclient()
    ae = None
    i = 0
    while(i<2):
        try:
            if timeout:
                r = httpclient.get(url, headers=headers, timeout=timeout)
            else:
                r = httpclient.get(url, headers=headers)
            r.raise_for_status()
            return r
        except Exception as e:
            ae = e
            url = url.replace("https", "http")
        i += 1
    if ae:
        raise ae
    raise ValueError(f"fetch {url} error")

