import pytesseract
from PIL import Image
import io

def extract_text(image_bytes: bytes) -> str:
    """
    Runs Tesseract OCR on the uploaded image bytes.
    Returns raw extracted text (used as a fallback for blurry images).
    """
    try:
        img = Image.open(io.BytesIO(image_bytes))
        # Convert to RGB in case of RGBA/palette images
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")
        text = pytesseract.image_to_string(img, config="--psm 6")
        return text.strip()
    except Exception as e:
        # OCR failure is non-fatal — Gemini Vision will still analyse the raw image
        return f"[OCR failed: {e}]"