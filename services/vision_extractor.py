"""
Aayu AI — Vision Extractor
Uses Gemini 1.5 Flash Vision API for phone camera photos.
"""
import google.generativeai as genai
import os
from PIL import Image


def extract_text_from_photo(image_path):
    """Extract blood test data from a phone camera photo using Gemini Vision.
    
    Args:
        image_path: Path to the phone photo.
    
    Returns:
        str: Extracted structured text from the report image.
    """
    api_key = os.environ.get('GEMINI_API_KEY', '')
    if not api_key:
        return None

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-flash-latest')

        img = Image.open(image_path)

        prompt = """You are a medical report data extractor. Analyze this blood test report image.
Extract ALL blood test parameters in this exact format, one per line:
TEST_NAME | VALUE | UNIT | REFERENCE_LOW | REFERENCE_HIGH

Rules:
- Extract every single parameter visible in the report
- Include the exact numeric values as shown
- Include units (g/dL, mg/dL, mIU/L, etc.)
- Include reference ranges if visible
- If reference range is not visible, use standard Indian adult ranges
- Also extract: Patient Name, Age, Gender, Lab Name, Test Date if visible

Start with a header line: PATIENT_INFO | name | age | gender | lab | date
Then list all parameters."""

        response = model.generate_content([prompt, img])
        return response.text.strip() if response.text else None

    except Exception as e:
        print(f"Vision extraction error: {e}")
        return None
