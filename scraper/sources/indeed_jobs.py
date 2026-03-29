"""
Indeed Jobs — scrapes branded content / production job postings.
These signal companies actively hiring producers = need freelance help NOW.
Uses Indeed MCP-compatible public RSS feeds.
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from scraper.filters import is_relevant

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; research-bot/1.0)",
}

SEARCH_QUERIES = [
    "content producer",
    "video producer branded content",
    "creative producer",
    "freelance producer",
    "social media content producer",
]

LOCATIONS = ["Toronto", "Canada", "Remote"]


def fetch() -> list[dict]:
    results = []
    seen_urls = set()

    for query in SEARCH_QUERIES:
        for location in LOCATIONS:
            try:
                url = (
                    f"https://ca.indeed.com/jobs"
                    f"?q={requests.utils.quote(query)}"
                    f"&l={requests.utils.quote(location)}"
                    f"&fromage=7"  # last 7 days only
                    f"&sort=date"
                )
                resp = requests.get(url, headers=HEADERS, timeout=15)
                if resp.status_code != 200:
                    continue

                soup = BeautifulSoup(resp.text, "lxml")
                cards = soup.select("[data-testid='slider_item'], .job_seen_beacon, .jobsearch-SerpJobCard")

                for card in cards:
                    title_el = card.select_one("h2 a, .jobTitle a, a[data-jk]")
                    company_el = card.select_one("[data-testid='company-name'], .companyName")
                    location_el = card.select_one("[data-testid='text-location'], .companyLocation")
                    link_el = card.select_one("h2 a, .jobTitle a")

                    if not title_el:
                        continue

                    title = title_el.get_text(strip=True)
                    company = company_el.get_text(strip=True) if company_el else "Unknown"
                    loc = location_el.get_text(strip=True) if location_el else location
                    href = title_el.get("href", "")
                    if href and not href.startswith("http"):
                        href = f"https://ca.indeed.com{href}"

                    if not is_relevant(title):
                        continue
                    if href in seen_urls:
                        continue

                    seen_urls.add(href)
                    results.append({
                        "name": title,
                        "company": company,
                        "location": loc,
                        "url": href,
                        "source": "Indeed CA",
                        "signal_type": "Job Posting",
                        "signal_detail": f"Actively hiring: {title}",
                        "date_found": datetime.now(timezone.utc).date().isoformat(),
                    })

            except Exception as e:
                print(f"[Indeed] Error for '{query}' in '{location}': {e}")

    print(f"[Indeed] Found {len(results)} leads")
    return results
