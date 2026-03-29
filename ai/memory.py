"""
Learn from Dre's pitch decisions over time.
Reads feedback.json and builds a preference prompt for the AI.
"""
import json
from pathlib import Path

FEEDBACK_PATH = Path(__file__).parent.parent / "data" / "feedback.json"


def load_feedback() -> dict:
    if not FEEDBACK_PATH.exists():
        return {"positive": [], "negative": []}
    try:
        with open(FEEDBACK_PATH) as f:
            return json.load(f)
    except Exception:
        return {"positive": [], "negative": []}


def save_feedback(feedback: dict):
    FEEDBACK_PATH.parent.mkdir(exist_ok=True)
    with open(FEEDBACK_PATH, "w") as f:
        json.dump(feedback, f, indent=2)


def build_preference_prompt(feedback: dict) -> str:
    positive = feedback.get("positive", [])
    negative = feedback.get("negative", [])

    if not positive and not negative:
        return ""

    lines = []
    if positive:
        lines.append("Leads Andre responded positively to (Pitched / Hot Lead):")
        for item in positive[-10:]:
            lines.append(f"  - {item.get('name', '')} at {item.get('company', '')}")

    if negative:
        lines.append("Leads Andre skipped or marked not a fit:")
        for item in negative[-10:]:
            lines.append(f"  - {item.get('name', '')} at {item.get('company', '')}")

    return "\n".join(lines)
