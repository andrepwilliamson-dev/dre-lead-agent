"""
Main orchestrator — collect → enrich → store.
Run daily via GitHub Actions.
"""
import os
import yaml
from pathlib import Path

from scraper.sources import indeed_jobs, productionhub, startup_funding
from storage.notion_sync import sync

CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"


def load_config() -> dict:
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)


def ai_enabled(cfg: dict) -> bool:
    return cfg.get("ai", {}).get("enabled", False) and bool(os.environ.get("GEMINI_API_KEY"))


def main():
    cfg = load_config()
    db_id = os.environ.get("NOTION_DATABASE_ID", "")

    if not db_id:
        print("[Main] ERROR: NOTION_DATABASE_ID not set")
        return

    print("=== Dre's Lead Intelligence Agent ===")
    print("Collecting leads from all sources...")

    sources = [
        ("Indeed CA", indeed_jobs),
        ("ProductionHUB", productionhub),
        ("Startup Funding", startup_funding),
    ]

    all_items = []
    for name, module in sources:
        try:
            items = module.fetch()
            print(f"[{name}] Collected {len(items)} items")
            all_items.extend(items)
        except Exception as e:
            print(f"[{name}] FAILED: {e}")

    # Deduplicate by URL
    seen, deduped = set(), []
    for item in all_items:
        url = item.get("url", "")
        if url and url not in seen:
            seen.add(url)
            deduped.append(item)
        elif not url:
            deduped.append(item)

    print(f"Total unique leads: {len(deduped)}")

    if ai_enabled(cfg) and deduped:
        from ai.memory import load_feedback, build_preference_prompt
        from ai.pipeline import analyse_batch

        ai_cfg = cfg.get("ai", {})
        feedback = load_feedback()
        preference = build_preference_prompt(feedback)

        context_path = Path(__file__).parent.parent / "profile" / "context.md"
        context = context_path.read_text() if context_path.exists() else ""

        print(f"Running AI scoring on {len(deduped)} leads...")
        deduped = analyse_batch(
            deduped,
            context=context,
            preference_prompt=preference,
            batch_size=ai_cfg.get("batch_size", 5),
            rate_limit=ai_cfg.get("rate_limit_seconds", 7),
        )
        min_score = ai_cfg.get("min_score", 5)
        before = len(deduped)
        deduped = [i for i in deduped if i.get("ai_score", 0) >= min_score]
        print(f"After score filter (min {min_score}): {len(deduped)} leads (filtered {before - len(deduped)})")
    else:
        print("[AI] Skipped — GEMINI_API_KEY not set or AI disabled")

    added, skipped = sync(db_id, deduped)
    print(f"=== Done — {added} new leads added to Notion, {skipped} skipped ===")


if __name__ == "__main__":
    main()
