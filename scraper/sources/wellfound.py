"""
Wellfound (AngelList) — funded startups hiring for content/creative roles.
These are exactly Dre's sweet spot: funded, building, need production.
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from scraper.filters import is_relevant

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

SEARCH_QUERIES = [
    "content-producer",
    "video-producer",
    "creative-producer",
    "social-media-producer",
    "brand-content",
]


def fetch() -> list[dict]:
    results = []
    seen = set()

    for query in SEARCH_QUERIES:
        try:
            url = f"https://wellfound.com/jobs?q={query}&remote=true"
            resp = requests.get(url, headers=HEADERS, timeout=15)
            if resp.status_code != 200:
                print(f"[Wellfound] HTTP {resp.status_code} for {query}")
                continue

            soup = BeautifulSoup(resp.text, "lxml")

            # Wellfound job cards
            cards = soup.select("[class*='JobListing'], [data-test='JobListing'], .job-listing")

            for card in cards:
                title_el = card.select_one("h2, h3, [class*='title'], [class*='Title']")
                company_el = card.select_one("[class*='company'], [class*='Company'], [class*='startup']")
                link_el = card.select_one("a[href]")

                if not title_el:
                    continue

                title = title_el.get_text(strip=True)
                company = company_el.get_text(strip=True) if company_el else "Unknown"
                href = link_el["href"] if link_el else ""
                if href and not href.startswith("http"):
                    href = f"https://wellfound.com{href}"

                if not is_relevant(title) or href in seen:
                    continue

                seen.add(href)
                results.append({
                    "name": title,
                    "company": company,
                    "location": "Remote / Various",
                    "url": href,
                    "source": "Wellfound",
                    "signal_type": "Job Posting",
                    "signal_detail": f"Funded startup hiring: {title}",
                    "date_found": datetime.now(timezone.utc).date().isoformat(),
                })

        except Exception as e:
            print(f"[Wellfound] Error for '{query}': {e}")

    print(f"[Wellfound] Found {len(results)} leads")
    return results
