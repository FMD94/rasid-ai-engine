from pathlib import Path
from transformers import pipeline

ROOT = Path(__file__).resolve().parents[2]
MODEL_DIR = ROOT / "models" / "en_transformer"

classifier = pipeline(
    "text-classification",
    model=str(MODEL_DIR),
    tokenizer=str(MODEL_DIR)
)

def analyze_en_text_transformer(text: str) -> dict:
    result = classifier(text)[0]

    return {
        "decision": result["label"].lower(),
        "confidence": round(float(result["score"]), 2),
        "reasons": [f"English transformer predicted: {result['label']}"],
        "language": "en"
    }