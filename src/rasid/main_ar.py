from src.rules.engine import apply_rules_ar

tests = [
    "ارباح مضمونة لفترة محدودة",
    "خصم حصري اليوم فقط",
    "منتج جديد وصل حديثا",
    "علاج نهائي بدون مخاطر"
]

for t in tests:
    decision, confidence, reasons = apply_rules_ar(t)
    print("-" * 60)
    print("TEXT:", t)
    print("DECISION:", decision)
    print("CONFIDENCE:", confidence)
    print("REASONS:", reasons)
