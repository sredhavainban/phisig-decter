import os
import pytesseract
import shutil
from PIL import Image, ImageOps, ImageEnhance

# ===============================
# TESSERACT OCR CONFIG (Linux-safe)
# Use `shutil.which` to locate tesseract binary on the PATH (works in Linux/WSL)
tesseract_cmd = shutil.which("tesseract")
if tesseract_cmd:
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    print("✅ Tesseract OCR found at:", tesseract_cmd)
else:
    print("❌ Tesseract OCR not installed")


def extract_text_from_image(image_path: str) -> str:
    """Extract text from webpage screenshot using Tesseract OCR"""

    try:
        img = Image.open(image_path)

        # Preprocessing
        img = img.convert("L")  # grayscale
        img = ImageOps.autocontrast(img)
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.3)

        # OCR
        text = pytesseract.image_to_string(img, lang="eng")

        if not text:
            return ""

        text = text.strip()
        return text[:10000]

    except Exception as e:
        print("OCR ERROR:", e)
        return ""


def extract_text(image_path: str) -> str:
    """Backward-compatible wrapper used by other modules.

    Calls `extract_text_from_image` and prints the raw OCR output for debugging.
    """
    try:
        txt = extract_text_from_image(image_path)
        try:
            print('OCR(helper) RAW TEXT:', repr(txt))
            print('OCR(helper) LEN=', len(txt))
        except Exception:
            pass
        return txt
    except Exception as e:
        print('OCR(wrapper) error:', e)
        return ''
