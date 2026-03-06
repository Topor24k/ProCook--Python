# ═══════════════════════════════════════════════════════════════════════════
# APPLICATION CONFIGURATION FILE - Environment-based Settings
# ═══════════════════════════════════════════════════════════════════════════
# This file demonstrates:
# 1. OOP INHERITANCE: Config classes inherit from base Config class
# 2. ENVIRONMENT-BASED CONFIGURATION: Different settings for dev/prod
# 3. POLYMORPHISM: Same interface (Config class) with different values
# 4. SECURITY: Loads sensitive data from environment variables (.env file)
# 5. DATABASE CONFIGURATION: Connection pooling and optimization settings
#
# Connects to:
# - backend/app.py: Loaded via app.config.from_object(config[config_name])
# - .env file: Environment variables loaded by load_dotenv()
# ═══════════════════════════════════════════════════════════════════════════

# Import os module for environment variable access
import os

# Import dotenv to load variables from .env file
# This keeps sensitive data (passwords, secrets) out of source code
from dotenv import load_dotenv

# Load environment variables from .env file in project root
# Variables become accessible via os.getenv()
load_dotenv()


# ═══════════════════════════════════════════════════════════════════════════
# BASE CONFIGURATION CLASS - Shared settings for all environments
# ═══════════════════════════════════════════════════════════════════════════
# This demonstrates OOP CLASS-BASED CONFIGURATION
# All settings are class attributes (loaded by Flask)
# ═══════════════════════════════════════════════════════════════════════════

class Config:
    """
    Base Configuration Class - OOP parent class for environment configs
    
    This demonstrates:
    - OOP CLASS DESIGN: Configuration as class attributes
    - DEFAULTS WITH OVERRIDES: Provides fallbacks if .env missing
    - SECURITY: Loads sensitive data from environment
    
    All child classes (DevelopmentConfig, ProductionConfig) inherit these
    Used in: backend/app.py via app.config.from_object()
    """
    
    # ═══ FLASK SECRET KEY ═══
    # Used for session encryption, CSRF protection, etc.
    # SECURITY: Must be random and secret in production
    # Loaded from .env file or uses dev default
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # ═══ DATABASE CONFIGURATION ═══
    # PostgreSQL connection string: postgresql://user:password@host:port/database
    # SECURITY: Loaded from .env to keep credentials out of source code
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://postgres:postgres@localhost:5432/procook'  # Fallback for dev
    )
    
    # Disable SQLAlchemy event system (saves memory)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # ═══ DATABASE CONNECTION POOLING ═══
    # These settings optimize database connection management
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,  # Test connections before using (handles stale connections)
        'pool_recycle': 300,    # Recycle connections after 5 minutes (prevents timeouts)
    }

    # ═══ SESSION CONFIGURATION ═══
    # SESSION SECURITY settings for Flask-Login
    # HttpOnly prevents JavaScript from reading cookies (XSS protection)
    SESSION_COOKIE_HTTPONLY = True
    
    # SameSite=Lax prevents CSRF attacks (cookies not sent on cross-site requests)
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Session expires after 24 hours (86400 seconds)
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours

    # ═══ FILE UPLOAD CONFIGURATION ═══
    # Directory for uploaded recipe images
    # Points to backend/uploads/ folder
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    
    # Maximum file upload size: 5 MB (prevents DOS attacks via large uploads)
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB max upload

    # ═══ CORS CONFIGURATION ═══
    # Allowed origins for cross-origin requests
    # Loaded from .env as comma-separated list
    # Example: CORS_ORIGINS=http://localhost:5173,http://localhost:5000
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:5173').split(',')

# ═══════════════════════════════════════════════════════════════════════════
# DEVELOPMENT CONFIGURATION - Settings for local development
# ═══════════════════════════════════════════════════════════════════════════
# OOP INHERITANCE: Inherits all settings from Config base class
# ═══════════════════════════════════════════════════════════════════════════

class DevelopmentConfig(Config):
    """
    Development Configuration - Used when running locally
    
    This demonstrates:
    - OOP INHERITANCE: Extends Config base class
    - ENVIRONMENT-SPECIFIC SETTINGS: Optimized for development
    
    Used when: FLASK_ENV=development in .env file
    Selected in: backend/app.py create_app() function
    """
    
    # Enable Flask debug mode (auto-reload, detailed error pages)
    # WARNING: Never enable in production (security risk)
    DEBUG = True
    
    # Allow cookies over HTTP (not just HTTPS) for local development
    # In production, this MUST be True (HTTPS only)
    SESSION_COOKIE_SECURE = False


# ═══════════════════════════════════════════════════════════════════════════
# PRODUCTION CONFIGURATION - Settings for deployment
# ═══════════════════════════════════════════════════════════════════════════
# OOP INHERITANCE: Inherits from Config, overrides security settings
# ═══════════════════════════════════════════════════════════════════════════

class ProductionConfig(Config):
    """
    Production Configuration - Used when deployed (Heroku, AWS, etc.)
    
    This demonstrates:
    - OOP INHERITANCE: Extends Config base class
    - SECURITY HARDENING: Strict security settings for production
    
    Used when: FLASK_ENV=production in environment
    Selected in: backend/app.py create_app() function
    """
    
    # Disable debug mode (no detailed errors, no auto-reload)
    # CRITICAL for security in production
    DEBUG = False
    
    # Require HTTPS for session cookies (prevents cookie theft)
    # SECURITY: Cookies only sent over encrypted connections
    SESSION_COOKIE_SECURE = True
    
    # SameSite=Lax prevents CSRF attacks
    SESSION_COOKIE_SAMESITE = 'Lax'


# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION DICTIONARY - Maps environment names to config classes
# ═══════════════════════════════════════════════════════════════════════════
# This demonstrates FACTORY PATTERN: Select configuration by name
# ═══════════════════════════════════════════════════════════════════════════

config = {
    'development': DevelopmentConfig,  # For local development
    'production': ProductionConfig,    # For deployed application
    'default': DevelopmentConfig,      # Fallback if FLASK_ENV not set
}
# Used in: backend/app.py with config[config_name]
# Example: app.config.from_object(config['development'])
