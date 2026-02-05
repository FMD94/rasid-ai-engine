from src.vision.ocr import extract_text_from_image
from src.rasid.pipeline_ar_text import analyze_ar_text


def analyze_ar_image(image_path: str, caption_text: str = "") -> dict:
    ocr_text = extract_text_from_image(image_path)
    combined_text = (caption_text + "\n" + ocr_text).strip()

    res = analyze_ar_text(combined_text)
    res["evidence"]["ocr_text"] = ocr_text
    res["evidence"]["image_path"] = image_path
    return res

