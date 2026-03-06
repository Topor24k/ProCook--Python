# ═══════════════════════════════════════════════════════════════════════════
# AUTHENTICATION ROUTES - User Management and CRUD Operations
# ═══════════════════════════════════════════════════════════════════════════
# This file demonstrates:
# 1. CRUD OPERATIONS on User model (CREATE: register, READ: user/profile, UPDATE: profile/password)
# 2. AUTHENTICATION: Login/logout with session management
# 3. INPUT VALIDATION: Email, password, and data validation with error handling
# 4. TRANSACTIONAL OPERATIONS: Database commits and rollbacks
# 5. OOP ENCAPSULATION: Using User model methods (set_password, check_password, to_dict)
#
# Connects to:
# - backend/models.py: User, Recipe, Comment, Rating models
# - backend/app.py: Registered as auth_bp with /api prefix
# - Flask-Login: login_user(), logout_user(), @login_required, current_user
# ═══════════════════════════════════════════════════════════════════════════

# Import re module for regex pattern matching in email/password validation
import re

# Import Flask utilities for handling requests and responses
from flask import Blueprint, request, jsonify, session

# Import Flask-Login components for user session management
from flask_login import login_user, logout_user, login_required, current_user

# Import password hashing for security (used in admin operations, if needed)
from werkzeug.security import generate_password_hash

# Import database models and session object
# Connects to: backend/models.py for all model definitions
from backend.models import db, User, Recipe, Comment, Rating, saved_recipes

# Create Blueprint object - groups related routes together
# Registered in: backend/app.py with app.register_blueprint(auth_bp, url_prefix='/api')
auth_bp = Blueprint('auth', __name__)


# ═══════════════════════════════════════════════════════════════════════════
# READ OPERATION: Get User's Recipes
# ═══════════════════════════════════════════════════════════════════════════
# CRUD: READ - Retrieves all recipes created by the authenticated user
# HTTP Method: GET
# URL: /api/my-recipes
# Authentication: Required (@login_required)
# Connects to: Recipe model in backend/models.py
# ═══════════════════════════════════════════════════════════════════════════

@auth_bp.route('/my-recipes', methods=['GET'])
@login_required  # Flask-Login decorator: requires user to be logged in
def my_recipes():
    """
    READ Operation: Fetch all recipes created by the current user
    
    This demonstrates:
    - DATABASE QUERY with filtering (WHERE user_id = ?)
    - OOP METHOD CHAINING: query.filter_by().order_by().all()
    - RELATIONSHIP TRAVERSAL: Uses Recipe.user_id foreign key
    
    Process:
    1. Flask-Login provides current_user from session
    2. Queries Recipe table filtering by current_user.id
    3. Orders results by creation date (newest first)
    4. Converts each Recipe object to dictionary using to_dict() method
    
    Returns: JSON array of user's recipes with ingredients
    """
    try:
        # TRANSACTIONAL READ: Query database for user's recipes
        # Recipe.query starts a SELECT statement
        # .filter_by(user_id=current_user.id) adds WHERE clause
        # .order_by(Recipe.created_at.desc()) adds ORDER BY clause for sorting
        # .all() executes query and returns list of Recipe objects
        recipes = Recipe.query.filter_by(user_id=current_user.id)\
            .order_by(Recipe.created_at.desc()).all()

        # Return success response with recipe data
        return jsonify({
            'success': True,
            # List comprehension calling OOP method Recipe.to_dict() on each recipe
            # include_ingredients=True loads related Ingredient records (EAGER LOADING)
            'data': [r.to_dict(include_ingredients=True) for r in recipes],
            'count': len(recipes)  # Total number of recipes
        })

    except Exception as e:
        # ERROR HANDLING: Catch database or serialization errors
        return jsonify({
            'success': False,
            'message': 'Failed to fetch your recipes.'
        }), 500  # HTTP 500 Internal Server Error


# ═══════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS - Input Validation (OOP Encapsulation)
# ═══════════════════════════════════════════════════════════════════════════
# These functions demonstrate SEPARATION OF CONCERNS:
# - Validation logic is separated from route handlers
# - Reusable across multiple routes
# - Makes testing easier
# ═══════════════════════════════════════════════════════════════════════════

