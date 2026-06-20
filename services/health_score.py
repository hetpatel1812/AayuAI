"""
Aayu AI — Health Score Computation Engine
Weighted scoring system (0-100) with organ-specific sub-scores.
"""


# Category weights for overall health score
CATEGORY_WEIGHTS = {
    'CBC': 0.20,
    'KFT': 0.15,
    'LFT': 0.10,
    'Glucose': 0.20,
    'Thyroid': 0.10,
    'Lipid': 0.15,
    'Vitamins': 0.10,
}


def compute_param_score(value, ref_low, ref_high, status):
    """Compute a 0-100 score for a single parameter.
    
    Normal = 100, borderline = 60-80, abnormal = 20-60, critical = 0-20
    """
    if status == 'NORMAL':
        # How centered is the value in the normal range?
        if ref_high == ref_low:
            return 100
        mid = (ref_low + ref_high) / 2
        range_half = (ref_high - ref_low) / 2
        deviation = abs(value - mid) / range_half if range_half > 0 else 0
        return max(70, 100 - (deviation * 30))

    elif status == 'CRITICAL':
        return 10

    else:  # HIGH or LOW
        # How far outside the range?
        if status == 'HIGH' and ref_high > 0:
            excess = (value - ref_high) / ref_high
        elif status == 'LOW' and ref_low > 0:
            excess = (ref_low - value) / ref_low
        else:
            excess = 0.2

        excess = min(excess, 1.0)
        return max(10, 70 - (excess * 50))


def compute_health_score(parameters):
    """Compute overall health score and sub-scores.
    
    Args:
        parameters: List of classified parameter dicts.
    
    Returns:
        dict: { 'overall': int, 'sub_scores': { category: int } }
    """
    category_scores = {}

    for param in parameters:
        cat = param.get('category', 'Other')
        score = compute_param_score(
            param['value'], param.get('ref_low', 0),
            param.get('ref_high', 0), param.get('status', 'NORMAL')
        )

        if cat not in category_scores:
            category_scores[cat] = []
        category_scores[cat].append(score)

    # Average each category
    sub_scores = {}
    for cat, scores in category_scores.items():
        sub_scores[cat] = round(sum(scores) / len(scores)) if scores else 100

    # Weighted overall
    overall = 0
    total_weight = 0
    for cat, weight in CATEGORY_WEIGHTS.items():
        if cat in sub_scores:
            overall += sub_scores[cat] * weight
            total_weight += weight

    if total_weight > 0:
        overall = round(overall / total_weight)
    else:
        overall = 100

    return {
        'overall': max(0, min(100, overall)),
        'sub_scores': sub_scores
    }
