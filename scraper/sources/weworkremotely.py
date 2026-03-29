"""
We Work Remotely — remote content, creative, and marketing roles.
Strong source for brands and content studios hiring remote producers.
"""
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from scraper.filters import is_relevant

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; research-bot/1.0)",
}

# WWR has public RSS feeds per category
RSS_FEEDS = [
    {
        "url": "https://weworkremotely.com/categories/remote-marketing-jobs.rss",
        "category": "Marketing"
    },
    {
        "url": "https://weworkremotely.com/categories/remote-design-jobs.rss",
        "category": "Design & Creative"
    },
]


def fetch() -> list[dict]:
    results = []
    seen = set()

    for feed in RSS_FEEDS:
        try:
            resp = requests.get(feed["url"], headers=HEADERS, timeout=15)
            if resp.status_code != 200:
                print(f"[WWR] HTTP {resp.status_code} for {feed['category']}")
                continue

            root = ET.fromstring(resp.text)
            items = root.findall(".//item")

            for item in items:
                title = item.findtext("title", "").strip()
                link = item.findtext("link", "").strip()
                company_region = title.split(":")
                
                if len(company_region) >= 2:
                    company = company_region[0].strip()
                    role = ":".join(company_region[1:]).strip()
                else:
                    company = "Unknown"
                    role = title

                if not is_relevant(role) or link in seen:
                    continue

                seen.add(link)
                results.append({
                    "name": role,
                    "company": company,
                    "location": "Remote",
                    "url": link,
                    "source": "We Work Remotely",
                    "signal_type": "Job Posting",
                    "signal_detail": f"Remote role: {role} at {company}",
                    "date_found": datetime.now(timezone.utc).date().isoformat(),
                })

        except Exception as e:
            print(f"[WWR] Error for {feed['category']}: {e}")

    print(f"[We Work Remotely] Found {len(results)} leads")
    return results
