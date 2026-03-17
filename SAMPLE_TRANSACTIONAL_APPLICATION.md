# Sample Transactional Application

## Overview
This document demonstrates the transactional operations in the ProCook Recipe Management System. The application uses Flask-SQLAlchemy to manage database transactions with full ACID (Atomicity, Consistency, Isolation, Durability) properties. Each transaction ensures data integrity through proper commit and rollback mechanisms.

---

## Transaction 1: User Registration

### Description
The user registration process creates a new user account with encrypted password storage. This transaction demonstrates a single-table INSERT operation with data validation and automatic password hashing.

### Code Snippet

```python
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
            return jsonify({'success': False, 'message': 'Validation failed.', 
                          'errors': errors}), 422

        # TRANSACTION START: Create new user with encrypted password
        user = User(name=name, email=email)
        user.set_password(password)  # OOP Encapsulation: hashes password
        db.session.add(user)
        db.session.commit()  # TRANSACTION COMMIT
        
        login_user(user, remember=True)
        return jsonify({'success': True, 'message': 'Registration successful!', 
                       'data': user.to_dict()}), 201
                       
    except Exception as e:
        db.session.rollback()  # TRANSACTION ROLLBACK on error
        return jsonify({'success': False, 
                       'message': 'Registration failed. Please try again.'}), 500
```

**Figure 1. User Registration Transaction Code**

### Sample Input

```json
{
  "name": "John Doe",
  "email": "john.doe@example.com",
  "password": "SecurePass123",
  "password_confirmation": "SecurePass123"
}
```

**Figure 2. User Registration Input Data**

### Sample Output

```json
{
  "success": true,
  "message": "Registration successful!",
  "data": {
    "id": 1,
    "name": "John Doe",
    "email": "john.doe@example.com",
    "created_at": "2026-03-11T08:30:00Z",
    "updated_at": "2026-03-11T08:30:00Z"
  }
}
```

**Figure 3. User Registration Success Response**

### Transaction Flow
1. **Input Validation**: Validates all input fields (name, email, password)
2. **Duplicate Check**: Queries database to ensure email is unique
3. **Password Encryption**: Uses Werkzeug's `generate_password_hash()` for security
4. **Database Insert**: Adds user to session and commits transaction
5. **Rollback on Failure**: Automatically rolls back if any error occurs

---

## Transaction 2: Recipe Creation with Ingredients

### Description
This complex transaction demonstrates a multi-table INSERT operation where a recipe and its related ingredients are created atomically. If any part fails, the entire transaction is rolled back, maintaining database consistency.

### Code Snippet

```python
# CRUD CREATE: inserts new recipe with related ingredients into database
@recipes_bp.route('', methods=['POST'])
@login_required
def store():
    try:
        if request.content_type and 'multipart/form-data' in request.content_type:
            data = request.form.to_dict()
            files = request.files
        else:
            data = request.get_json() or {}
            files = None

        errors = validate_recipe_data(data, files)
        if errors:
            return jsonify({'success': False, 'message': 'Recipe validation failed', 
                          'errors': errors}), 422

        ingredients_raw = data.get('ingredients')
        if isinstance(ingredients_raw, str):
            ingredients_raw = json.loads(ingredients_raw)

        image_path = None
        if files and 'image' in files:
            image_path = save_image(files['image'])

        prep_time = int(data['prep_time'])
        cook_time = int(data['cook_time'])

        # TRANSACTION START: Create recipe with multiple related entities
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
        db.session.flush()  # Get recipe.id before committing

        # Create related ingredients within same transaction
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

        db.session.commit()  # TRANSACTION COMMIT: All or nothing
        return jsonify({
            'success': True,
            'message': 'Recipe created successfully!',
            'data': recipe.to_dict(include_ingredients=True)
        }), 201
        
    except Exception as e:
        db.session.rollback()  # TRANSACTION ROLLBACK: Undo all changes
        return jsonify({'success': False, 
                       'message': 'Failed to create recipe. Please try again.'}), 500
```

**Figure 4. Recipe Creation Transaction Code**

