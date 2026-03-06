# ═══════════════════════════════════════════════════════════════════════════
# RATING ROUTES - CRUD Operations for Recipe Ratings
# ═══════════════════════════════════════════════════════════════════════════
# This file demonstrates:
# 1. UPSERT PATTERN: CREATE or UPDATE rating in one operation
# 2. AGGREGATE FUNCTIONS: Calculate average rating using SQL AVG()
# 3. UNIQUE CONSTRAINTS: One rating per user per recipe
# 4. BUSINESS LOGIC: Prevent users from rating their own recipes
# 5. TRANSACTIONAL OPERATIONS: Database commits with rollback
#
# Connects to:
# - backend/models.py: Rating and Recipe models
# - backend/app.py: Registered as ratings_bp with /api/recipes prefix
# ═══════════════════════════════════════════════════════════════════════════

# Import Flask utilities
from flask import Blueprint, request, jsonify

# Import Flask-Login for authentication
from flask_login import login_required, current_user

# Import database models
# Connects to: backend/models.py for Rating and Recipe classes
from backend.models import db, Rating, Recipe

# Create Blueprint - groups rating-related routes
# Registered in: backend/app.py with url_prefix='/api/recipes'
ratings_bp = Blueprint('ratings', __name__)


# ═══════════════════════════════════════════════════════════════════════════
# CREATE/UPDATE OPERATION: Submit or Update Rating (UPSERT)
# ═══════════════════════════════════════════════════════════════════════════
# CRUD: CREATE or UPDATE - Upsert rating (insert or update if exists)
# HTTP Method: POST
# URL: /api/recipes/<recipe_id>/rating
# Authentication: Required (@login_required)
# Demonstrates: UPSERT PATTERN, AGGREGATE FUNCTIONS, BUSINESS LOGIC
# ═══════════════════════════════════════════════════════════════════════════

@ratings_bp.route('/<int:recipe_id>/rating', methods=['POST'])
@login_required  # Must be logged in to rate
def store(recipe_id):
    """
    CREATE/UPDATE Operation: Rate a recipe (UPSERT pattern)
    
    This demonstrates:
    - UPSERT PATTERN: Updates existing rating or creates new one
    - BUSINESS LOGIC: Prevents self-rating (can't rate own recipe)
    - AGGREGATE FUNCTIONS: Calculates AVG rating using SQL
    - UNIQUE CONSTRAINT: One rating per user per recipe (in model)
    - TRANSACTIONAL COMMIT: Saves rating to database
    
    Process:
    1. Verify recipe exists
    2. Prevent user from rating own recipe (business rule)
    3. Validate rating value (1-5)
    4. Check if user already rated (UPDATE) or not (CREATE)
    5. Calculate updated average rating using SQL AVG()
    6. COMMIT transaction
    
    Request Body: { "rating": 1-5 }
    
    Returns: JSON with rating and updated statistics
    """
    try:
        recipe = Recipe.query.get(recipe_id)
        if not recipe:
            return jsonify({
                'success': False,
                'message': 'Recipe not found.'
            }), 404

        # Prevent rating own recipe
        if recipe.user_id == current_user.id:
            return jsonify({
                'success': False,
                'message': 'You cannot rate your own recipe.'
            }), 403

        data = request.get_json()

        try:
            rating_value = int(data.get('rating', 0))
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'message': 'Validation failed.',
                'errors': {'rating': ['Rating must be a number.']}
            }), 422

        if rating_value < 1 or rating_value > 5:
            return jsonify({
                'success': False,
                'message': 'Validation failed.',
                'errors': {'rating': ['Rating must be between 1 and 5.']}
            }), 422

        # Update or create
        rating = Rating.query.filter_by(
            recipe_id=recipe_id,
            user_id=current_user.id
        ).first()

        if rating:
            rating.rating = rating_value
        else:
            rating = Rating(
                recipe_id=recipe_id,
                user_id=current_user.id,
                rating=rating_value,
            )
            db.session.add(rating)

        db.session.commit()

        # Get updated stats
        avg = db.session.query(db.func.avg(Rating.rating)).filter(
            Rating.recipe_id == recipe_id
        ).scalar()
        count = Rating.query.filter_by(recipe_id=recipe_id).count()

        return jsonify({
            'success': True,
            'message': 'Rating submitted successfully.',
            'data': {
                'rating': rating.to_dict(),
                'averageRating': round(float(avg), 1) if avg else 0,
                'ratingsCount': count
            }
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Failed to submit rating.'
        }), 500


# ── Get user's rating (authenticated) ──
@ratings_bp.route('/<int:recipe_id>/rating', methods=['GET'])
@login_required
def show(recipe_id):
    try:
        recipe = Recipe.query.get(recipe_id)
        if not recipe:
            return jsonify({
                'success': False,
                'message': 'Recipe not found.'
            }), 404

        user_rating = Rating.query.filter_by(
            recipe_id=recipe_id,
            user_id=current_user.id
        ).first()

        avg = db.session.query(db.func.avg(Rating.rating)).filter(
            Rating.recipe_id == recipe_id
        ).scalar()
        count = Rating.query.filter_by(recipe_id=recipe_id).count()

        return jsonify({
            'success': True,
            'data': {
                'userRating': user_rating.rating if user_rating else None,
                'averageRating': round(float(avg), 1) if avg else 0,
                'ratingsCount': count
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to fetch rating.'
        }), 500


# ── Get public rating (no auth) ──
@ratings_bp.route('/<int:recipe_id>/rating/public', methods=['GET'])
def show_public(recipe_id):
    try:
        recipe = Recipe.query.get(recipe_id)
        if not recipe:
            return jsonify({
                'success': False,
                'message': 'Recipe not found.'
            }), 404

        avg = db.session.query(db.func.avg(Rating.rating)).filter(
            Rating.recipe_id == recipe_id
        ).scalar()
        count = Rating.query.filter_by(recipe_id=recipe_id).count()

        return jsonify({
            'success': True,
            'data': {
                'averageRating': round(float(avg), 1) if avg else 0,
                'ratingsCount': count,
                'recipeOwnerId': recipe.user_id
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to fetch rating.'
        }), 500


# ── Delete user's rating ──
@ratings_bp.route('/<int:recipe_id>/rating', methods=['DELETE'])
@login_required
def destroy(recipe_id):
    try:
        recipe = Recipe.query.get(recipe_id)
        if not recipe:
            return jsonify({
                'success': False,
                'message': 'Recipe not found.'
            }), 404

        rating = Rating.query.filter_by(
            recipe_id=recipe_id,
            user_id=current_user.id
        ).first()

        if not rating:
            return jsonify({
                'success': False,
                'message': 'Rating not found.'
            }), 404

        db.session.delete(rating)
        db.session.commit()

        avg = db.session.query(db.func.avg(Rating.rating)).filter(
            Rating.recipe_id == recipe_id
        ).scalar()
        count = Rating.query.filter_by(recipe_id=recipe_id).count()

        return jsonify({
            'success': True,
            'message': 'Rating removed successfully.',
            'data': {
                'averageRating': round(float(avg), 1) if avg else 0,
                'ratingsCount': count
            }
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Failed to delete rating.'
        }), 500
