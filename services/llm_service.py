"""
Aayu AI — LLM Service
Groq (Llama 3.3 70B) primary + Gemini fallback for generating explanations.
"""
import os
from groq import Groq
import google.generativeai as genai


def get_explanation(parameter, language='en'):
    """Generate AI explanation for a blood test parameter.
    
    Tries Groq first, falls back to Gemini if rate-limited.
    
    Args:
        parameter: Dict with test, value, unit, status, ref_low, ref_high
        language: 'en', 'hi', or 'gu'
    
    Returns:
        str: Plain language explanation of the parameter.
    """
    # SKIP LLM FOR NORMAL PARAMETERS TO SAVE TIME & API LIMITS
    if parameter['status'] == 'NORMAL':
        return f"Your {parameter['test']} is perfectly normal. Keep it up!"

    prompt = _build_prompt(parameter, language)

    # Try Groq first (faster, free tier)
    explanation = _call_groq(prompt)
    if explanation:
        return explanation

    # Fallback to Gemini
    explanation = _call_gemini(prompt)
    if explanation:
        return explanation

    return f"{parameter['test']} value is {parameter['value']} {parameter['unit']}. Status: {parameter['status']}."


def _build_prompt(param, language):
    lang_instruction = {
        'en': 'Explain in simple English.',
        'hi': 'Explain in simple Hindi (Devanagari script).',
        'gu': 'Explain in simple Gujarati (Gujarati script).'
    }.get(language, 'Explain in simple English.')

    return f"""You are a medical educator AI. {lang_instruction}

Blood Test Result:
- Test: {param['test']}
- Your Value: {param['value']} {param['unit']}
- Normal Range: {param.get('ref_low', '?')} – {param.get('ref_high', '?')} {param['unit']}
- Status: {param['status']}

Explain what this test measures, what the patient's value means, potential symptoms, and what they should do next. Keep it under 100 words. Use simple language a non-medical person can understand. If the value is abnormal, suggest an Indian diet tip."""


def _call_groq(prompt):
    api_key = os.environ.get('GROQ_API_KEY', '')
    if not api_key:
        return None
    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model=os.environ.get('GROQ_MODEL', 'llama-3.3-70b-versatile'),
            messages=[{'role': 'user', 'content': prompt}],
            temperature=0.3,
            max_tokens=300
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Groq error: {e}")
        return None


def _call_gemini(prompt):
    api_key = os.environ.get('GEMINI_API_KEY', '')
    if not api_key:
        return None
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-flash-latest')
        response = model.generate_content(prompt)
        return response.text.strip() if response.text else None
    except Exception as e:
        print(f"Gemini error: {e}")
        return None

def structure_raw_text(raw_text):
    """
    Takes raw, unstructured text from pdfplumber or EasyOCR and uses Gemini to structure it 
    into the strict pipe-separated format required by the backend.
    """
    if not raw_text:
        return ""
        
    prompt = f"""You are a medical data extraction bot. 
I have raw, messy text extracted from a medical report using OCR/PDF extraction.
You must reformat it into exactly this format, one parameter per line:
TEST_NAME | VALUE | UNIT | REFERENCE_LOW | REFERENCE_HIGH

Rules:
1. Do not include any markdown formatting, backticks, or extra conversational text.
2. Only output the lines containing parameters.
3. If a reference range is missing, leave it blank (e.g. Test | 10 | mg/dL | | ).
4. If there's patient info, put it on the first line: PATIENT_INFO | name | age | gender | lab | date

Here is the raw text:
{raw_text}
"""
    # Use Gemini 1.5 Flash instead of Groq to avoid token rate limits on huge PDFs
    return _call_gemini(prompt) or ""