### Sample Input

```json
{
  "title": "Classic Spaghetti Carbonara",
  "short_description": "Traditional Italian pasta with eggs, cheese, and pancetta",
  "cuisine_type": "Italian",
  "category": "Main Course",
  "prep_time": 10,
  "cook_time": 15,
  "serving_size": 4,
  "preparation_notes": "Cook pasta al dente. Mix eggs and cheese before adding to hot pasta. Do not scramble the eggs.",
  "ingredients": [
    {
      "name": "Spaghetti",
      "measurement": "400g",
      "substitution_option": "Linguine or fettuccine",
      "allergen_info": "Contains gluten"
    },
    {
      "name": "Pancetta",
      "measurement": "200g, diced",
      "substitution_option": "Bacon or guanciale",
      "allergen_info": "Pork product"
    },
    {
      "name": "Eggs",
      "measurement": "4 large",
      "substitution_option": null,
      "allergen_info": "Contains eggs"
    },
    {
      "name": "Pecorino Romano",
      "measurement": "100g, grated",
      "substitution_option": "Parmesan cheese",
      "allergen_info": "Contains dairy"
    },
    {
      "name": "Black Pepper",
      "measurement": "2 tsp, freshly ground",
      "substitution_option": null,
      "allergen_info": null
    }
  ]
}
```

**Figure 5. Recipe Creation Input Data with Multiple Ingredients**

### Sample Output

```json
{
  "success": true,
  "message": "Recipe created successfully!",
  "data": {
    "id": 15,
    "user_id": 1,
    "title": "Classic Spaghetti Carbonara",
    "short_description": "Traditional Italian pasta with eggs, cheese, and pancetta",
    "image": null,
    "cuisine_type": "Italian",
    "category": "Main Course",
    "prep_time": 10,
    "cook_time": 15,
    "total_time": 25,
    "serving_size": 4,
    "preparation_notes": "Cook pasta al dente. Mix eggs and cheese before adding to hot pasta. Do not scramble the eggs.",
    "average_rating": 0,
    "ratings_count": 0,
    "created_at": "2026-03-11T09:15:00Z",
    "updated_at": "2026-03-11T09:15:00Z",
    "ingredients": [
      {
        "id": 75,
        "recipe_id": 15,
        "name": "Spaghetti",
        "measurement": "400g",
        "substitution_option": "Linguine or fettuccine",
        "allergen_info": "Contains gluten",
        "order": 1,
        "created_at": "2026-03-11T09:15:00Z",
        "updated_at": "2026-03-11T09:15:00Z"
      },
      {
        "id": 76,
        "recipe_id": 15,
        "name": "Pancetta",
        "measurement": "200g, diced",
        "substitution_option": "Bacon or guanciale",
        "allergen_info": "Pork product",
        "order": 2,
        "created_at": "2026-03-11T09:15:00Z",
        "updated_at": "2026-03-11T09:15:00Z"
      },
      {
        "id": 77,
        "recipe_id": 15,
        "name": "Eggs",
        "measurement": "4 large",
        "substitution_option": null,
        "allergen_info": "Contains eggs",
        "order": 3,
        "created_at": "2026-03-11T09:15:00Z",
        "updated_at": "2026-03-11T09:15:00Z"
      },
      {
        "id": 78,
        "recipe_id": 15,
        "name": "Pecorino Romano",
        "measurement": "100g, grated",
        "substitution_option": "Parmesan cheese",
        "allergen_info": "Contains dairy",
        "order": 4,
        "created_at": "2026-03-11T09:15:00Z",
        "updated_at": "2026-03-11T09:15:00Z"
      },
      {
        "id": 79,
        "recipe_id": 15,
        "name": "Black Pepper",
        "measurement": "2 tsp, freshly ground",
        "substitution_option": null,
        "allergen_info": null,
        "order": 5,
        "created_at": "2026-03-11T09:15:00Z",
        "updated_at": "2026-03-11T09:15:00Z"
      }
    ]
  }
}
```

**Figure 6. Recipe Creation Success Response with All Ingredients**

