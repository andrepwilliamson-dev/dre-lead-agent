"""
Pre-filter leads before sending to AI — fast keyword check.
"""
import yaml
from pathlib import Path

_config = None

def _load_config():
    global _config
    if _config is None:
        config_path = Path(__file__).parent.parent / "config.yaml"
        with open(config_path) as f:
            _config = yaml.safe_load(f)
    return _config

def is_relevant(text: str) -> bool:
    """Return True if text passes keyword filters."""
    cfg = _load_config()
    text_lower = text.lower()

    blocked = cfg.get("filters", {}).get("blocked_keywords", [])
    if any(kw.lower() in text_lower for kw in blocked):
        return False

    required = cfg.get("filters", {}).get("required_keywords", [])
    if required and not any(kw.lower() in text_lower for kw in required):
        return False

    return True
