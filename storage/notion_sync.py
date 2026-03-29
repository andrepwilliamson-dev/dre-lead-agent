"""
Notion storage — syncs leads into Dre's Lead Intelligence database.
Deduplicates by URL before every push.
"""
import os
import requests
from datetime import datetime

NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "")
NOTION_DB_ID = os.environ.get("NOTION_DATABASE_ID", "")

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}


def _get_existing_urls() -> set:
    """Fetch all URLs already in the database to deduplicate."""
    existing = set()
    url = f"https://api.notion.com/v1/databases/{NOTION_DB_ID}/query"
    cursor = None

    while True:
        body = {"page_size": 100}
        if cursor:
            body["start_cursor"] = cursor

        resp = requests.post(url, headers=HEADERS, json=body, timeout=15)
        if resp.status_code != 200:
            print(f"[Notion] Failed to fetch existing: {resp.status_code}")
            break

        data = resp.json()
        for page in data.get("results", []):
            props = page.get("properties", {})
            url_prop = props.get("URL", {}).get("url", "")
            if url_prop:
                existing.add(url_prop)

        if not data.get("has_more"):
            break
        cursor = data.get("next_cursor")

    return existing


def sync(db_id: str, items: list[dict]) -> tuple[int, int]:
    """Push new leads to Notion. Returns (added, skipped)."""
    if not NOTION_TOKEN or not db_id:
        print("[Notion] Missing NOTION_TOKEN or NOTION_DATABASE_ID")
        return 0, 0

    global NOTION_DB_ID
    NOTION_DB_ID = db_id

    existing_urls = _get_existing_urls()
    added, skipped = 0, 0

    for item in items:
        item_url = item.get("url", "")
        if item_url and item_url in existing_urls:
            skipped += 1
            continue

        score = item.get("ai_score", 0)
        if score < 5:
            skipped += 1
            continue

        success = _create_page(item)
        if success:
            added += 1
            if item_url:
                existing_urls.add(item_url)
        else:
            skipped += 1

    return added, skipped


def _create_page(item: dict) -> bool:
    """Create a single Notion page for a lead."""
    score = item.get("ai_score", 0)
    priority = "🔥 Hot" if score >= 8 else "⭐ Strong" if score >= 6 else "👀 Review"

    payload = {
        "parent": {"database_id": NOTION_DB_ID},
        "properties": {
            "Name": {
                "title": [{"text": {"content": item.get("name", "Untitled")}}]
            },
            "Company": {
                "rich_text": [{"text": {"content": item.get("company", "")}}]
            },
            "Source": {
                "select": {"name": item.get("source", "Unknown")}
            },
            "Signal Type": {
                "select": {"name": item.get("signal_type", "Job Posting")}
            },
            "Signal Detail": {
                "rich_text": [{"text": {"content": item.get("signal_detail", "")}}]
            },
            "Why Relevant": {
                "rich_text": [{"text": {"content": item.get("why_relevant", "")}}]
            },
            "Pitch Angle": {
                "rich_text": [{"text": {"content": item.get("pitch_angle", "")}}]
            },
            "Location": {
                "rich_text": [{"text": {"content": item.get("location", "")}}]
            },
            "URL": {
                "url": item.get("url") or None
            },
            "AI Score": {
                "number": score
            },
            "Priority": {
                "select": {"name": priority}
            },
            "Status": {
                "select": {"name": "New Lead"}
            },
            "Date Found": {
                "date": {"start": item.get("date_found", datetime.now().date().isoformat())}
            },
        }
    }

    resp = requests.post(
        "https://api.notion.com/v1/pages",
        headers=HEADERS,
        json=payload,
        timeout=15,
    )

    if resp.status_code == 200:
        return True
    else:
        print(f"[Notion] Failed to create page: {resp.status_code} — {resp.text[:200]}")
        return False
