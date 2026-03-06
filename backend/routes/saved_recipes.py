# ═══════════════════════════════════════════════════════════════════════════
# SAVED RECIPES ROUTES - CRUD on Many-to-Many Relationship
# ═══════════════════════════════════════════════════════════════════════════
# This file demonstrates:
# 1. MANY-TO-MANY CRUD: Operating on junction table (saved_recipes)
# 2. TOGGLE PATTERN: Save/unsave in single operation
# 3. RELATIONSHIP QUERIES: Uses User.saved relationship
# 4. RAW SQL EXECUTION: Direct table operations with db.session.execute()
# 5. TRANSACTIONAL OPERATIONS: INSERT/DELETE with commits
#
# Connects to:
# - backend/models.py: saved_recipes table, User.saved relationship
# - backend/app.py: Registered as saved_bp with /api prefix
# ═══════════════════════════════════════════════════════════════════════════

# Import Flask utilities
from flask import Blueprint, jsonify

# Import Flask-Login for authentication
from flask_login import login_required, current_user

# Import database models and saved_recipes table
# Connects to: backend/models.py
from backend.models import db, Recipe, saved_recipes as saved_recipes_table

# Create Blueprint - groups saved recipe routes
# Registered in: backend/app.py with url_prefix='/api'
saved_bp = Blueprint('saved', __name__)


# ═══════════════════════════════════════════════════════════════════════════
# READ OPERATION: List User's Saved Recipes
# ═══════════════════════════════════════════════════════════════════════════
# CRUD: READ - Retrieves all recipes saved by current user
# HTTP Method: GET
# URL: /api/saved-recipes
# Authentication: Required (@login_required)
# Demonstrates: MANY-TO-MANY QUERY through OOP relationship
# ═══════════════════════════════════════════════════════════════════════════

@saved_bp.route('/saved-recipes', methods=['GET'])
@login_required  # Must be logged in
def index():
    """
    READ Operation: Get all recipes saved by user
    
    This demonstrates:
    - MANY-TO-MANY QUERY: Uses User.saved relationship
    - OOP RELATIONSHIP: Traverses through junction table
    - AUTOMATIC JOIN: SQLAlchemy handles JOIN for us
    - ORDERING: Orders by save date (created_at in junction table)
    
    Process:
    1. Access current_user.saved (OOP relationship)
    2. Order by saved date (descending)
    3. Convert recipes to dictionaries
    
    SQL Generated:
    SELECT recipes.* FROM recipes
    JOIN saved_recipes ON recipes.id = saved_recipes.recipe_id
    WHERE saved_recipes.user_id = ?
    ORDER BY saved_recipes.created_at DESC
    
    Returns: JSON array of saved recipes
    """
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


# ═══════════════════════════════════════════════════════════════════════════
# CREATE/DELETE OPERATION: Toggle Save Status (TOGGLE PATTERN)
# ═══════════════════════════════════════════════════════════════════════════
# CRUD: CREATE or DELETE - Toggles saved status in one operation
# HTTP Method: POST
# URL: /api/recipes/<recipe_id>/save
# Authentication: Required (@login_required)
# Demonstrates: RAW SQL, TOGGLE PATTERN, JUNCTION TABLE OPERATIONS
# ═══════════════════════════════════════════════════════════════════════════

@saved_bp.route('/recipes/<int:recipe_id>/save', methods=['POST'])
@login_required  # Must be logged in
def toggle(recipe_id):
    """
    CREATE/DELETE Operation: Toggle recipe save status
    
    This demonstrates:
    - TOGGLE PATTERN: If saved, unsave; if not saved, save
    - RAW SQL EXECUTION: Uses db.session.execute() for direct table access
    - MANY-TO-MANY INSERT/DELETE: Operations on junction table
    - TRANSACTIONAL OPERATIONS: Commits INSERT or DELETE
    
    Process:
    1. Verify recipe exists
    2. Check if already saved (READ operation on junction table)
    3. If saved: DELETE from saved_recipes table (UNSAVE)
    4. If not saved: INSERT into saved_recipes table (SAVE)
    5. COMMIT transaction
    
    SQL for UNSAVE:
    DELETE FROM saved_recipes
    WHERE user_id = ? AND recipe_id = ?
    
    SQL for SAVE:
    INSERT INTO saved_recipes (user_id, recipe_id, created_at, updated_at)
    VALUES (?, ?, NOW(), NOW())
    
    Returns: JSON with new save status
    """
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
