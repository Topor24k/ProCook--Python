# ═══════════════════════════════════════════════════════════════════════════
# RECIPE ROUTES - Full CRUD Operations on Recipes
# ═══════════════════════════════════════════════════════════════════════════
# This file demonstrates:
# 1. COMPLETE CRUD: CREATE (store), READ (index, show), UPDATE (update), DELETE (destroy)
# 2. FILE UPLOAD HANDLING: Image uploads with validation and storage
# 3. TRANSACTIONAL OPERATIONS: Database commits with rollback on failure
# 4. RELATIONSHIP MANAGEMENT: Creating/updating recipes with related ingredients
# 5. CASCADE OPERATIONS: Ingredients are automatically deleted/updated with recipe
# 6. AUTHORIZATION: Users can only edit/delete their own recipes
#
# Connects to:
# - backend/models.py: Recipe and Ingredient models
# - backend/app.py: Registered as recipes_bp with /api/recipes prefix
# - Frontend: React components consume these APIs
# ═══════════════════════════════════════════════════════════════════════════

# Import os for file system operations (file paths, directory creation)
import os

# Import json for parsing JSON strings from FormData
import json

# Import uuid for generating unique filenames (prevents collisions)
import uuid

# Import time for timestamp-based filenames
import time

# Import Flask utilities
from flask import Blueprint, request, jsonify, current_app

# Import Flask-Login for authentication
from flask_login import login_required, current_user

# Import database models
# Connects to: backend/models.py for Recipe and Ingredient classes
from backend.models import db, Recipe, Ingredient

# Create Blueprint object - groups recipe-related routes
# Registered in: backend/app.py with app.register_blueprint(recipes_bp, url_prefix='/api/recipes')
recipes_bp = Blueprint('recipes', __name__)


# ═══════════════════════════════════════════════════════════════════════════
# HELPER FUNCTION: Recipe Data Validation
# ═══════════════════════════════════════════════════════════════════════════
# This demonstrates SEPARATION OF CONCERNS: validation logic separated from routes
# Used in: store() and update() routes for CREATE and UPDATE operations
# ═══════════════════════════════════════════════════════════════════════════

def validate_recipe_data(data, files=None):
    """
    Validates all recipe input data before database operations
    
    This demonstrates INPUT VALIDATION for data integrity
    Prevents invalid data from reaching the database
    
    Parameters:
    - data: Dictionary of recipe fields
    - files: Optional file upload dictionary
    
    Returns: Dictionary of validation errors (empty if valid)
    """
    # Collect all validation errors in dictionary
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
    """
    FILE UPLOAD HANDLER: Saves uploaded recipe image to filesystem
    
    This demonstrates:
    - FILE SYSTEM OPERATIONS: Creating directories and saving files
    - UNIQUE FILENAME GENERATION: Prevents naming collisions
    - SECURITY: Validates file extension
    
    Process:
    1. Create recipes directory if it doesn't exist
    2. Generate unique filename (timestamp + UUID)
    3. Save file to backend/uploads/recipes/
    4. Return relative path for database storage
    
    Used in: store() (CREATE) and update() (UPDATE) routes
    Connected to: Recipe.image field in backend/models.py
    Served by: serve_upload() route in backend/app.py
    
    Returns: Relative file path (e.g., "recipes/1234567890_abc.jpg")
    """
    # Get upload directory from Flask config (backend/uploads/)
    upload_dir = current_app.config['UPLOAD_FOLDER']
    
    # Create recipes subdirectory (backend/uploads/recipes/)
    recipes_dir = os.path.join(upload_dir, 'recipes')
    os.makedirs(recipes_dir, exist_ok=True)  # exist_ok prevents error if already exists

    # Extract file extension (jpg, png, etc.)
    ext = file.filename.rsplit('.', 1)[-1].lower()
    
    # Generate unique filename: timestamp + UUID (prevents naming conflicts)
    # Example: 1709567890_a1b2c3d4e5f6.jpg
    filename = f"{int(time.time())}_{uuid.uuid4().hex}.{ext}"
    
    # Full filesystem path
    filepath = os.path.join(recipes_dir, filename)
    
    # Save uploaded file to disk
    file.save(filepath)
    
    # Return relative path (stored in database, served via /uploads/ route)
    return f"recipes/{filename}"


# ═══════════════════════════════════════════════════════════════════════════
# READ OPERATION: List All Recipes
# ═══════════════════════════════════════════════════════════════════════════
# CRUD: READ - Retrieves list of all recipes with author info
# HTTP Method: GET
# URL: /api/recipes
# Authentication: Not required (public)
# Connects to: Recipe model with User relationship (OOP)
# ═══════════════════════════════════════════════════════════════════════════

@recipes_bp.route('', methods=['GET'])
def index():
    """
    READ Operation: Fetch all recipes from database
    
    This demonstrates:
    - TRANSACTIONAL READ: SELECT query with JOIN
    - EAGER LOADING: Loads related User data to avoid N+1 queries
    - OOP RELATIONSHIP TRAVERSAL: Recipe.user relationship
    - OPTIONAL PAGINATION: Supports limit parameter
    
    Process:
    1. Build query withjoined User data (EAGER LOADING)
    2. Apply optional limit for pagination
    3. Order by creation date (newest first)
    4. Convert Recipe objects to dictionaries
    
    Query Parameters:
    - limit: Optional integer to limit results (max 100)
    
    Returns: JSON array of recipes with user info
    """
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


