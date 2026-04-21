"""
SignLens - main.py
FastAPI backend — Street Sign Detection & Translation
Run: uvicorn main:app --reload --port 8000
"""

import io
import os
import logging
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from PIL import Image

from ocr import extract_text
from translator import translate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="SignLens API", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend")

class TranslateRequest(BaseModel):
    text: str
    target_language: str

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "SignLens API v3.0"}

@app.get("/api/languages")
def languages():
    return {"languages": [
        {"code": "en", "name": "English",   "script": "Latin"},
        {"code": "kn", "name": "Kannada",   "script": "ಕನ್ನಡ"},
        {"code": "te", "name": "Telugu",    "script": "తెలుగు"},
        {"code": "ta", "name": "Tamil",     "script": "தமிழ்"},
        {"code": "mr", "name": "Marathi",   "script": "मराठी"},
        {"code": "ml", "name": "Malayalam", "script": "മലയാളം"},
        {"code": "hi", "name": "Hindi",     "script": "हिन्दी"},
        {"code": "fr", "name": "French",    "script": "Latin"},
        {"code": "es", "name": "Spanish",   "script": "Latin"},
        {"code": "ar", "name": "Arabic",    "script": "عربي"},
    ]}

@app.post("/api/upload-image")
async def upload_image(
    file: UploadFile = File(...),
    language: str = Form(default="en")
):
    allowed = ["image/jpeg","image/jpg","image/png","image/webp"]
    ct = (file.content_type or "").lower()
    if ct not in allowed:
        raise HTTPException(400, f"Unsupported file type. Use JPG, PNG or WEBP.")

    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(400, "Uploaded file is empty.")

    try:
        pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception as e:
        raise HTTPException(400, f"Cannot read image: {e}")

    # OCR
    try:
        ocr_result = extract_text(pil_image)
    except Exception as e:
        logger.error(f"OCR error: {e}")
        raise HTTPException(500, f"OCR failed: {e}")

    detected = ocr_result["text"].strip()
    confidence = ocr_result["confidence"]
    preprocessed_b64 = ocr_result["preprocessed_b64"]

    if not detected:
        raise HTTPException(422, "No text detected. Try a clearer photo with visible text.")

    # Translate
    translated = detected  # default fallback
    try:
        result = translate(detected, language)
        if result:
            translated = result
    except Exception as e:
        logger.error(f"Translation error: {e}")

    return {
        "status": "success",
        "detected_text": detected,
        "translated_text": translated,
        "confidence": round(confidence, 1),
        "target_language": language,
        "preprocessed_image": preprocessed_b64
    }

@app.post("/api/translate")
def translate_only(req: TranslateRequest):
    if not req.text.strip():
        raise HTTPException(400, "Text is empty.")
    result = translate(req.text, req.target_language)
    if not result:
        raise HTTPException(503, "Translation unavailable.")
    return {"original": req.text, "translated": result, "language": req.target_language}

# Serve frontend
if os.path.isdir(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
