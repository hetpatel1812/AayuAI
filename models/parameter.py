"""
Aayu AI — Parameter Model
"""


class Parameter:
    """Individual blood test parameter with AI-generated explanation."""

    def __init__(self, report_id, test_name, value, unit, ref_low, ref_high,
                 status='NORMAL', category='CBC'):
        self.id = None
        self.report_id = report_id
        self.test_name = test_name
        self.value = value
        self.unit = unit
        self.ref_low = ref_low
        self.ref_high = ref_high
        self.status = status  # 'NORMAL', 'HIGH', 'LOW', 'CRITICAL'
        self.category = category  # 'CBC', 'KFT', 'LFT', 'Glucose', 'Lipid', 'Thyroid', 'Vitamins'

        # AI-generated content
        self.explanation = ''
        self.diet_tip = ''
        self.specialist = ''

    def to_dict(self):
        return {
            'test': self.test_name,
            'value': self.value,
            'unit': self.unit,
            'refLow': self.ref_low,
            'refHigh': self.ref_high,
            'status': self.status,
            'cat': self.category,
            'explanation': self.explanation,
            'diet': self.diet_tip,
            'specialist': self.specialist
        }