### Transaction Flow
1. **Input Validation**: Validates recipe data and all ingredients
2. **Image Upload**: Saves image file to server (if provided)
3. **Recipe Creation**: Adds recipe to database session
4. **Flush Operation**: Obtains recipe ID without committing
5. **Ingredients Creation**: Adds all ingredients linked to recipe ID
6. **Atomic Commit**: Commits all changes as single transaction
7. **Automatic Rollback**: Reverts all changes if any error occurs

---

## Transaction 3: Recipe Rating (UPSERT Pattern)

### Description
This transaction demonstrates the UPSERT (UPDATE or INSERT) pattern where a user's rating for a recipe is either created or updated. It also calculates aggregate statistics in the same transaction.

### Code Snippet

```python
# CRUD CREATE/UPDATE: creates new rating or updates existing (UPSERT pattern)
@ratings_bp.route('/<int:recipe_id>/rating', methods=['POST'])
@login_required
def store(recipe_id):
    try:
        recipe = Recipe.query.get(recipe_id)
        if not recipe:
            return jsonify({'success': False, 'message': 'Recipe not found.'}), 404
        if recipe.user_id == current_user.id:
            return jsonify({'success': False, 
                          'message': 'You cannot rate your own recipe.'}), 403

        data = request.get_json()
        try:
            rating_value = int(data.get('rating', 0))
        except (ValueError, TypeError):
            return jsonify({'success': False, 'message': 'Validation failed.', 
                          'errors': {'rating': ['Rating must be a number.']}}), 422

        if rating_value < 1 or rating_value > 5:
            return jsonify({'success': False, 'message': 'Validation failed.', 
                          'errors': {'rating': ['Rating must be between 1 and 5.']}}), 422

        # TRANSACTION START: UPSERT operation (update or insert)
        rating = Rating.query.filter_by(recipe_id=recipe_id, 
                                       user_id=current_user.id).first()
        if rating:
            # UPDATE: Modify existing rating
            rating.rating = rating_value
        else:
            # INSERT: Create new rating
            rating = Rating(recipe_id=recipe_id, user_id=current_user.id, 
                          rating=rating_value)
            db.session.add(rating)

        db.session.commit()  # TRANSACTION COMMIT

        # Calculate aggregate statistics after commit
        avg = db.session.query(db.func.avg(Rating.rating)).filter(
            Rating.recipe_id == recipe_id).scalar()
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
        db.session.rollback()  # TRANSACTION ROLLBACK
        return jsonify({'success': False, 
                       'message': 'Failed to submit rating.'}), 500
```

**Figure 7. Rating UPSERT Transaction Code**

### Sample Input (First Rating)

```json
{
  "rating": 5
}
```

**Figure 8. Rating Submission Input Data**

### Sample Output (First Rating)

```json
{
  "success": true,
  "message": "Rating submitted successfully.",
  "data": {
    "rating": {
      "id": 42,
      "recipe_id": 15,
      "user_id": 2,
      "rating": 5,
      "created_at": "2026-03-11T10:30:00Z",
      "updated_at": "2026-03-11T10:30:00Z"
    },
    "averageRating": 5.0,
    "ratingsCount": 1
  }
}
```

**Figure 9. First Rating Success Response**

### Sample Output (Updated Rating)

```json
{
  "success": true,
  "message": "Rating submitted successfully.",
  "data": {
    "rating": {
      "id": 42,
      "recipe_id": 15,
      "user_id": 2,
      "rating": 4,
      "created_at": "2026-03-11T10:30:00Z",
      "updated_at": "2026-03-11T11:45:00Z"
    },
    "averageRating": 4.0,
    "ratingsCount": 1
  }
}
```

**Figure 10. Updated Rating Response (Same User Updates Their Rating)**

### Transaction Flow
1. **Authorization Check**: Verifies user cannot rate their own recipe
2. **Validation**: Ensures rating is between 1 and 5
3. **Query Existing**: Checks if user has already rated this recipe
4. **Conditional Operation**: Updates existing rating OR creates new rating
5. **Atomic Commit**: Saves changes to database
6. **Aggregate Calculation**: Computes average rating and total count
7. **Rollback on Error**: Reverts changes if transaction fails

