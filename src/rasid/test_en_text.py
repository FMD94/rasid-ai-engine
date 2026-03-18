from src.rasid.pipeline_en_text import analyze_en_text

tests = [
    "Guaranteed profit within 24 hours",
    "Limited offer today only",
    "Buy one get one free",
    "Miracle cure with no side effects"
]

for t in tests:
    result = analyze_en_text(t)
    print("-" * 60)
    print("TEXT:", t)
    print("DECISION:", result["decision"])
    print("CONFIDENCE:", result["confidence"])
    print("REASONS:", result["reasons"])