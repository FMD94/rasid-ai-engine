from src.vision.ocr import extract_text_from_image
from src.rasid.pipeline_text_auto import analyze_text_auto
from src.rasid.pipeline_ar_text import analyze_ar_text
from src.rasid.pipeline_en_text import analyze_en_text


def analyze_ar_image(image_path: str, caption_text: str = "", language_hint: str = "") -> dict:
    """
    OCR -> combine with optional caption -> bilingual text analyzer
    If language_hint is provided ('ar' or 'en'), force that pipeline.
    """
    ocr_text = extract_text_from_image(image_path)
    combined_text = (caption_text + "\n" + ocr_text).strip()

    if language_hint == "ar":
        res = analyze_ar_text(combined_text)
        res["language"] = "ar"
    elif language_hint == "en":
        res = analyze_en_text(combined_text)
        res["language"] = "en"
    else:
        res = analyze_text_auto(combined_text)

    if "evidence" not in res:
        res["evidence"] = {}

    res["evidence"]["ocr_text"] = ocr_text
    res["evidence"]["image_path"] = image_path
    res["evidence"]["language_hint"] = language_hint

    return res