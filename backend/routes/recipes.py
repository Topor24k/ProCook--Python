import os
import json
import uuid
import time
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from backend.models import db, Recipe, Ingredient

recipes_bp = Blueprint('recipes', __name__)


# ── Validation helper ──
def validate_recipe_data(data, files=None):
    errors = {}

    title = (data.get('title') or '').strip()
    if not title or len(title) < 3:
        errors['title'] = ['Recipe title must be at least 3 characters.']
    elif len(title) > 255:
        errors['title'] = ['Recipe title cannot exceed 255 characters.']

    short_description = (data.get('short_description') or '').strip()
    if not short_description or len(short_description) < 10:
        errors['short_description'] = ['Description must be at least 10 characters.']
    elif len(short_description) > 500:
        errors['short_description'] = ['Description cannot exceed 500 characters.']

    cuisine_type = (data.get('cuisine_type') or '').strip()
    if not cuisine_type:
        errors['cuisine_type'] = ['Please select a cuisine type.']

    category = (data.get('category') or '').strip()
    if not category:
        errors['category'] = ['Please select a category.']

    try:
        prep_time = int(data.get('prep_time', 0))
        if prep_time < 1 or prep_time > 1440:
            errors['prep_time'] = ['Preparation time must be between 1 and 1440 minutes.']
    except (ValueError, TypeError):
        errors['prep_time'] = ['Preparation time must be a number.']

    try:
        cook_time = int(data.get('cook_time', 0))
        if cook_time < 0 or cook_time > 1440:
            errors['cook_time'] = ['Cooking time must be between 0 and 1440 minutes.']
    except (ValueError, TypeError):
        errors['cook_time'] = ['Cooking time must be a number.']

    try:
        serving_size = int(data.get('serving_size', 0))
        if serving_size < 1 or serving_size > 100:
            errors['serving_size'] = ['Serving size must be between 1 and 100.']
    except (ValueError, TypeError):
        errors['serving_size'] = ['Serving size must be a number.']

    preparation_notes = (data.get('preparation_notes') or '').strip()
    if preparation_notes and len(preparation_notes) < 20:
        errors['preparation_notes'] = ['Instructions must be at least 20 characters.']

    # Parse ingredients
    ingredients_raw = data.get('ingredients')
    if isinstance(ingredients_raw, str):
        try:
            ingredients_raw = json.loads(ingredients_raw)
        except json.JSONDecodeError:
            errors['ingredients'] = ['Invalid ingredients data.']
            ingredients_raw = []

    if not ingredients_raw or not isinstance(ingredients_raw, list) or len(ingredients_raw) < 1:
        errors['ingredients'] = ['At least one ingredient is required.']
    elif len(ingredients_raw) > 50:
        errors['ingredients'] = ['Cannot add more than 50 ingredients.']
    else:
        for i, ing in enumerate(ingredients_raw):
            if not (ing.get('name') or '').strip():
                errors[f'ingredients.{i}.name'] = ['Ingredient name is required.']
            if not (ing.get('measurement') or '').strip():
                errors[f'ingredients.{i}.measurement'] = ['Ingredient measurement is required.']

    # Validate image file if present
    if files and 'image' in files:
        image = files['image']
        allowed_ext = {'jpeg', 'jpg', 'png', 'gif', 'webp'}
        ext = image.filename.rsplit('.', 1)[-1].lower() if '.' in image.filename else ''
        if ext not in allowed_ext:
            errors['image'] = ['Image must be jpeg, jpg, png, gif, or webp.']

    return errors


def save_image(file):
    """Save uploaded image and return the storage path."""
    upload_dir = current_app.config['UPLOAD_FOLDER']
    recipes_dir = os.path.join(upload_dir, 'recipes')
    os.makedirs(recipes_dir, exist_ok=True)

    ext = file.filename.rsplit('.', 1)[-1].lower()
    filename = f"{int(time.time())}_{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(recipes_dir, filename)
    file.save(filepath)
    return f"recipes/{filename}"


# ── List all recipes ──
@recipes_bp.route('', methods=['GET'])
def index():
    try:
        query = Recipe.query.options(
            db.joinedload(Recipe.user)
        )

        limit = request.args.get('limit')
        if limit:
            limit = min(int(limit), 100)
            query = query.limit(limit)

        recipes = query.order_by(Recipe.created_at.desc()).all()

        return jsonify({
            'success': True,
            'data': [r.to_dict(include_user=True) for r in recipes],
            'count': len(recipes)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to fetch recipes.'
        }), 500


# ── Show single recipe ──
@recipes_bp.route('/<int:recipe_id>', methods=['GET'])
def show(recipe_id):
    try:
        recipe = Recipe.query.options(
            db.joinedload(Recipe.user),
            db.joinedload(Recipe.ingredients),
        ).get(recipe_id)

        if not recipe:
            return jsonify({
                'success': False,
                'message': 'Recipe not found.'
            }), 404

        return jsonify({
            'success': True,
            'data': recipe.to_dict(include_ingredients=True, include_user=True)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to fetch recipe details.'
        }), 500


