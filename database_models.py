from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100), nullable=True)
    lang = db.Column(db.String(10), default='en')
    sms_notifications = db.Column(db.Boolean, default=True)
    email_notifications = db.Column(db.Boolean, default=True)
    
    reports = db.relationship('Report', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.email}>'

class Report(db.Model):
    __tablename__ = 'reports'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    patient_name = db.Column(db.String(100))
    patient_age = db.Column(db.String(20))
    patient_gender = db.Column(db.String(20))
    lab_name = db.Column(db.String(100))
    test_date = db.Column(db.String(50))
    health_score = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    
    parameters = db.relationship('Parameter', backref='report', lazy=True, cascade="all, delete-orphan")

class Parameter(db.Model):
    __tablename__ = 'parameters'
    
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('reports.id'), nullable=False)
    test_name = db.Column(db.String(100))
    category = db.Column(db.String(50), default='Other')
    value = db.Column(db.String(50))
    unit = db.Column(db.String(50))
    ref_low = db.Column(db.String(50))
    ref_high = db.Column(db.String(50))
    status = db.Column(db.String(20))  # NORMAL, HIGH, LOW, CRITICAL
    explanation = db.Column(db.Text)
    diet_tip = db.Column(db.Text)
