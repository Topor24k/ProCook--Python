import re
from flask import Blueprint, request, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from backend.models import db, User, Recipe, Comment, Rating, saved_recipes

auth_bp = Blueprint('auth', __name__)


# CRUD READ: retrieves all recipes created by current user
@auth_bp.route('/my-recipes', methods=['GET'])
@login_required
def my_recipes():
    try:
        # OOP: uses foreign key relationship to filter recipes by user_id
        recipes = Recipe.query.filter_by(user_id=current_user.id).order_by(Recipe.created_at.desc()).all()
        return jsonify({'success': True, 'data': [r.to_dict(include_ingredients=True) for r in recipes], 'count': len(recipes)})
    except Exception as e:
        return jsonify({'success': False, 'message': 'Failed to fetch your recipes.'}), 500


def validate_email(email):
    """Validates email format using regex pattern"""
    email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    return bool(email_pattern.match(email))


def validate_password(password):
    """Validates password strength (minimum 8 characters, requires uppercase, lowercase, digit)"""
    if len(password) < 8:
        return False, 'Password must be at least 8 characters.'
    if not re.search(r'[A-Z]', password):
        return False, 'Password must contain an uppercase letter.'
    if not re.search(r'[a-z]', password):
        return False, 'Password must contain a lowercase letter.'
    if not re.search(r'\d', password):
        return False, 'Password must contain a digit.'
    return True, None


# CRUD CREATE: inserts new user into database
@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        errors = {}

        name = (data.get('name') or '').strip()
        if not name or len(name) < 2:
            errors['name'] = ['Name must be at least 2 characters.']
        elif len(name) > 255:
            errors['name'] = ['Name cannot exceed 255 characters.']

        email = (data.get('email') or '').strip().lower()
        if not email:
            errors['email'] = ['Email is required.']
        elif not validate_email(email):
            errors['email'] = ['Invalid email format.']
        elif User.query.filter_by(email=email).first():
            errors['email'] = ['Email is already registered.']

        password = data.get('password', '')
        is_valid, error_msg = validate_password(password)
        if not is_valid:
            errors['password'] = [error_msg]

        password_confirmation = data.get('password_confirmation', '')
        if password != password_confirmation:
            errors['password_confirmation'] = ['Passwords do not match.']

        if errors:
            return jsonify({'success': False, 'message': 'Validation failed.', 'errors': errors}), 422

        # CRUD CREATE: creates User object with OOP encapsulation for password hashing
        user = User(name=name, email=email)
        user.set_password(password)  # OOP Encapsulation: hashes password
        db.session.add(user)
        db.session.commit()

        login_user(user, remember=True)
        return jsonify({'success': True, 'message': 'Registration successful!', 'data': {'user': user.to_dict()}}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Registration failed. Please try again.'}), 500


# CRUD READ: authenticates user and creates session
@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = (data.get('email') or '').strip().lower()
        password = data.get('password', '')

        if not email or not password:
            return jsonify({'success': False, 'message': 'Email and password are required.'}), 422

        # CRUD READ: queries user by email
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):  # OOP Encapsulation: verifies password
            return jsonify({'success': False, 'message': 'Invalid email or password.'}), 401

        login_user(user, remember=True)
        return jsonify({'success': True, 'message': 'Login successful!', 'data': {'user': user.to_dict()}})
    except Exception as e:
        return jsonify({'success': False, 'message': 'Login failed. Please try again.'}), 500


# CRUD DELETE: destroys user session (logs out)
@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    try:
        logout_user()
        return jsonify({'success': True, 'message': 'Logged out successfully.'})
    except Exception as e:
        return jsonify({'success': False, 'message': 'Logout failed.'}), 500


# CRUD READ: retrieves current authenticated user data
@auth_bp.route('/user', methods=['GET'])
@login_required
def get_user():
    try:
        return jsonify({'success': True, 'data': {'user': current_user.to_dict()}})  # OOP: uses to_dict() method
    except Exception as e:
        return jsonify({'success': False, 'message': 'Failed to fetch user data.'}), 500


# CRUD READ: retrieves user profile with related counts
@auth_bp.route('/profile', methods=['GET'])
@login_required
def profile():
    try:
        # CRUD READ: counts related records through relationships
        recipes_count = Recipe.query.filter_by(user_id=current_user.id).count()
        saved_count = current_user.saved.count()  # OOP: uses many-to-many relationship
        comments_count = Comment.query.filter_by(user_id=current_user.id).count()
        ratings_count = Rating.query.filter_by(user_id=current_user.id).count()

        return jsonify({
            'success': True,
            'data': {
                'user': current_user.to_dict(),
                'stats': {
                    'recipesCount': recipes_count,
                    'savedCount': saved_count,
                    'commentsCount': comments_count,
                    'ratingsCount': ratings_count
                }
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': 'Failed to fetch profile.'}), 500


# CRUD UPDATE: modifies user profile information
@auth_bp.route('/profile', methods=['PUT'])
@login_required
def update_profile():
    try:
        data = request.get_json()
        errors = {}

        name = (data.get('name') or '').strip()
        if not name or len(name) < 2:
            errors['name'] = ['Name must be at least 2 characters.']
        elif len(name) > 255:
            errors['name'] = ['Name cannot exceed 255 characters.']

        if errors:
            return jsonify({'success': False, 'message': 'Validation failed.', 'errors': errors}), 422

        # CRUD UPDATE: modifies User object fields
        current_user.name = name
        db.session.commit()
        return jsonify({'success': True, 'message': 'Profile updated successfully.', 'data': {'user': current_user.to_dict()}})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Failed to update profile.'}), 500


# CRUD UPDATE: changes user password
@auth_bp.route('/profile/password', methods=['PUT'])
@login_required
def change_password():
    try:
        data = request.get_json()
        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')
        password_confirmation = data.get('password_confirmation', '')

        # OOP Encapsulation: verifies current password
        if not current_user.check_password(current_password):
            return jsonify({'success': False, 'message': 'Current password is incorrect.'}), 422

        is_valid, error_msg = validate_password(new_password)
        if not is_valid:
            return jsonify({'success': False, 'message': 'Validation failed.', 'errors': {'new_password': [error_msg]}}), 422

        if new_password != password_confirmation:
            return jsonify({'success': False, 'message': 'Validation failed.', 'errors': {'password_confirmation': ['Passwords do not match.']}}), 422

        # CRUD UPDATE: modifies password using OOP encapsulation
        current_user.set_password(new_password)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Password changed successfully.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Failed to change password.'}), 500


# CRUD DELETE: removes user account and all related data
@auth_bp.route('/profile', methods=['DELETE'])
@login_required
def delete_account():
    try:
        # CRUD DELETE: removes user (CASCADE deletes related comments and ratings)
        db.session.delete(current_user)
        db.session.commit()
        logout_user()
        return jsonify({'success': True, 'message': 'Account deleted successfully.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Failed to delete account.'}), 500
