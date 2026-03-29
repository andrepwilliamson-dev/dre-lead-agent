"""
Startup Funding News — monitors TechCrunch and BetaKit RSS for Canadian/consumer startups
that just raised money. Funding = budget = content needs incoming.
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
        "name": "BetaKit",
        "url": "https://betakit.com/feed/",
        "focus": "Canadian startups",
    },
    {
        "name": "TechCrunch Startups",
        "url": "https://techcrunch.com/category/startups/feed/",
        "focus": "Global startups with consumer angle",
    },
]

FUNDING_KEYWORDS = [
    "raises", "funding", "seed", "series a", "series b",
    "million", "investment", "backed", "venture", "round"
]

CONTENT_INDUSTRIES = [
    "lifestyle", "consumer", "entertainment", "food", "beverage",
    "fashion", "beauty", "sports", "media", "music", "gaming",
    "health", "wellness", "travel", "retail", "e-commerce"
]


def fetch() -> list[dict]:
    results = []

    for feed in RSS_FEEDS:
        try:
            resp = requests.get(feed["url"], headers=HEADERS, timeout=15)
            if resp.status_code != 200:
                continue

            root = ET.fromstring(resp.text)
            items = root.findall(".//item")

            for item in items:
                title = item.findtext("title", "").strip()
                link = item.findtext("link", "").strip()
                description = item.findtext("description", "").strip()
                pub_date = item.findtext("pubDate", "").strip()

                combined = f"{title} {description}".lower()

                # Must mention funding
                if not any(kw in combined for kw in FUNDING_KEYWORDS):
                    continue

                # Should be in a content-friendly industry
                industry_match = next(
                    (ind for ind in CONTENT_INDUSTRIES if ind in combined), None
                )
                if not industry_match:
                    continue

                results.append({
                    "name": title,
                    "company": _extract_company(title),
                    "location": "Unknown — check listing",
                    "url": link,
                    "source": feed["name"],
                    "signal_type": "Funding Announcement",
                    "signal_detail": f"Just raised money — {industry_match} space. Budget incoming.",
                    "date_found": datetime.now(timezone.utc).date().isoformat(),
                })

        except Exception as e:
            print(f"[{feed['name']}] Error: {e}")

    print(f"[Startup Funding] Found {len(results)} leads")
    return results


def _extract_company(title: str) -> str:
    """Best-effort company extraction from headline."""
    for word in ["raises", "secures", "closes", "announces", "gets"]:
        if word in title.lower():
            return title.lower().split(word)[0].strip().title()
    return title.split(" ")[0]
