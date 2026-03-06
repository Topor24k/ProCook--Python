# ═══════════════════════════════════════════════════════════════════════════
# APPLICATION ENTRY POINT - Sugdan ang Flask Development Server
# Simula sa Application - Magsugod sa Flask Development Server
# ═══════════════════════════════════════════════════════════════════════════
# Kini nga file nagpakita sa (This file demonstrates):
# 1. APPLICATION FACTORY PATTERN: Magtawag ug create_app() para makuha ang Flask instance
# 2. ENTRY POINT: Sugdan dire kon magrun ug 'python run.py'
# 3. DEVELOPMENT SERVER: Magpadagan sa Flask's built-in server para sa testing
#
# Paggamit (Usage):
# - Development: python run.py (magsugod sa server sa http://0.0.0.0:5000)
# - Production: Gamita ang WSGI server sama sa Gunicorn hinuon
#
# Konektado sa (Connects to):
# - backend/app.py: create_app() function nga naghimo sa Flask application
# - backend/config.py: Nag-load sa configuration base sa FLASK_ENV
# ═══════════════════════════════════════════════════════════════════════════

"""Entry point para sa pagpadagan sa Flask application - Sugdan dinhi."""

# I-import ang application factory function
# Konekta sa: backend/app.py diin gi-define ang create_app()
from backend.app import create_app

# ═══ PAGHIMO UG FLASK APPLICATION INSTANCE (Create Flask App) ═══
# Tawagun ang factory function para maghimo ug ma-configure ang Flask app
# Kini magsugod sa (This executes):
# 1. Configuration loading (backend/config.py) - Pag-load sa settings
# 2. Database initialization (backend/models.py) - Pag-setup sa database
# 3. Extension setup (CORS, Flask-Login, Migrate) - Pag-install sa plugins
# 4. Blueprint registration (tanan routes gikan sa backend/routes/)
# 5. Error handler setup - Pag-setup sa error handling
app = create_app()

# ═══ SUGDAN ANG DEVELOPMENT SERVER (Start Development Server) ═══
# Kini nga block modagan lang kon i-execute directly ang 'python run.py'
# (dili modagan kon gi-import sa WSGI server sama sa Gunicorn)
if __name__ == '__main__':
    # Sugdi ang Flask development server (Start the server)
    # Mga Parameters:
    # - host='0.0.0.0': Maminaw sa tanan network interfaces (accessible gikan sa ubang devices)
    # - port=5000: Modagan sa port 5000 (default Flask port)
    # - debug=True: I-enable ang auto-reload ug detailed error pages (gikan sa config.py)
    #
    # PASIDAAN (WARNING): Kini nga development server DILI angay para sa production!
    # Production deployment kinahanglan mogamit ug:
    # - Gunicorn: gunicorn -w 4 "backend.app:create_app()"
    # - uWSGI: uwsgi --http :5000 --wsgi-file run.py --callable app
    #
    # Ang server modagan hangtud mopindot ka ug Ctrl+C para pahunungon
    app.run(host='0.0.0.0', port=5000, debug=True)
