# ═══════════════════════════════════════════════════════════════════════════
# FLASK APPLICATION FACTORY FILE - Application Setup and Configuration
# ═══════════════════════════════════════════════════════════════════════════
# This file demonstrates:
# 1. APPLICATION FACTORY PATTERN: create_app() function creates Flask instances
# 2. DEPENDENCY INJECTION: Extensions are initialized with app context
# 3. MIDDLEWARE CONFIGURATION: CORS, Login Manager, Database connections
# 4. BLUEPRINT REGISTRATION: Modular route organization (Separation of Concerns)
# 5. ERROR HANDLING: Custom error handlers for authentication
#
# Connects to:
# - run.py: Calls create_app() to start the application
# - backend/config.py: Loads configuration settings
# - backend/models.py: Initializes database with db.init_app(app)
# - backend/routes/*.py: Registers all route blueprints for API endpoints
# ═══════════════════════════════════════════════════════════════════════════

# Import os module for file system and environment variable operations
import os

# Import Flask core components
from flask import Flask, jsonify, send_from_directory  # Flask class, JSON responses, static file serving

# Import CORS (Cross-Origin Resource Sharing) for frontend-backend communication
# Allows React frontend (port 5173) to communicate with Flask backend (port 5000)
from flask_cors import CORS

# Import Flask-Login for user session authentication management
# Provides @login_required decorator and current_user object
from flask_login import LoginManager

# Import Flask-Migrate for database migration management (schema version control)
from flask_migrate import Migrate

# Import configuration dictionary from config.py (connects to backend/config.py)
from backend.config import config

# Import database instance and User model (connects to backend/models.py)
# db is used for database initialization, User is required by LoginManager
from backend.models import db, User


# ═══════════════════════════════════════════════════════════════════════════
# APPLICATION FACTORY FUNCTION - Creates and configures Flask app instance
# ═══════════════════════════════════════════════════════════════════════════
# This demonstrates the FACTORY DESIGN PATTERN in OOP
# Benefits:
# - Allows multiple app instances with different configurations (testing, production)
# - Delays initialization until app context is created
# - Enables proper dependency injection
# Called from: run.py when starting the server
# ═══════════════════════════════════════════════════════════════════════════

