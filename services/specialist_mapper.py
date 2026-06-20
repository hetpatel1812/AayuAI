"""
Aayu AI — Specialist Mapper
Maps abnormal organ markers to recommended specialist types.
"""

SPECIALIST_MAP = {
    'CBC': 'Hematologist',
    'KFT': 'Nephrologist',
    'LFT': 'Hepatologist / Gastroenterologist',
    'Glucose': 'Endocrinologist',
    'Thyroid': 'Endocrinologist',
    'Lipid': 'Cardiologist',
    'Vitamins': 'General Physician',
}

# Specific parameter overrides
PARAM_SPECIALIST = {
    'hemoglobin': 'Hematologist',
    'rbc': 'Hematologist',
    'wbc': 'Hematologist / Oncologist',
    'platelets': 'Hematologist',
    'creatinine': 'Nephrologist',
    'urea': 'Nephrologist',
    'uric acid': 'Rheumatologist',
    'sgpt': 'Hepatologist',
    'sgot': 'Hepatologist',
    'bilirubin': 'Gastroenterologist',
    'glucose': 'Endocrinologist',
    'hba1c': 'Endocrinologist / Diabetologist',
    'tsh': 'Endocrinologist',
    't3': 'Endocrinologist',
    't4': 'Endocrinologist',
    'cholesterol': 'Cardiologist',
    'ldl': 'Cardiologist',
    'hdl': 'Cardiologist',
    'triglycerides': 'Cardiologist',
    'vitamin d': 'General Physician / Orthopedist',
    'vitamin b12': 'General Physician / Neurologist',
    'iron': 'Hematologist',
    'calcium': 'Endocrinologist',
    'potassium': 'Nephrologist / Cardiologist',
    'sodium': 'Nephrologist',
}


def get_specialist(test_name, category='Other', status='NORMAL'):
    """Get recommended specialist for an abnormal parameter.
    
    Args:
        test_name: Name of the blood test.
        category: Parameter category (CBC, KFT, etc.).
        status: Parameter status (HIGH, LOW, CRITICAL, NORMAL).
    
    Returns:
        str: Recommended specialist, or empty string if normal.
    """
    if status == 'NORMAL':
        return ''

    # Check specific parameter mapping first
    name_lower = test_name.lower()
    for key, specialist in PARAM_SPECIALIST.items():
        if key in name_lower:
            return specialist

    # Fall back to category mapping
    return SPECIALIST_MAP.get(category, 'General Physician')
