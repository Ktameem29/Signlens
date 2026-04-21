"""
SignLens - ocr.py
Improved OCR pipeline using OpenCV preprocessing + Tesseract
Handles multiple languages and real street sign images
"""

import io
import base64
import numpy as np
import cv2
import pytesseract
from PIL import Image


def preprocess_image(pil_image: Image.Image) -> list:
    """
    Generate multiple preprocessed versions to maximise OCR accuracy.
    Returns list of (label, numpy_bgr_image) tuples.
    """
    img = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

    # Resize to standard width
    target_w = 1200
    h, w = img.shape[:2]
    if w < target_w:
        scale = target_w / w
        img = cv2.resize(img, (target_w, int(h * scale)), interpolation=cv2.INTER_CUBIC)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    versions = []

    # Version 1: Adaptive threshold
    denoised = cv2.medianBlur(gray, 3)
    thresh1 = cv2.adaptiveThreshold(denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                     cv2.THRESH_BINARY, 31, 10)
    versions.append(("adaptive", cv2.cvtColor(thresh1, cv2.COLOR_GRAY2BGR)))

    # Version 2: Otsu threshold
    _, thresh2 = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    versions.append(("otsu", cv2.cvtColor(thresh2, cv2.COLOR_GRAY2BGR)))

    # Version 3: Sharpened original
    kernel = np.array([[-1,-1,-1],[-1,9,-1],[-1,-1,-1]])
    sharpened = cv2.filter2D(gray, -1, kernel)
    versions.append(("sharp", cv2.cvtColor(sharpened, cv2.COLOR_GRAY2BGR)))

    # Version 4: Contrast enhanced
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    enhanced = clahe.apply(gray)
    versions.append(("clahe", cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)))

    return versions


def run_tesseract(pil_image: Image.Image, config: str) -> tuple:
    """Run tesseract and return (text, avg_confidence)"""
    try:
        data = pytesseract.image_to_data(
            pil_image, config=config,
            output_type=pytesseract.Output.DICT
        )
        words, confs = [], []
        for i, word in enumerate(data["text"]):
            conf = int(data["conf"][i])
            if conf > 30 and word.strip():
                words.append(word.strip())
                confs.append(conf)
        text = " ".join(words)
        avg = float(np.mean(confs)) if confs else 0.0
        return text, avg
    except Exception:
        return "", 0.0


def to_base64(bgr_img: np.ndarray) -> str:
    ok, buf = cv2.imencode(".png", bgr_img)
    if not ok:
        return ""
    return base64.b64encode(buf.tobytes()).decode("utf-8")


def extract_text(pil_image: Image.Image) -> dict:
    """
    Try multiple preprocessing + tesseract config combinations.
    Return the best result (highest confidence, non-empty text).
    """
    versions = preprocess_image(pil_image)

    configs = [
        r"--oem 3 --psm 6",   # Uniform block of text
        r"--oem 3 --psm 11",  # Sparse text
        r"--oem 3 --psm 4",   # Single column
        r"--oem 3 --psm 3",   # Fully automatic
        r"--oem 3 --psm 7",   # Single line
    ]

    best_text = ""
    best_conf = 0.0
    best_img  = versions[0][1]

    for label, bgr in versions:
        pil = Image.fromarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))
        for cfg in configs:
            text, conf = run_tesseract(pil, cfg)
            # Prefer result with real words (letters) and higher confidence
            if text.strip() and conf > best_conf and any(c.isalpha() for c in text):
                best_text = text
                best_conf = conf
                best_img  = bgr

    # Final fallback: plain string on original
    if not best_text.strip():
        try:
            best_text = pytesseract.image_to_string(
                pil_image, config=r"--oem 3 --psm 6"
            ).strip()
        except Exception:
            best_text = ""

    return {
        "text": best_text,
        "confidence": round(best_conf, 2),
        "preprocessed_b64": to_base64(best_img)
    }
