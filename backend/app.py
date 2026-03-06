# ═══════════════════════════════════════════════════════════════════════════
# FLASK APPLICATION FACTORY FILE - Pag-setup ug Configuration sa Application
# File para sa Paghimo sa Flask Application
# ═══════════════════════════════════════════════════════════════════════════
# Kini nga file nagpakita sa (This file demonstrates):
# 1. APPLICATION FACTORY PATTERN: create_app() function naghimo ug Flask instances
# 2. DEPENDENCY INJECTION: Ang mga extensions gi-initialize with app context
# 3. MIDDLEWARE CONFIGURATION: CORS, Login Manager, Database connections
# 4. BLUEPRINT REGISTRATION: Modular route organization (Separation of Concerns)
# 5. ERROR HANDLING: Custom error handlers para sa authentication
#
# Konektado sa (Connects to):
# - run.py: Nagtawag ug create_app() para magsugod sa application
# - backend/config.py: Nag-load sa configuration settings
# - backend/models.py: Nag-initialize sa database gamit ang db.init_app(app)
# - backend/routes/*.py: Nag-register sa tanan route blueprints para sa API endpoints
# ═══════════════════════════════════════════════════════════════════════════

# I-import ang os module para sa file system ug environment variable operations
import os

# I-import ang Flask core components - Pundasyon sa framework
from flask import Flask, jsonify, send_from_directory  # Flask class, JSON responses, pag-serve sa static files

# I-import ang CORS (Cross-Origin Resource Sharing) para sa frontend-backend communication
# Nagtugot sa React frontend (port 5173) nga makig-communicate sa Flask backend (port 5000)
from flask_cors import CORS

# I-import ang Flask-Login para sa user session authentication management
# Naghatag ug @login_required decorator ug current_user object
from flask_login import LoginManager

# I-import ang Flask-Migrate para sa database migration management (schema version control)
from flask_migrate import Migrate

# I-import ang configuration dictionary gikan sa config.py (konekta sa backend/config.py)
from backend.config import config

# I-import ang database instance ug User model (konekta sa backend/models.py)
# db gigamit para sa database initialization, User kinahanglan sa LoginManager
from backend.models import db, User


# ═══════════════════════════════════════════════════════════════════════════
# APPLICATION FACTORY FUNCTION - Naghimo ug nag-configure sa Flask app instance
# Function Para Sa Paghimo Sa Application
# ═══════════════════════════════════════════════════════════════════════════
# Kini nagpakita sa FACTORY DESIGN PATTERN sa OOP
# Mga Kaayohan (Benefits):
# - Nagtugot ug daghang app instances nga lain-laing configurations (testing, production)
# - Naglangan sa initialization hangtud mahimo ang app context
# - Nag-enable sa proper dependency injection
# Ginatawag gikan sa: run.py kon magsugod ang server
# ═══════════════════════════════════════════════════════════════════════════

