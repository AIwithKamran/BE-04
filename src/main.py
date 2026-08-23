import os
import time
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup



USER_AGENT = 'FlyRankInternshipA9/1.0 (+https://github.com/AIwithKamran/BE-04.git)'
TIMEOUT = 10
CACHE_DIR = 'cache'

BASE_CATALOGUE_URL = "https://books.toscrape.com/catalogue/page-1.html"

os.makedirs(CACHE_DIR, exist_ok=True)


def fetch(url, cache_filename):
    '''Fetch a URL politely, using a local cache to avoid re-hitting the site.'''
    cache_path = os.path.join(CACHE_DIR, cache_filename)

    if os.path.exists(cache_path):
        with open(cache_path, 'r', encoding='utf-8') as f:
            html = f.read()
        print(f"CACHE HIT. {cache_filename} {len(html)} bytes")
        return html, True

    headers = {"User-Agent": USER_AGENT}
    response = requests.get(url, headers=headers, timeout=TIMEOUT)

    if response.status_code != 200:
        raise Exception(f"Failed Fetch: {url} returned status {response.status_code}")

    html = response.text
    print(f"FETCH: {cache_filename} ({len(html)} bytes)")

    with open(cache_path, "w", encoding='utf-8') as f:
        f.write(html)
    return html, False


def discover_book_urls():
    """Follow catalogue pages via their own 'next' links, collecting unique book URLs."""
    book_urls = []
    page_num = 1
    current_url = BASE_CATALOGUE_URL

    while current_url:
        cache_filename = f"catalogue-page-{page_num}.html"
        html, was_cached = fetch(current_url, cache_filename)
        if not was_cached:
            time.sleep(0.5)

        soup = BeautifulSoup(html, 'html.parser')

        for article in soup.select('article.product_pod h3 a'):
            relative_href = article.get('href')
            if relative_href:
                book_urls.append(urljoin(current_url, relative_href))

        next_link = soup.select_one("li.next a")
        if next_link and next_link.get('href'):
            page_num += 1
            current_url = urljoin(current_url, next_link['href'])
        else:
            current_url = None

    unique_urls = list(dict.fromkeys(book_urls))
    print(f"catalogue_pages={page_num}")
    print(f"discovered={len(book_urls)}")
    print(f"unique_urls={len(unique_urls)}")
    return unique_urls
if __name__ == "__main__":
    urls = discover_book_urls()
       