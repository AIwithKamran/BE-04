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