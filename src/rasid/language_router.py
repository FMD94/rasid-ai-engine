import re

ARABIC_PATTERN = re.compile(r'[\u0600-\u06FF]')

def detect_language(text: str) -> str:
    """
    Very simple language detector:
    - if Arabic characters exist in strong amount -> 'ar'
    - otherwise -> 'en'
    """

    if not text or not text.strip():
        return "unknown"

    arabic_chars = len(ARABIC_PATTERN.findall(text))
    english_chars = len(re.findall(r'[A-Za-z]', text))

    if arabic_chars > english_chars:
        return "ar"
    elif english_chars > 0:
        return "en"
    else:
        return "unknown"