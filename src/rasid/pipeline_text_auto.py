from src.rasid.language_router import detect_language
from src.rasid.pipeline_ar_text import analyze_ar_text
from src.rasid.pipeline_en_text import analyze_en_text

def analyze_text_auto(text: str) -> dict:
    lang = detect_language(text)

    if lang == "ar":
        result = analyze_ar_text(text)
        result["language"] = "ar"
        return result

    if lang == "en":
        result = analyze_en_text(text)
        result["language"] = "en"
        return result

    return {
        "decision": "flagged",
        "confidence": 0.0,
        "reasons": ["Could not confidently detect language"],
        "language": "unknown"
    }