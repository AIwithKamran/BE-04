import os
import time
import requests


USER_AGENT = 'FlyRankInternshipA9/1.0 (+https://github.com/AIwithKamran/BE-04.git)'
TIMEOUT = 10
CACHE_DIR = 'cache'

os.makedirs(CACHE_DIR, exist_ok=True)


def fetch(url, cache_filename):
    '''Fetch a URL politely, using a local cache to avoid re-hitting the site.'''
    cache_path = os.path.join(CACHE_DIR, cache_filename)

    if os.path.exists(cache_path):
        with open(cache_path, 'r', encoding='utf-8') as f:
            html = f.read()
        print(f"CACHE HIT. {cache_filename} {len(html)} bytes")
        return html

    headers = {"User-Agent": USER_AGENT}
    response = requests.get(url, headers=headers, timeout=TIMEOUT)

    if response.status_code != 200:
        raise Exception(f"Failed Fetch: {url} returned status {response.status_code}")

    html = response.text
    print(f"FETCH: {cache_filename} ({len(html)} bytes)")

    with open(cache_path, "w", encoding='utf-8') as f:
        f.write(html)
    return html


if __name__ == "__main__":
    url = "https://books.toscrape.com/catalogue/page-1.html"
    html = fetch(url, "catalogue-page-1.html")
    