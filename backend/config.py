import os
from dotenv import load_dotenv

load_dotenv()


# OOP: Base configuration class - child classes inherit these settings
class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/procook')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB max upload
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:5173').split(',')


# OOP Inheritance: extends Config with development-specific settings
class DevelopmentConfig(Config):
    DEBUG = True
    SESSION_COOKIE_SECURE = False


# OOP Inheritance: extends Config with production-specific security settings
class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True


# OOP Polymorphism: same interface (config dictionary) with different implementations
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
