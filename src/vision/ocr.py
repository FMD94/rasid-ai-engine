from PIL import Image
import pytesseract
import cv2
import numpy as np

def _preprocess_for_ocr(img_bgr, scale=2):
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    # upscale (helps small text)
    if scale != 1:
        gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

    # denoise + binarize
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    thr = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 31, 10
    )
    return thr

def _crop_regions(img_bgr):
    """Return common text regions: top & bottom bands + full frame fallback."""
    h, w = img_bgr.shape[:2]
    top = img_bgr[0:int(h*0.35), 0:w]
    bottom = img_bgr[int(h*0.65):h, 0:w]
    return [top, bottom, img_bgr]

def extract_text_from_image(image_path: str, lang="ara") -> str:
    img_bgr = cv2.imread(image_path)
    if img_bgr is None:
        return ""

    texts = []
    for region in _crop_regions(img_bgr):
        proc = _preprocess_for_ocr(region, scale=2)
        pil = Image.fromarray(proc)

        # psm 6 = assume a block of text; good for captions
        config = "--psm 6"
        t = pytesseract.image_to_string(pil, lang=lang, config=config)
        t = t.strip()
        if t:
            texts.append(t)

    # keep unique lines
    joined = "\n".join(texts)
    return joined.strip()
