# Polite Scraper — Books to Scrape

## Target classification
[Your Stage 0 section — site, why, scope, robots.txt result, the closing sentence]

## How to run
\`\`\`bash
git clone <your-repo-url>
cd scraper
pip install -r requirements.txt
python src/main.py
\`\`\`
Produces `output/books.json`, `output/errors.json`, and `output/run-report.json`.

## Lane
Python 3.10+, using `requests`, `beautifulsoup4`, `pydantic`.

## Record schema
| Field | Type | Notes |
|---|---|---|
| title | string | |
| product_url | URL | canonical identity |
| price_text | string | raw, e.g. "£51.77" |
| price_gbp | float | normalized |
| availability_text | string | |
| rating_text | string or null | |
| description | string or null | some books have none |
| source_page | URL | catalogue page it was discovered on |
| fetched_at | ISO timestamp (UTC) | |

## Politeness rules
- Identifying User-Agent: `FlyRankInternshipA9/1.0 (+<your repo link>)`
- 10s timeout per request
- 500ms minimum delay between real (non-cached) requests
- Status code checked before parsing; only 200 is treated as success
- Local HTML cache — during development, the site is hit once per page, never repeatedly

## Sample run report
\`\`\`json
[paste a real run-report.json here]
\`\`\`

## Why no browser was needed
The book data (title, price, availability, description) is present directly in the server-rendered HTML — view-source on any page shows it plainly. A headless browser like Playwright would add startup cost and memory overhead for zero benefit here, since there's no JavaScript rendering step between the server response and the visible data.

## Ethics note
This scraper only touches a purpose-built public sandbox (Books to Scrape). In general: prefer an official API when one exists, never bypass logins/paywalls/CAPTCHAs, collect only the data actually needed, and identify yourself honestly via User-Agent.

## Known limitation
[Pick one honestly — e.g. "Retry logic is a single retry with a fixed 1s wait, not exponential backoff — that's planned for A16" or "Rating is parsed from a CSS class name, which is a bit fragile if the site changes its markup."]



## AI vs me

### My prompt (given to AI in isolation, without re-reading the assignment)

Act as a senior backend engineer. Build a Python web scraper/crawler targeting
https://books.toscrape.com.

Scope: Crawl only the first 3 catalogue pages (follow the site's own "next"
pagination link — don't hardcode page URLs), collecting all book detail page
URLs from those 3 pages (should total 60 unique books).

Raw extraction — for each book page, extract exactly these 8 fields:
title, product_url, price_text, availability_text, rating_text, description,
source_page, fetched_at
- product_url must be an absolute URL (resolve relative links properly, e.g.
  with urljoin, not string concatenation)
- source_page = the catalogue page the book link was discovered on (absolute URL)
- fetched_at = current UTC timestamp, ISO format
- description can be null — some books have none; never invent text

Politeness requirements:
- Send a custom User-Agent: FlyRankInternshipA9/1.0 (+link-to-repo)
- Each HTTP request must have a 10-second timeout (separate concern from the
  delay below)
- Wait at least 500ms between real network requests (not needed for cache hits)
- Cache every fetched page's HTML to a local cache/ directory, keyed by page
  — on rerun, read from cache instead of hitting the network again
- Check the HTTP status code before parsing; only 200 is treated as success

Cleaning/normalization:
- Convert price_text (e.g. "£51.77") into a numeric price_gbp field using
  regex, keeping the original price_text too
- Treat product_url as the record's unique identity — deduplicate by it

Validation:
- Define a schema (use Pydantic) requiring: title (str), product_url (valid
  URL), price_text (str), price_gbp (float), availability_text (str),
  rating_text (str or null), description (str or null), source_page (valid
  URL), fetched_at (str)
- Validate every record before storing. Valid records go to output/books.json;
  invalid records go to output/errors.json along with the reason they failed
- Running the scraper twice must produce the same 60 records, never
  duplicates (idempotent)

Failure handling:
- Each page must be fetched independently — one broken/failed page must not
  crash the whole run
- Retry once on timeout or 5xx server errors (with a short wait before
  retrying); do NOT retry on 404 or 403
- Log every failed page with its URL and reason

Reporting:
- After every run, write output/run-report.json containing: start time,
  duration in seconds, catalogue pages fetched, total detail pages attempted,
  valid record count, invalid record count, failed page count, and failed
  page details

Stack: Python 3.10+, requests for HTTP, BeautifulSoup (bs4) for HTML parsing,
pydantic for schema validation. Single entry file is fine.

### Checkpoint comparison

| Checkpoint | My version | AI version |
|---|---|---|
| catalogue_pages | 3 | 3 |
| unique book URLs | 60 | 60 |
| valid records (first run) | 60 | 60 |
| valid records (rerun) | 60 (idempotent) | 60 (idempotent) |
| failed page injection test | 60 good + 1 failed, run survives | 60 good + 1 failed, run survives — identical behavior |

Both versions pass every checkpoint identically. The difference is in *how* they get there.

### What the AI did better — and do I understand it?

1. **Cache filenames use a SHA-256 hash of the URL** instead of slicing the URL path for a slug (mine: `a-light-in-the-attic_1000.html`, AI's: `detail-3f9a2b8c1d4e5f60.html`). My slug approach assumes a fixed URL shape and could break or produce an invalid filename if a URL ever looked different. A hash always produces a safe, fixed-length filename regardless of structure. Trade-off: mine is human-readable and easier to debug by eye; the AI's is opaque but more robust. I understand this fully — it's a reasonable engineering trade-off, not something mysterious.

2. **`discover_book_urls()` catches failures on the catalogue pages themselves and breaks the loop cleanly**, instead of crashing. My version only wraps *detail page* extraction in a safe wrapper (`extract_book_safe`) — if catalogue page 2 itself failed to fetch, my whole script would crash with an unhandled exception. This is a genuine gap in my error handling that I hadn't considered, and the AI's version caught it even though my prompt never explicitly asked for it.

3. **More defensive extraction** — the AI's `extract_book` explicitly checks whether `title`/`price`/`availability` tags are missing and raises a clear `ValueError` with a message, instead of crashing with a raw `AttributeError` on `.get_text()` like mine would. Easier to diagnose from a failure log.

### What it got wrong or silently skipped

1. **Neither version tracks cache-hit count in the run report**, even though "cache hits" is explicitly one of the honest numbers Stage 5 asks for. This wasn't in my prompt, so this isn't really the AI "getting it wrong" — it's a direct gap in my spec that carried straight through.
2. Otherwise, on every checkpoint I actually tested (record count, idempotency, failure survival), the AI's output behaved identically to mine. It didn't hallucinate fields, skip validation, or silently drop the delay/timeout distinction I originally got wrong in draft 1 of my prompt.

### What my prompt forgot to say

1. Never asked for cache-hit tracking in the run report.
2. Never specified what should happen if a *catalogue page itself* fails (only covered detail page failures) — the AI handled it better than mine anyway, but that was a reasonable default on its part, not something my prompt asked for.
3. Never specified a cache filename convention, so the AI made its own reasonable choice (hashing) rather than matching mine.

### The rematch

For a second pass, I'd add two lines to my prompt:
- "Track and report the number of cache hits per run, separately from fresh fetches, in run-report.json."
- "Catalogue page fetch failures must also be caught and logged individually, the same way detail page failures are — not allowed to crash the whole run."

Both are direct fixes for gaps this rematch actually surfaced, not guesses.