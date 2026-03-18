from pathlib import Path
import joblib

ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = ROOT / "models" / "en_text_baseline.joblib"

model = joblib.load(MODEL_PATH)

def analyze_en_text(text: str) -> dict:
    pred = model.predict([text])[0]

    confidence = 0.65
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba([text])[0]
        classes = list(model.classes_)
        confidence = float(proba[classes.index(pred)])

    return {
        "decision": pred,
        "confidence": round(confidence, 2),
        "reasons": [f"English ML predicted: {pred}"],
        "language": "en"
    }