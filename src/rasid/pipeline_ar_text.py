from pathlib import Path
import joblib

from src.rules.engine import apply_rules_ar

ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = ROOT / "models" / "ar_text_baseline.joblib"


def analyze_ar_text(text: str) -> dict:
    """
    Hybrid pipeline:
    1) Apply rules first (policy layer).
    2) If rules => blocked, stop (highest priority).
    3) Otherwise run ML model.
    4) If rules flagged but ML approved => keep flagged (rules override).
    """
    # 1) Rules layer
    r_decision, r_conf, r_reasons = apply_rules_ar(text)

    if r_decision == "blocked":
        return {
            "decision": "blocked",
            "confidence": r_conf,
            "reasons": r_reasons,
            "evidence": {"text": text, "rules_decision": r_decision},
        }

    # 2) ML layer
    model = joblib.load(MODEL_PATH)

    ml_pred = model.predict([text])[0]

    # If model supports probabilities, use them (better confidence)
    ml_conf = 0.65
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba([text])[0]
        classes = list(model.classes_)
        ml_conf = float(proba[classes.index(ml_pred)])

    # 3) Merge decisions
    decision = ml_pred
    reasons = [f"ML predicted: {ml_pred} (conf={ml_conf:.2f})"]

    # Rules can upgrade approved -> flagged
    if r_decision == "flagged" and decision == "approved":
        decision = "flagged"
        reasons = r_reasons + ["Rules override: flagged (urgency/manipulation)"]

    # If rules flagged and ML blocked, keep blocked (ML says higher risk)
    if r_decision == "flagged" and ml_pred == "blocked":
        decision = "blocked"
        reasons = r_reasons + [f"ML predicted blocked (conf={ml_conf:.2f})"]

    # If rules approved but ML flagged/blocked, accept ML (learning signal)
    if r_decision == "approved" and ml_pred in ["flagged", "blocked"]:
        reasons = ["Rules saw nothing, but ML learned risk patterns."] + reasons

    return {
        "decision": decision,
        "confidence": round(ml_conf, 2),
        "reasons": reasons,
        "evidence": {
            "text": text,
            "rules_decision": r_decision,
            "ml_prediction": ml_pred,
        },
    }
