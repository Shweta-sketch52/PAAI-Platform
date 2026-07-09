import os
from dotenv import load_dotenv

load_dotenv()

def _make_db_url(url: str) -> str:
    """
    Convert any postgresql:// URL to postgresql+pg8000://
    pg8000 is pure Python — no compilation needed on Windows.
    Falls back to SQLite if no DATABASE_URL is set (great for local dev).
    """
    if not url:
        return 'sqlite:///paai_dev.db'
    # Already has a driver prefix — leave it
    if '+' in url.split('://')[0]:
        return url
    # Replace bare postgresql:// or postgres://
    return url.replace('postgresql://', 'postgresql+pg8000://', 1)\
               .replace('postgres://',    'postgresql+pg8000://', 1)

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'paai-dev-secret-change-in-production')
    _raw_db   = os.environ.get('DATABASE_URL', '')
    SQLALCHEMY_DATABASE_URI     = _make_db_url(_raw_db)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED            = True
    MAX_CONTENT_LENGTH          = 16 * 1024 * 1024   # 16 MB
    UPLOAD_FOLDER               = os.path.join(os.path.dirname(__file__), 'app', 'static', 'uploads')
    ALLOWED_EXTENSIONS          = {'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx'}
    MAIL_SERVER                 = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT                   = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS                = True
    MAIL_USERNAME               = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD               = os.environ.get('MAIL_PASSWORD')
    OPENAI_API_KEY              = os.environ.get('OPENAI_API_KEY', '')
    SESSION_COOKIE_HTTPONLY     = True
    SESSION_COOKIE_SAMESITE     = 'Lax'
    PERMANENT_SESSION_LIFETIME  = 86400   # 24 hours

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True

config = {
    'development': DevelopmentConfig,
    'production':  ProductionConfig,
    'default':     DevelopmentConfig,
}
