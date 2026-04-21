"""
SignLens - ocr.py
OCR pipeline using OpenCV preprocessing + Tesseract
"""

import io
import base64
import numpy as np
import cv2
import pytesseract
from PIL import Image


def preprocess_image(pil_image: Image.Image) -> np.ndarray:
    """
    OpenCV preprocessing pipeline:
    1. Resize to 1024px width
    2. Convert to grayscale
    3. Denoise
    4. Adaptive threshold
    5. Deskew
    """
    img = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

    # 1. Resize
    target_w = 1024
    h, w = img.shape[:2]
    if w != target_w:
        scale = target_w / w
        img = cv2.resize(img, (target_w, int(h * scale)), interpolation=cv2.INTER_CUBIC)

    # 2. Grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 3. Denoise
    gray = cv2.medianBlur(gray, 3)

    # 4. Adaptive threshold
    thresh = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        blockSize=31, C=10
    )

    # 5. Deskew
    thresh = _deskew(thresh)

    return cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)


def _deskew(img: np.ndarray) -> np.ndarray:
    """Correct skew angle using minAreaRect"""
    coords = np.column_stack(np.where(img > 0))
    if coords.shape[0] < 5:
        return img
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = 90 + angle
    h, w = img.shape[:2]
    M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
    return cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)


def to_base64(bgr_img: np.ndarray) -> str:
    """Encode OpenCV image as base64 PNG string"""
    ok, buf = cv2.imencode(".png", bgr_img)
    if not ok:
        return ""
    return base64.b64encode(buf.tobytes()).decode("utf-8")


def extract_text(pil_image: Image.Image) -> dict:
    """
    Full OCR pipeline.
    Returns: { text, confidence, preprocessed_b64 }
    """
    processed = preprocess_image(pil_image)
    processed_pil = Image.fromarray(cv2.cvtColor(processed, cv2.COLOR_BGR2RGB))

    # Tesseract config: LSTM engine, uniform text block
    config = r"--oem 3 --psm 6"

    data = pytesseract.image_to_data(
        processed_pil,
        config=config,
        output_type=pytesseract.Output.DICT
    )

    words = []
    confidences = []
    for i, word in enumerate(data["text"]):
        conf = int(data["conf"][i])
        if conf > 0 and word.strip():
            words.append(word)
            confidences.append(conf)

    text = " ".join(words)
    avg_conf = float(np.mean(confidences)) if confidences else 0.0

    # Fallback to simple string extraction
    if not text.strip():
        text = pytesseract.image_to_string(processed_pil, config=config)

    return {
        "text": text,
        "confidence": round(avg_conf, 2),
        "preprocessed_b64": to_base64(processed)
    }
