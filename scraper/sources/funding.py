"""
TechCrunch Crunchbase RSS — scrapes startup funding announcements.
Method: RSS feed
Signal: Companies that just raised money are about to spend on content/marketing.
Targets: Canadian and US startups, Series A/B/C raises
"""
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from scraper.filters import is_relevant

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; research-bot/1.0)",
}

RSS_FEEDS = [
    {
        "url": "https://techcrunch.com/category/startups/feed/",
        "name": "TechCrunch Startups",
    },
    {
        "url": "https://techcrunch.com/tag/funding/feed/",
        "name": "TechCrunch Funding",
    },
    {
        "url": "https://betakit.com/feed/",
        "name": "Betakit (Canadian Tech)",
    },
]

FUNDING_KEYWORDS = [
    "raises", "raised", "funding", "series a", "series b", "series c",
    "seed round", "million", "investment", "backed", "venture"
]

CONTENT_ADJACENT_KEYWORDS = [
    "media", "content", "marketing", "brand", "creative", "advertising",
    "social", "video", "platform", "studio", "entertainment", "streaming",
    "fintech", "consumer", "ecommerce", "retail", "health", "wellness",
    "food", "fashion", "beauty", "lifestyle", "travel", "education"
]


def fetch() -> list[dict]:
    results = []
    seen_urls = set()

    for feed in RSS_FEEDS:
        try:
            items = _parse_rss(feed["url"], feed["name"])
            for item in items:
                if item["url"] not in seen_urls:
                    seen_urls.add(item["url"])
                    results.append(item)
        except Exception as e:
            print(f"[Funding] Error fetching {feed['name']}: {e}")

    print(f"[Funding] Found {len(results)} funding signals")
    return results


def _parse_rss(url: str, source_name: str) -> list[dict]:
    results = []

    resp = requests.get(url, headers=HEADERS, timeout=15)
    if resp.status_code != 200:
        print(f"[Funding] Got status {resp.status_code} for {url}")
        return []

    try:
        root = ET.fromstring(resp.text)
    except ET.ParseError as e:
        print(f"[Funding] XML parse error for {url}: {e}")
        return []

    for item in root.findall(".//item"):
        title = item.findtext("title", "").strip()
        link = item.findtext("link", "").strip()
        description = item.findtext("description", "").strip()
        pub_date = item.findtext("pubDate", "").strip()

        combined = (title + " " + description).lower()

        # Must mention funding
        has_funding = any(kw in combined for kw in FUNDING_KEYWORDS)
        if not has_funding:
            continue

        # Prefer content-adjacent industries
        is_content_adjacent = any(kw in combined for kw in CONTENT_ADJACENT_KEYWORDS)

        results.append({
            "title": title,
            "company": _extract_company(title),
            "location": "Various",
            "description": description[:300] if description else "",
            "signal": f"Funding announcement: {title}",
            "source": source_name,
            "url": link,
            "date_found": datetime.now(timezone.utc).date().isoformat(),
            "is_content_adjacent": is_content_adjacent,
        })

    return results


def _extract_company(title: str) -> str:
    """Best-effort company name extraction from funding headline."""
    # Common patterns: "Acme raises $5M" or "Acme, a Toronto startup, raises..."
    import re
    match = re.match(r"^([A-Z][^\,\.]+?)(?:\s+raises|\s+secures|\s+closes|\s+announces|\,)", title)
    if match:
        return match.group(1).strip()
    return title.split(" ")[0] if title else "Unknown"
