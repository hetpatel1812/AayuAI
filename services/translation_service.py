"""
Aayu AI — Translation Service
IndicTrans2 via HuggingFace Inference API for Hindi and Gujarati translations.
"""
import os
import requests


HUGGINGFACE_API = 'https://api-inference.huggingface.co/models/'

# IndicTrans2 model endpoints
MODELS = {
    'hi': 'ai4bharat/indictrans2-en-indic-1B',
    'gu': 'ai4bharat/indictrans2-en-indic-1B',
}


def translate_text(text, target_lang='hi'):
    """Translate English text to Hindi or Gujarati using IndicTrans2.
    
    Args:
        text: English text to translate.
        target_lang: Target language code ('hi' for Hindi, 'gu' for Gujarati).
    
    Returns:
        str: Translated text, or original if translation fails.
    """
    if target_lang == 'en':
        return text

    hf_token = os.environ.get('HF_TOKEN', '')
    model = MODELS.get(target_lang, MODELS['hi'])

    try:
        headers = {}
        if hf_token:
            headers['Authorization'] = f'Bearer {hf_token}'

        response = requests.post(
            f'{HUGGINGFACE_API}{model}',
            headers=headers,
            json={'inputs': text, 'parameters': {'tgt_lang': target_lang}},
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get('translation_text', text)

    except Exception as e:
        print(f"Translation error: {e}")

    return text  # Return original if translation fails


def translate_report(parameters, target_lang='hi'):
    """Translate all parameter explanations in a report.
    
    Args:
        parameters: List of parameter dicts with 'explanation' field.
        target_lang: Target language code.
    
    Returns:
        list: Parameters with translated explanations.
    """
    for param in parameters:
        if param.get('explanation'):
            param['explanation'] = translate_text(param['explanation'], target_lang)
        if param.get('diet'):
            param['diet'] = translate_text(param['diet'], target_lang)
    return parameters
