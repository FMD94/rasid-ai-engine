from pathlib import Path
from transformers import pipeline

ROOT = Path(__file__).resolve().parents[2]
MODEL_DIR = ROOT / "models" / "ar_transformer"

classifier = pipeline(
    "text-classification",
    model=str(MODEL_DIR),
    tokenizer=str(MODEL_DIR)
)

def analyze_ar_text_transformer(text: str) -> dict:
    result = classifier(
        text,
        truncation=True,
        max_length=512
    )[0]

    return {
        "decision": result["label"].lower(),
        "confidence": round(float(result["score"]), 2),
        "reasons": [f"Arabic transformer predicted: {result['label']}"],
        "language": "ar"
    }