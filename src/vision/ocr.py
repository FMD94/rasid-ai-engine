from pathlib import Path
from PIL import Image
import pytesseract

TESSERACT_EXE = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

if Path(TESSERACT_EXE).exists():
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_EXE


def extract_text_from_image(image_path: str) -> str:
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img, lang="ara+eng")
    return text.strip()
