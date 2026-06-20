"""
Aayu AI — Chat History Model
"""
from datetime import datetime


class ChatMessage:
    """Chat message for AI conversation history."""

    def __init__(self, user_id, report_id, role, content):
        self.id = None
        self.user_id = user_id
        self.report_id = report_id
        self.role = role  # 'user' or 'ai'
        self.content = content
        self.created_at = datetime.utcnow()

    def to_dict(self):
        return {
            'role': self.role,
            'content': self.content,
            'created_at': self.created_at.isoformat()
        }