# ── Create recipe ──
@recipes_bp.route('', methods=['POST'])
@login_required
def store():
    try:
        # Support both JSON and FormData
        if request.content_type and 'multipart/form-data' in request.content_type:
            data = request.form.to_dict()
            files = request.files
        else:
            data = request.get_json() or {}
            files = None

        errors = validate_recipe_data(data, files)
        if errors:
            return jsonify({
                'success': False,
                'message': 'Recipe validation failed',
                'errors': errors
            }), 422

        # Parse ingredients
        ingredients_raw = data.get('ingredients')
        if isinstance(ingredients_raw, str):
            ingredients_raw = json.loads(ingredients_raw)

        # Handle image upload
        image_path = None
        if files and 'image' in files:
            image_path = save_image(files['image'])

        prep_time = int(data['prep_time'])
        cook_time = int(data['cook_time'])

        recipe = Recipe(
            user_id=current_user.id,
            title=data['title'].strip(),
            short_description=data['short_description'].strip(),
            image=image_path,
            cuisine_type=data['cuisine_type'].strip(),
            category=data['category'].strip(),
            prep_time=prep_time,
            cook_time=cook_time,
            total_time=prep_time + cook_time,
            serving_size=int(data['serving_size']),
            preparation_notes=(data.get('preparation_notes') or '').strip() or None,
        )
        db.session.add(recipe)
        db.session.flush()  # Get recipe.id

        for i, ing in enumerate(ingredients_raw):
            ingredient = Ingredient(
                recipe_id=recipe.id,
                name=ing['name'].strip(),
                measurement=ing['measurement'].strip(),
                substitution_option=(ing.get('substitution_option') or '').strip() or None,
                allergen_info=(ing.get('allergen_info') or '').strip() or None,
                order=i + 1,
            )
            db.session.add(ingredient)

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Recipe created successfully!',
            'data': recipe.to_dict(include_ingredients=True)
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Failed to create recipe. Please try again.'
        }), 500


# ── Update recipe ──
@recipes_bp.route('/<int:recipe_id>', methods=['PUT'])
@login_required
def update(recipe_id):
    try:
        recipe = Recipe.query.get(recipe_id)
        if not recipe:
            return jsonify({
                'success': False,
                'message': 'Recipe not found.'
            }), 404

        if recipe.user_id != current_user.id:
            return jsonify({
                'success': False,
                'message': 'You do not have permission to edit this recipe.'
            }), 403

        # Support both JSON and FormData
        if request.content_type and 'multipart/form-data' in request.content_type:
            data = request.form.to_dict()
            files = request.files
        else:
            data = request.get_json() or {}
            files = None

        errors = validate_recipe_data(data, files)
        if errors:
            return jsonify({
                'success': False,
                'message': 'Recipe validation failed',
                'errors': errors
            }), 422

        # Parse ingredients
        ingredients_raw = data.get('ingredients')
        if isinstance(ingredients_raw, str):
            ingredients_raw = json.loads(ingredients_raw)

        # Handle image upload
        if files and 'image' in files:
            # Delete old image
            if recipe.image:
                old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], recipe.image)
                if os.path.exists(old_path):
                    os.remove(old_path)
            recipe.image = save_image(files['image'])

        prep_time = int(data['prep_time'])
        cook_time = int(data['cook_time'])

        recipe.title = data['title'].strip()
        recipe.short_description = data['short_description'].strip()
        recipe.cuisine_type = data['cuisine_type'].strip()
        recipe.category = data['category'].strip()
        recipe.prep_time = prep_time
        recipe.cook_time = cook_time
        recipe.total_time = prep_time + cook_time
        recipe.serving_size = int(data['serving_size'])
        recipe.preparation_notes = (data.get('preparation_notes') or '').strip() or None

        # Replace ingredients
        Ingredient.query.filter_by(recipe_id=recipe.id).delete()
        for i, ing in enumerate(ingredients_raw):
            ingredient = Ingredient(
                recipe_id=recipe.id,
                name=ing['name'].strip(),
                measurement=ing['measurement'].strip(),
                substitution_option=(ing.get('substitution_option') or '').strip() or None,
                allergen_info=(ing.get('allergen_info') or '').strip() or None,
                order=i + 1,
            )
            db.session.add(ingredient)

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Recipe updated successfully!',
            'data': recipe.to_dict(include_ingredients=True)
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Failed to update recipe. Please try again.'
        }), 500


# ── Delete recipe ──
@recipes_bp.route('/<int:recipe_id>', methods=['DELETE'])
@login_required
def destroy(recipe_id):
    try:
        recipe = Recipe.query.get(recipe_id)
        if not recipe:
            return jsonify({
                'success': False,
                'message': 'Recipe not found.'
            }), 404

        if recipe.user_id != current_user.id:
            return jsonify({
                'success': False,
                'message': 'You do not have permission to delete this recipe.'
            }), 403

        # Delete image file
        if recipe.image:
            old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], recipe.image)
            if os.path.exists(old_path):
                os.remove(old_path)

        db.session.delete(recipe)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Recipe deleted successfully.'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Failed to delete recipe. Please try again.'
        }), 500


# ── My recipes ──
@recipes_bp.route('/my-recipes', methods=['GET'])
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
