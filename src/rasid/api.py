from fastapi import FastAPI, UploadFile, File, Form
from pathlib import Path
import shutil

from src.rasid.pipeline_ar_text import analyze_ar_text
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


@app.post("/analyze/image")
def analyze_image(
    file: UploadFile = File(...),
    caption_text: str = Form("")
):
    file_path = UPLOAD_DIR / file.filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = analyze_ar_image(str(file_path), caption_text=caption_text)
    return result


@app.post("/analyze/video")
def analyze_video(file: UploadFile = File(...)):
    file_path = UPLOAD_DIR / file.filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = analyze_ar_video(str(file_path))
    return result