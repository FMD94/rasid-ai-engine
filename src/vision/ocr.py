from pathlib import Path
from PIL import Image
import pytesseract
import cv2

# Windows Tesseract path
TESSERACT_EXE = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

if Path(TESSERACT_EXE).exists():
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_EXE


def _preprocess_for_ocr(img_bgr, scale: int = 2):
    """
    Improve OCR quality by:
    - converting to grayscale
    - resizing
    - light denoising
    - adaptive thresholding
    """
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    if scale != 1:
        gray = cv2.resize(
            gray,
            None,
            fx=scale,
            fy=scale,
            interpolation=cv2.INTER_CUBIC
        )

    gray = cv2.GaussianBlur(gray, (3, 3), 0)

    thresh = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        10
    )

    return thresh


def _crop_regions(img_bgr):
    """
    Return common text regions:
    - top band
    - bottom band
    - full frame fallback
    """
    h, w = img_bgr.shape[:2]

    top = img_bgr[0:int(h * 0.35), 0:w]
    bottom = img_bgr[int(h * 0.65):h, 0:w]

    return [top, bottom, img_bgr]


def extract_text_from_image(image_path: str, lang: str = "ara+eng") -> str:
    """
    Extract bilingual text from image using Tesseract OCR.
    Default language is English + Arabic.

    Args:
        image_path: path to image file
        lang: OCR language pack(s), default "eng+ara"

    Returns:
        Extracted text as a string
    """
    img_bgr = cv2.imread(image_path)

    if img_bgr is None:
        return ""

    texts = []

    for region in _crop_regions(img_bgr):
        processed = _preprocess_for_ocr(region, scale=2)
        pil_img = Image.fromarray(processed)

        # psm 6 works well for captions and ad text blocks
        config = "--psm 6"

        text = pytesseract.image_to_string(
            pil_img,
            lang=lang,
            config=config
        ).strip()

        if text:
            texts.append(text)

    # remove duplicates while preserving order
    unique_texts = list(dict.fromkeys(texts))

    return "\n".join(unique_texts).strip()