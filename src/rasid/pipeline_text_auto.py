from src.rasid.language_router import detect_language
from src.rasid.pipeline_ar_text_transformer import analyze_ar_text_transformer
from src.rasid.pipeline_en_text_transformer import analyze_en_text_transformer


def analyze_text_auto(text: str) -> dict:
    lang = detect_language(text)

    if lang == "ar":
        result = analyze_ar_text_transformer(text)
        result["language"] = "ar"
        result["routing_mode"] = "direct_ar_transformer"
        return result

    if lang == "en":
        result = analyze_en_text_transformer(text)
        result["language"] = "en"
        result["routing_mode"] = "direct_en_transformer"
        return result

    # fallback: run both and keep stronger
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
        ar_result["reasons"] = [
            "Language unclear; ran both transformer pipelines and selected Arabic result."
        ] + ar_result.get("reasons", [])
        return ar_result

    en_result["language"] = "en"
    en_result["routing_mode"] = "fallback_dual_inference_transformer"
    en_result["fallback_comparison"] = {
        "ar_confidence": ar_conf,
        "en_confidence": en_conf
    }
    en_result["reasons"] = [
        "Language unclear; ran both transformer pipelines and selected English result."
    ] + en_result.get("reasons", [])
    return en_result