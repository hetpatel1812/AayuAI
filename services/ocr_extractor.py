"""
Aayu AI — OCR Extractor
Uses OpenCV preprocessing + EasyOCR for scanned images.
"""
import cv2
import numpy as np
import easyocr


# Initialize EasyOCR reader (lazy-loaded)
_reader = None


def _get_reader():
    global _reader
    if _reader is None:
        _reader = easyocr.Reader(['en'], gpu=False)
    return _reader


def preprocess_image(image_path):
    """Apply OpenCV preprocessing to improve OCR accuracy.
    
    Steps: grayscale → denoise → adaptive threshold → deskew
    """
    img = cv2.imread(image_path)
    if img is None:
        return None

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Denoise
    denoised = cv2.fastNlMeansDenoising(gray, h=10)

    # Adaptive threshold for better text contrast
    thresh = cv2.adaptiveThreshold(
        denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 11, 2
    )

    return thresh


def extract_text_from_image(image_path):
    """Extract text from a scanned image using EasyOCR.
    
    Args:
        image_path: Path to the scanned image file.
    
    Returns:
        str: Extracted text content.
    """
    try:
        processed = preprocess_image(image_path)
        if processed is None:
            return None

        reader = _get_reader()
        results = reader.readtext(processed, detail=0, paragraph=True)
        text = '\n'.join(results)
        return text.strip() if text.strip() else None

    except Exception as e:
        print(f"OCR extraction error: {e}")
        return None
