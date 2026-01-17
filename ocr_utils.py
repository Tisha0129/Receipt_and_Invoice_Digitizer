import cv2
import numpy as np
import pytesseract
import re
from pdf2image import convert_from_bytes
import streamlit as st
import json
import requests

# ---------------- CONFIG ----------------
POPPLER_PATH = r"D:\poppler-25.12.0\Library\bin"
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

MODEL_NAME = "models/gemini-2.5-flash"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1/{MODEL_NAME}:generateContent"


# ---------------- LOAD IMAGE / PDF ----------------
def load_image(file_path):
    try:
        if file_path.lower().endswith(".pdf"):
            with open(file_path, "rb") as f:
                pdf_bytes = f.read()

            pages = convert_from_bytes(
                pdf_bytes,
                dpi=300,
                poppler_path=POPPLER_PATH
            )

            image = np.array(pages[0])
            return cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        else:
            img = cv2.imread(file_path)
            if img is None:
                raise ValueError("OpenCV failed to read image")
            return img
    except Exception as e:
        st.error(f"Failed to load document: {e}")
        return None


def cv_to_rgb(img):
    if img is None:
        st.stop()
    if len(img.shape) == 2:
        return cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


# ---------------- PREPROCESS ----------------
def preprocess_for_ocr(file_path):
    img = load_image(file_path)
    if img is None:
        st.stop()

    img = cv2.resize(img, None, fx=2.5, fy=2.5, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)

    gray = cv2.fastNlMeansDenoising(gray, h=20)

    thresh = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY, 31, 10
    )

    return img, thresh


# ---------------- OCR ----------------
def extract_text_from_image(image):
    config = (
        "--oem 3 --psm 4 "
        "-c preserve_interword_spaces=1 "
        "-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789₹.$:/- "
    )
    return pytesseract.image_to_string(image, config=config)


# ---------------- CLEAN OCR TEXT ----------------
def clean_ocr_text(text):
    text = text.replace("|", "I")
    text = text.replace("₹", "Rs ")
    text = re.sub(r"[^\x00-\x7F]+", " ", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()


# ---------------- PUBLIC PARSER (USED BY APP) ----------------
def parse_receipt_text(ocr_text):
    if "GEMINI_API_KEY" not in st.session_state:
        raise RuntimeError("Gemini API key missing")

    clean_text = clean_ocr_text(ocr_text)
    return gemini_parse_receipt(clean_text)


# ---------------- GEMINI PARSER ----------------
def gemini_parse_receipt(clean_text):
    api_key = st.session_state["GEMINI_API_KEY"]

    prompt = f"""
You are a JSON generator.

Rules:
- Output ONLY valid JSON
- No markdown
- No explanation
- Use null if unknown

Schema:
{{
  "vendor": string | null,
  "date": "YYYY-MM-DD" | null,
  "total": number | null,
  "tax": number | null,
  "line_items": [
    {{
      "name": string,
      "quantity": number,
      "price": number
    }}
  ]
}}

Receipt text:
{clean_text}
"""

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0}
    }

    response = requests.post(
        f"{GEMINI_URL}?key={api_key}",
        headers={"Content-Type": "application/json"},
        json=payload,
        timeout=30
    )

    response.raise_for_status()
    raw = response.json()

    text = raw["candidates"][0]["content"]["parts"][0]["text"]

    parsed = extract_json_from_text(text)
    return validate_parsed_data(parsed)


# ---------------- ROBUST JSON EXTRACTOR ----------------
def extract_json_from_text(text):
    text = text.replace("```json", "").replace("```", "").strip()

    # Try direct parse
    try:
        return json.loads(text)
    except Exception:
        pass

    # Regex recovery
    matches = re.findall(r"\{[\s\S]*\}", text)
    for m in matches:
        try:
            return json.loads(m)
        except Exception:
            continue

    raise ValueError("Gemini returned invalid JSON")


# ---------------- VALIDATION ----------------
def validate_parsed_data(data):
    result = {
        "vendor": data.get("vendor"),
        "date": data.get("date"),
        "total": data.get("total"),
        "tax": data.get("tax"),
        "line_items": []
    }

    for item in data.get("line_items", []):
        try:
            name = item.get("name")
            price = float(item.get("price"))
            qty = int(item.get("quantity", 1))

            if name and price > 0:
                result["line_items"].append({
                    "name": name.strip(),
                    "quantity": qty,
                    "price": price
                })
        except Exception:
            continue

    return result
