from src.rasid.pipeline_ar_text import analyze_ar_text

tests = [
    "ارباح مضمونة خلال 24 ساعة",           # should be blocked (rules)
    "خصم حصري اليوم فقط",                  # flagged (rules)
    "منتج جديد وصل حديثا",                 # approved likely
    "فرصة عمل براتب ممتاز — قدم الآن",     # flagged likely
    "نتائج مضمونة بدون أي آثار جانبية",    # blocked (rules)
]

for t in tests:
    res = analyze_ar_text(t)
    print("-" * 70)
    print("TEXT:", t)
    print("DECISION:", res["decision"])
    print("CONFIDENCE:", res["confidence"])
    print("REASONS:", res["reasons"])
