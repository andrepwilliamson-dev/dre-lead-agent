"""
One-time setup — creates the Lead Intelligence database in your Notion workspace.
Run this ONCE before the first agent run:
  python setup_notion.py
"""
import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "")
HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}


def get_parent_page_id() -> str:
    """Find a page to create the database under."""
    resp = requests.post(
        "https://api.notion.com/v1/search",
        headers=HEADERS,
        json={"filter": {"value": "page", "property": "object"}, "page_size": 10},
    )
    results = resp.json().get("results", [])
    if not results:
        print("ERROR: No pages found in your Notion workspace.")
        print("Create a page in Notion first, then re-run this script.")
        sys.exit(1)
    page = results[0]
    print(f"Using Notion page: {page.get('id')} as parent")
    return page["id"]


def create_database(parent_id: str) -> str:
    payload = {
        "parent": {"type": "page_id", "page_id": parent_id},
        "title": [{"type": "text", "text": {"content": "🎬 Lead Intelligence — Dre"}}],
        "properties": {
            "Name":          {"title": {}},
            "Company":       {"rich_text": {}},
            "Source":        {"select": {"options": [
                                {"name": "Indeed CA", "color": "blue"},
                                {"name": "ProductionHUB", "color": "orange"},
                                {"name": "BetaKit", "color": "green"},
                                {"name": "TechCrunch Startups", "color": "red"},
                             ]}},
            "Signal Type":   {"select": {"options": [
                                {"name": "Job Posting", "color": "purple"},
                                {"name": "Funding Announcement", "color": "yellow"},
                                {"name": "Production Gig", "color": "pink"},
                             ]}},
            "Signal Detail": {"rich_text": {}},
            "Why Relevant":  {"rich_text": {}},
            "Pitch Angle":   {"rich_text": {}},
            "Location":      {"rich_text": {}},
            "URL":           {"url": {}},
            "AI Score":      {"number": {"format": "number"}},
            "Priority":      {"select": {"options": [
                                {"name": "🔥 Hot", "color": "red"},
                                {"name": "⭐ Strong", "color": "yellow"},
                                {"name": "👀 Review", "color": "gray"},
                             ]}},
            "Status":        {"select": {"options": [
                                {"name": "New Lead", "color": "blue"},
                                {"name": "Pitched", "color": "purple"},
                                {"name": "In Conversation", "color": "green"},
                                {"name": "Booked", "color": "pink"},
                                {"name": "Hot Lead", "color": "red"},
                                {"name": "Skip", "color": "gray"},
                                {"name": "Not a Fit", "color": "default"},
                                {"name": "No Response", "color": "default"},
                             ]}},
            "Date Found":    {"date": {}},
        },
    }

    resp = requests.post("https://api.notion.com/v1/databases", headers=HEADERS, json=payload)
    if resp.status_code == 200:
        db_id = resp.json()["id"]
        print(f"\n✅ Database created successfully!")
        print(f"\n👉 Copy this Database ID into your GitHub Secrets as NOTION_DATABASE_ID:")
        print(f"\n   {db_id}\n")
        return db_id
    else:
        print(f"ERROR creating database: {resp.status_code}")
        print(resp.text)
        sys.exit(1)


if __name__ == "__main__":
    if not NOTION_TOKEN:
        print("ERROR: NOTION_TOKEN not set. Add it to your .env file.")
        sys.exit(1)

    print("Setting up your Lead Intelligence database in Notion...")
    parent_id = get_parent_page_id()
    create_database(parent_id)