---

## Transaction 4: Recipe Update with Ingredient Replacement

### Description
This complex transaction demonstrates updating a recipe while completely replacing its ingredients. The old ingredients are deleted and new ones are created, all within a single atomic transaction.

### Code Snippet

```python
# CRUD UPDATE: modifies existing recipe and replaces ingredients
@recipes_bp.route('/<int:recipe_id>', methods=['PUT'])
@login_required
def update(recipe_id):
    try:
        recipe = Recipe.query.get(recipe_id)
        if not recipe:
            return jsonify({'success': False, 'message': 'Recipe not found.'}), 404
        if recipe.user_id != current_user.id:
            return jsonify({'success': False, 
                          'message': 'You do not have permission to edit this recipe.'}), 403

        if request.content_type and 'multipart/form-data' in request.content_type:
            data = request.form.to_dict()
            files = request.files
        else:
            data = request.get_json() or {}
            files = None

        errors = validate_recipe_data(data, files)
        if errors:
            return jsonify({'success': False, 'message': 'Recipe validation failed', 
                          'errors': errors}), 422

        ingredients_raw = data.get('ingredients')
        if isinstance(ingredients_raw, str):
            ingredients_raw = json.loads(ingredients_raw)

        if files and 'image' in files:
            if recipe.image:
                old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], recipe.image)
                if os.path.exists(old_path):
                    os.remove(old_path)
            recipe.image = save_image(files['image'])

        prep_time = int(data['prep_time'])
        cook_time = int(data['cook_time'])

        # TRANSACTION START: Update recipe and replace all ingredients
        recipe.title = data['title'].strip()
        recipe.short_description = data['short_description'].strip()
        recipe.cuisine_type = data['cuisine_type'].strip()
        recipe.category = data['category'].strip()
        recipe.prep_time = prep_time
        recipe.cook_time = cook_time
        recipe.total_time = prep_time + cook_time
        recipe.serving_size = int(data['serving_size'])
        recipe.preparation_notes = (data.get('preparation_notes') or '').strip() or None

        # DELETE all existing ingredients
        Ingredient.query.filter_by(recipe_id=recipe.id).delete()
        
        # CREATE new ingredients
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

        db.session.commit()  # TRANSACTION COMMIT: All changes saved atomically
        return jsonify({
            'success': True,
            'message': 'Recipe updated successfully!',
            'data': recipe.to_dict(include_ingredients=True)
        })
        
    except Exception as e:
        db.session.rollback()  # TRANSACTION ROLLBACK: Restore original state
        return jsonify({'success': False, 
                       'message': 'Failed to update recipe. Please try again.'}), 500
```

**Figure 11. Recipe Update Transaction with Ingredient Replacement**

### Sample Input

```json
{
  "title": "Classic Spaghetti Carbonara (Updated)",
  "short_description": "Authentic Italian pasta with eggs, pecorino cheese, and guanciale",
  "cuisine_type": "Italian",
  "category": "Main Course",
  "prep_time": 12,
  "cook_time": 18,
  "serving_size": 4,
  "preparation_notes": "Use room temperature eggs. Reserve pasta water. Toss pasta in pan off heat to prevent scrambling.",
  "ingredients": [
    {
      "name": "Spaghetti",
      "measurement": "400g",
      "substitution_option": "Bucatini",
      "allergen_info": "Contains gluten"
    },
    {
      "name": "Guanciale",
      "measurement": "150g, cut into strips",
      "substitution_option": "Pancetta",
      "allergen_info": "Pork product"
    },
    {
      "name": "Egg Yolks",
      "measurement": "4 large",
      "substitution_option": null,
      "allergen_info": "Contains eggs"
    },
    {
      "name": "Pecorino Romano",
      "measurement": "120g, finely grated",
      "substitution_option": null,
      "allergen_info": "Contains dairy"
    }
  ]
}
```

