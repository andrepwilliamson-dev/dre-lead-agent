"""
One-time setup — creates the Lead Intelligence database in your Notion workspace.
Run once: python setup.py

You'll need:
- NOTION_TOKEN in your .env
- A Notion page ID to create the database inside (NOTION_PARENT_PAGE_ID)
"""
import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

NOTION_VERSION = "2022-06-28"


def headers():
    return {
        "Authorization": f"Bearer {os.environ['NOTION_TOKEN']}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_VERSION,
    }


def create_database(parent_page_id: str) -> str:
    """Creates the Lead Intelligence database. Returns the database ID."""

    payload = {
        "parent": {"type": "page_id", "page_id": parent_page_id},
        "title": [{"type": "text", "text": {"content": "🎯 Lead Intelligence — Dre"}}],
        "properties": {
            "Name": {"title": {}},
            "Company": {"rich_text": {}},
            "Source": {
                "select": {
                    "options": [
                        {"name": "Indeed", "color": "blue"},
                        {"name": "LinkedIn", "color": "purple"},
                        {"name": "ProductionHUB", "color": "green"},
                        {"name": "TechCrunch Startups", "color": "orange"},
                        {"name": "TechCrunch Funding", "color": "orange"},
                        {"name": "Betakit (Canadian Tech)", "color": "red"},
                        {"name": "Manual", "color": "gray"},
                    ]
                }
            },
            "Location": {"rich_text": {}},
            "Signal": {"rich_text": {}},
            "AI Score": {"number": {"format": "number"}},
            "Priority": {
                "select": {
                    "options": [
                        {"name": "🔥 Hot", "color": "red"},
                        {"name": "⚡ Strong", "color": "orange"},
                        {"name": "👀 Worth a Look", "color": "yellow"},
                        {"name": "❄️ Low", "color": "blue"},
                    ]
                }
            },
            "Status": {
                "select": {
                    "options": [
                        {"name": "New", "color": "gray"},
                        {"name": "Pitched", "color": "blue"},
                        {"name": "In Talks", "color": "purple"},
                        {"name": "Booked", "color": "green"},
                        {"name": "Interested", "color": "yellow"},
                        {"name": "Not a Fit", "color": "red"},
                        {"name": "No Response", "color": "gray"},
                        {"name": "Skip", "color": "gray"},
                    ]
                }
            },
            "URL": {"url": {}},
            "Date Found": {"date": {}},
            "Notes": {"rich_text": {}},
        },
    }

    resp = requests.post(
        "https://api.notion.com/v1/databases",
        json=payload,
        headers=headers(),
        timeout=15,
    )

    if resp.status_code not in (200, 201):
        print(f"ERROR: {resp.status_code} — {resp.text}")
        sys.exit(1)

    db_id = resp.json()["id"]
    return db_id


def main():
    parent_page_id = os.environ.get("NOTION_PARENT_PAGE_ID", "").strip()

    if not parent_page_id:
        print("""
ERROR: NOTION_PARENT_PAGE_ID not set.

To find your page ID:
1. Open a Notion page where you want the database to live
2. Click Share → Copy link
3. The ID is the last part of the URL (32 characters, looks like: abc123def456...)
4. Add it to your .env file as NOTION_PARENT_PAGE_ID=your_page_id_here
        """)
        sys.exit(1)

    print("Creating Lead Intelligence database in Notion...")
    db_id = create_database(parent_page_id)

    print(f"""
✅ Database created successfully!

Your NOTION_DATABASE_ID is:
{db_id}

Add this to your .env file:
NOTION_DATABASE_ID={db_id}

And add it to GitHub Secrets as NOTION_DATABASE_ID.
    """)


if __name__ == "__main__":
    main()
