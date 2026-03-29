"""
Indeed — scrapes content production job postings for startups and mid-size brands.
Method: HTML scraping
Targets: Content Producer, Video Producer, Creative Director, Brand Content roles
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from scraper.filters import is_relevant

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

SEARCH_QUERIES = [
    ("content producer", "Toronto"),
    ("video producer", "Toronto"),
    ("branded content producer", "Canada"),
    ("content producer", "remote"),
    ("freelance producer", "Canada"),
    ("creative producer", "Toronto"),
]


def fetch() -> list[dict]:
    results = []
    seen_urls = set()

    for query, location in SEARCH_QUERIES:
        try:
            items = _scrape_indeed(query, location)
            for item in items:
                if item["url"] not in seen_urls and is_relevant(item["title"] + " " + item.get("description", "")):
                    seen_urls.add(item["url"])
                    results.append(item)
        except Exception as e:
            print(f"[Indeed] Error scraping '{query}' in '{location}': {e}")

    print(f"[Indeed] Found {len(results)} relevant listings")
    return results


def _scrape_indeed(query: str, location: str) -> list[dict]:
    results = []
    params = {
        "q": query,
        "l": location,
        "sort": "date",
        "fromage": "3",  # last 3 days only
    }

    resp = requests.get(
        "https://ca.indeed.com/jobs",
        params=params,
        headers=HEADERS,
        timeout=15
    )

    if resp.status_code != 200:
        print(f"[Indeed] Got status {resp.status_code} for '{query}'")
        return []

    soup = BeautifulSoup(resp.text, "lxml")
    cards = soup.select("[class*='job_seen_beacon'], [class*='jobsearch-ResultsList'] li")

    for card in cards:
        try:
            title_el = card.select_one("h2 a, [class*='jobTitle'] a")
            company_el = card.select_one("[class*='companyName'], [data-testid='company-name']")
            location_el = card.select_one("[class*='companyLocation'], [data-testid='text-location']")
            snippet_el = card.select_one("[class*='job-snippet'], [class*='underShelfFooter']")

            if not title_el:
                continue

            title = title_el.get_text(strip=True)
            href = title_el.get("href", "")
            url = f"https://ca.indeed.com{href}" if href.startswith("/") else href

            results.append({
                "title": title,
                "company": company_el.get_text(strip=True) if company_el else "Unknown",
                "location": location_el.get_text(strip=True) if location_el else location,
                "description": snippet_el.get_text(strip=True) if snippet_el else "",
                "signal": f"Job posting: {title}",
                "source": "Indeed",
                "url": url,
                "date_found": datetime.now(timezone.utc).date().isoformat(),
            })
        except Exception:
            continue

    return results
