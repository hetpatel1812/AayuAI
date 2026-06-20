"""
Aayu AI — Indian Diet Recommender
Rule-based Indian diet recommendations for abnormal blood values.
"""

DIET_RECOMMENDATIONS = {
    'hemoglobin': {
        'LOW': 'Eat palak (spinach), rajma, pomegranate, dates, sesame seeds, and beetroot. Pair iron-rich foods with Vitamin C (lemon, amla) for better absorption.',
        'HIGH': 'Stay well hydrated. Reduce red meat intake. Consult a hematologist.'
    },
    'glucose': {
        'HIGH': 'Avoid maida, white rice, sugar, soft drinks, and fruit juices. Eat methi (fenugreek), karela (bitter gourd), brown rice, oats, and dal. Walk 30 min daily.',
    },
    'hba1c': {
        'HIGH': 'Follow a low glycemic index diet. Replace white rice with brown rice or millets (bajra, jowar). Add cinnamon to tea. Exercise 30 min daily.',
    },
    'cholesterol': {
        'HIGH': 'Reduce ghee, butter, and fried snacks. Use olive oil or mustard oil. Eat oats, walnuts, flaxseed. Add methi and garlic to cooking.',
    },
    'triglycerides': {
        'HIGH': 'Avoid sugar, refined carbs, and fruit juice. Eat omega-3 rich flaxseed, walnuts, and fatty fish. Reduce alcohol completely.',
    },
    'hdl': {
        'LOW': 'Exercise regularly (brisk walking, cycling). Eat walnuts, almonds, flaxseed, olive oil. Include coconut in moderation.',
    },
    'ldl': {
        'HIGH': 'Reduce saturated fats (ghee, butter, paneer). Eat soluble fiber: oats, rajma, chana. Use mustard oil for cooking.',
    },
    'uric acid': {
        'HIGH': 'Avoid red meat, organ meats, shellfish, and alcohol. Drink 3+ litres water daily. Eat cherries, low-fat dairy, and cucumber.',
    },
    'tsh': {
        'HIGH': 'Eat iodized salt, eggs, fish, dairy. Avoid excess raw cruciferous vegetables (cabbage, broccoli) and soy products.',
        'LOW': 'Eat cruciferous vegetables (broccoli, cauliflower). Avoid excess iodine. Consult endocrinologist.',
    },
    'vitamin d': {
        'LOW': 'Get 20 min morning sunlight daily (before 10 AM). Eat fortified milk, eggs, mushrooms. Consider Vitamin D3 supplements.',
    },
    'vitamin b12': {
        'LOW': 'Eat eggs, dairy, paneer, curd. If vegetarian, consider B12 supplements or fortified foods.',
    },
    'iron': {
        'LOW': 'Eat palak, rajma, chana, jaggery, dates, amla. Cook in iron kadhai. Take with Vitamin C for absorption.',
    },
    'creatinine': {
        'HIGH': 'Reduce protein intake temporarily. Stay hydrated. Avoid NSAIDs (painkillers). Eat cucumber, lauki (bottle gourd).',
    },
    'bilirubin': {
        'HIGH': 'Drink plenty of water and fresh sugarcane juice. Avoid oily/fried foods. Eat papaya and radish.',
    },
}


def get_diet_tip(test_name, status):
    """Get an Indian diet recommendation for an abnormal parameter.
    
    Args:
        test_name: Name of the blood test.
        status: 'HIGH', 'LOW', 'CRITICAL', or 'NORMAL'.
    
    Returns:
        str: Diet recommendation, or empty string if normal.
    """
    if status == 'NORMAL':
        return ''

    name_lower = test_name.lower()
    for key, tips in DIET_RECOMMENDATIONS.items():
        if key in name_lower:
            return tips.get(status, tips.get('HIGH', tips.get('LOW', '')))

    return ''
