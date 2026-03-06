# ═══════════════════════════════════════════════════════════════════════════
# APPLICATION ENTRY POINT - Starts the Flask Development Server
# ═══════════════════════════════════════════════════════════════════════════
# This file demonstrates:
# 1. APPLICATION FACTORY PATTERN: Calls create_app() to get Flask instance
# 2. ENTRY POINT: Starting point when running 'python run.py'
# 3. DEVELOPMENT SERVER: Runs Flask's built-in server for testing
#
# Usage:
# - Development: python run.py (starts server on http://0.0.0.0:5000)
# - Production: Use WSGI server like Gunicorn instead
#
# Connects to:
# - backend/app.py: create_app() function that builds the Flask application
# - backend/config.py: Loads configuration based on FLASK_ENV
# ═══════════════════════════════════════════════════════════════════════════

"""Entry point for running the Flask application."""

# Import the application factory function
# Connects to: backend/app.py where create_app() is defined
from backend.app import create_app

# ═══ CREATE FLASK APPLICATION INSTANCE ═══
# Call the factory function to create and configure Flask app
# This executes:
# 1. Configuration loading (backend/config.py)
# 2. Database initialization (backend/models.py)
# 3. Extension setup (CORS, Flask-Login, Migrate)
# 4. Blueprint registration (all routes from backend/routes/)
# 5. Error handler setup
app = create_app()

# ═══ START DEVELOPMENT SERVER ═══
# This block only runs when executing 'python run.py' directly
# (not when imported by WSGI server like Gunicorn)
if __name__ == '__main__':
    # Start Flask development server
    # Parameters:
    # - host='0.0.0.0': Listen on all network interfaces (accessible from other devices)
    # - port=5000: Run on port 5000 (default Flask port)
    # - debug=True: Enable auto-reload and detailed error pages (from config.py)
    #
    # WARNING: This development server is NOT suitable for production
    # Production deployment should use:
    # - Gunicorn: gunicorn -w 4 "backend.app:create_app()"
    # - uWSGI: uwsgi --http :5000 --wsgi-file run.py --callable app
    #
    # The server will run until you press Ctrl+C to stop it
    app.run(host='0.0.0.0', port=5000, debug=True)
