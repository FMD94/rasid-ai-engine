import joblib

MODEL_PATH = "models/en_text_baseline.joblib"

model = joblib.load(MODEL_PATH)

def analyze_en_text(text: str):

    pred = model.predict([text])[0]
    prob = model.predict_proba([text]).max()

    return {
        "decision": pred,
        "confidence": float(prob),
        "reasons": ["ML predicted English ad risk"]
    }