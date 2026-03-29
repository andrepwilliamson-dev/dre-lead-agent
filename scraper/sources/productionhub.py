"""
ProductionHUB — scrapes active production job listings.
Direct signal: companies actively producing content and need crew.
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from scraper.filters import is_relevant

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; research-bot/1.0)",
}

BASE_URL = "https://www.productionhub.com"
SEARCH_URL = f"{BASE_URL}/jobs/search?keywords=producer&location=canada&remote=1"


def fetch() -> list[dict]:
    results = []
    try:
        resp = requests.get(SEARCH_URL, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            print(f"[ProductionHUB] HTTP {resp.status_code}")
            return results

        soup = BeautifulSoup(resp.text, "lxml")
        listings = soup.select(".job-listing, .listing-item, article.job")

        for item in listings:
            title_el = item.select_one("h2, h3, .job-title, .listing-title")
            company_el = item.select_one(".company-name, .employer")
            link_el = item.select_one("a[href]")

            if not title_el:
                continue

            title = title_el.get_text(strip=True)
            company = company_el.get_text(strip=True) if company_el else "Unknown"
            href = link_el["href"] if link_el else ""
            if href and not href.startswith("http"):
                href = f"{BASE_URL}{href}"

            if not is_relevant(title):
                continue

            results.append({
                "name": title,
                "company": company,
                "location": "Canada / Remote",
                "url": href,
                "source": "ProductionHUB",
                "signal_type": "Production Gig",
                "signal_detail": f"Active production listing: {title}",
                "date_found": datetime.now(timezone.utc).date().isoformat(),
            })

    except Exception as e:
        print(f"[ProductionHUB] Error: {e}")

    print(f"[ProductionHUB] Found {len(results)} leads")
    return results
