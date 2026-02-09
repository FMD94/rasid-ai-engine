from src.rasid.pipeline_ar_video import analyze_ar_video

# Path to your test video
video_path = "data/ar/videos/test1.mp4"

result = analyze_ar_video(video_path)

print("DECISION:", result["decision"])
print("CONFIDENCE:", result["confidence"])
print("REASONS:", result["reasons"])

print("\n--- VIDEO EVIDENCE ---")
print("Frames extracted:", result["evidence"]["frame_count"])
print("Deepfake score:", result["evidence"]["deepfake_score"])
print("Audio extracted:", bool(result["evidence"]["audio_path"]))

print("\n--- OCR TEXT FROM FRAMES ---")
print(result["evidence"]["ocr_text"])
