from src.rasid.pipeline_ar_image import analyze_ar_image

img_path = "data/ar/images/macTest.jpg"
res = analyze_ar_image(img_path)

print("DECISION:", res["decision"])
print("CONFIDENCE:", res["confidence"])
print("REASONS:", res["reasons"])
print("\n--- OCR TEXT ---\n", res["evidence"]["ocr_text"])
