from fastapi import FastAPI, UploadFile, File, Form
from pathlib import Path
from typing import Optional
import shutil
import requests

from fastapi.middleware.cors import CORSMiddleware

from src.rasid.database import save_analysis_to_db
from src.rasid.logger import save_analysis_log

from src.rasid.pipeline_en_text import analyze_en_text
from src.rasid.pipeline_ar_text import analyze_ar_text
from src.rasid.pipeline_text_auto import analyze_text_auto
from src.rasid.pipeline_ar_image import analyze_ar_image
from src.rasid.pipeline_ar_video import analyze_ar_video

from src.vision.deepfake_detector import detector


app = FastAPI(title="RASID API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


def add_deepfake_signal(result: dict, deepfake_result: dict, media_type: str):
    result["deepfake_score"] = deepfake_result.get("deepfake_score")
    result["deepfake_risk"] = deepfake_result.get("deepfake_risk")

    reasons = result.get("reasons", [])
    if not isinstance(reasons, list):
        reasons = [str(reasons)]

    deepfake_reason = deepfake_result.get("deepfake_reason")
    if deepfake_reason:
        reasons.append(deepfake_reason)

    if deepfake_result.get("deepfake_risk") == "high":
        result["decision"] = "blocked"
        reasons.append(f"High visual manipulation risk detected in {media_type}.")

    elif deepfake_result.get("deepfake_risk") == "medium" and result.get("decision") == "approved":
        result["decision"] = "flagged"
        reasons.append(f"Medium visual manipulation risk detected in {media_type}.")

    result["reasons"] = reasons
    return result


def save_result(result: dict, source: str, input_type: str):
    result["input_type"] = input_type
    save_analysis_log(result, source=source)
    save_analysis_to_db(result, source=source)
    return result


@app.get("/")
def root():
    return {"message": "RASID API is running"}


@app.post("/analyze/text")
def analyze_text(text: str = Form(...)):
    result = analyze_ar_text(text)
    return save_result(result, source="text_api", input_type="text")


@app.post("/analyze/text/en")
def analyze_text_en(text: str = Form(...)):
    result = analyze_en_text(text)
    return save_result(result, source="text_en_api", input_type="text")


@app.post("/analyze/text/auto")
def analyze_text_auto_endpoint(text: str = Form(...)):
    result = analyze_text_auto(text)
    return save_result(result, source="text_auto_api", input_type="text")


@app.post("/analyze/image")
def analyze_image(
    file: UploadFile = File(...),
    caption_text: str = Form(""),
    language_hint: str = Form("")
):
    file_path = UPLOAD_DIR / file.filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = analyze_ar_image(
        str(file_path),
        caption_text=caption_text,
        language_hint=language_hint.strip().lower()
    )

    deepfake_result = detector.analyze_image(str(file_path))
    result = add_deepfake_signal(result, deepfake_result, media_type="image")

    return save_result(result, source="image_api", input_type="image")


@app.post("/analyze/image-url")
def analyze_image_url(image_url: str = Form(...)):
    try:
        response = requests.get(image_url, timeout=20)
        response.raise_for_status()

        suffix = Path(image_url.split("?")[0]).suffix.lower()
        if suffix not in [".jpg", ".jpeg", ".png", ".webp"]:
            suffix = ".jpg"

        file_path = UPLOAD_DIR / f"image_from_url{suffix}"

        with open(file_path, "wb") as buffer:
            buffer.write(response.content)

        result = analyze_ar_image(str(file_path))
        result["source_url"] = image_url

        deepfake_result = detector.analyze_image(str(file_path))
        result = add_deepfake_signal(result, deepfake_result, media_type="image URL")

        return save_result(result, source="image_url_api", input_type="image_url")

    except Exception as e:
        result = {
            "decision": "error",
            "confidence": 0,
            "language": "unknown",
            "source_url": image_url,
            "reasons": [f"Could not analyze image URL: {str(e)}"]
        }
        return save_result(result, source="image_url_api", input_type="image_url")


@app.post("/analyze/video")
def analyze_video(file: UploadFile = File(...)):
    file_path = UPLOAD_DIR / file.filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = analyze_ar_video(str(file_path))

    deepfake_result = detector.analyze_video(str(file_path))
    result = add_deepfake_signal(result, deepfake_result, media_type="video")

    return save_result(result, source="video_api", input_type="video")


@app.post("/analyze/video-url")
def analyze_video_url(video_url: str = Form(...)):
    try:
        response = requests.get(video_url, timeout=20)
        response.raise_for_status()

        suffix = Path(video_url.split("?")[0]).suffix.lower()
        if suffix not in [".mp4", ".webm", ".mov"]:
            suffix = ".mp4"

        file_path = UPLOAD_DIR / f"video_from_url{suffix}"

        with open(file_path, "wb") as buffer:
            buffer.write(response.content)

        result = analyze_ar_video(str(file_path))
        result["source_url"] = video_url

        deepfake_result = detector.analyze_video(str(file_path))
        result = add_deepfake_signal(result, deepfake_result, media_type="video URL")

        return save_result(result, source="video_url_api", input_type="video_url")

    except Exception as e:
        result = {
            "decision": "error",
            "confidence": 0,
            "language": "unknown",
            "source_url": video_url,
            "reasons": [f"Could not analyze video URL: {str(e)}"]
        }
        return save_result(result, source="video_url_api", input_type="video_url")


@app.post("/analyze")
def analyze_unified(
    text: str = Form(""),
    caption_text: str = Form(""),
    file: Optional[UploadFile] = File(None)
):
    if text.strip() and file is None:
        result = analyze_text_auto(text.strip())
        return save_result(result, source="text_auto_api", input_type="text")

    if file is not None:
        file_path = UPLOAD_DIR / file.filename

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        suffix = file_path.suffix.lower()

        if suffix in [".png", ".jpg", ".jpeg", ".webp"]:
            result = analyze_ar_image(str(file_path), caption_text=caption_text)

            deepfake_result = detector.analyze_image(str(file_path))
            result = add_deepfake_signal(result, deepfake_result, media_type="image")

            return save_result(result, source="image_api", input_type="image")

        if suffix in [".mp4", ".mov", ".avi", ".mkv"]:
            result = analyze_ar_video(str(file_path))

            deepfake_result = detector.analyze_video(str(file_path))
            result = add_deepfake_signal(result, deepfake_result, media_type="video")

            return save_result(result, source="video_api", input_type="video")

        return {
            "decision": "error",
            "confidence": 0,
            "language": "unknown",
            "input_type": "unsupported",
            "reasons": [f"Unsupported file type: {suffix}"]
        }

    return {
        "decision": "error",
        "confidence": 0,
        "language": "unknown",
        "input_type": "empty",
        "reasons": ["Please provide either text or a supported image/video file."]
    }