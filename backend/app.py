import os
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from flask_login import LoginManager
from flask_migrate import Migrate
from backend.config import config
from backend.models import db, User


def create_app(config_name=None):
    """OOP Factory Pattern: creates Flask app instances with environment-specific configuration"""
    
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'default')

    app = Flask(__name__, static_folder=None)
    
    # OOP Polymorphism: loads different config class based on environment
    app.config.from_object(config[config_name])

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Initialize extensions with dependency injection pattern
    db.init_app(app)
    Migrate(app, db)

    # CORS: enables React frontend to communicate with Flask backend across different ports
    CORS(app,
         origins=app.config['CORS_ORIGINS'],
         supports_credentials=True,
         allow_headers=['Content-Type', 'Accept', 'X-XSRF-TOKEN'],
         expose_headers=['Set-Cookie'])

    # Flask-Login: manages user authentication and sessions
    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        """CRUD READ: loads User object from database using session ID"""
        return User.query.get(int(user_id))

    @login_manager.unauthorized_handler
    def unauthorized():
        """Returns JSON error when unauthenticated user accesses protected route"""
        return jsonify({'success': False, 'message': 'User not authenticated.'}), 401

    # Register blueprints: organizes routes into modular components (separation of concerns)
    from backend.routes.auth import auth_bp
    from backend.routes.recipes import recipes_bp
    from backend.routes.comments import comments_bp
    from backend.routes.ratings import ratings_bp
    from backend.routes.saved_recipes import saved_bp

    # CRUD operations: each blueprint handles CREATE, READ, UPDATE, DELETE for its resource
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(recipes_bp, url_prefix='/api/recipes')
    app.register_blueprint(comments_bp, url_prefix='/api/recipes')
    app.register_blueprint(ratings_bp, url_prefix='/api/recipes')
    app.register_blueprint(saved_bp, url_prefix='/api')

    @app.route('/sanctum/csrf-cookie', methods=['GET'])
    def csrf_cookie():
        """Compatibility endpoint for Laravel Sanctum-style CSRF protection"""
        return '', 204

    @app.route('/uploads/<path:filename>')
    def serve_upload(filename):
        """Serves uploaded recipe images from backend/uploads/ directory"""
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    # SPA serving: handles React frontend routing in production
    dist_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dist')

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_frontend(path):
        """Serves React SPA - returns index.html for client-side routing or static assets"""
        if path and os.path.exists(os.path.join(dist_dir, path)):
            return send_from_directory(dist_dir, path)
        
        index_file = os.path.join(dist_dir, 'index.html')
        if os.path.exists(index_file):
            return send_from_directory(dist_dir, 'index.html')
        
        return jsonify({'message': 'ProCook API is running. Build the frontend with: npm run build'}), 200

    return app
