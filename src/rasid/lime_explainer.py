import numpy as np
import torch
from lime.lime_text import LimeTextExplainer

from transformers import AutoTokenizer, AutoModelForSequenceClassification
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

AR_MODEL_DIR = ROOT / "models" / "ar_transformer"
EN_MODEL_DIR = ROOT / "models" / "en_transformer"

CLASS_NAMES = ["approved", "flagged", "blocked"]

_ar_tokenizer = None
_ar_model = None
_en_tokenizer = None
_en_model = None


def load_model(lang: str):
    global _ar_tokenizer, _ar_model, _en_tokenizer, _en_model

    if lang == "ar":
        if _ar_tokenizer is None or _ar_model is None:
            _ar_tokenizer = AutoTokenizer.from_pretrained(str(AR_MODEL_DIR))
            _ar_model = AutoModelForSequenceClassification.from_pretrained(str(AR_MODEL_DIR))
            _ar_model.eval()
        return _ar_tokenizer, _ar_model

    if _en_tokenizer is None or _en_model is None:
        _en_tokenizer = AutoTokenizer.from_pretrained(str(EN_MODEL_DIR))
        _en_model = AutoModelForSequenceClassification.from_pretrained(str(EN_MODEL_DIR))
        _en_model.eval()
    return _en_tokenizer, _en_model


def predict_proba(texts, lang: str):
    tokenizer, model = load_model(lang)

    encodings = tokenizer(
        list(texts),
        truncation=True,
        padding=True,
        max_length=128,
        return_tensors="pt"
    )

    with torch.no_grad():
        outputs = model(**encodings)
        probs = torch.softmax(outputs.logits, dim=1).cpu().numpy()

    return probs


def explain_with_lime(text: str, lang: str, target_label: str, num_features: int = 6):
    explainer = LimeTextExplainer(class_names=CLASS_NAMES)

    label_map = {
    "Safe": "approved",
    "Manipulative": "flagged",
    "Fraud": "blocked",
    "approved": "approved",
    "flagged": "flagged",
    "blocked": "blocked"
}

    target_label = label_map.get(target_label, target_label)
    label_id = CLASS_NAMES.index(target_label)

    explanation = explainer.explain_instance(
        text,
        lambda texts: predict_proba(texts, lang),
        labels=[label_id],
        num_features=num_features,
        num_samples=500
    )

    features = explanation.as_list(label=label_id)

    return [
        {
            "word": word,
            "weight": round(float(weight), 4)
        }
        for word, weight in features
    ]