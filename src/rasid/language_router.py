import re

ARABIC_PATTERN = re.compile(r'[\u0600-\u06FF]')
ENGLISH_PATTERN = re.compile(r'[A-Za-z]')


def detect_language(text: str) -> str:
    if not text or not text.strip():
        return "unknown"

    arabic_chars = len(ARABIC_PATTERN.findall(text))
    english_chars = len(ENGLISH_PATTERN.findall(text))

    total = arabic_chars + english_chars

    # Very weak signal
    if total < 5:
        return "unknown"

    # 🔥 NEW LOGIC (important)
    # If Arabic exists at all → prefer Arabic UNLESS English is dominant
    if arabic_chars > 0:
        if english_chars > arabic_chars * 3:
            return "en"
        return "ar"

    # Otherwise normal English detection
    if english_chars > 0:
        return "en"

    return "unknown"