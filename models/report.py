"""
Aayu AI — Report Model
"""
from datetime import datetime


class Report:
    """Blood test report with health scores."""

    def __init__(self, user_id, member_id, lab_name='', test_date=None,
                 input_mode='pdf', language='en'):
        self.id = None
        self.user_id = user_id
        self.member_id = member_id
        self.lab_name = lab_name
        self.test_date = test_date or datetime.utcnow()
        self.input_mode = input_mode  # 'pdf', 'scan', 'phone'
        self.language = language  # 'en', 'hi', 'gu'

        # Scores (computed after analysis)
        self.health_score = 0
        self.blood_score = 0
        self.kidney_score = 0
        self.liver_score = 0
        self.glucose_score = 0
        self.thyroid_score = 0
        self.lipid_score = 0
        self.vitamin_score = 0

        # Counts
        self.total_params = 0
        self.abnormal_count = 0
        self.critical_count = 0

        self.created_at = datetime.utcnow()

    def to_dict(self):
        return {
            'id': self.id,
            'lab_name': self.lab_name,
            'test_date': self.test_date.isoformat() if self.test_date else None,
            'input_mode': self.input_mode,
            'health_score': self.health_score,
            'total_params': self.total_params,
            'abnormal_count': self.abnormal_count,
            'critical_count': self.critical_count
        }