def create_app(config_name=None):
    """
    Application factory function - naghimo ug nag-configure sa Flask application
    
    OOP DESIGN PATTERN: Factory Method
    Kini nga function naghimo ug Flask app instances nga angay nga na-configure
    Nagtugot sa paghimo ug lain-laing instances para sa development, testing, production
    
    Mga Parameters:
    - config_name: 'development', 'production', or 'default' (gikan sa backend/config.py)
    
    Mobalik ug (Returns): Na-configure na nga Flask application instance
    
    Ginatawag gikan sa: run.py para magsugod sa application server
    """
    
    # ═══ PAG-LOAD SA CONFIGURATION (Configuration Loading) ═══
    # Kuhaon ang config name gikan sa environment variable o mogamit ug 'default'
    # Kini nagpakita sa ENVIRONMENT-BASED CONFIGURATION (12-factor app pattern)
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'default')  # Magbasa gikan sa .env file

    # Paghimo ug Flask application instance (Create Flask app)
    # static_folder=None kay kita mismo mag-handle sa static files manually (tan-awa ang serve_frontend sa ubos)
    # Kini naghatag kanato ug kontrol kon unsaon pag-serve sa frontend build files
    app = Flask(__name__,
                static_folder=None)  # Kita manual mag-serve sa static files
    
    # I-load ang configuration gikan sa backend/config.py base sa environment
    # config[config_name] mobalik ug DevelopmentConfig o ProductionConfig class
    # app.config.from_object() mag-load sa tanan UPPERCASE attributes gikan sa klase
    # Kini nagpakita sa OOP POLYMORPHISM (lain-laing config classes apan parehas nga interface)
    app.config.from_object(config[config_name])

    # ═══ FILE SYSTEM SETUP - Pag-setup sa File System ═══
    # Sigurohon nga naa ang upload directory para sa user-uploaded recipe images
    # Maghimo ug backend/uploads/ folder kon wala pa
    # Gigamit sa: backend/routes/recipes.py save_image() function
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # ═══════════════════════════════════════════════════════════════════════════
    # INITIALIZE EXTENSIONS - Pag-initialize sa mga Extensions (Dependency Injection Pattern)
    # ═══════════════════════════════════════════════════════════════════════════
    # Kini nagpakita sa DEPENDENCY INJECTION: ang extensions gi-bind sa app human mahimo
    
    # ═══ DATABASE INITIALIZATION - Pag-initialize sa Database ═══
    # Nag-konekta sa SQLAlchemy ORM ngadto sa Flask app gamit ang application context
    # Human ani, ang 'db' object gikan sa backend/models.py makahimo na ug database operations
    # Kini nagtukod sa DATABASE CONNECTION para sa tanan CRUD operations
    db.init_app(app)
    
    # I-initialize ang Flask-Migrate para sa database schema migrations
    # Nagtugot ug version control para sa mga pagbag-o sa database structure
    # Mga Commands: flask db init, flask db migrate, flask db upgrade
    Migrate(app, db)

    # ═══ CORS CONFIGURATION (Cross-Origin Resource Sharing) ═══
    # Nagtugot sa React frontend (http://localhost:5173) nga makatawag sa Flask backend (http://localhost:5000)
    # Kon wala ang CORS, ang browser mo-block sa cross-origin requests para sa security
    CORS(app,
         origins=app.config['CORS_ORIGINS'],  # Mga allowed origins gikan sa config.py
         supports_credentials=True,            # Nagtugot ug cookies (para sa Flask-Login sessions)
         allow_headers=['Content-Type', 'Accept', 'X-XSRF-TOKEN'],  # Allowed request headers
         expose_headers=['Set-Cookie'])       # Nagtugot sa frontend nga makabasa sa Set-Cookie header

    # ═══ AUTHENTICATION SETUP - Pag-setup sa Authentication (Flask-Login) ═══
    # Nag-manage sa user sessions ug authentication state
    # Naghatag sa: @login_required decorator, current_user object
    login_manager = LoginManager()
    loginmanager.init_app(app)  # I-bind ang LoginManager sa app

    # ═══════════════════════════════════════════════════════════════════════════
    # USER LOADER CALLBACK - Kinahanglan ni Flask-Login (Required by Flask-Login)
    # ═══════════════════════════════════════════════════════════════════════════
    @login_manager.user_loader
    def load_user(user_id):
        """
        Flask-Login callback para i-reload ang user object gikan sa user_id nga naka-store sa session
        
        Kini nagpakita sa OOP CALLBACK PATTERN:
        - Flask-Login motawag ani nga function para makuha ang User object gikan sa session ID
        - Nag-konekta sa session cookie ngadto sa User model instance
        
        Unsaon paglihok (How it works):
        1. Ang user mag-log in (backend/routes/auth.py login())
        2. Flask-Login magtago sa user.id sa session cookie
        3. Sa sunod nga requests, kini nga function mag-load sa User gikan sa database gamit nang ID
        4. Ang User object mahimong available isip current_user sa tanan route handlers
        
        Konekta sa: User model sa backend/models.py (READ operation)
        Gigamit sa: Tanan @login_required routes para ma-access ang current_user
        
        TRANSACTIONAL: Nag-query sa database para mag-READ sa user record
        """
        return User.query.get(int(user_id))  # SQL: SELECT * FROM users WHERE id = ?

    # ═══════════════════════════════════════════════════════════════════════════
    # UNAUTHORIZED HANDLER - Custom error response para sa authentication failures
    # Handler sa Wala Ma-authorize nga User
    # ═══════════════════════════════════════════════════════════════════════════
    @login_manager.unauthorized_handler
    def unauthorized():
        """
        Custom error handler kon ang user mo-access ug @login_required route nga wala pa mag-log in
        
        Kini nagpakita sa ERROR HANDLING ug API CONSISTENCY:
        - Mobalik ug JSON response imbes nga HTML redirect
        - Naghatag ug consistent nga error format para sa frontend
        
        Ma-trigger kon (Triggered when):
        - Ang user mosulay ug access sa protected route nga wala'y session cookie
        - Ang session nag-expire o dili valid
        - Ang user wala pa nag-log in
        
        Gigamit sa: Tanan routes nga naka-decorate ug @login_required
        Ang frontend mo-handle niini: I-redirect sa login page kon makadawat ug 401 status
        """
        return jsonify({
            'success': False,
            'message': 'User not authenticated.'
        }), 401  # HTTP 401 Unauthorized status code

    # ═══════════════════════════════════════════════════════════════════════════
    # BLUEPRINT REGISTRATION - Modular Route Organization (Pag-organize sa mga Routes)
    # ═══════════════════════════════════════════════════════════════════════════
    # Kini nagpakita sa SEPARATION OF CONCERNS ug MODULAR ARCHITECTURE:
    # - Ang matag blueprint nag-handle sa related functionality (auth, recipes, comments, etc.)
    # - Ang mga routes naka-organize sa lain-laing files para sa maintainability
    # - Ang url_prefix nag-add sa namespace sa tanan routes sa blueprint
    #
    # Blueprint Pattern Benefits - Mga Kaayohan:
    # - Code organization (related routes naka-grupo)
    # - Reusability (ang blueprints pwede gamiton sa lain-laing apps)
    # - Team collaboration (lain-laing developers naka-work sa lain-laing blueprints)
    # ═══════════════════════════════════════════════════════════════════════════
    
    # I-import ang tanan blueprint objects gikan sa route modules
    # Ang matag blueprint gi-define sa iyang kaugalingong file gamit ang Blueprint()
    from backend.routes.auth import auth_bp              # User authentication ug profile
    from backend.routes.recipes import recipes_bp        # Recipe CRUD operations
    from backend.routes.comments import comments_bp      # Comment CRUD operations
    from backend.routes.ratings import ratings_bp        # Rating CRUD operations
    from backend.routes.saved_recipes import saved_bp    # Saved recipes management

    # I-register ang authentication blueprint - nag-handle sa user registration, login, profile
    # URL prefix: /api
    # Mga Routes: /api/register, /api/login, /api/logout, /api/user, /api/profile
    # Konekta sa: backend/routes/auth.py
    # CRUD Operations: CREATE (register), READ (user, profile), UPDATE (profile, password), DELETE (logout)
    app.register_blueprint(auth_bp, url_prefix='/api')
    
    # I-register ang recipes blueprint - nag-handle sa recipe CRUD operations
    # URL prefix: /api/recipes
    # Mga Routes: /api/recipes, /api/recipes/<id>
    # Konekta sa: backend/routes/recipes.py
    # CRUD Operations: CREATE (store), READ (index, show), UPDATE (update), DELETE (destroy)
    app.register_blueprint(recipes_bp, url_prefix='/api/recipes')
    
    # I-register ang comments blueprint - nag-handle sa comment CRUD operations
    # URL prefix: /api/recipes
    # Mga Routes: /api/recipes/<id>/comments, /api/recipes/<id>/comments/<comment_id>
    # Konekta sa: backend/routes/comments.py
    # CRUD Operations: CREATE (store), READ (index), UPDATE (update), DELETE (destroy)
    app.register_blueprint(comments_bp, url_prefix='/api/recipes')
    
    # I-register ang ratings blueprint - nag-handle sa recipe rating operations
    # URL prefix: /api/recipes
    # Mga Routes: /api/recipes/<id>/rating, /api/recipes/<id>/rating/public
    # Konekta sa: backend/routes/ratings.py
    # CRUD Operations: CREATE/UPDATE (store), READ (show, show_public), DELETE (destroy)
    app.register_blueprint(ratings_bp, url_prefix='/api/recipes')
    
    # I-register ang saved recipes blueprint - nag-handle sa pag-save/bookmark sa recipes
    # URL prefix: /api
    # Mga Routes: /api/saved-recipes, /api/recipes/<id>/saved, /api/recipes/<id>/save
    # Konekta sa: backend/routes/saved_recipes.py
    # CRUD Operations: CREATE (toggle save), READ (index, check), DELETE (toggle unsave)
    app.register_blueprint(saved_bp, url_prefix='/api')

    # ═══════════════════════════════════════════════════════════════════════════
    # COMPATIBILITY ENDPOINT - CSRF Cookie (Laravel/Sanctum compatibility)
    # Endpoint para sa Compatibility
    # ═══════════════════════════════════════════════════════════════════════════
    @app.route('/sanctum/csrf-cookie', methods=['GET'])
    def csrf_cookie():
        """
        Compatibility endpoint para sa Laravel Sanctum-style CSRF protection
        
        Ang Laravel's Sanctum SPA authentication kinahanglan mo-hit ani nga endpoint una
        para makuha ang CSRF token. Ang Flask-Login naggamit ug lain nga session approach, mao nga
        mobalik lang ta ug 204 No Content para ma-satisfy ang frontend expectations.
        
        Kini nagpakita sa API COMPATIBILITY: Pagmantener sa existing frontend contracts
        
        Gigamit sa: Frontend auth services nga nag-expect ug Laravel-style CSRF handling
        """
        return '', 204  # 204 No Content - success nga walay response body

    # ═══════════════════════════════════════════════════════════════════════════
    # FILE SERVING ROUTES - Pag-serve sa mga Static Files ug Assets
    # ═══════════════════════════════════════════════════════════════════════════
    
    @app.route('/uploads/<path:filename>')
    def serve_upload(filename):
        """
        Nag-serve sa mga uploaded files (recipe images) gikan sa backend/uploads/ directory
        
        Kini nagpakita sa FILE SERVING:
        - Ang uploaded images naka-store sa backend/uploads/recipes/
        - Kini nga route naghimo kanila nga accessible pinaagi sa URL
        
        Pananglitan (Example): /uploads/recipes/1234567890_abc123.jpg
        
        Gigamit sa:
        - backend/routes/recipes.py: save_image() nag-store sa files dinhi
        - Frontend: Nag-display sa recipe images gamit kining mga URLs
        - Recipe model: ang image field nagtipig sa relative path
        """
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    # ═══════════════════════════════════════════════════════════════════════════
    # SPA (Single Page Application) SERVING - Pag-serve sa Frontend
    # ═══════════════════════════════════════════════════════════════════════════
    # Kuhaon ang path sa 'dist' folder (built frontend)
    # Kon magrun ka ug 'npm run build', ang Vite magtukod ug optimized production files sa dist/
    dist_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dist')

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_frontend(path):
        """
        Nag-serve sa React SPA (Single Page Application) para sa production deployment
        
        Kini nagpakita sa SPA HOSTING:
        - Ang tanan routes nga wala ma-handle sa /api blueprints mo-fall through dinhi
        - Nag-serve sa built React app gikan sa dist/ folder
        - Mobalik ug index.html para sa client-side routing (React Router nag-handle sa navigation)
        
        Unsaon paglihok (How it works):
        1. Ang user mo-request ug /recipes, /login, etc.
        2. Walay API blueprint nga mo-match (sila tanan /api/*)
        3. Kini nga function mag-serve sa dist/index.html
        4. Ang React Router mo-take over ug mag-render sa appropriate component
        
        Nota (Note): Sa development, ang frontend modagan sa lain nga Vite server (port 5173)
        Kini gigamit lang sa production kon ang frontend ug backend nag-run sa same server
        
        Gigamit sa: Production deployment (Heroku, AWS, etc.)
        Development: Ang frontend gi-serve sa Vite dev server sa localhost:5173
        """
        # I-check kon ang gi-request nga path naa isip static file (JS, CSS, images)
        if path and os.path.exists(os.path.join(dist_dir, path)):
            return send_from_directory(dist_dir, path)
        
        # Kon dili, i-serve ang index.html (tugoti ang React Router nga mo-handle sa route)
        index_file = os.path.join(dist_dir, 'index.html')
        if os.path.exists(index_file):
            return send_from_directory(dist_dir, 'index.html')
        
        # Kon walay dist folder, ipakita ang helpful message
        return jsonify({'message': 'ProCook API is running. Build the frontend with: npm run build'}), 200

    # ═══════════════════════════════════════════════════════════════════════════
    # I-balik ang na-configure na nga Flask app instance (Return configured app)
    # ═══════════════════════════════════════════════════════════════════════════
    return app
