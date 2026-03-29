"""
AI enrichment pipeline — scores leads for Dre in batches.
"""
from ai.client import generate
from pathlib import Path


def _chunks(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]


def analyse_batch(
    items: list[dict],
    context: str = "",
    preference_prompt: str = "",
    batch_size: int = 5,
    rate_limit: float = 7.0,
) -> list[dict]:
    """Score and enrich a list of leads. Returns items with ai_score and pitch_angle added."""
    enriched = []

    for batch in _chunks(items, batch_size):
        prompt = _build_prompt(batch, context, preference_prompt)
        result = generate(prompt, rate_limit=rate_limit)

        scored = result.get("leads", [])
        if len(scored) != len(batch):
            # Fallback: attach raw items unscored
            for item in batch:
                item.setdefault("ai_score", 0)
                item.setdefault("pitch_angle", "Manual review needed")
                item.setdefault("why_relevant", "")
                enriched.append(item)
        else:
            for item, score_data in zip(batch, scored):
                item["ai_score"] = score_data.get("score", 0)
                item["pitch_angle"] = score_data.get("pitch_angle", "")
                item["why_relevant"] = score_data.get("why_relevant", "")
                enriched.append(item)

    return enriched


def _build_prompt(batch: list[dict], context: str, preference_prompt: str) -> str:
    leads_text = ""
    for i, lead in enumerate(batch):
        leads_text += f"""
Lead {i+1}:
  Title/Name: {lead.get('name', '')}
  Company: {lead.get('company', '')}
  Source: {lead.get('source', '')}
  Signal Type: {lead.get('signal_type', '')}
  Signal Detail: {lead.get('signal_detail', '')}
  Location: {lead.get('location', '')}
"""

    return f"""You are a lead scoring assistant for Andre Williamson, a Senior Producer and Creative Operations Leader based in Toronto.

PRODUCER PROFILE:
{context}

PAST PREFERENCES:
{preference_prompt or "No history yet — score based on profile."}

LEADS TO SCORE:
{leads_text}

Score each lead from 1-10 based on how likely this is to result in paid freelance production work for Andre.

10 = Perfect fit. Startup or mid-size brand in lifestyle/consumer/entertainment that clearly needs production help.
7-9 = Strong fit. Good client type, relevant signal.
4-6 = Possible fit. Worth reviewing manually.
1-3 = Weak fit. Wrong industry, wrong client size, or too vague.

Also provide:
- why_relevant: 1 sentence on WHY this is a lead for Andre specifically
- pitch_angle: 1 sentence on how Andre should open his outreach (be specific, reference the signal)

Respond ONLY with valid JSON in this exact format:
{{
  "leads": [
    {{
      "score": 8,
      "why_relevant": "...",
      "pitch_angle": "..."
    }}
  ]
}}

Return exactly {len(batch)} objects in the leads array, in the same order as the input leads.
"""
