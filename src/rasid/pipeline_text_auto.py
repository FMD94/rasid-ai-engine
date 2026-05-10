from src.rasid.language_router import detect_language
from src.rasid.pipeline_ar_text_transformer import analyze_ar_text_transformer
from src.rasid.pipeline_en_text_transformer import analyze_en_text_transformer
from src.rasid.lime_explainer import explain_with_lime


EN_FLAGGED_PHRASES = [
    "sign up now",
    "join today",
    "get started now",
    "don’t miss",
    "don't miss",
    "limited time offer",
    "exclusive access",
    "start today",
    "register now",
    "discover our services",
    "check out",
    "latest deals",
    "sign up today",
    "discover our new services",
    "take advantage",
    "offer before it ends",
    "selected customers",
    "reported noticeable improvements",
    "join now",
    "limited offer",
    "try this method",
    "could see better results",
    "may help",
    "claims to improve",
    "potential opportunities",
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
    "تعرف على خدماتنا",
    "قد يساعد",
    "يدعي",
    "فرصًا محتملة",
    "عرض لفترة محدودة",
    "قد ينتهي قريبًا",
    "نتائج أفضل",
    "بعض البرامج تعد",
    "سجل اليوم",
    "لا تضيع الفرصة",
    "اكتشف خدماتنا",
    "استفد من العرض",
    "قبل انتهائه",
    "ابدأ رحلتك",
    "جرب الآن",
    "النتائج تختلف",
]

EN_BLOCKED_PHRASES = [
    "guaranteed profit",
    "zero risk",
    "instant results",
    "miracle cure",
    "guaranteed results",
    "earn money instantly",
    "make thousands daily",
    "no risk",
    "without risk",
    "double your money",
    "passive income",
    "secret investment",
    "cures diabetes instantly",
    "cures all diseases",
    "guaranteed system",
    "double your crypto",
    "crypto investment",
    "no losses",
    "absolutely no losses",
    "fixed income",
    "millionaires only",
    "cure for every health condition",
    "within just a few hours",
    "guaranteed daily profits",
]

AR_BLOCKED_PHRASES = [
    "أرباح مضمونة",
    "بدون مخاطر",
    "نتائج فورية",
    "علاج نهائي",
    "نتائج مضمونة",
    "اكسب المال بسرعة",
    "دخل ثابت مضمون",
    "ربح يومي ثابت",
    "بدون أي خسارة",
    "بدون أي مخاطرة",
    "اربح يوميًا",
    "أرباح ضخمة",
    "خلال ساعات",
    "منتج طبي سحري",
    "يقضي على جميع الأمراض",
    "اربح المال من التداول",
    "بدون خبرة أو مخاطرة",
    "دخل ثابت",
    "بسرعة وسهولة",
    "نتائج مؤكدة",
]


def apply_rule_boost(text: str, result: dict, lang: str) -> dict:
    text_lower = text.lower()

    if lang == "en":
        blocked_phrases = EN_BLOCKED_PHRASES
        flagged_phrases = EN_FLAGGED_PHRASES
    else:
        blocked_phrases = AR_BLOCKED_PHRASES
        flagged_phrases = AR_FLAGGED_PHRASES

    for phrase in blocked_phrases:
        if phrase in text_lower:
            result["decision"] = "blocked"
            result["reasons"] = [f"Rule matched blocked phrase: {phrase}"] + result.get("reasons", [])
            result["rule_override"] = True
            return result

    for phrase in flagged_phrases:
        if phrase in text_lower:
            result["decision"] = "flagged"
            result["reasons"] = [f"Rule matched flagged phrase: {phrase}"] + result.get("reasons", [])
            result["rule_override"] = True
            return result

    result["rule_override"] = False
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


def analyze_text_auto(text: str) -> dict:
    lang = detect_language(text)

    if lang == "ar":
        result = analyze_ar_text_transformer(text)
        result["language"] = "ar"
        result["routing_mode"] = "direct_ar_transformer"
        result = apply_rule_boost(text, result, "ar")
        result = add_lime_explanation(text, result, "ar")
        return result

    if lang == "en":
        result = analyze_en_text_transformer(text)
        result["language"] = "en"
        result["routing_mode"] = "direct_en_transformer"
        result = apply_rule_boost(text, result, "en")
        result = add_lime_explanation(text, result, "en")
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
        ar_result = add_lime_explanation(text, ar_result, "ar")
        return ar_result

    en_result["language"] = "en"
    en_result["routing_mode"] = "fallback_dual_inference_transformer"
    en_result["fallback_comparison"] = {
        "ar_confidence": ar_conf,
        "en_confidence": en_conf
    }
    en_result = apply_rule_boost(text, en_result, "en")
    en_result = add_lime_explanation(text, en_result, "en")
    return en_result