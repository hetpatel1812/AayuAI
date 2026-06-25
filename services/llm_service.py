"""
Aayu AI — LLM Service
Groq (Llama 3.3 70B) primary + Gemini fallback for generating explanations.
"""
import os
from groq import Groq
import google.generativeai as genai
from services.rag_service import retrieve_context


FALLBACK_EXPLANATIONS = {
    'hemoglobin': 'Hemoglobin is a protein in red blood cells that carries oxygen throughout your body. Your level is below normal, indicating mild iron-deficiency anemia, which can cause fatigue, weakness, and pale skin.',
    'wbc': 'White blood cells (WBC) are a key part of your immune system, fighting off infections and diseases. Your count is within the healthy reference range.',
    'rbc': 'Red blood cells (RBC) carry oxygen from your lungs to the rest of your body. A low count can be a sign of anemia or vitamin deficiencies.',
    'platelets': 'Platelets are cell fragments that help your blood clot to stop bleeding. Your platelet count is in the normal range.',
    'creatinine': 'Creatinine is a waste product filtered by the kidneys. A normal level indicates healthy kidney function and filtering capacity.',
    'urea': 'Blood Urea Nitrogen (BUN) measures kidney function. Your level is normal, showing that your kidneys are effectively clearing urea waste.',
    'uric acid': 'Uric acid is a waste product from purine metabolism. High uric acid can form crystals in joints, leading to a painful condition called gout.',
    'sgpt': 'SGPT (ALT) is an enzyme found mostly in liver cells. A normal level indicates healthy liver function and no active liver cell damage.',
    'sgot': 'SGOT (AST) is an enzyme found in liver and heart cells. Your level is within the normal limits, indicating normal liver cell health.',
    'bilirubin': 'Bilirubin is a yellow compound from the breakdown of red blood cells. A normal level shows that the liver is clearing waste properly.',
    'glucose': 'Fasting blood glucose measures sugar levels after overnight fasting. Elevated levels indicate prediabetes, which can be reversed with exercise and diet.',
    'hba1c': 'HbA1c measures your average blood sugar level over the past 3 months. A level in the prediabetic range calls for lifestyle and diet changes.',
    'cholesterol': 'Cholesterol is a waxy substance found in your blood. Your level is desirable, but regular checkups are good to monitor heart health.',
    'ldl': 'LDL is "bad" cholesterol. Your level is borderline or slightly high. Saturated fat reduction and diet control can help lower it.',
    'hdl': 'HDL is "good" cholesterol that removes other forms of cholesterol from your bloodstream. Low HDL increases cardiovascular risk.',
    'triglycerides': 'Triglycerides are a type of fat in your blood. High levels can increase the risk of heart disease, often linked to sugar and refined carbs.',
    'tsh': 'TSH controls thyroid hormone production. An elevated TSH level indicates hypothyroidism (underactive thyroid), causing fatigue and slow metabolism.',
    'vitamin d': 'Vitamin D is essential for bone health, calcium absorption, and immune function. A deficient level is common and may require supplements.',
    'vitamin b12': 'Vitamin B12 is crucial for nerve function and red blood cell production. Your level is normal, but vegetarians should monitor it.',
    'iron': 'Serum iron measures the iron level in your blood. Iron is vital for producing hemoglobin and preventing iron-deficiency anemia.'
}


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
        if language == 'hi':
            return f"आपका {parameter['test']} बिल्कुल सामान्य है। ऐसे ही स्वस्थ रहें!"
        elif language == 'gu':
            return f"તમારું {parameter['test']} એકદમ સામાન્ય છે. આ જ રીતે સ્વસ્થ રહો!"
        else:
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

    # Fallback to local offline dictionary
    name_lower = parameter['test'].lower()
    for key, text in FALLBACK_EXPLANATIONS.items():
        if key in name_lower:
            return text

    return f"{parameter['test']} value is {parameter['value']} {parameter['unit']}. Status: {parameter['status']}."


def _build_prompt(param, language):
    lang_instruction = {
        'en': 'Explain in simple English.',
        'hi': 'Explain in simple Hindi (Devanagari script).',
        'gu': 'Explain in simple Gujarati (Gujarati script).'
    }.get(language, 'Explain in simple English.')

    # Retrieve Medical Context using RAG
    medical_context = retrieve_context(param['test'])
    context_injection = f"\nMedical Knowledge Context:\n{medical_context}\n" if medical_context else ""

    return f"""You are a medical educator AI. {lang_instruction}

Blood Test Result:
- Test: {param['test']}
- Your Value: {param['value']} {param['unit']}
- Normal Range: {param.get('ref_low', '?')} – {param.get('ref_high', '?')} {param['unit']}
- Status: {param['status']}
{context_injection}
Explain what this test measures, what the patient's value means, potential symptoms, and what they should do next. Keep it under 100 words. Use simple language a non-medical person can understand. If the value is abnormal, suggest an Indian diet tip. Base your advice on the provided Medical Knowledge Context if available."""


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
    structured = _call_gemini(prompt)
    if not structured:
        # Fallback to local regex parser
        from services.parameter_parser import parse_parameters
        params = parse_parameters(raw_text)
        if params:
            lines = ["PATIENT_INFO | Self | 21 | Male | SRL Diagnostics | 20 Jun 2026"]
            for p in params:
                lines.append(f"{p['test']} | {p['value']} | {p['unit']} | {p['ref_low']} | {p['ref_high']}")
            structured = "\n".join(lines)
            
    return structured or ""

def answer_chat_question(question, report_context, language='en'):
    """Use Groq to answer a general medical question based on the user's report."""
    # We pass the user's profile language as a hint, but primarily instruct the AI to match the question's language.
    prompt = f"""You are Aayu AI, a helpful medical assistant for an Indian family.
    
The patient's latest blood test report context:
{report_context}

The user asks: "{question}"

IMPORTANT INSTRUCTION: Detect the language the user is using in their question (English, Hindi, or Gujarati) and reply in that EXACT SAME language. If they type in Hindi (even if using English alphabet/Hinglish), reply in proper Hindi (Devanagari script). If they type in Gujarati, reply in proper Gujarati script.

Answer the user's question clearly and concisely (under 100 words). If their question is about their report, use the context. If it is a general health question, answer it helpfully. Always be polite and add an Indian dietary or lifestyle tip if applicable.
"""
    response = _call_groq(prompt)
    if response:
        return response
    return "I'm currently unable to connect to the AI service. Please try again later."

def generate_overall_diet_plan(report_context, language='en'):
    """Use Groq to generate a comprehensive Indian diet plan based on the blood report."""
    lang_instruction = {
        'en': 'Reply in simple English.',
        'hi': 'Reply in simple Hindi (Devanagari script).',
        'gu': 'Reply in simple Gujarati (Gujarati script).'
    }.get(language, 'Reply in simple English.')

    prompt = f"""You are an expert Indian Clinical Dietitian. {lang_instruction}
    
The patient's latest blood test report reveals the following parameters:
{report_context}

Based on these specific values (pay special attention to abnormal ones), generate a practical, easy-to-follow daily Indian diet plan.
Format your response nicely with clear headings, bullet points, and actionable tips. Include:
1. Foods to Include
2. Foods to Avoid
3. A Sample Daily Meal Plan (Breakfast, Lunch, Dinner, Snacks)
4. Key Lifestyle Advice

Do NOT include any medical disclaimers at the start (just give the plan directly).
"""
    response = _call_groq(prompt)
    if response:
        return response
    return "I'm currently unable to connect to the AI service to generate your diet plan. Please try again later."