**Figure 12. Recipe Update Input Data**

### Sample Output

```json
{
  "success": true,
  "message": "Recipe updated successfully!",
  "data": {
    "id": 15,
    "user_id": 1,
    "title": "Classic Spaghetti Carbonara (Updated)",
    "short_description": "Authentic Italian pasta with eggs, pecorino cheese, and guanciale",
    "image": null,
    "cuisine_type": "Italian",
    "category": "Main Course",
    "prep_time": 12,
    "cook_time": 18,
    "total_time": 30,
    "serving_size": 4,
    "preparation_notes": "Use room temperature eggs. Reserve pasta water. Toss pasta in pan off heat to prevent scrambling.",
    "average_rating": 4.0,
    "ratings_count": 1,
    "created_at": "2026-03-11T09:15:00Z",
    "updated_at": "2026-03-11T14:20:00Z",
    "ingredients": [
      {
        "id": 80,
        "recipe_id": 15,
        "name": "Spaghetti",
        "measurement": "400g",
        "substitution_option": "Bucatini",
        "allergen_info": "Contains gluten",
        "order": 1,
        "created_at": "2026-03-11T14:20:00Z",
        "updated_at": "2026-03-11T14:20:00Z"
      },
      {
        "id": 81,
        "recipe_id": 15,
        "name": "Guanciale",
        "measurement": "150g, cut into strips",
        "substitution_option": "Pancetta",
        "allergen_info": "Pork product",
        "order": 2,
        "created_at": "2026-03-11T14:20:00Z",
        "updated_at": "2026-03-11T14:20:00Z"
      },
      {
        "id": 82,
        "recipe_id": 15,
        "name": "Egg Yolks",
        "measurement": "4 large",
        "substitution_option": null,
        "allergen_info": "Contains eggs",
        "order": 3,
        "created_at": "2026-03-11T14:20:00Z",
        "updated_at": "2026-03-11T14:20:00Z"
      },
      {
        "id": 83,
        "recipe_id": 15,
        "name": "Pecorino Romano",
        "measurement": "120g, finely grated",
        "substitution_option": null,
        "allergen_info": "Contains dairy",
        "order": 4,
        "created_at": "2026-03-11T14:20:00Z",
        "updated_at": "2026-03-11T14:20:00Z"
      }
    ]
  }
}
```

**Figure 13. Recipe Update Success Response**

### Transaction Flow
1. **Authorization**: Verifies user owns the recipe
2. **Validation**: Validates all updated fields
3. **Image Handling**: Replaces old image file if new one provided
4. **Recipe Update**: Modifies recipe fields
5. **Bulk Delete**: Removes all existing ingredients
6. **Bulk Insert**: Creates all new ingredients
7. **Atomic Commit**: Saves all changes in single transaction
8. **Rollback on Failure**: Restores original recipe and ingredients if error occurs

---

## Transaction 5: Saved Recipe Toggle (Many-to-Many)

### Description
This transaction demonstrates managing many-to-many relationships through a junction table. It toggles the saved status of a recipe for a user by either inserting or deleting a record in the junction table.

### Code Snippet

```python
# CRUD CREATE/DELETE: toggles saved status in many-to-many relationship
@saved_bp.route('/recipes/<int:recipe_id>/save', methods=['POST'])
@login_required
def toggle(recipe_id):
    try:
        recipe = Recipe.query.get(recipe_id)
        if not recipe:
            return jsonify({'success': False, 'message': 'Recipe not found.'}), 404

        # TRANSACTION START: Toggle save status in junction table
        # Check if save relationship already exists
        existing = db.session.query(saved_recipes_table).filter(
            saved_recipes_table.c.user_id == current_user.id,
            saved_recipes_table.c.recipe_id == recipe_id,
        ).first()

        if existing:
            # DELETE: Remove record from junction table (unsave)
            db.session.execute(
                saved_recipes_table.delete().where(
                    (saved_recipes_table.c.user_id == current_user.id) &
                    (saved_recipes_table.c.recipe_id == recipe_id)
                )
            )
            db.session.commit()  # TRANSACTION COMMIT
            return jsonify({
                'success': True,
                'message': 'Recipe removed from saved recipes.',
                'data': {'isSaved': False}
            })
        else:
            # INSERT: Add record to junction table (save)
            db.session.execute(
                saved_recipes_table.insert().values(
                    user_id=current_user.id,
                    recipe_id=recipe_id
                )
            )
            db.session.commit()  # TRANSACTION COMMIT
            return jsonify({
                'success': True,
                'message': 'Recipe saved successfully!',
                'data': {'isSaved': True}
            })
            
    except Exception as e:
        db.session.rollback()  # TRANSACTION ROLLBACK
        return jsonify({'success': False, 
                       'message': 'Failed to update saved status.'}), 500
```

