from fastapi import FastAPI, UploadFile, File, Form
from pathlib import Path
from typing import Optional
import shutil

from src.rasid.pipeline_en_text import analyze_en_text
from src.rasid.pipeline_ar_text import analyze_ar_text
from src.rasid.pipeline_text_auto import analyze_text_auto
from src.rasid.pipeline_ar_image import analyze_ar_image
from src.rasid.pipeline_ar_video import analyze_ar_video

app = FastAPI(title="RASID API", version="1.0")

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@app.get("/")
def root():
    return {"message": "RASID API is running"}


@app.post("/analyze/text")
def analyze_text(text: str = Form(...)):
    result = analyze_ar_text(text)
    return result

@app.post("/analyze/text/en")
def analyze_text_en(text: str = Form(...)):
    result = analyze_en_text(text)
    return result

@app.post("/analyze/text/auto")
def analyze_text_auto_endpoint(text: str = Form(...)):
    result = analyze_text_auto(text)
    return result

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
    return result


@app.post("/analyze/video")
def analyze_video(file: UploadFile = File(...)):
    file_path = UPLOAD_DIR / file.filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = analyze_ar_video(str(file_path))
    return result


@app.post("/analyze")
def analyze_unified(
    text: str = Form(""),
    caption_text: str = Form(""),
    file: Optional[UploadFile] = File(None)
):
    # Case 1: text only
    if text.strip() and file is None:
        result = analyze_ar_text(text.strip())
        result["input_type"] = "text"
        return result

    # Case 2 or 3: file uploaded
    if file is not None:
        file_path = UPLOAD_DIR / file.filename

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        suffix = file_path.suffix.lower()

        # Image types
        if suffix in [".png", ".jpg", ".jpeg", ".webp"]:
            result = analyze_ar_image(str(file_path), caption_text=caption_text)
            result["input_type"] = "image"
            return result

        # Video types
        if suffix in [".mp4", ".mov", ".avi", ".mkv"]:
            result = analyze_ar_video(str(file_path))
            result["input_type"] = "video"
            return result

        return {
            "error": f"Unsupported file type: {suffix}"
        }

    return {
        "error": "Please provide either text or a supported image/video file."
    }