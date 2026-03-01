from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from backend.models import db, Rating, Recipe

ratings_bp = Blueprint('ratings', __name__)


# ── Submit / update rating ──
@ratings_bp.route('/<int:recipe_id>/rating', methods=['POST'])
@login_required
def store(recipe_id):
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
