from src.rasid.language_router import detect_language
from src.rasid.pipeline_ar_text_transformer import analyze_ar_text_transformer
from src.rasid.pipeline_en_text_transformer import analyze_en_text_transformer

EN_FLAGGED_PHRASES = [
    "sign up now",
    "join today",
    "get started now",
    "don’t miss",
    "don't miss",
    "limited time offer",
    "exclusive access",
    "start today",
    "unlock",
    "act now",
    "register now",
    "discover our services"
]

AR_FLAGGED_PHRASES = [
    "سجل الآن",
    "انضم الآن",
    "ابدأ اليوم",
    "لا تفوت",
    "لفترة محدودة",
    "اكتشف الآن",
    "عرض اليوم",
    "سارع الآن",
    "احجز الآن",
    "تعرف على خدماتنا"
]

EN_BLOCKED_PHRASES = [
    "guaranteed profit",
    "zero risk",
    "instant results",
    "miracle cure",
    "guaranteed results",
    "earn money instantly",
    "make thousands daily"
]

AR_BLOCKED_PHRASES = [
    "أرباح مضمونة",
    "بدون مخاطر",
    "نتائج فورية",
    "علاج نهائي",
    "نتائج مضمونة",
    "اكسب المال بسرعة",
    "دخل ثابت مضمون"
]


def apply_rule_boost(text: str, result: dict, lang: str) -> dict:
    text_lower = text.lower()

    if lang == "en":
        blocked_phrases = EN_BLOCKED_PHRASES
        flagged_phrases = EN_FLAGGED_PHRASES
    else:
        blocked_phrases = AR_BLOCKED_PHRASES
        flagged_phrases = AR_FLAGGED_PHRASES

    # Strong blocked override
    for phrase in blocked_phrases:
        if phrase in text_lower:
            result["decision"] = "blocked"
            result["reasons"] = [f"Rule matched blocked phrase: {phrase}"] + result.get("reasons", [])
            result["rule_override"] = True
            return result

    # Soft flagged override
    for phrase in flagged_phrases:
        if phrase in text_lower and result.get("decision") == "approved":
            result["decision"] = "flagged"
            result["reasons"] = [f"Rule matched flagged phrase: {phrase}"] + result.get("reasons", [])
            result["rule_override"] = True
            return result

    result["rule_override"] = False
    return result


def analyze_text_auto(text: str) -> dict:
    lang = detect_language(text)

    if lang == "ar":
        result = analyze_ar_text_transformer(text)
        result["language"] = "ar"
        result["routing_mode"] = "direct_ar_transformer"
        result = apply_rule_boost(text, result, "ar")
        return result

    if lang == "en":
        result = analyze_en_text_transformer(text)
        result["language"] = "en"
        result["routing_mode"] = "direct_en_transformer"
        result = apply_rule_boost(text, result, "en")
        return result

    ar_result = analyze_ar_text_transformer(text)
    en_result = analyze_en_text_transformer(text)

    ar_conf = float(ar_result.get("confidence", 0.0))
    en_conf = float(en_result.get("confidence", 0.0))

    if ar_conf >= en_conf:
        ar_result["language"] = "ar"
        ar_result["routing_mode"] = "fallback_dual_inference_transformer"
        ar_result["fallback_comparison"] = {
            "ar_confidence": ar_conf,
            "en_confidence": en_conf
        }
        ar_result = apply_rule_boost(text, ar_result, "ar")
        return ar_result

    en_result["language"] = "en"
    en_result["routing_mode"] = "fallback_dual_inference_transformer"
    en_result["fallback_comparison"] = {
        "ar_confidence": ar_conf,
        "en_confidence": en_conf
    }
    en_result = apply_rule_boost(text, en_result, "en")
    return en_result