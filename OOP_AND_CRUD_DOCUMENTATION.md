# ProCook Python - OOP & CRUD Documentation

## Table of Contents
1. [Object-Oriented Programming (OOP)](#object-oriented-programming-oop)
2. [CRUD Operations](#crud-operations)
3. [File Structure](#file-structure)

---

## Object-Oriented Programming (OOP)

### 📁 File: `backend/models.py`

This file contains all the database models using **SQLAlchemy ORM** (Object-Relational Mapping).

---

### 1. **User Model** 
**Class**: `User(UserMixin, db.Model)`

#### Inheritance
- `UserMixin` - Provides Flask-Login methods (is_authenticated, is_active, get_id)
- `db.Model` - SQLAlchemy base model class

#### Attributes (Properties)
```python
id                  : Integer (Primary Key)
name                : String(255)
email               : String(255) - Unique
email_verified_at   : DateTime (nullable)
password            : String(255) - Hashed
remember_token      : String(100) (nullable)
created_at          : DateTime
updated_at          : DateTime
```

#### Relationships
```python
recipes     : One-to-Many with Recipe
comments    : One-to-Many with Comment
ratings     : One-to-Many with Rating
saved       : Many-to-Many with Recipe (through saved_recipes table)
```

#### Methods
```python
set_password(password)
    - Hashes password using werkzeug.security
    - Stores hashed password in database
    
check_password(password)
    - Verifies password against stored hash
    - Returns: Boolean
    
to_dict()
    - Converts User object to dictionary
    - Returns: Dict with id, name, email, timestamps
```

#### OOP Concepts Used
- **Encapsulation**: Password is private, accessed via methods
- **Data Hiding**: Password hash not exposed in to_dict()
- **Polymorphism**: to_dict() can be overridden

---

### 2. **Recipe Model**
**Class**: `Recipe(db.Model)`

#### Inheritance
- `db.Model` - SQLAlchemy base model class

#### Attributes
```python
id                  : Integer (Primary Key)
user_id             : Integer (Foreign Key → users.id)
title               : String(255)
short_description   : Text
image               : String(255) (nullable)
cuisine_type        : String(100)
category            : String(100)
prep_time           : Integer
cook_time           : Integer
total_time          : Integer
serving_size        : Integer
preparation_notes   : Text (nullable)
created_at          : DateTime
updated_at          : DateTime
```

#### Relationships
```python
user        : Many-to-One with User
ingredients : One-to-Many with Ingredient (cascade delete)
comments    : One-to-Many with Comment (cascade delete)
ratings     : One-to-Many with Rating (cascade delete)
saved_by    : Many-to-Many with User (through saved_recipes)
```

#### Methods
```python
average_rating()
    - Calculates average rating from all ratings
    - Uses SQLAlchemy aggregate function
    - Returns: Float (rounded to 1 decimal)
    
ratings_count()
    - Counts total ratings for recipe
    - Returns: Integer
    
to_dict(include_ingredients=False, include_user=True)
    - Converts Recipe to dictionary
    - Parameters control related data inclusion
    - Returns: Dict with recipe data
```

#### OOP Concepts Used
- **Composition**: Recipe contains Ingredients
- **Aggregation**: Recipe references User
- **Method Overloading**: to_dict() with optional parameters
- **Database Indexes**: Optimized queries on user_id, title

---

### 3. **Ingredient Model**
**Class**: `Ingredient(db.Model)`

#### Attributes
```python
id                  : Integer (Primary Key)
recipe_id           : Integer (Foreign Key → recipes.id)
name                : String(255)
measurement         : String(100)
substitution_option : String(255) (nullable)
allergen_info       : String(255) (nullable)
order               : Integer
created_at          : DateTime
updated_at          : DateTime
```

#### Relationships
```python
recipe : Many-to-One with Recipe
```

#### Methods
```python
to_dict()
    - Serializes Ingredient to dictionary
    - Returns: Dict with all ingredient fields
```

#### OOP Concepts Used
- **Tight Coupling**: Ingredient depends on Recipe (cascade delete)
- **Ordered Collection**: `order` field maintains sequence

---

### 4. **Comment Model**
**Class**: `Comment(db.Model)`

#### Attributes
```python
id          : Integer (Primary Key)
recipe_id   : Integer (Foreign Key → recipes.id)
user_id     : Integer (Foreign Key → users.id)
parent_id   : Integer (Foreign Key → comments.id, nullable)
comment     : Text
created_at  : DateTime
updated_at  : DateTime
```

#### Relationships
```python
recipe  : Many-to-One with Recipe
user    : Many-to-One with User
parent  : Self-referential (for nested comments)
replies : One-to-Many with Comment (nested structure)
```

#### Methods
```python
to_dict(include_replies=False)
    - Serializes Comment with optional nested replies
    - Supports recursive relationships
    - Returns: Dict with comment and user data
```

#### OOP Concepts Used
- **Self-Reference**: Comments can reply to comments
- **Recursion**: Nested comment structure
- **Tree Structure**: Parent-child hierarchy

---

### 5. **Rating Model**
**Class**: `Rating(db.Model)`

#### Attributes
```python
id          : Integer (Primary Key)
recipe_id   : Integer (Foreign Key → recipes.id)
user_id     : Integer (Foreign Key → users.id)
rating      : SmallInteger (1-5)
created_at  : DateTime
updated_at  : DateTime
```

#### Constraints
- **Unique Constraint**: One rating per user per recipe
- **Database Index**: Optimized on recipe_id

#### Methods
```python
to_dict()
    - Converts Rating to dictionary
    - Returns: Dict with rating data
```

#### OOP Concepts Used
- **Business Logic**: Rating validation (1-5)
- **Data Integrity**: Unique constraint enforced

---

### 6. **Category Model** (Unused in current app)
**Class**: `Category(db.Model)`

#### Attributes
```python
id          : Integer (Primary Key)
name        : String(255)
slug        : String(255) - Unique
description : Text (nullable)
icon        : String(255) (nullable)
order       : Integer
created_at  : DateTime
updated_at  : DateTime
```

#### Relationships
```python
products : One-to-Many with Product
```

---

### 7. **Product Model** (Unused in current app)
**Class**: `Product(db.Model)`

#### Attributes
```python
id          : Integer (Primary Key)
category_id : Integer (Foreign Key)
name        : String(255)
slug        : String(255) - Unique
description : Text
features    : Text (nullable)
price       : Numeric(10,2)
sale_price  : Numeric(10,2) (nullable)
sku         : String(255) - Unique
stock       : Integer
image       : String(255) (nullable)
is_featured : Boolean
is_active   : Boolean
created_at  : DateTime
updated_at  : DateTime
```

---

### 8. **Association Table**
**Table**: `saved_recipes`

#### Structure
```python
id          : Integer (Primary Key)
user_id     : Integer (Foreign Key → users.id)
recipe_id   : Integer (Foreign Key → recipes.id)
created_at  : DateTime
updated_at  : DateTime
```

#### Constraints
- **Unique Constraint**: One save per user per recipe

#### OOP Concepts
- **Many-to-Many Relationship**: Users can save multiple recipes
- **Junction Table**: Implements association pattern

---

## CRUD Operations

### 📁 File: `backend/routes/auth.py`

#### **User Authentication & Profile Management**

### 1. **Register (CREATE)**
**Endpoint**: `POST /api/register`

**OOP Concepts**:
- Object instantiation: `user = User(name=name, email=email)`
- Encapsulation: `user.set_password(password)`
- Validation: Helper methods `validate_email()`, `validate_password()`

**Process**:
1. Validate input (name, email, password)
2. Create new User object
3. Hash password using `set_password()`
4. Save to database
5. Login user with Flask-Login

**Business Rules**:
- Name: 2-255 characters, letters and spaces only
- Email: Valid format, unique
- Password: 8+ chars, uppercase, lowercase, digit

---

### 2. **Login (READ)**
**Endpoint**: `POST /api/login`

**OOP Concepts**:
- Querying: `User.query.filter_by(email=email).first()`
- Method invocation: `user.check_password(password)`

**Process**:
1. Find user by email
2. Verify password hash
3. Create session with Flask-Login

---

### 3. **Logout**
**Endpoint**: `POST /api/logout`
**Auth Required**: Yes

**Process**:
1. Clear Flask-Login session
2. Clear session data

---

### 4. **Get Current User (READ)**
**Endpoint**: `GET /api/user`
**Auth Required**: Yes

**OOP Concepts**:
- Serialization: `current_user.to_dict()`

---

### 5. **Get Profile (READ)**
**Endpoint**: `GET /api/profile`
**Auth Required**: Yes

**OOP Concepts**:
- Lazy loading relationships
- Aggregation: `user.recipes.count()`

**Returns**:
- User data
- Statistics (recipes, comments, ratings, saved)

---

### 6. **Update Profile (UPDATE)**
**Endpoint**: `PUT /api/profile`
**Auth Required**: Yes

**OOP Concepts**:
- Object modification
- Validation before update

**Process**:
1. Validate new name and email
2. Check email uniqueness
3. Update user object
4. Commit to database

---

### 7. **Change Password (UPDATE)**
**Endpoint**: `PUT /api/profile/password`
**Auth Required**: Yes

**Process**:
1. Verify current password
2. Validate new password
3. Hash and save new password

---

### 8. **My Recipes (READ)**
**Endpoint**: `GET /api/my-recipes`
**Auth Required**: Yes

**OOP Concepts**:
- Filtering: `Recipe.query.filter_by(user_id=current_user.id)`
- Ordering: `order_by(Recipe.created_at.desc())`

---

### 📁 File: `backend/routes/recipes.py`

#### **Recipe Management**

### 1. **List All Recipes (READ)**
**Endpoint**: `GET /api/recipes`

**OOP Concepts**:
- Query building
- Eager loading: `db.joinedload(Recipe.user)`
- List comprehension: `[r.to_dict() for r in recipes]`

**Business Logic**:
- Optional limit parameter (max 100)
- Ordered by creation date (newest first)
- Includes user information

---

### 2. **Show Recipe (READ)**
**Endpoint**: `GET /api/recipes/:id`

**OOP Concepts**:
- Single object retrieval: `Recipe.query.get(recipe_id)`
- Related data loading

**Returns**:
- Recipe with ingredients and user

---

### 3. **Create Recipe (CREATE)**
**Endpoint**: `POST /api/recipes`
**Auth Required**: Yes

**OOP Concepts**:
- Object instantiation
- Related object creation (ingredients)
- File handling: `save_image()`
- Transaction management

**Process**:
1. Validate recipe data
2. Handle image upload
3. Create Recipe object
4. Flush to get recipe.id
5. Create related Ingredient objects
6. Commit transaction

**Validation Rules**:
- Title: 3-255 characters
- Description: 10-500 characters
- Prep/cook time: 0-1440 minutes
- Serving size: 1-100
- Ingredients: 1-50 required
- Image: jpeg, jpg, png, gif, webp

**File Handling**:
- Uploads stored in `uploads/recipes/`
- Filename: `{timestamp}_{uuid}.{extension}`

---

### 4. **Update Recipe (UPDATE)**
**Endpoint**: `PUT /api/recipes/:id`
**Auth Required**: Yes (Owner only)

**OOP Concepts**:
- Authorization check: `recipe.user_id != current_user.id`
- Object modification
- Related object replacement

**Process**:
1. Find recipe
2. Check ownership
3. Validate new data
4. Update recipe fields
5. Delete old image if new uploaded
6. Replace all ingredients
7. Commit changes

---

### 5. **Delete Recipe (DELETE)**
**Endpoint**: `DELETE /api/recipes/:id`
**Auth Required**: Yes (Owner only)

**OOP Concepts**:
- Cascade delete (ingredients, comments, ratings deleted automatically)
- File cleanup

**Process**:
1. Find recipe
2. Check ownership
3. Delete image file
4. Delete recipe (cascades to related data)

---

### 📁 File: `backend/routes/comments.py`

#### **Comment Management**

### 1. **List Comments (READ)**
**Endpoint**: `GET /api/recipes/:id/comments`

**OOP Concepts**:
- Hierarchical data: Parent-child relationships
- Recursive serialization: `to_dict(include_replies=True)`

**Returns**:
- Top-level comments with nested replies

---

### 2. **Create Comment (CREATE)**
**Endpoint**: `POST /api/recipes/:id/comments`
**Auth Required**: Yes

**OOP Concepts**:
- Optional parent reference (for replies)
- Validation

**Business Rules**:
- Comment: 1-1000 characters
- Parent comment must exist in same recipe

---

### 3. **Update Comment (UPDATE)**
**Endpoint**: `PUT /api/recipes/:id/comments/:comment_id`
**Auth Required**: Yes (Author only)

**Process**:
1. Find comment
2. Check ownership
3. Validate new text
4. Update and save

---

### 4. **Delete Comment (DELETE)**
**Endpoint**: `DELETE /api/recipes/:id/comments/:comment_id`
**Auth Required**: Yes (Author only)

**OOP Concepts**:
- Cascade delete (replies deleted automatically)

---

### 📁 File: `backend/routes/ratings.py`

#### **Rating Management**

### 1. **Submit/Update Rating (CREATE/UPDATE)**
**Endpoint**: `POST /api/recipes/:id/rating`
**Auth Required**: Yes

**OOP Concepts**:
- Upsert pattern (update or insert)
- Business rule: Can't rate own recipe

**Process**:
1. Check recipe exists
2. Prevent self-rating
3. Validate rating (1-5)
4. Find existing rating or create new
5. Update rating value
6. Return updated statistics

---

### 2. **Get User Rating (READ)**
**Endpoint**: `GET /api/recipes/:id/rating`
**Auth Required**: Yes

**Returns**:
- User's rating (if exists)
- Average rating
- Total ratings count

---

### 3. **Get Public Rating (READ)**
**Endpoint**: `GET /api/recipes/:id/rating/public`

**OOP Concepts**:
- Aggregate functions: `db.func.avg()`

---

### 4. **Delete Rating (DELETE)**
**Endpoint**: `DELETE /api/recipes/:id/rating`
**Auth Required**: Yes

**Process**:
1. Find user's rating
2. Delete rating
3. Return updated statistics

---

### 📁 File: `backend/routes/saved_recipes.py`

#### **Saved Recipes (Bookmarks)**

### 1. **List Saved Recipes (READ)**
**Endpoint**: `GET /api/saved-recipes`
**Auth Required**: Yes

**OOP Concepts**:
- Many-to-many relationship access
- Ordering by association table field

---

### 2. **Check if Saved (READ)**
**Endpoint**: `GET /api/recipes/:id/saved`
**Auth Required**: Yes

**Returns**:
- Boolean indicating if recipe is saved by user

---

### 3. **Toggle Save/Unsave (CREATE/DELETE)**
**Endpoint**: `POST /api/recipes/:id/save`
**Auth Required**: Yes

**OOP Concepts**:
- Toggle pattern (add or remove)
- Direct table manipulation

**Process**:
1. Check if already saved
2. If saved: Remove from association table
3. If not saved: Add to association table

---

## File Structure

### Core Application Files

```
backend/
├── __init__.py           # Package initialization
├── app.py               # Flask app factory
├── config.py            # Configuration classes
├── models.py            # ORM models (OOP classes)
└── routes/
    ├── __init__.py      # Blueprint registration
    ├── auth.py          # User authentication CRUD
    ├── recipes.py       # Recipe CRUD
    ├── comments.py      # Comment CRUD
    ├── ratings.py       # Rating CRUD
    └── saved_recipes.py # Saved recipes CRUD
```

### Database Diagram

```
┌─────────────┐         ┌─────────────┐
│    users    │◄────────┤   recipes   │
└──────┬──────┘         └──────┬──────┘
       │                       │
       │                       │
       ├───────┐         ┌─────┴─────┐
       │       │         │           │
       ▼       ▼         ▼           ▼
  ┌─────────┐ ┌───────┐ ┌──────────┐ ┌──────────┐
  │comments │ │ratings│ │ingredients│ │saved_    │
  └─────────┘ └───────┘ └──────────┘ │recipes   │
                                      │(junction)│
                                      └──────────┘
```

---

## OOP Design Patterns Used

### 1. **Active Record Pattern**
- Models are both data and behavior
- Example: `user.set_password()`, `recipe.average_rating()`

### 2. **Factory Pattern**
- Flask app creation: `create_app()`
- Blueprint registration

### 3. **Repository Pattern**
- SQLAlchemy Query interface
- Example: `User.query.filter_by()`

### 4. **Proxy Pattern**
- Flask-Login's `current_user`
- Lazy-loaded relationships

### 5. **Strategy Pattern**
- `to_dict()` methods with different serialization strategies

### 6. **Decorator Pattern**
- `@login_required`
- `@route` decorators

---

## Key OOP Principles Applied

### 1. **Encapsulation**
- Password hashing hidden in `set_password()`
- Database operations encapsulated in models

### 2. **Inheritance**
- `User(UserMixin, db.Model)`
- All models inherit from `db.Model`

### 3. **Polymorphism**
- All models implement `to_dict()` differently
- Relationship loading variations

### 4. **Abstraction**
- ORM abstracts SQL queries
- Blueprints abstract routing

### 5. **Composition**
- Recipe contains Ingredients
- Comment contains nested Comments

### 6. **Separation of Concerns**
- Models: Data structure
- Routes: Business logic
- Validation: Separate helper functions

---

## Security Features (OOP Implementation)

### 1. **Password Hashing**
```python
def set_password(self, password):
    self.password = generate_password_hash(password)
```

### 2. **Authorization Checks**
```python
if recipe.user_id != current_user.id:
    return jsonify({'error': 'Unauthorized'}), 403
```

### 3. **Input Validation**
- Email format validation
- Password strength validation
- Data type validation

### 4. **SQL Injection Prevention**
- ORM parameterized queries
- No raw SQL strings with user input

---

## Best Practices Demonstrated

1. **DRY (Don't Repeat Yourself)**
   - Validation helpers reused
   - `to_dict()` methods standardized

2. **Single Responsibility Principle**
   - Each route handles one operation
   - Models only handle data

3. **Error Handling**
   - Try-catch blocks in all routes
   - Transaction rollback on errors

4. **RESTful API Design**
   - Standard HTTP methods
   - Consistent response format

5. **Database Optimization**
   - Indexes on frequently queried fields
   - Eager loading to prevent N+1 queries

---

## Summary

This ProCook application demonstrates comprehensive use of:
- **OOP**: Classes, inheritance, encapsulation, polymorphism
- **CRUD**: Full Create, Read, Update, Delete operations
- **Database Design**: Normalized tables, relationships, constraints
- **Design Patterns**: Factory, Repository, Active Record, Decorator
- **Security**: Authentication, authorization, password hashing
- **Best Practices**: Validation, error handling, RESTful API

---

**Generated**: March 5, 2026  
**Project**: ProCook - Python Recipe Manager  
**Framework**: Flask + SQLAlchemy + Flask-Login
