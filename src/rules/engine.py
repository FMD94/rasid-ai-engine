from pathlib import Path
from typing import Tuple, List
import yaml

ROOT = Path(__file__).resolve().parents[2]
RULES_PATH = ROOT / "src" / "rules" / "policy_ar.yaml"

def _normalize(text: str) -> str:
    return " ".join(text.strip().lower().split())

def load_rules() -> dict:
    with open(RULES_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def apply_rules_ar(text: str) -> Tuple[str, float, List[str]]:
    rules = load_rules()
    t = _normalize(text)
    reasons: List[str] = []

    for phrase in rules.get("blocked_phrases", []):
        if _normalize(phrase) in t:
            reasons.append(f"Blocked phrase detected: {phrase}")

    if reasons:
        return "blocked", 0.90, reasons

    for phrase in rules.get("flagged_phrases", []):
        if _normalize(phrase) in t:
            reasons.append(f"Flagged phrase detected: {phrase}")

    if reasons:
        return "flagged", 0.70, reasons

    return "approved", 0.60, ["No policy phrases detected"]