def validate_email(email):
    """
    Validates email format using regex pattern matching
    
    This demonstrates INPUT VALIDATION for data integrity
    
    Pattern explanation:
    - ^[a-zA-Z0-9._%+-]+ : Local part (before @)
    - @[a-zA-Z0-9.-]+ : Domain name
    - \.[a-zA-Z]{2,}$ : Top-level domain (.com, .org, etc.)
    
    Used in: register(), login(), update_profile()
    
    Returns: True if email format is valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password(password):
    """
    Validates password strength requirements
    
    This demonstrates SECURITY VALIDATION
    
    Requirements:
    - At least 8 characters long
    - Contains at least 1 uppercase letter
    - Contains at least 1 lowercase letter
    - Contains at least 1 digit
    
    Used in: register()
    
    Returns: True if password meets requirements, False otherwise
    """
    # Check minimum length
    if len(password) < 8:
        return False
    # Regex pattern: (?=.*[a-z]) = has lowercase, (?=.*[A-Z]) = has uppercase, (?=.*\d) = has digit
    return bool(re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)', password))


# ═══════════════════════════════════════════════════════════════════════════
# CREATE OPERATION: User Registration
# ═══════════════════════════════════════════════════════════════════════════
# CRUD: CREATE - Creates new user account in database
# HTTP Method: POST
# URL: /api/register
# Authentication: Not required (public route)
# Connects to: User model in backend/models.py
# ═══════════════════════════════════════════════════════════════════════════

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    CREATE Operation: Register a new user account
    
    This demonstrates:
    - TRANSACTIONAL INSERT: Creates new User record
    - INPUT VALIDATION: Multi-field validation with error collection
    - OOP ENCAPSULATION: Uses User.set_password() method for secure hash
    - ERROR HANDLING: Try-catch with rollback on failure
    - SESSION MANAGEMENT: Auto-login after successful registration
    
    Process:
    1. Extract and validate input data (name, email, password)
    2. Check for duplicate email (UNIQUE constraint)
    3. Create User object with validated data
    4. Hash password using User.set_password() method
    5. Insert into database (TRANSACTIONAL COMMIT)
    6. Auto-login the new user
    
    Request Body (JSON):
    {
        "name": "John Doe",
        "email": "john@example.com",
        "password": "SecurePass123",
        "password_confirmation": "SecurePass123"
    }
    
    Returns: JSON with success status and user data
    """
    try:
        # Extract JSON data from HTTP request body
        data = request.get_json()
        
        # Dictionary to collect validation errors (all fields validated before response)
        errors = {}

        # ═══ VALIDATION: Name Field ═══
        # Strip whitespace from input for clean data
        name = (data.get('name') or '').strip()
        
        # Validate name length (minimum 2 characters)
        if not name or len(name) < 2:
            errors['name'] = ['Name must be at least 2 characters.']
        # Validate name doesn't exceed database column limit
        elif len(name) > 255:
            errors['name'] = ['Name cannot exceed 255 characters.']
        # Validate name contains only letters and spaces (no special characters)
        elif not re.match(r'^[a-zA-Z\s]+$', name):
            errors['name'] = ['Name can only contain letters and spaces.']

        # ═══ VALIDATION: Email Field ═══
        # Normalize email to lowercase for consistency
        email = (data.get('email') or '').strip().lower()
        
        # Check if email is provided
        if not email:
            errors['email'] = ['Email address is required.']
        # Validate email format using helper function
        elif not validate_email(email):
            errors['email'] = ['Please provide a valid email address.']
        # Check for duplicate email (TRANSACTIONAL READ)
        # User.query.filter_by(email=email).first() executes SELECT query
        # This demonstrates UNIQUE CONSTRAINT checking at application level
        elif User.query.filter_by(email=email).first():
            errors['email'] = ['This email is already registered. Please login instead.']

        # ═══ VALIDATION: Password Fields ═══
        password = data.get('password') or ''
        password_confirmation = data.get('password_confirmation') or ''
        
        # Check if password is provided
        if not password:
            errors['password'] = ['Password is required.']
        # Validate password strength using helper function
        elif not validate_password(password):
            errors['password'] = ['Password must be at least 8 characters with one uppercase letter, one lowercase letter, and one number.']
        # Verify password confirmation matches (prevents typos)
        elif password != password_confirmation:
            errors['password'] = ['Password confirmation does not match.']

        # ═══ EARLY RETURN if validation fails ═══
        # If any errors were collected, return them without database operation
        if errors:
            return jsonify({
                'success': False,
                'message': 'Validation failed',
                'errors': errors  # Field-specific errors for frontend display
            }), 422  # HTTP 422 Unprocessable Entity (validation errors)

        # ═══ CREATE: Database Transaction ═══
        # Create new User instance (OOP object instantiation)
        user = User(name=name, email=email)
        
        # Set password using OOP method (ENCAPSULATION)
        # This hashes the password securely before storing
        # Connects to: User.set_password() in backend/models.py
        user.set_password(password)
        
        # Add user to database session (prepares for INSERT)
        # This doesn't execute SQL yet (transaction not committed)
        db.session.add(user)
        
        # COMMIT TRANSACTION: Executes SQL INSERT statement
        # SQL: INSERT INTO users (name, email, password, created_at, updated_at) VALUES (?, ?, ?, ?, ?)
        # This is the actual CREATE operation in CRUD
        db.session.commit()

        # ═══ AUTO-LOGIN after registration ═══
        # login_user() creates session cookie for new user
        # remember=True makes session persist across browser restarts
        # Connects to: Flask-Login session management
        login_user(user, remember=True)

        # Return success response with user data
        return jsonify({
            'success': True,
            'message': 'Registration successful! Welcome to ProCook.',
            # Uses User.to_dict() method (OOP ABSTRACTION)
            'user': user.to_dict()
        }), 201  # HTTP 201 Created (resource successfully created)

    except Exception as e:
        # ERROR HANDLING: Catch any unexpected errors during transaction
        # ROLLBACK TRANSACTION: Undoes any database changes made in this try block
        # This demonstrates TRANSACTIONAL INTEGRITY (all-or-nothing operation)
        db.session.rollback()
        
        return jsonify({
            'success': False,
            'message': 'Registration failed. Please try again.'
        }), 500  # HTTP 500 Internal Server Error


