# 🎬 Dre's Lead Intelligence Agent

Automated lead finder for freelance branded content and production work.
Runs every morning, drops qualified leads into Notion, ready to pitch by 9am.

**Stack: Python · Gemini AI (free) · GitHub Actions (free) · Notion**

---

## What It Does

Monitors 3 sources daily:
- **Indeed CA** — companies posting for Content Producer, Video Producer, Creative Producer roles (they need freelance help NOW)
- **ProductionHUB** — active production gigs in Canada / Remote
- **BetaKit + TechCrunch** — startups that just raised funding in lifestyle/consumer/entertainment (budget is incoming)

AI scores each lead 1–10 for fit. Only scores 5+ land in Notion.
Each lead includes: Company, Signal, Why It's Relevant to You, and a suggested Pitch Angle.

---

## Setup (One Time — 20 minutes)

### Step 1: Get Your API Keys

**Notion Integration Token:**
1. Go to https://www.notion.so/my-integrations
2. Click "New Integration" → name it "Lead Agent"
3. Copy the token → save it

**Gemini API Key (Free):**
1. Go to https://aistudio.google.com/app/apikey
2. Create a new API key → copy it

### Step 2: Set Up Notion Database

```bash
# Clone this repo
git clone https://github.com/andrepwilliamson-dev/dre-lead-agent.git
cd dre-lead-agent

# Install dependencies
pip install -r requirements.txt

# Create your .env file
cp .env.example .env
# Edit .env and add your NOTION_TOKEN

# Run the setup script — creates your database in Notion
python setup_notion.py
```

Copy the Database ID it prints out — you'll need it in Step 3.

**Important:** Go to your Notion database page → click "..." → "Add connections" → add your integration.

### Step 3: Add GitHub Secrets

In your GitHub repo → Settings → Secrets and variables → Actions → New repository secret:

| Secret Name | Value |
|---|---|
| `NOTION_TOKEN` | Your Notion integration token |
| `NOTION_DATABASE_ID` | The ID from Step 2 |
| `GEMINI_API_KEY` | Your Gemini API key |

### Step 4: Push and Activate

```bash
git add .
git commit -m "Initial setup"
git push origin main
```

Go to GitHub → Actions → "Dre's Lead Intelligence Agent" → Run workflow (manual trigger to test).

---

## Daily Workflow

The agent runs automatically at 9am UTC (5am ET) every day.

**Your morning routine:**
1. Open Notion → Lead Intelligence database
2. Filter by "New Lead" status, sort by AI Score descending
3. Review 🔥 Hot and ⭐ Strong leads first
4. Write tailored pitches using the "Pitch Angle" field as your opener
5. Update Status → "Pitched" / "Skip" / "Not a Fit"

The AI learns from your decisions over time and gets better at scoring.

---

## Customization

Edit `config.yaml` to tune without touching code:
- Add/remove keywords in `filters`
- Add industries or locations in `targets`
- Adjust minimum AI score (`ai.min_score`)

Edit `profile/context.md` to update your profile, recent credits, or sweet spot clients.

---

## Run Manually

```bash
# Set env vars first
export NOTION_TOKEN=...
export NOTION_DATABASE_ID=...
export GEMINI_API_KEY=...

# Run
python -m scraper.main
```

---

## File Structure

```
dre-lead-agent/
├── config.yaml              # Tune keywords, filters, scoring
├── profile/context.md       # Your producer profile (AI uses this to score)
├── scraper/
│   ├── main.py              # Orchestrator
│   ├── filters.py           # Fast pre-filter
│   └── sources/
│       ├── indeed_jobs.py   # Job board scraper
│       ├── productionhub.py # Production gig board
│       └── startup_funding.py # Funding news RSS
├── ai/
│   ├── client.py            # Gemini API client
│   ├── pipeline.py          # Batch scoring
│   └── memory.py            # Learn from feedback
├── storage/
│   └── notion_sync.py       # Notion database sync
├── data/feedback.json       # Lead decision history
├── setup_notion.py          # One-time DB setup
└── .github/workflows/
    └── scraper.yml          # Daily automation
```
