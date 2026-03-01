import os
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from flask_login import LoginManager
from flask_migrate import Migrate

from backend.config import config
from backend.models import db, User


def create_app(config_name=None):
    """Application factory."""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'default')

    app = Flask(__name__,
                static_folder=None)  # We serve static files manually
    app.config.from_object(config[config_name])

    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # ── Extensions ──
    db.init_app(app)
    Migrate(app, db)

    CORS(app,
         origins=app.config['CORS_ORIGINS'],
         supports_credentials=True,
         allow_headers=['Content-Type', 'Accept', 'X-XSRF-TOKEN'],
         expose_headers=['Set-Cookie'])

    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @login_manager.unauthorized
    def unauthorized():
        return jsonify({
            'success': False,
            'message': 'User not authenticated.'
        }), 401

    # ── Register blueprints ──
    from backend.routes.auth import auth_bp
    from backend.routes.recipes import recipes_bp
    from backend.routes.comments import comments_bp
    from backend.routes.ratings import ratings_bp
    from backend.routes.saved_recipes import saved_bp

    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(recipes_bp, url_prefix='/api/recipes')
    app.register_blueprint(comments_bp, url_prefix='/api/recipes')
    app.register_blueprint(ratings_bp, url_prefix='/api/recipes')
    app.register_blueprint(saved_bp, url_prefix='/api')

    # ── CSRF cookie endpoint (compatibility with frontend) ──
    @app.route('/sanctum/csrf-cookie', methods=['GET'])
    def csrf_cookie():
        """Compatibility endpoint – Flask sessions don't need a separate CSRF cookie
        for JSON APIs protected by SameSite cookies, so we just return 204."""
        return '', 204

    # ── Serve uploaded files ──
    @app.route('/uploads/<path:filename>')
    def serve_upload(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    # ── Serve built frontend (production) ──
    dist_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dist')

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_frontend(path):
        """Serve the React SPA. API routes are handled by blueprints above."""
        if path and os.path.exists(os.path.join(dist_dir, path)):
            return send_from_directory(dist_dir, path)
        index_file = os.path.join(dist_dir, 'index.html')
        if os.path.exists(index_file):
            return send_from_directory(dist_dir, 'index.html')
        return jsonify({'message': 'ProCook API is running. Build the frontend with: npm run build'}), 200

    return app
