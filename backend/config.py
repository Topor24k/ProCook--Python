# ═══════════════════════════════════════════════════════════════════════════
# APPLICATION CONFIGURATION FILE - Environment-based Settings
# Mga Settings sa Application nga Base sa Environment
# ═══════════════════════════════════════════════════════════════════════════
# Kini nga file nagpakita sa (This file demonstrates):
# 1. OOP INHERITANCE: Ang Config classes nanggikan (inherit) sa base Config class
# 2. ENVIRONMENT-BASED CONFIGURATION: Lain-laing settings para sa dev/prod
# 3. POLYMORPHISM: Parehas nga interface (Config class) pero lain ang values
# 4. SECURITY: Nag-load ug sensitive data gikan sa environment variables (.env file)
# 5. DATABASE CONFIGURATION: Connection pooling ug optimization settings
#
# Konektado sa (Connects to):
# - backend/app.py: Gi-load via app.config.from_object(config[config_name])
# - .env file: Mga environment variables gi-load pinaagi sa load_dotenv()
# ═══════════════════════════════════════════════════════════════════════════

# I-import ang os module para sa pag-access sa environment variables
import os

# I-import ang dotenv para maka-load ug variables gikan sa .env file
# Kini nagbantay sa sensitive data (passwords, secrets) aron dili ma-include sa source code
from dotenv import load_dotenv

# I-load ang environment variables gikan sa .env file sa project root
# Ang variables ma-accessible na pinaagi sa os.getenv()
load_dotenv()


# ═══════════════════════════════════════════════════════════════════════════
# BASE CONFIGURATION CLASS - Shared settings para sa tanan environments
# Pundasyon nga Klase para sa Configuration
# ═══════════════════════════════════════════════════════════════════════════
# Kini nagpakita sa OOP CLASS-BASED CONFIGURATION
# Tanan settings kay class attributes (giload sa Flask)
# ═══════════════════════════════════════════════════════════════════════════

class Config:
    """
    Base Configuration Class - OOP parent class para sa environment configs
    
    Kini nagpakita sa (This demonstrates):
    - OOP CLASS DESIGN: Configuration isip class attributes
    - DEFAULTS WITH OVERRIDES: Naghatag fallbacks kon walay .env file
    - SECURITY: Nag-load ug sensitive data gikan sa environment
    
    Tanan child classes (DevelopmentConfig, ProductionConfig) nanggikan dinhi (inherit)
    Gigamit sa: backend/app.py via app.config.from_object()
    """
    
    # ═══ FLASK SECRET KEY ═══
    # Gigamit para sa session encryption, CSRF protection, etc.
    # SECURITY: Kinahanglan random ug secret sa production
    # Giload gikan sa .env file o mogamit ug dev default
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # ═══ DATABASE CONFIGURATION ═══
    # PostgreSQL connection string: postgresql://user:password@host:port/database
    # SECURITY: Giload gikan sa .env para magbantay sa credentials aron dili maapil sa source code
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://postgres:postgres@localhost:5432/procook'  # Fallback para sa dev
    )
    
    # I-disable ang SQLAlchemy event system (magtipig ug memory)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # ═══ DATABASE CONNECTION POOLING ═══
    # Kini nga settings nag-optimize sa database connection management
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,  # Test connections una gamiton (handles stale connections)
        'pool_recycle': 300,    # I-recycle ang connections human 5 minutes (prevents timeouts)
    }

    # ═══ SESSION CONFIGURATION ═══
    # SESSION SECURITY settings para sa Flask-Login
    # HttpOnly nagpugong sa JavaScript nga makabasa ug cookies (XSS protection)
    SESSION_COOKIE_HTTPONLY = True
    
    # SameSite=Lax nagpugong sa CSRF attacks (cookies dili ipadala sa cross-site requests)
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Ang session mahurot human 24 hours (86400 seconds) - Session expires
    PERMANENT_SESSION_LIFETIME = 86400  # 24 ka oras

    # ═══ FILE UPLOAD CONFIGURATION ═══
    # Directory alang sa mga uploaded recipe images
    # Nagtudlo sa backend/uploads/ folder
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    
    # Maximum file upload size: 5 MB (nagpugong sa DOS attacks pinaagi sa dagkong uploads)
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB max upload

    # ═══ CORS CONFIGURATION ═══
    # Allowed origins para sa cross-origin requests
    # Giload gikan sa .env isip comma-separated list
    # Pananglitan (Example): CORS_ORIGINS=http://localhost:5173,http://localhost:5000
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:5173').split(',')

