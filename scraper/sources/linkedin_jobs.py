"""
LinkedIn Job Search (public) — scrapes content/production roles from brands and studios.
Method: LinkedIn public job search (no auth required for basic listings)
Signal: Companies posting for content leads = they need production support now.
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from scraper.filters import is_relevant
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

SEARCH_QUERIES = [
    {"keywords": "content producer", "location": "Toronto, Ontario, Canada"},
    {"keywords": "video producer brand", "location": "Canada"},
    {"keywords": "branded content producer freelance", "location": "Canada"},
    {"keywords": "creative producer", "location": "Toronto, Ontario, Canada"},
    {"keywords": "head of content", "location": "Toronto, Ontario, Canada"},
    {"keywords": "content producer", "location": "United States"},
]


def fetch() -> list[dict]:
    results = []
    seen_urls = set()

    for query in SEARCH_QUERIES:
        try:
            items = _scrape_linkedin(query["keywords"], query["location"])
            for item in items:
                if item["url"] not in seen_urls and is_relevant(item["title"]):
                    seen_urls.add(item["url"])
                    results.append(item)
            time.sleep(2)  # Respectful rate limiting
        except Exception as e:
            print(f"[LinkedIn] Error for '{query['keywords']}': {e}")

    print(f"[LinkedIn] Found {len(results)} listings")
    return results


def _scrape_linkedin(keywords: str, location: str) -> list[dict]:
    results = []

    params = {
        "keywords": keywords,
        "location": location,
        "f_TPR": "r86400",  # Last 24 hours
        "sortBy": "DD",
    }

    resp = requests.get(
        "https://www.linkedin.com/jobs/search",
        params=params,
        headers=HEADERS,
        timeout=15
    )

    if resp.status_code != 200:
        print(f"[LinkedIn] Got status {resp.status_code}")
        return []

    soup = BeautifulSoup(resp.text, "lxml")
    cards = soup.select(".job-search-card, .base-card, [class*='job-card']")

    for card in cards:
        try:
            title_el = card.select_one("h3, .base-search-card__title, [class*='job-title']")
            company_el = card.select_one("h4, .base-search-card__subtitle, [class*='company']")
            location_el = card.select_one(".job-search-card__location, [class*='location']")
            link_el = card.select_one("a[href]")

            if not title_el or not link_el:
                continue

            title = title_el.get_text(strip=True)
            href = link_el.get("href", "")
            # Clean LinkedIn tracking params
            clean_url = href.split("?")[0] if "?" in href else href

            results.append({
                "title": title,
                "company": company_el.get_text(strip=True) if company_el else "Unknown",
                "location": location_el.get_text(strip=True) if location_el else location,
                "description": "",
                "signal": f"LinkedIn job posting: {title}",
                "source": "LinkedIn",
                "url": clean_url,
                "date_found": datetime.now(timezone.utc).date().isoformat(),
            })
        except Exception:
            continue

    return results
