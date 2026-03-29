"""
BetaKit — Canadian startup news focused on consumer/lifestyle brands.
Filters specifically for industries where branded content is essential.
"""
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; research-bot/1.0)",
}

# Industries where startups NEED video/branded content
CONTENT_INDUSTRIES = [
    "lifestyle", "consumer", "fashion", "beauty", "food", "beverage",
    "fitness", "wellness", "health", "travel", "hospitality", "retail",
    "ecommerce", "e-commerce", "entertainment", "media", "music",
    "gaming", "sports", "restaurant", "apparel", "skincare", "alcohol",
    "beverage", "pet", "baby", "home", "furniture", "dating", "social"
]

FUNDING_KEYWORDS = [
    "raises", "raised", "funding", "seed", "series a", "series b",
    "million", "investment", "backed", "venture", "round", "capital"
]

# Industries to explicitly exclude
EXCLUDE_INDUSTRIES = [
    "cybersecurity", "enterprise", "b2b", "saas", "fintech banking",
    "insurance", "legal", "accounting", "logistics", "supply chain",
    "mining", "oil", "gas", "pharmaceutical", "biotech", "medtech"
]


def fetch() -> list[dict]:
    results = []

    try:
        resp = requests.get("https://betakit.com/feed/", headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            print(f"[BetaKit] HTTP {resp.status_code}")
            return results

        root = ET.fromstring(resp.text)
        items = root.findall(".//item")

        for item in items:
            title = item.findtext("title", "").strip()
            link = item.findtext("link", "").strip()
            description = item.findtext("description", "").strip()
            combined = f"{title} {description}".lower()

            # Must mention funding
            if not any(kw in combined for kw in FUNDING_KEYWORDS):
                continue

            # Must not be in excluded industries
            if any(ex in combined for ex in EXCLUDE_INDUSTRIES):
                continue

            # Must be in a content-friendly industry
            industry = next((ind for ind in CONTENT_INDUSTRIES if ind in combined), None)
            if not industry:
                continue

            company = _extract_company(title)
            results.append({
                "name": title,
                "company": company,
                "location": "Canada",
                "url": link,
                "source": "BetaKit",
                "signal_type": "Funding Announcement",
                "signal_detail": f"Canadian {industry} startup just raised — content budget incoming.",
                "date_found": datetime.now(timezone.utc).date().isoformat(),
            })

    except Exception as e:
        print(f"[BetaKit] Error: {e}")

    print(f"[BetaKit] Found {len(results)} leads")
    return results


def _extract_company(title: str) -> str:
    for trigger in ["raises", "secures", "closes", "announces", "gets", "raised"]:
        if trigger in title.lower():
            idx = title.lower().index(trigger)
            return title[:idx].strip().title()
    return title.split(" ")[0]
