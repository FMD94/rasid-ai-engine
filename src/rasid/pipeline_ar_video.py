from pathlib import Path

from src.video.extract import extract_frames
from src.video.transcribe import extract_audio
from src.video.deepfake import deepfake_risk_score
from src.vision.deepfake_detector import detector

from src.vision.ocr import extract_text_from_image
from src.rasid.pipeline_text_auto import analyze_text_auto

ROOT = Path(__file__).resolve().parents[2]


def analyze_ar_video(video_path: str, frames_fps: float = 1.0, max_frames: int = 20) -> dict:
    """
    Video pipeline:
    1) Extract frames -> OCR each frame -> merge OCR text
    2) Extract audio -> (transcript placeholder for now)
    3) Deepfake risk score (stub now)
    4) Feed merged text into Arabic hybrid text analyzer
    5) Apply final decision hierarchy
    """
    video_path = str(video_path)

    # 1) Frames OCR
    frames_dir = ROOT / "data" / "ar" / "videos" / "_frames_tmp"
    frame_paths = extract_frames(video_path, str(frames_dir), fps=1, max_frames=25)

    ocr_chunks = []
    for fp in frame_paths:
        txt = extract_text_from_image(fp)
        if txt:
            ocr_chunks.append(txt)

    ocr_text = "\n".join(ocr_chunks).strip()

    # 2) Audio extraction (transcript later)
    audio_dir = ROOT / "data" / "ar" / "videos" / "_audio_tmp"
    audio_path = extract_audio(video_path, str(audio_dir / "audio.wav"))
    transcript_text = ""  # TODO: speech-to-text (Phase 1.5)

    # 3) Deepfake risk
    df_score = float(deepfake_risk_score(video_path))

    # 4) Merge text signals -> analyze
    combined_text = "\n".join([t for t in [ocr_text, transcript_text] if t]).strip()
    text_result = analyze_text_auto(combined_text if combined_text else " ")

    # 5) Final decision hierarchy (per your plan)
    decision = text_result["decision"]
    confidence = text_result["confidence"]
    reasons = list(text_result["reasons"])

    # Deepfake rule: if high risk -> flagged (override)
    if df_score >= 0.7:
        decision = "flagged"
        reasons = [f"Deepfake risk high (score={df_score:.2f})"] + reasons
        confidence = max(confidence, 0.7)

    return {
        "decision": decision,
        "confidence": confidence,
        "reasons": reasons,
        "evidence": {
            "video_path": video_path,
            "frame_count": len(frame_paths),
            "ocr_text": ocr_text,
            "audio_path": audio_path,
            "transcript_text": transcript_text,
            "deepfake_score": df_score,
            "text_engine_result": text_result,
        }
    }
