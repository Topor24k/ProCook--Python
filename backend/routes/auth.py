import re
from flask import Blueprint, request, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from backend.models import db, User, Recipe, Comment, Rating, saved_recipes

auth_bp = Blueprint('auth', __name__)


# ── My recipes (at /api/my-recipes) ──
@auth_bp.route('/my-recipes', methods=['GET'])
@login_required
def my_recipes():
    try:
        recipes = Recipe.query.filter_by(user_id=current_user.id)\
            .order_by(Recipe.created_at.desc()).all()

        return jsonify({
            'success': True,
            'data': [r.to_dict(include_ingredients=True) for r in recipes],
            'count': len(recipes)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to fetch your recipes.'
        }), 500


# ── Helpers ──
def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password(password):
    """At least 8 chars, 1 uppercase, 1 lowercase, 1 digit."""
    if len(password) < 8:
        return False
    return bool(re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)', password))


# ── Register ──
@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        errors = {}

        # Validate name
        name = (data.get('name') or '').strip()
        if not name or len(name) < 2:
            errors['name'] = ['Name must be at least 2 characters.']
        elif len(name) > 255:
            errors['name'] = ['Name cannot exceed 255 characters.']
        elif not re.match(r'^[a-zA-Z\s]+$', name):
            errors['name'] = ['Name can only contain letters and spaces.']

        # Validate email
        email = (data.get('email') or '').strip().lower()
        if not email:
            errors['email'] = ['Email address is required.']
        elif not validate_email(email):
            errors['email'] = ['Please provide a valid email address.']
        elif User.query.filter_by(email=email).first():
            errors['email'] = ['This email is already registered. Please login instead.']

        # Validate password
        password = data.get('password') or ''
        password_confirmation = data.get('password_confirmation') or ''
        if not password:
            errors['password'] = ['Password is required.']
        elif not validate_password(password):
            errors['password'] = ['Password must be at least 8 characters with one uppercase letter, one lowercase letter, and one number.']
        elif password != password_confirmation:
            errors['password'] = ['Password confirmation does not match.']

        if errors:
            return jsonify({
                'success': False,
                'message': 'Validation failed',
                'errors': errors
            }), 422

        user = User(name=name, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        login_user(user, remember=True)

        return jsonify({
            'success': True,
            'message': 'Registration successful! Welcome to ProCook.',
            'user': user.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Registration failed. Please try again.'
        }), 500


# ── Login ──
@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        errors = {}

        email = (data.get('email') or '').strip().lower()
        password = data.get('password') or ''

        if not email:
            errors['email'] = ['Please provide your email address.']
        elif not validate_email(email):
            errors['email'] = ['Please provide a valid email address.']

        if not password:
            errors['password'] = ['Please provide your password.']

        if errors:
            return jsonify({
                'success': False,
                'message': 'Login validation failed',
                'errors': errors
            }), 422

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            return jsonify({
                'success': False,
                'message': 'Invalid credentials. Please check your email and password.',
                'errors': {
                    'email': ['The provided credentials are incorrect.']
                }
            }), 401

        login_user(user, remember=True)

        return jsonify({
            'success': True,
            'message': 'Login successful! Welcome back.',
            'user': user.to_dict()
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Login failed. Please try again.'
        }), 500


# ── Logout ──
@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    try:
        logout_user()
        session.clear()
        return jsonify({
            'success': True,
            'message': 'Logged out successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Logout failed. Please try again.'
        }), 500


# ── Get current user ──
@auth_bp.route('/user', methods=['GET'])
@login_required
def get_user():
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
