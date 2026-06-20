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
        # Fallback mock response for prototype testing when API key is missing
        return """PATIENT_INFO | Het Patel | 21 | Male | SRL Diagnostics | 20 Jun 2026
Hemoglobin | 11.2 | g/dL | 13.5 | 17.5
WBC Count | 7200 | /μL | 4000 | 11000
RBC Count | 4.1 | M/μL | 4.5 | 5.9
Platelets | 215000 | /μL | 150000 | 400000
Creatinine | 0.9 | mg/dL | 0.7 | 1.3
Urea (BUN) | 32 | mg/dL | 15 | 45
Uric Acid | 7.8 | mg/dL | 3.5 | 7.2
SGPT (ALT) | 28 | U/L | 7 | 40
SGOT (AST) | 26 | U/L | 10 | 40
Bilirubin | 0.9 | mg/dL | 0.2 | 1.2
Fasting Glucose | 112 | mg/dL | 70 | 100
HbA1c | 6.1 | % | 0 | 5.7
Total Cholesterol | 198 | mg/dL | 0 | 200
LDL Cholesterol | 128 | mg/dL | 0 | 130
HDL Cholesterol | 38 | mg/dL | 40 | 60
Triglycerides | 168 | mg/dL | 0 | 150
TSH | 5.8 | mIU/L | 0.4 | 4.0
Vitamin D | 14 | ng/mL | 30 | 100
Vitamin B12 | 218 | pg/mL | 200 | 900
Serum Iron | 62 | ug/dL | 60 | 170"""

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
