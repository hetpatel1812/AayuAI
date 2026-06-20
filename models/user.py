"""
Aayu AI — User Model
"""
from datetime import datetime


class User:
    """User model for authentication and profile management."""

    def __init__(self, name, email, password_hash, city='', lang='en'):
        self.id = None
        self.name = name
        self.email = email
        self.password_hash = password_hash
        self.city = city
        self.lang = lang
        self.created_at = datetime.utcnow()

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'city': self.city,
            'lang': self.lang,
            'created_at': self.created_at.isoformat()
        }
