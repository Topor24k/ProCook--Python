from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from backend.models import db, Recipe, saved_recipes as saved_recipes_table

saved_bp = Blueprint('saved', __name__)


# ── List saved recipes ──
@saved_bp.route('/saved-recipes', methods=['GET'])
@login_required
def index():
    try:
        recipes = current_user.saved.order_by(
            saved_recipes_table.c.created_at.desc()
        ).all()

        return jsonify({
            'success': True,
            'data': [r.to_dict(include_user=True) for r in recipes],
            'count': len(recipes)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to fetch saved recipes.'
        }), 500


# ── Check if saved ──
@saved_bp.route('/recipes/<int:recipe_id>/saved', methods=['GET'])
@login_required
def check(recipe_id):
    try:
        recipe = Recipe.query.get(recipe_id)
        if not recipe:
            return jsonify({
                'success': False,
                'message': 'Recipe not found.'
            }), 404

        is_saved = db.session.query(saved_recipes_table).filter(
            saved_recipes_table.c.user_id == current_user.id,
            saved_recipes_table.c.recipe_id == recipe_id,
        ).first() is not None

        return jsonify({
            'success': True,
            'data': {
                'isSaved': is_saved
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to check saved status.'
        }), 500


# ── Toggle save/unsave ──
@saved_bp.route('/recipes/<int:recipe_id>/save', methods=['POST'])
@login_required
def toggle(recipe_id):
    try:
        recipe = Recipe.query.get(recipe_id)
        if not recipe:
            return jsonify({
                'success': False,
                'message': 'Recipe not found.'
            }), 404

        existing = db.session.query(saved_recipes_table).filter(
            saved_recipes_table.c.user_id == current_user.id,
            saved_recipes_table.c.recipe_id == recipe_id,
        ).first()

        if existing:
            # Unsave
            db.session.execute(
                saved_recipes_table.delete().where(
                    (saved_recipes_table.c.user_id == current_user.id) &
                    (saved_recipes_table.c.recipe_id == recipe_id)
                )
            )
            db.session.commit()
            return jsonify({
                'success': True,
                'message': 'Recipe unsaved successfully.',
                'data': {'isSaved': False}
            })
        else:
            # Save
            db.session.execute(
                saved_recipes_table.insert().values(
                    user_id=current_user.id,
                    recipe_id=recipe_id,
                )
            )
            db.session.commit()
            return jsonify({
                'success': True,
                'message': 'Recipe saved successfully.',
                'data': {'isSaved': True}
            }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Failed to toggle saved status.'
        }), 500
