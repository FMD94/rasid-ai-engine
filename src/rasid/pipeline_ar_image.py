from src.vision.ocr import extract_text_from_image
from src.rasid.pipeline_text_auto import analyze_text_auto

def analyze_ar_image(image_path: str, caption_text: str = "") -> dict:
    ocr_text = extract_text_from_image(image_path)
    combined_text = (caption_text + "\n" + ocr_text).strip()

    res = analyze_text_auto(combined_text)
    res["evidence"]["ocr_text"] = ocr_text
    res["evidence"]["image_path"] = image_path
    return res

