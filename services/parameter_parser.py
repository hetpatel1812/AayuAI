"""
Aayu AI — Parameter Parser
Uses regex patterns to extract blood test parameters from raw text.
"""
import re


# Common blood test parameter patterns (Indian lab formats)
PARAMETER_PATTERNS = [
    # Format: Test Name ... Value Unit (Range: Low - High)
    r'([\w\s\(\)]+?)\s+(\d+\.?\d*)\s*(g/dL|mg/dL|mIU/L|ng/mL|pg/mL|U/L|%|/μL|M/μL|ug/dL|mmol/L|IU/mL)\s*(?:[\(\[]?\s*(\d+\.?\d*)\s*[-–]\s*(\d+\.?\d*)\s*[\)\]]?)?',
]

# Known parameter name mappings
KNOWN_PARAMS = {
    'hemoglobin': {'cat': 'CBC', 'unit': 'g/dL', 'ref_low': 13.5, 'ref_high': 17.5},
    'wbc': {'cat': 'CBC', 'unit': '/μL', 'ref_low': 4000, 'ref_high': 11000},
    'rbc': {'cat': 'CBC', 'unit': 'M/μL', 'ref_low': 4.5, 'ref_high': 5.9},
    'platelets': {'cat': 'CBC', 'unit': '/μL', 'ref_low': 150000, 'ref_high': 400000},
    'creatinine': {'cat': 'KFT', 'unit': 'mg/dL', 'ref_low': 0.7, 'ref_high': 1.3},
    'urea': {'cat': 'KFT', 'unit': 'mg/dL', 'ref_low': 15, 'ref_high': 45},
    'uric acid': {'cat': 'KFT', 'unit': 'mg/dL', 'ref_low': 3.5, 'ref_high': 7.2},
    'sgpt': {'cat': 'LFT', 'unit': 'U/L', 'ref_low': 7, 'ref_high': 40},
    'sgot': {'cat': 'LFT', 'unit': 'U/L', 'ref_low': 10, 'ref_high': 40},
    'bilirubin': {'cat': 'LFT', 'unit': 'mg/dL', 'ref_low': 0.2, 'ref_high': 1.2},
    'glucose': {'cat': 'Glucose', 'unit': 'mg/dL', 'ref_low': 70, 'ref_high': 100},
    'hba1c': {'cat': 'Glucose', 'unit': '%', 'ref_low': 0, 'ref_high': 5.7},
    'cholesterol': {'cat': 'Lipid', 'unit': 'mg/dL', 'ref_low': 0, 'ref_high': 200},
    'ldl': {'cat': 'Lipid', 'unit': 'mg/dL', 'ref_low': 0, 'ref_high': 130},
    'hdl': {'cat': 'Lipid', 'unit': 'mg/dL', 'ref_low': 40, 'ref_high': 60},
    'triglycerides': {'cat': 'Lipid', 'unit': 'mg/dL', 'ref_low': 0, 'ref_high': 150},
    'tsh': {'cat': 'Thyroid', 'unit': 'mIU/L', 'ref_low': 0.4, 'ref_high': 4.0},
    'vitamin d': {'cat': 'Vitamins', 'unit': 'ng/mL', 'ref_low': 30, 'ref_high': 100},
    'vitamin b12': {'cat': 'Vitamins', 'unit': 'pg/mL', 'ref_low': 200, 'ref_high': 900},
    'iron': {'cat': 'Vitamins', 'unit': 'ug/dL', 'ref_low': 60, 'ref_high': 170},
}


def parse_parameters(raw_text):
    """Parse blood test parameters from extracted text.
    
    Args:
        raw_text: Raw text extracted from report.
    
    Returns:
        list[dict]: List of parsed parameter dictionaries.
    """
    if not raw_text:
        return []

    parameters = []
    lines = raw_text.split('\n')

    for line in lines:
        line = line.strip()
        if not line or len(line) < 5:
            continue

        for pattern in PARAMETER_PATTERNS:
            matches = re.findall(pattern, line, re.IGNORECASE)
            for match in matches:
                test_name = match[0].strip()
                value = float(match[1])
                unit = match[2]
                ref_low = float(match[3]) if match[3] else 0
                ref_high = float(match[4]) if match[4] else 0

                # Look up known parameters for category and defaults
                known = _find_known_param(test_name)
                if known and ref_low == 0 and ref_high == 0:
                    ref_low = known['ref_low']
                    ref_high = known['ref_high']

                parameters.append({
                    'test': test_name,
                    'value': value,
                    'unit': unit,
                    'ref_low': ref_low,
                    'ref_high': ref_high,
                    'category': known['cat'] if known else 'Other'
                })

    return parameters


def _find_known_param(test_name):
    """Match a test name to known parameters."""
    name_lower = test_name.lower()
    for key, info in KNOWN_PARAMS.items():
        if key in name_lower:
            return info
    return None
