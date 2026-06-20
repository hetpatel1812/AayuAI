"""
Aayu AI — Family Member Model
"""
from datetime import datetime


class FamilyMember:
    """Family member profile with age-adjusted reference ranges."""

    def __init__(self, user_id, name, age, gender, relation, conditions=''):
        self.id = None
        self.user_id = user_id
        self.name = name
        self.age = age
        self.gender = gender  # 'M' or 'F'
        self.relation = relation  # 'self', 'father', 'mother', 'spouse', etc.
        self.conditions = conditions  # Comma-separated: 'Diabetic, Hypertensive'
        self.created_at = datetime.utcnow()

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'gender': self.gender,
            'relation': self.relation,
            'conditions': self.conditions
        }