def create_app(config_name=None):
    """
    Application factory function - creates and configures Flask application
    
    OOP DESIGN PATTERN: Factory Method
    This function creates Flask app instances with proper configuration
    Allows creating different instances for development, testing, production
    
    Parameters:
    - config_name: 'development', 'production', or 'default' (from backend/config.py)
    
    Returns: Configured Flask application instance
    
    Called from: run.py to start the application server
    """
    
    # ═══ CONFIGURATION LOADING ═══
    # Get config name from environment variable or use 'default'
    # This demonstrates ENVIRONMENT-BASED CONFIGURATION (12-factor app pattern)
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'default')  # Reads from .env file

    # Create Flask application instance
    # static_folder=None means we handle static files manually (see serve_frontend below)
    # This gives us control over how frontend build files are served
    app = Flask(__name__,
                static_folder=None)  # We serve static files manually
    
    # Load configuration from backend/config.py based on environment
    # config[config_name] returns DevelopmentConfig or ProductionConfig class
    # app.config.from_object() loads all UPPERCASE attributes from that class
    # This demonstrates OOP POLYMORPHISM (different config classes with same interface)
    app.config.from_object(config[config_name])

    # ═══ FILE SYSTEM SETUP ═══
    # Ensure upload directory exists for user-uploaded recipe images
    # Creates backend/uploads/ folder if it doesn't exist
    # Used by: backend/routes/recipes.py save_image() function
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # ═══════════════════════════════════════════════════════════════════════════
    # INITIALIZE EXTENSIONS (Dependency Injection Pattern)
    # ═══════════════════════════════════════════════════════════════════════════
    # These demonstrate DEPENDENCY INJECTION: extensions are bound to app after creation
    
    # ═══ DATABASE INITIALIZATION ═══
    # Connects SQLAlchemy ORM to Flask app using application context
    # After this, 'db' object from backend/models.py can perform database operations
    # This establishes the DATABASE CONNECTION for all CRUD operations
    db.init_app(app)
    
    # Initialize Flask-Migrate for database schema migrations
    # Allows version control for database structure changes
    # Commands: flask db init, flask db migrate, flask db upgrade
    Migrate(app, db)

    # ═══ CORS CONFIGURATION (Cross-Origin Resource Sharing) ═══
    # Enables React frontend (http://localhost:5173) to call Flask backend (http://localhost:5000)
    # Without CORS, browser blocks cross-origin requests for security
    CORS(app,
         origins=app.config['CORS_ORIGINS'],  # Allowed origins from config.py
         supports_credentials=True,            # Allows cookies (for Flask-Login sessions)
         allow_headers=['Content-Type', 'Accept', 'X-XSRF-TOKEN'],  # Allowed request headers
         expose_headers=['Set-Cookie'])       # Allows frontend to read Set-Cookie header

    # ═══ AUTHENTICATION SETUP (Flask-Login) ═══
    # Manages user sessions and authentication state
    # Provides: @login_required decorator, current_user object
    login_manager = LoginManager()
    login_manager.init_app(app)  # Bind LoginManager to app

    # ═══════════════════════════════════════════════════════════════════════════
    # USER LOADER CALLBACK - Required by Flask-Login
    # ═══════════════════════════════════════════════════════════════════════════
    @login_manager.user_loader
    def load_user(user_id):
        """
        Flask-Login callback to reload user object from user_id stored in session
        
        This demonstrates OOP CALLBACK PATTERN:
        - Flask-Login calls this function to get User object from session ID
        - Connects session cookie to User model instance
        
        How it works:
        1. User logs in (backend/routes/auth.py login())
        2. Flask-Login stores user.id in session cookie
        3. On subsequent requests, this function loads User from database using that ID
        4. User object becomes available as current_user in all route handlers
        
        Connects to: User model in backend/models.py (READ operation)
        Used in: All @login_required routes to access current_user
        
        TRANSACTIONAL: Queries database to READ user record
        """
        return User.query.get(int(user_id))  # SQL: SELECT * FROM users WHERE id = ?

    # ═══════════════════════════════════════════════════════════════════════════
    # UNAUTHORIZED HANDLER - Custom error response for authentication failures
    # ═══════════════════════════════════════════════════════════════════════════
    @login_manager.unauthorized_handler
    def unauthorized():
        """
        Custom error handler when user accesses @login_required route without logging in
        
        This demonstrates ERROR HANDLING and API CONSISTENCY:
        - Returns JSON response instead of HTML redirect
        - Provides consistent error format for frontend
        
        Triggered when:
        - User tries to access protected route without session cookie
        - Session expires or is invalid
        - User is not logged in
        
        Used by: All routes decorated with @login_required
        Frontend handles this: Redirects to login page when it receives 401 status
        """
        return jsonify({
            'success': False,
            'message': 'User not authenticated.'
        }), 401  # HTTP 401 Unauthorized status code

    # ═══════════════════════════════════════════════════════════════════════════
    # BLUEPRINT REGISTRATION - Modular Route Organization
    # ═══════════════════════════════════════════════════════════════════════════
    # This demonstrates SEPARATION OF CONCERNS and MODULAR ARCHITECTURE:
    # - Each blueprint handles related functionality (auth, recipes, comments, etc.)
    # - Routes are organized in separate files for maintainability
    # - url_prefix adds namespace to all routes in the blueprint
    #
    # Blueprint Pattern Benefits:
    # - Code organization (related routes grouped together)
    # - Reusability (blueprints can be reused in different apps)
    # - Team collaboration (different developers work on different blueprints)
    # ═══════════════════════════════════════════════════════════════════════════
    
    # Import all blueprint objects from route modules
    # Each blueprint is defined in its respective file with Blueprint()
    from backend.routes.auth import auth_bp              # User authentication and profile
    from backend.routes.recipes import recipes_bp        # Recipe CRUD operations
    from backend.routes.comments import comments_bp      # Comment CRUD operations
    from backend.routes.ratings import ratings_bp        # Rating CRUD operations
    from backend.routes.saved_recipes import saved_bp    # Saved recipes management

    # Register authentication blueprint - handles user registration, login, profile
    # URL prefix: /api
    # Routes: /api/register, /api/login, /api/logout, /api/user, /api/profile
    # Connects to: backend/routes/auth.py
    # CRUD Operations: CREATE (register), READ (user, profile), UPDATE (profile, password), DELETE (logout)
    app.register_blueprint(auth_bp, url_prefix='/api')
    
    # Register recipes blueprint - handles recipe CRUD operations
    # URL prefix: /api/recipes
    # Routes: /api/recipes, /api/recipes/<id>
    # Connects to: backend/routes/recipes.py
    # CRUD Operations: CREATE (store), READ (index, show), UPDATE (update), DELETE (destroy)
    app.register_blueprint(recipes_bp, url_prefix='/api/recipes')
    
    # Register comments blueprint - handles comment CRUD operations
    # URL prefix: /api/recipes
    # Routes: /api/recipes/<id>/comments, /api/recipes/<id>/comments/<comment_id>
    # Connects to: backend/routes/comments.py
    # CRUD Operations: CREATE (store), READ (index), UPDATE (update), DELETE (destroy)
    app.register_blueprint(comments_bp, url_prefix='/api/recipes')
    
    # Register ratings blueprint - handles recipe rating operations
    # URL prefix: /api/recipes
    # Routes: /api/recipes/<id>/rating, /api/recipes/<id>/rating/public
    # Connects to: backend/routes/ratings.py
    # CRUD Operations: CREATE/UPDATE (store), READ (show, show_public), DELETE (destroy)
    app.register_blueprint(ratings_bp, url_prefix='/api/recipes')
    
    # Register saved recipes blueprint - handles saving/bookmarking recipes
    # URL prefix: /api
    # Routes: /api/saved-recipes, /api/recipes/<id>/saved, /api/recipes/<id>/save
    # Connects to: backend/routes/saved_recipes.py
    # CRUD Operations: CREATE (toggle save), READ (index, check), DELETE (toggle unsave)
    app.register_blueprint(saved_bp, url_prefix='/api')

    # ═══════════════════════════════════════════════════════════════════════════
    # COMPATIBILITY ENDPOINT - CSRF Cookie (Laravel/Sanctum compatibility)
    # ═══════════════════════════════════════════════════════════════════════════
    @app.route('/sanctum/csrf-cookie', methods=['GET'])
    def csrf_cookie():
        """
        Compatibility endpoint for Laravel Sanctum-style CSRF protection
        
        Laravel's Sanctum SPA authentication requires hitting this endpoint first
        to get CSRF token. Flask-Login uses different session approach, so we
        just return 204 No Content to satisfy frontend expectations.
        
        This demonstrates API COMPATIBILITY: Maintaining existing frontend contracts
        
        Used by: Frontend auth services that expect Laravel-style CSRF handling
        """
        return '', 204  # 204 No Content - success with no response body

    # ═══════════════════════════════════════════════════════════════════════════
    # FILE SERVING ROUTES - Static asset delivery
    # ═══════════════════════════════════════════════════════════════════════════
    
    @app.route('/uploads/<path:filename>')
    def serve_upload(filename):
        """
        Serves uploaded files (recipe images) from backend/uploads/ directory
        
        This demonstrates FILE SERVING:
        - Uploaded images are stored in backend/uploads/recipes/
        - This route makes them accessible via URL
        
        Example: /uploads/recipes/1234567890_abc123.jpg
        
        Used by:
        - backend/routes/recipes.py: save_image() stores files here
        - Frontend: Displays recipe images using these URLs
        - Recipe model: image field stores the relative path
        """
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    # ═══════════════════════════════════════════════════════════════════════════
    # SPA (Single Page Application) SERVING - Frontend delivery
    # ═══════════════════════════════════════════════════════════════════════════
    # Get path to 'dist' folder (built frontend)
    # When you run 'npm run build', Vite creates optimized production files in dist/
    dist_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dist')

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_frontend(path):
        """
        Serves React SPA (Single Page Application) for production deployment
        
        This demonstrates SPA HOSTING:
        - All routes not handled by /api blueprints fall through to here
        - Serves built React app from dist/ folder
        - Returns index.html for client-side routing (React Router handles navigation)
        
        How it works:
        1. User requests /recipes, /login, etc.
        2. No API blueprint matches (they're all /api/*)
        3. This function serves dist/index.html
        4. React Router takes over and renders appropriate component
        
        Note: In development, frontend runs on separate Vite server (port 5173)
        This is only used in production when both frontend and backend run on same server
        
        Used by: Production deployment (Heroku, AWS, etc.)
        Development: Frontend served by Vite dev server at localhost:5173
        """
        # Check if requested path exists as a static file (JS, CSS, images)
        if path and os.path.exists(os.path.join(dist_dir, path)):
            return send_from_directory(dist_dir, path)
        
        # Otherwise, serve index.html (let React Router handle the route)
        index_file = os.path.join(dist_dir, 'index.html')
        if os.path.exists(index_file):
            return send_from_directory(dist_dir, 'index.html')
        
        # If dist folder doesn't exist, show helpful message
        return jsonify({'message': 'ProCook API is running. Build the frontend with: npm run build'}), 200

    # ═══════════════════════════════════════════════════════════════════════════
    # Return configured Flask app instance
    # ═══════════════════════════════════════════════════════════════════════════
    return app
