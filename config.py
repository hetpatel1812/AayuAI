"""
Aayu AI — Configuration
Environment variable loading and app configuration.
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'aayu-ai-dev-secret-key-2026')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///instance/aayu.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # AI API Keys
    GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')

    # Model configuration
    GROQ_MODEL = os.environ.get('GROQ_MODEL', 'openai/gpt-oss-120b')
    GEMINI_MODEL = os.environ.get('GEMINI_MODEL', 'gemini-1.5-flash')

    # Upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'bmp', 'tiff'}

    # ChromaDB
    CHROMA_COLLECTION = 'aayu_medical_knowledge'
    CHROMA_PERSIST_DIR = os.path.join(os.path.dirname(__file__), 'chroma_db')


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
