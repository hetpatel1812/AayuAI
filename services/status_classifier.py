"""
Aayu AI — Status Classifier
Classifies blood test values as NORMAL, HIGH, LOW, or CRITICAL.
"""


# Critical thresholds (life-threatening values)
CRITICAL_THRESHOLDS = {
    'hemoglobin': {'low': 7.0, 'high': 20.0},
    'glucose': {'low': 50, 'high': 400},
    'creatinine': {'low': 0, 'high': 4.0},
    'platelets': {'low': 50000, 'high': 1000000},
    'potassium': {'low': 2.5, 'high': 6.5},
}


def classify_status(test_name, value, ref_low, ref_high):
    """Classify a blood test value into status categories.
    
    Args:
        test_name: Name of the test parameter.
        value: The measured value.
        ref_low: Lower bound of normal range.
        ref_high: Upper bound of normal range.
    
    Returns:
        str: 'NORMAL', 'HIGH', 'LOW', or 'CRITICAL'
    """
    # Check critical thresholds first
    name_lower = test_name.lower()
    for key, thresholds in CRITICAL_THRESHOLDS.items():
        if key in name_lower:
            if value <= thresholds['low'] or value >= thresholds['high']:
                return 'CRITICAL'

    # Standard classification
    if ref_low > 0 and value < ref_low:
        return 'LOW'
    elif ref_high > 0 and value > ref_high:
        return 'HIGH'
    else:
        return 'NORMAL'


def classify_all(parameters):
    """Classify all parameters in a list.
    
    Args:
        parameters: List of parameter dicts with test, value, ref_low, ref_high.
    
    Returns:
        list[dict]: Parameters with 'status' field added.
    """
    for param in parameters:
        param['status'] = classify_status(
            param['test'], param['value'],
            param.get('ref_low', 0), param.get('ref_high', 0)
        )
    return parameters