# ═══════════════════════════════════════════════════════════════════════════
# READ OPERATION: User Login (Authentication)
# ═══════════════════════════════════════════════════════════════════════════
# CRUD: READ - Authenticates user credentials and creates session
# HTTP Method: POST
# URL: /api/login
# Authentication: Not required (public route)
# Connects to: User model in backend/models.py
# ═══════════════════════════════════════════════════════════════════════════

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    READ Operation: Authenticate user and create session
    
    This demonstrates:
    - DATABASE QUERY: SELECT user WHERE email = ?
    - AUTHENTICATION: Password verification using hashed comparison
    - OOP ENCAPSULATION: Uses User.check_password() method
    - SESSION CREATION: Flask-Login creates session cookie
    - SECURITY: Password never returned, only validated
    
    Process:
    1. Validate input (email format, required fields)
    2. Query database for user by email (TRANSACTIONAL READ)
    3. Verify password matches stored hash
    4. Create session cookie for authenticated user
    
    Request Body (JSON):
    {
        "email": "john@example.com",
        "password": "SecurePass123"
    }
    
    Returns: JSON with success status and user data
    """
    try:
        # Extract JSON data from request
        data = request.get_json()
        errors = {}

        # ═══ VALIDATION: Email and Password ═══
        email = (data.get('email') or '').strip().lower()
        password = data.get('password') or ''

        # Validate email is provided
        if not email:
            errors['email'] = ['Please provide your email address.']
        # Validate email format
        elif not validate_email(email):
            errors['email'] = ['Please provide a valid email address.']

        # Validate password is provided
        if not password:
            errors['password'] = ['Please provide your password.']

        # Early return if validation fails
        if errors:
            return jsonify({
                'success': False,
                'message': 'Login validation failed',
                'errors': errors
            }), 422  # HTTP 422 Unprocessable Entity

        # ═══ READ: Query Database for User ═══
        # TRANSACTIONAL READ: SELECT * FROM users WHERE email = ?
        # .first() returns User object or None if not found
        user = User.query.filter_by(email=email).first()

        # ═══ AUTHENTICATION: Verify Credentials ═══
        # Check if user exists AND password matches
        # user.check_password() uses OOP ENCAPSULATION (hides bcrypt comparison)
        # Connects to: User.check_password() in backend/models.py
        if not user or not user.check_password(password):
            # SECURITY: Generic error message (don't reveal if email exists)
            return jsonify({
                'success': False,
                'message': 'Invalid credentials. Please check your email and password.',
                'errors': {
                    'email': ['The provided credentials are incorrect.']
                }
            }), 401  # HTTP 401 Unauthorized (authentication failed)

        # ═══ CREATE SESSION: Login Successful ═══
        # login_user() creates session cookie containing user.id
        # Flask-Login stores this in encrypted cookie sent to browser
        # Browser sends this cookie with all future requests
        # remember=True makes session persist (doesn't expire when browser closes)
        login_user(user, remember=True)

        # Return success response
        return jsonify({
            'success': True,
            'message': 'Login successful! Welcome back.',
            # Uses User.to_dict() (OOP ABSTRACTION) - password NOT included
            'user': user.to_dict()
        })

    except Exception as e:
        # ERROR HANDLING: Catch unexpected errors
        return jsonify({
            'success': False,
            'message': 'Login failed. Please try again.'
        }), 500  # HTTP 500 Internal Server Error


# ═══════════════════════════════════════════════════════════════════════════
# DELETE OPERATION: User Logout (Session Termination)
# ═══════════════════════════════════════════════════════════════════════════
# CRUD: DELETE - Destroys user session (logs out)
# HTTP Method: POST
# URL: /api/logout
# Authentication: Required (@login_required)
# ═══════════════════════════════════════════════════════════════════════════

@auth_bp.route('/logout', methods=['POST'])
@login_required  # Requires active session
def logout():
    """
    DELETE Operation: Terminate user session (logout)
    
    This demonstrates:
    - SESSION MANAGEMENT: Destroys Flask-Login session
    - SECURITY: Clears all session data
    - No database transaction (session-only operation)
    
    Process:
    1. Flask-Login removes user from session
    2. Clear all session cookies
    3. Browser must login again to access protected routes
    
    Returns: JSON confirmation of logout
    """
    try:
        # Remove user from Flask-Login session
        # This invalidates the session cookie
        logout_user()
        
        # Clear all session data (additional security)
        # Ensures no residual data remains in session
        session.clear()
        
        return jsonify({
            'success': True,
            'message': 'Logged out successfully'
        })
        
    except Exception as e:
        # ERROR HANDLING
        return jsonify({
            'success': False,
            'message': 'Logout failed. Please try again.'
        }), 500


# ═══════════════════════════════════════════════════════════════════════════
# READ OPERATION: Get Current Authenticated User
# ═══════════════════════════════════════════════════════════════════════════
# CRUD: READ - Returns currently logged-in user's data
# HTTP Method: GET
# URL: /api/user
# Authentication: Required (@login_required)
# ═══════════════════════════════════════════════════════════════════════════

@auth_bp.route('/user', methods=['GET'])
@login_required  # Requires active session
def get_user():
    """
    READ Operation: Get current user information
    
    This demonstrates:
    - SESSION READING: Flask-Login provides current_user object
    - OOP ABSTRACTION: Uses User.to_dict() method
    - No database query needed (user loaded from session by Flask-Login)
    
    Process:
    1. Flask-Login loads current_user from session cookie
    2. Uses @login_manager.user_loader callback (in backend/app.py)
    3. Returns user data as JSON
    
    Used by: Frontend to check authentication status and get user info
    
    Returns: JSON with current user data
    """
    try:
        # current_user is provided by Flask-Login
        # Already loaded from database using user_id in session cookie
        # See @login_manager.user_loader in backend/app.py
        return jsonify({
            'success': True,
            # Uses User.to_dict() (OOP ABSTRACTION)
            'data': current_user.to_dict()
        })
        
    except Exception as e:
        # ERROR HANDLING
        return jsonify({
            'success': False,
            'message': 'Failed to fetch user information.'
        }), 500
    try:
        return jsonify({
            'success': True,
            'data': current_user.to_dict()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to fetch user information.'
        }), 500


# ── Profile (with stats) ──
@auth_bp.route('/profile', methods=['GET'])
@login_required
def profile():
    try:
        user = current_user
        return jsonify({
            'success': True,
            'data': {
                'user': user.to_dict(),
                'stats': {
                    'recipes_count': user.recipes.count(),
                    'comments_count': user.comments.count(),
                    'ratings_count': user.ratings.count(),
                    'saved_count': user.saved.count(),
                }
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to fetch profile information.'
        }), 500


# ── Update profile ──
@auth_bp.route('/profile', methods=['PUT'])
@login_required
def update_profile():
    try:
        data = request.get_json()
        errors = {}

        name = (data.get('name') or '').strip()
        email = (data.get('email') or '').strip().lower()

        if not name or len(name) > 255:
            errors['name'] = ['Name is required and must be under 255 characters.']
        if not email or not validate_email(email):
            errors['email'] = ['A valid email is required.']
        elif email != current_user.email:
            if User.query.filter_by(email=email).first():
                errors['email'] = ['This email is already in use.']

        if errors:
            return jsonify({
                'success': False,
                'message': 'Validation failed.',
                'errors': errors
            }), 422

        current_user.name = name
        current_user.email = email
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Profile updated successfully.',
            'data': current_user.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Failed to update profile.'
        }), 500


# ── Change password ──
@auth_bp.route('/profile/password', methods=['PUT'])
@login_required
def change_password():
    try:
        data = request.get_json()
        errors = {}

        current_password = data.get('current_password') or ''
        new_password = data.get('password') or ''
        password_confirmation = data.get('password_confirmation') or ''

        if not current_password:
            errors['current_password'] = ['Current password is required.']
        elif not current_user.check_password(current_password):
            errors['current_password'] = ['The current password is incorrect.']

        if not new_password or len(new_password) < 8:
            errors['password'] = ['New password must be at least 8 characters.']
        elif new_password != password_confirmation:
            errors['password'] = ['Password confirmation does not match.']

        if errors:
            return jsonify({
                'success': False,
                'message': 'Validation failed.' if 'current_password' not in errors else 'Current password is incorrect.',
                'errors': errors
            }), 422

        current_user.set_password(new_password)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Password changed successfully.'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Failed to change password.'
        }), 500


# ── Delete account ──
@auth_bp.route('/profile', methods=['DELETE'])
@login_required
def delete_account():
    try:
        data = request.get_json()
        errors = {}

        password = data.get('password') or ''
        mode = data.get('mode') or ''

        if not password:
            errors['password'] = ['Password is required.']
        elif not current_user.check_password(password):
            errors['password'] = ['The password is incorrect.']

        if mode not in ('delete_all', 'keep_data'):
            errors['mode'] = ['Invalid mode. Must be delete_all or keep_data.']

        if errors:
            return jsonify({
                'success': False,
                'message': 'Validation failed.',
                'errors': errors
            }), 422

        user = current_user
        user_id = user.id

        if mode == 'delete_all':
            # Delete all user's recipes (cascade deletes ingredients, comments, ratings)
            recipes = Recipe.query.filter_by(user_id=user_id).all()
            for recipe in recipes:
                Comment.query.filter_by(recipe_id=recipe.id).delete()
                Rating.query.filter_by(recipe_id=recipe.id).delete()
                db.session.execute(
                    saved_recipes.delete().where(saved_recipes.c.recipe_id == recipe.id)
                )
                db.session.delete(recipe)

            # Delete user's comments & ratings on other recipes
            Comment.query.filter_by(user_id=user_id).delete()
            Rating.query.filter_by(user_id=user_id).delete()
            db.session.execute(
                saved_recipes.delete().where(saved_recipes.c.user_id == user_id)
            )
        else:
            # keep_data: nullify user_id so content remains
            Recipe.query.filter_by(user_id=user_id).update({'user_id': None})
            Comment.query.filter_by(user_id=user_id).update({'user_id': None})
            Rating.query.filter_by(user_id=user_id).update({'user_id': None})
            db.session.execute(
                saved_recipes.delete().where(saved_recipes.c.user_id == user_id)
            )

        logout_user()
        session.clear()
        db.session.delete(user)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Account deleted successfully.'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Failed to delete account. Please try again.'
        }), 500
