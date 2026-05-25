from src.rasid.language_router import detect_language
from src.rasid.pipeline_ar_text_transformer import analyze_ar_text_transformer
from src.rasid.pipeline_en_text_transformer import analyze_en_text_transformer
from src.rasid.lime_explainer import explain_with_lime


EN_FLAGGED_PHRASES = [
    "limited time offer",
    "exclusive access",
    "act now",
    "register now",
    "don't miss",
    "don’t miss",
    "offer expires",
    "only today"
]

AR_FLAGGED_PHRASES = [
    "لفترة محدودة",
    "عرض محدود",
    "سارع الآن",
    "سجل الآن",
    "لا تفوت",
    "العرض ينتهي",
    "اليوم فقط"
]

EN_BLOCKED_PHRASES = [
    "guaranteed profit",
    "zero risk",
    "double your money",
    "miracle cure",
    "guaranteed results",
    "earn money instantly",
    "make thousands daily",
    "no risk investment",
    "instant cure"
]

AR_BLOCKED_PHRASES = [
    "أرباح مضمونة",
    "بدون مخاطر",
    "ضاعف أموالك",
    "علاج نهائي",
    "نتائج مضمونة",
    "اكسب المال بسرعة",
    "دخل ثابت مضمون",
    "استثمار بدون مخاطر",
    "علاج فوري"
]


def apply_rule_boost(text: str, result: dict, lang: str) -> dict:
    text_lower = text.lower()

    if lang == "en":
        blocked_phrases = EN_BLOCKED_PHRASES
        flagged_phrases = EN_FLAGGED_PHRASES
    else:
        blocked_phrases = AR_BLOCKED_PHRASES
        flagged_phrases = AR_FLAGGED_PHRASES

    reasons = result.get("reasons", [])
    if not isinstance(reasons, list):
        reasons = [str(reasons)]

    for phrase in blocked_phrases:
        if phrase.lower() in text_lower:
            result["decision"] = "blocked"
            result["reasons"] = [f"Rule matched blocked phrase: {phrase}"] + reasons
            result["rule_override"] = True
            return result

    for phrase in flagged_phrases:
        if phrase.lower() in text_lower and result.get("decision") != "approved":
            result["decision"] = "flagged"
            result["reasons"] = [f"Rule matched flagged phrase: {phrase}"] + reasons
            result["rule_override"] = True
            return result

    result["reasons"] = reasons
    result["rule_override"] = False
    return result


def apply_safety_gate(result: dict) -> dict:
    confidence = float(result.get("confidence", 0))
    decision = result.get("decision", "approved")

    reasons = result.get("reasons", [])
    if not isinstance(reasons, list):
        reasons = [str(reasons)]

    strong_fraud_reason = any(
        "blocked phrase" in str(reason).lower()
        or "guaranteed profit" in str(reason).lower()
        or "zero risk" in str(reason).lower()
        or "double your money" in str(reason).lower()
        or "miracle cure" in str(reason).lower()
        or "أرباح مضمونة" in str(reason)
        or "بدون مخاطر" in str(reason)
        or "ضاعف أموالك" in str(reason)
        or "علاج نهائي" in str(reason)
        for reason in reasons
    )

    if decision == "blocked" and confidence < 0.60 and not strong_fraud_reason:
        result["decision"] = "flagged"
        reasons.append("Low-confidence fraud prediction was downgraded to manipulative.")

    elif decision == "flagged" and confidence < 0.65:
        result["decision"] = "approved"
        reasons.append("Low-confidence manipulative prediction was treated as safe.")

    result["reasons"] = reasons
    return result


def add_user_friendly_explanation(result: dict) -> dict:
    decision = result.get("decision", "approved")
    reasons = result.get("reasons", [])

    if not isinstance(reasons, list):
        reasons = [str(reasons)]

    if decision == "approved":
        result["explanation"] = (
            "RASID classified this content as Safe because no strong manipulative, fraudulent, "
            "or high-risk advertising patterns were detected."
        )

    elif decision == "flagged":
        result["explanation"] = (
            "RASID classified this content as Manipulative because it contains persuasive advertising "
            "signals such as urgency, exclusivity, pressure language, or promotional wording."
        )

    elif decision == "blocked":
        result["explanation"] = (
            "RASID classified this content as Fraud because it contains high-risk claims such as "
            "guaranteed profit, zero-risk investment, instant results, or unrealistic promises."
        )

    else:
        result["explanation"] = "RASID could not determine a clear safety category for this content."

    return result


def add_lime_explanation(text: str, result: dict, lang: str) -> dict:
    try:
        result["lime_explanation"] = explain_with_lime(
            text=text,
            lang=lang,
            target_label=result["decision"]
        )
    except Exception as e:
        result["lime_explanation"] = [{"error": str(e)}]

    return result


def finalize_result(text: str, result: dict, lang: str) -> dict:
    result = apply_rule_boost(text, result, lang)
    result = apply_safety_gate(result)
    result = add_user_friendly_explanation(result)
    result = add_lime_explanation(text, result, lang)
    return result


def analyze_text_auto(text: str) -> dict:
    lang = detect_language(text)

    if lang == "ar":
        result = analyze_ar_text_transformer(text)
        result["language"] = "ar"
        result["routing_mode"] = "direct_ar_transformer"
        return finalize_result(text, result, "ar")

    if lang == "en":
        result = analyze_en_text_transformer(text)
        result["language"] = "en"
        result["routing_mode"] = "direct_en_transformer"
        return finalize_result(text, result, "en")

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
        return finalize_result(text, ar_result, "ar")

    en_result["language"] = "en"
    en_result["routing_mode"] = "fallback_dual_inference_transformer"
    en_result["fallback_comparison"] = {
        "ar_confidence": ar_conf,
        "en_confidence": en_conf
    }
    return finalize_result(text, en_result, "en")