**Figure 14. Saved Recipe Toggle Transaction Code**

### Sample Output (Saving Recipe)

```json
{
  "success": true,
  "message": "Recipe saved successfully!",
  "data": {
    "isSaved": true
  }
}
```

**Figure 15. Recipe Saved Success Response**

### Sample Output (Unsaving Recipe)

```json
{
  "success": true,
  "message": "Recipe removed from saved recipes.",
  "data": {
    "isSaved": false
  }
}
```

**Figure 16. Recipe Unsaved Success Response**

### Transaction Flow
1. **Recipe Validation**: Verifies recipe exists
2. **Relationship Query**: Checks if user has already saved the recipe
3. **Conditional Operation**:
   - If exists: DELETE from junction table (unsave)
   - If not exists: INSERT into junction table (save)
4. **Atomic Commit**: Saves change to database
5. **Response**: Returns new saved status
6. **Rollback on Error**: Reverts operation if transaction fails

---

## Transaction Properties (ACID)

### Atomicity
All transactions in the ProCook application are atomic. Either all operations within a transaction complete successfully, or none of them do. This is enforced by:
- `db.session.commit()` - Commits all changes
- `db.session.rollback()` - Reverts all changes on error

**Example**: When creating a recipe with 5 ingredients, if ingredient #4 fails validation, the entire transaction (recipe + all ingredients) is rolled back.

### Consistency
Database constraints ensure consistency:
- Foreign key relationships (CASCADE DELETE)
- Unique constraints (email uniqueness)
- NOT NULL constraints
- Check constraints (rating 1-5)

### Isolation
Flask-SQLAlchemy uses database isolation levels to prevent concurrent transaction conflicts. Each transaction operates independently until committed.

### Durability
Once committed, transactions are permanently stored in the PostgreSQL database and survive system failures through write-ahead logging (WAL).

---

## Error Handling and Rollback

### Code Pattern

```python
try:
    # Transaction operations
    db.session.add(entity)
    db.session.commit()
    return success_response
except Exception as e:
    db.session.rollback()  # Automatically reverts all changes
    return error_response
```

**Figure 17. Standard Transaction Error Handling Pattern**

### Example Error Response

```json
{
  "success": false,
  "message": "Failed to create recipe. Please try again.",
  "errors": {
    "title": ["Recipe title must be at least 3 characters."],
    "ingredients": ["At least one ingredient is required."]
  }
}
```

**Figure 18. Transaction Validation Error Response**

---

## Summary

The ProCook Recipe Management System demonstrates robust transactional operations with:

1. **Single-table transactions**: User registration with encrypted passwords
2. **Multi-table transactions**: Recipe creation with related ingredients
3. **UPSERT operations**: Rating creation or update based on existence
4. **Complex updates**: Recipe modification with complete ingredient replacement
5. **Many-to-many operations**: Saved recipe toggle through junction table

All transactions follow ACID principles and include proper error handling with automatic rollback mechanisms to ensure data integrity and consistency.

---

## Running the Application

The application runs on Flask development server:

```
Flask app 'backend.app'
Debug mode: on
Running on http://127.0.0.1:5000
```

**Figure 19. Application Server Status**

Access the API endpoints at `http://127.0.0.1:5000/api/` for testing transactional operations.