# ═══════════════════════════════════════════════════════════════════════════
# READ OPERATION: Get Single Recipe with Details
# ═══════════════════════════════════════════════════════════════════════════
# CRUD: READ - Retrieves one recipe with all details and ingredients
# HTTP Method: GET
# URL: /api/recipes/<id>
# Authentication: Not required (public)
# Connects to: Recipe and Ingredient models (OOP RELATIONSHIPS)
# ═══════════════════════════════════════════════════════════════════════════

@recipes_bp.route('/<int:recipe_id>', methods=['GET'])
def show(recipe_id):
    """
    READ Operation: Fetch single recipe with full details
    
    This demonstrates:
    - TRANSACTIONAL READ: SELECT with multiple JOINs
    - EAGER LOADING: Loads User and Ingredients in one query
    - OOP RELATIONSHIPS: Traverses recipe.user and recipe.ingredients
    - ERROR HANDLING: 404 if recipe not found
    
    Process:
    1. Query database for recipe by ID
    2. EAGER LOAD related User and Ingredients (prevents N+1)
    3. Return 404 if not found
    4. Convert to dictionary with all related data
    
    URL Parameters:
    - recipe_id: Integer ID of recipe to retrieve
    
    Returns: JSON object with recipe, user, and ingredients
    """
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


# ═══════════════════════════════════════════════════════════════════════════
# CREATE OPERATION: Create New Recipe with Ingredients
# ═══════════════════════════════════════════════════════════════════════════
# CRUD: CREATE - Inserts new Recipe and related Ingredients
# HTTP Method: POST
# URL: /api/recipes
# Authentication: Required (@login_required)
# Connects to: Recipe and Ingredient models
# ═══════════════════════════════════════════════════════════════════════════

@recipes_bp.route('', methods=['POST'])
@login_required  # Must be logged in to create recipes
def store():
    """
    CREATE Operation: Create new recipe with ingredients
    
    This demonstrates:
    - TRANSACTIONAL INSERT: Creates Recipe and multiple Ingredients in one transaction
    - FILE UPLOAD HANDLING: Processes and stores recipe image
    - OOP COMPOSITION: Recipe "has many" Ingredients
    - ROLLBACK ON ERROR: Maintains data integrity
    - CASCADE RELATIONSHIP: Ingredients tied to recipe
    
    Process:
    1. Validate all input data (validation helper)
    2. Handle file upload if image provided
    3. Create Recipe object with current_user as author
    4. Use db.session.flush() to get recipe.id
    5. Create Ingredient objects linked to recipe
    6. COMMIT transaction (INSERT operations)
    7. ROLLBACK if any error occurs
    
    Request: multipart/form-data or JSON
    
    Returns: JSON with created recipe and ingredients
    """
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


# ═══════════════════════════════════════════════════════════════════════════
# UPDATE OPERATION: Modify Existing Recipe
# ═══════════════════════════════════════════════════════════════════════════
# CRUD: UPDATE - Modifies Recipe and replaces Ingredients
# HTTP Method: PUT
# URL: /api/recipes/<id>
# Authentication: Required (must be recipe owner)
# Connects to: Recipe and Ingredient models
# ═══════════════════════════════════════════════════════════════════════════

@recipes_bp.route('/<int:recipe_id>', methods=['PUT'])
@login_required  # Must be logged in
def update(recipe_id):
    """
    UPDATE Operation: Modify existing recipe
    
    This demonstrates:
    - TRANSACTIONAL UPDATE: Modifies Recipe and replaces Ingredients
    - AUTHORIZATION: Only recipe owner can update
    - FILE REPLACEMENT: Deletes old image, uploads new one
    - CASCADE DELETE: Old ingredients deleted, new ones created
    - ROLLBACK ON ERROR: All-or-nothing transaction
    
    Process:
    1. Find recipe by ID (READ)
    2. Check ownership (AUTHORIZATION)
    3. Validate new data
    4. Handle image replacement if new file uploaded
    5. Update Recipe fields
    6. DELETE old ingredients
    7. CREATE new ingredients
    8. COMMIT transaction
    
    URL Parameters:
    - recipe_id: ID of recipe to update
    
    Returns: JSON with updated recipe and ingredients
    """
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


# ═══════════════════════════════════════════════════════════════════════════
# DELETE OPERATION: Remove Recipe and All Related Data
# ═══════════════════════════════════════════════════════════════════════════
# CRUD: DELETE - Removes Recipe with CASCADE deletion of related records
# HTTP Method: DELETE
# URL: /api/recipes/<id>
# Authentication: Required (must be recipe owner)
# Connects to: Recipe, Ingredient, Comment, Rating models (CASCADE)
# ═══════════════════════════════════════════════════════════════════════════

@recipes_bp.route('/<int:recipe_id>', methods=['DELETE'])
@login_required  # Must be logged in
def destroy(recipe_id):
    """
    DELETE Operation: Remove recipe and all related data
    
    This demonstrates:
    - TRANSACTIONAL DELETE: Removes Recipe from database
    - CASCADE OPERATIONS: Automatically deletes related records:
      - All Ingredients (cascade='all, delete-orphan')
      - All Comments (cascade='all, delete-orphan')
      - All Ratings (cascade='all, delete-orphan')
      - All SavedRecipes entries
    - FILE DELETION: Removes image file from filesystem
    - AUTHORIZATION: Only recipe owner can delete
    - ROLLBACK ON ERROR: Maintains data integrity
    
    Process:
    1. Find recipe by ID (READ)
    2. Check ownership (AUTHORIZATION)
    3. Delete image file from disk
    4. Delete recipe from database (CASCADE deletes related records)
    5. COMMIT transaction
    
    URL Parameters:
    - recipe_id: ID of recipe to delete
    
    Returns: JSON confirmation of deletion
    """
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