# ═══════════════════════════════════════════════════════════════════════════
# DEVELOPMENT CONFIGURATION - Settings para sa local development
# Mga Settings sa Pag-develop sa Local
# ═══════════════════════════════════════════════════════════════════════════
# OOP INHERITANCE: Nanggikan (Inherits) sa tanan settings gikan sa Config base class
# ═══════════════════════════════════════════════════════════════════════════

class DevelopmentConfig(Config):
    """
    Development Configuration - Gigamit kon nagpadagan locally (sa imong computer)
    
    Kini nagpakita sa (This demonstrates):
    - OOP INHERITANCE: Nag-extend sa Config base class
    - ENVIRONMENT-SPECIFIC SETTINGS: Gi-optimize para sa development
    
    Gigamit kon (Used when): FLASK_ENV=development sa .env file
    Gipili sa: backend/app.py create_app() function
    """
    
    # I-enable ang Flask debug mode (auto-reload, detailed error pages)
    # PAHIMANGNO (WARNING): Ayaw i-enable sa production (security risk!)
    DEBUG = True
    
    # Tugoti ang cookies sa HTTP (dili lang HTTPS) para sa local development
    # Sa production, kini KINAHANGLAN True (HTTPS lang)
    SESSION_COOKIE_SECURE = False


# ═══════════════════════════════════════════════════════════════════════════
# PRODUCTION CONFIGURATION - Settings para sa deployment (pag-launch sa production)
# Mga Settings para sa Production/Live na Server
# ═══════════════════════════════════════════════════════════════════════════
# OOP INHERITANCE: Nanggikan sa Config, nag-override sa security settings
# ═══════════════════════════════════════════════════════════════════════════

class ProductionConfig(Config):
    """
    Production Configuration - Gigamit kon gi-deploy na (Heroku, AWS, etc.)
    
    Kini nagpakita sa (This demonstrates):
    - OOP INHERITANCE: Nag-extend sa Config base class
    - SECURITY HARDENING: Estrikto nga security settings para sa production
    
    Gigamit kon (Used when): FLASK_ENV=production sa environment
    Gipili sa: backend/app.py create_app() function
    """
    
    # I-disable ang debug mode (walay detailed errors, walay auto-reload)
    # IMPORTANTE (CRITICAL) kini para sa security sa production
    DEBUG = False
    
    # Kinahanglan HTTPS para sa session cookies (nagpugong sa cookie theft)
    # SECURITY: Ang cookies ipadala lang pinaagi sa encrypted connections
    SESSION_COOKIE_SECURE = True
    
    # SameSite=Lax nagpugong sa CSRF attacks
    SESSION_COOKIE_SAMESITE = 'Lax'


# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION DICTIONARY - Nag-map sa environment names ngadto sa config classes
# Dictionary nga Nag-organize sa mga Configuration
# ═══════════════════════════════════════════════════════════════════════════
# Kini nagpakita sa FACTORY PATTERN: Pagpili ug configuration base sa ngalan
# ═══════════════════════════════════════════════════════════════════════════

config = {
    'development': DevelopmentConfig,  # Para sa local development (pag-develop sa imong PC)
    'production': ProductionConfig,    # Para sa deployed application (live na sa internet)
    'default': DevelopmentConfig,      # Fallback kon wala gi-set ang FLASK_ENV
}
# Gigamit sa: backend/app.py with config[config_name]
# Pananglitan (Example): app.config.from_object(config['development'])
