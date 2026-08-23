import os
import time
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from datetime import datetime, timezone


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


MAX_CATALOGUE_PAGES = 3


def extract_book(url, source_page):
    """Fetch one book detail page and extract raw fields (no cleaning yet)."""
    # Build a safe cache filename from the URL
    cache_filename = url.rstrip("/").split("/")[-2] + ".html"

    html, was_cached = fetch(url, cache_filename)
    if not was_cached:
        time.sleep(0.5)

    soup = BeautifulSoup(html, "html.parser")

    # Aim selectors at the product area, not the whole document
    product = soup.select_one("div.product_main")
    table = soup.select_one("table.table.table-striped")
    description_tag = soup.select_one("#product_description ~ p")

    title = product.select_one("h1").get_text(strip=True)
    price_text = product.select_one("p.price_color").get_text(strip=True)
    availability_text = product.select_one("p.availability").get_text(strip=True)

    # Rating is stored as a CSS class like "star-rating Three"
    rating_tag = product.select_one("p.star_rating, p.star-rating")
    rating_text = None
    if rating_tag:
        classes = rating_tag.get("class", [])
        rating_text = next((c for c in classes if c != "star-rating"), None)

    description = description_tag.get_text(strip=True) if description_tag else None

    record = {
        "title": title,
        "product_url": url,
        "price_text": price_text,
        "availability_text": availability_text,
        "rating_text": rating_text,
        "description": description,
        "source_page": source_page,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }

    return record


def discover_book_urls():
    """Follow catalogue pages via their own 'next' links, collecting unique book URLs.
    Scope limited to the first MAX_CATALOGUE_PAGES pages, per assignment."""
    book_urls = []
    page_num = 1
    current_url = BASE_CATALOGUE_URL

    while current_url and page_num <= MAX_CATALOGUE_PAGES:
        cache_filename = f"catalogue-page-{page_num}.html"
        html, was_cached = fetch(current_url, cache_filename)
        if not was_cached:
            time.sleep(0.5)

        soup = BeautifulSoup(html, "html.parser")

        for article in soup.select("article.product_pod h3 a"):
            relative_href = article["href"]
            absolute_url = urljoin(current_url, relative_href)
            book_urls.append(absolute_url)

        next_link = soup.select_one("li.next a")
        if next_link and page_num < MAX_CATALOGUE_PAGES:
            page_num += 1
            current_url = urljoin(current_url, next_link["href"])
        else:
            current_url = None

    unique_urls = list(dict.fromkeys(book_urls))

    print(f"catalogue_pages={page_num}")
    print(f"discovered={len(book_urls)}")
    print(f"unique_urls={len(unique_urls)}")

    return unique_urls

def discover_book_urls():
    book_entries = []  # list of (book_url, source_catalogue_page)
    page_num = 1
    current_url = BASE_CATALOGUE_URL

    while current_url and page_num <= MAX_CATALOGUE_PAGES:
        cache_filename = f"catalogue-page-{page_num}.html"
        html, was_cached = fetch(current_url, cache_filename)
        if not was_cached:
            time.sleep(0.5)

        soup = BeautifulSoup(html, "html.parser")

        for article in soup.select("article.product_pod h3 a"):
            relative_href = article["href"]
            absolute_url = urljoin(current_url, relative_href)
            book_entries.append((absolute_url, current_url))

        next_link = soup.select_one("li.next a")
        if next_link and page_num < MAX_CATALOGUE_PAGES:
            page_num += 1
            current_url = urljoin(current_url, next_link["href"])
        else:
            current_url = None

    # De-duplicate by book URL, keeping first source page seen
    seen = {}
    for book_url, source_page in book_entries:
        if book_url not in seen:
            seen[book_url] = source_page

    print(f"catalogue_pages={page_num}")
    print(f"discovered={len(book_entries)}")
    print(f"unique_urls={len(seen)}")

    return seen  # dict: book_url -> source_page

if __name__ == "__main__":
    url_map = discover_book_urls()
    records = [extract_book(url, source) for url, source in url_map.items()]

    print(f"detail_pages={len(records)}")
    print(records[0])
       