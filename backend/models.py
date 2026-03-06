# ═══════════════════════════════════════════════════════════════════════════
# DATABASE MODELS FILE - Demonstrates OOP (Object-Oriented Programming)
# ═══════════════════════════════════════════════════════════════════════════
# This file defines the database structure using SQLAlchemy ORM (Object-Relational Mapping)
# It connects to: backend/app.py (initialization), all route files (CRUD operations)
# ═══════════════════════════════════════════════════════════════════════════

# Import datetime for handling timestamp fields (created_at, updated_at)
from datetime import datetime

# Import SQLAlchemy - the ORM that allows us to interact with PostgreSQL database using Python classes
# Connects to: backend/app.py where db.init_app(app) initializes the database connection
from flask_sqlalchemy import SQLAlchemy

# Import UserMixin - provides default implementations for Flask-Login user management
# This is OOP INHERITANCE - User class will inherit authentication methods from UserMixin
# Connects to: backend/app.py where LoginManager uses these methods for user session management
from flask_login import UserMixin

# Import password hashing utilities for secure password storage
# Used in User class methods for OOP ENCAPSULATION of password security logic
from werkzeug.security import generate_password_hash, check_password_hash

# Create SQLAlchemy database instance - this is the main database object
# This will be initialized in backend/app.py with db.init_app(app)
# All models will use this 'db' object to define tables and perform transactions
db = SQLAlchemy()


# ═══════════════════════════════════════════════════════════════════════════
# MANY-TO-MANY ASSOCIATION TABLE: saved_recipes
# ═══════════════════════════════════════════════════════════════════════════
# This is a JOIN TABLE that implements a MANY-TO-MANY relationship between Users and Recipes
# - One user can save many recipes
# - One recipe can be saved by many users
# This demonstrates DATABASE DESIGN PATTERNS for complex relationships
# Connects to: User model (saved relationship), Recipe model (saved_by relationship)
# Used in: backend/routes/saved_recipes.py for CRUD operations on saved recipes
# ═══════════════════════════════════════════════════════════════════════════

saved_recipes = db.Table(
    'saved_recipes',  # Table name in PostgreSQL database
    
    # Primary key - unique identifier for each save action
    db.Column('id', db.Integer, primary_key=True),
    
    # Foreign key to users table - CASCADE delete means if user is deleted, their saved recipes are removed
    # This demonstrates REFERENTIAL INTEGRITY - maintaining consistent relationships between tables
    db.Column('user_id', db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
    
    # Foreign key to recipes table - CASCADE delete means if recipe is deleted, all saves are removed
    # This is a TRANSACTIONAL CONSTRAINT ensuring data consistency
    db.Column('recipe_id', db.Integer, db.ForeignKey('recipes.id', ondelete='CASCADE'), nullable=False),
    
    # Timestamp when recipe was saved - tracks when the many-to-many relationship was created
    db.Column('created_at', db.DateTime, default=datetime.utcnow),
    
    # Timestamp when save was last modified - auto-updates on any change (onupdate parameter)
    db.Column('updated_at', db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow),
    
    # Unique constraint prevents duplicate saves - a user cannot save the same recipe twice
    # This is a DATABASE CONSTRAINT ensuring business logic at the database level
    db.UniqueConstraint('user_id', 'recipe_id', name='uq_user_recipe_saved'),
)


# ═══════════════════════════════════════════════════════════════════════════
# USER MODEL CLASS - Core OOP Principles Demonstration
# ═══════════════════════════════════════════════════════════════════════════
# This class demonstrates:
# 1. OOP INHERITANCE: Inherits from UserMixin (Flask-Login) and db.Model (SQLAlchemy)
# 2. OOP ENCAPSULATION: Password hashing is hidden inside methods (set_password, check_password)
# 3. OOP ABSTRACTION: Complex database operations are abstracted into simple method calls
# 4. RELATIONSHIPS: One-to-Many relationships with Recipe, Comment, Rating
# 5. Many-to-Many relationship with Recipe through saved_recipes table
#
# Connects to:
# - backend/app.py: LoginManager uses this for authentication (@login_manager.user_loader)
# - backend/routes/auth.py: User registration, login, profile (CREATE, READ, UPDATE operations)
# - backend/routes/recipes.py: Links recipes to their creators (READ operations)
# - backend/routes/comments.py: Links comments to users (CREATE, READ operations)
# - backend/routes/ratings.py: Links ratings to users (CREATE, READ, DELETE operations)
# - backend/routes/saved_recipes.py: Manages saved recipes (CREATE, READ, DELETE operations)
# ═══════════════════════════════════════════════════════════════════════════

class User(UserMixin, db.Model):
    """
    User Model - Represents application users in the database
    
    OOP INHERITANCE EXPLANATION:
    - UserMixin: Provides is_authenticated, is_active, is_anonymous, get_id() methods
    - db.Model: Base class for all SQLAlchemy models, provides database functionality
    """
    
    # Define the PostgreSQL table name for this model
    __tablename__ = 'users'

    # ═══ PRIMARY KEY ═══
    # Auto-incrementing unique identifier for each user (PRIMARY KEY constraint)
    id = db.Column(db.Integer, primary_key=True)
    
    # ═══ USER DATA FIELDS ═══
    # User's full name - String with max 255 characters, cannot be null
    name = db.Column(db.String(255), nullable=False)
    
    # User's email address - String with UNIQUE constraint (no duplicates allowed)
    # This enforces business rule: one email = one account
    email = db.Column(db.String(255), unique=True, nullable=False)
    
    # Email verification timestamp - nullable (null = not verified yet)
    email_verified_at = db.Column(db.DateTime, nullable=True)
    
    # Hashed password - NEVER stores plain text for SECURITY
    # This demonstrates ENCAPSULATION: password is hidden, only hash is stored
    password = db.Column(db.String(255), nullable=False)
    
    # Token for "remember me" functionality in Flask-Login sessions
    remember_token = db.Column(db.String(100), nullable=True)
    
    # ═══ TIMESTAMP FIELDS (Audit Trail) ═══
    # Auto-populated when user registers (CREATE operation timestamp)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Auto-updated whenever user data changes (UPDATE operation timestamp)
    # The 'onupdate' parameter makes this automatic
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ═══════════════════════════════════════════════════════════════════════════
    # OOP RELATIONSHIPS - Defining connections to other models
    # ═══════════════════════════════════════════════════════════════════════════
    # These demonstrate OOP COMPOSITION: User "has many" recipes, comments, ratings
    # 'backref' creates reverse relationship (recipe.user gives the User object)
    # 'lazy=dynamic' returns a query object instead of loading all records immediately (PERFORMANCE OPTIMIZATION)
    # 'foreign_keys' explicitly specifies which column links to this table
    
    # ONE-TO-MANY: One user can create many recipes
    # Used in: backend/routes/recipes.py for filtering user's recipes
    # Used in: backend/routes/auth.py for displaying recipe count in profile
    recipes = db.relationship('Recipe', backref='user', lazy='dynamic',
                              foreign_keys='Recipe.user_id')
    
    # ONE-TO-MANY: One user can write many comments
    # Used in: backend/routes/comments.py for displaying commenter name
    # Used in: backend/routes/auth.py for displaying comment count in profile
    comments = db.relationship('Comment', backref='user', lazy='dynamic',
                               foreign_keys='Comment.user_id')
    
    # ONE-TO-MANY: One user can give many ratings
    # Used in: backend/routes/ratings.py for checking if user already rated a recipe
    # Used in: backend/routes/auth.py for displaying rating count in profile
    ratings = db.relationship('Rating', backref='user', lazy='dynamic',
                              foreign_keys='Rating.user_id')
    
    # MANY-TO-MANY: User can save many recipes, Recipe can be saved by many users
    # 'secondary=saved_recipes' specifies the association table to use
    # 'backref=saved_by' allows recipe.saved_by to get all users who saved it
    # Used in: backend/routes/saved_recipes.py for managing saved recipes (CRUD operations)
    saved = db.relationship('Recipe', secondary=saved_recipes, lazy='dynamic',
                            backref=db.backref('saved_by', lazy='dynamic'))

    # ═══════════════════════════════════════════════════════════════════════════
    # OOP METHODS - Encapsulating Business Logic
    # ═══════════════════════════════════════════════════════════════════════════
    
    def set_password(self, password):
        """
        OOP ENCAPSULATION: Hides password hashing complexity
        
        Takes plain text password and stores it as a secure hash
        This method is called during:
        - User registration (CREATE operation in backend/routes/auth.py register())
        - Password change (UPDATE operation in backend/routes/auth.py change_password())
        
        Security note: Uses werkzeug.security which implements bcrypt hashing
        The original password cannot be recovered from the hash (one-way function)
        """
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """
        OOP ENCAPSULATION: Hides password verification complexity
        
        Compares plain text password against stored hash
        Returns True if password matches, False otherwise
        
        This method is called during:
        - User login (READ operation in backend/routes/auth.py login())
        - Password change verification (READ operation in backend/routes/auth.py change_password())
        
        Connects to: backend/routes/auth.py for authentication logic
        """
        return check_password_hash(self.password, password)

    def to_dict(self):
        """
        OOP ABSTRACTION: Converts database model to JSON-serializable dictionary
        
        This method implements the DATA TRANSFER OBJECT (DTO) pattern
        Provides a safe way to send user data to frontend without exposing sensitive fields
        Notice: password field is NOT included for SECURITY
        
        This method is called in:
        - backend/routes/auth.py: register(), login(), get_user(), profile(), update_profile()
        - backend/routes/recipes.py: Returns user info with recipes (READ operations)
        
        Returns: Dictionary that can be converted to JSON for API responses
        """
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            # ISO 8601 format with 'Z' suffix indicates UTC timezone
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None,
            'updated_at': self.updated_at.isoformat() + 'Z' if self.updated_at else None,
        }


# ═══════════════════════════════════════════════════════════════════════════
# RECIPE MODEL CLASS - Central Entity with Complex Relationships
# ═══════════════════════════════════════════════════════════════════════════
# This class demonstrates:
# 1. OOP INHERITANCE: Inherits from db.Model (SQLAlchemy base)
# 2. ONE-TO-MANY RELATIONSHIPS: Has many Ingredients, Comments, Ratings
# 3. MANY-TO-ONE RELATIONSHIP: Belongs to one User (creator)
# 4. CASCADE OPERATIONS: Demonstrates TRANSACTIONAL integrity with cascade deletes
# 5. DATABASE INDEXING: Performance optimization with indexed columns
# 6. AGGREGATE FUNCTIONS: Calculates average rating using SQL functions
#
# Connects to:
# - backend/routes/recipes.py: Full CRUD operations (CREATE, READ, UPDATE, DELETE)
# - backend/routes/comments.py: Recipes have comments (READ operations)
# - backend/routes/ratings.py: Recipes have ratings (CREATE, READ operations)
# - backend/routes/saved_recipes.py: Recipes can be saved (CREATE, DELETE operations)
# - backend/routes/auth.py: Display user's recipes in profile
# ═══════════════════════════════════════════════════════════════════════════

class Recipe(db.Model):
    """
    Recipe Model - Represents cooking recipes created by users
    
    This is a CENTRAL ENTITY in the database - most other tables reference recipes
    Demonstrates REFERENTIAL INTEGRITY through foreign keys and CASCADE operations
    """
    
    # Define the PostgreSQL table name for this model
    __tablename__ = 'recipes'

    # ═══ PRIMARY KEY ═══
    # Auto-incrementing unique identifier for each recipe
    id = db.Column(db.Integer, primary_key=True)
    
    # ═══ FOREIGN KEY (MANY-TO-ONE relationship with User) ═══
    # Links recipe to its creator (User)
    # 'SET NULL' means if user is deleted, recipe remains but user_id becomes null
    # This preserves data even when user accounts are removed
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    
    # ═══ RECIPE INFORMATION FIELDS ═══
    # Recipe title - required field, searchable (see __table_args__ for index)
    title = db.Column(db.String(255), nullable=False)
    
    # Brief description shown in recipe listings
    short_description = db.Column(db.Text, nullable=False)
    
    # Path to recipe image stored in backend/uploads/recipes/ directory
    # Image upload handled in backend/routes/recipes.py using save_image() function
    image = db.Column(db.String(255), nullable=True)
    
    # Category fields for filtering and organizing recipes
    cuisine_type = db.Column(db.String(100), nullable=False)  # e.g., Italian, Chinese, Mexican
    category = db.Column(db.String(100), nullable=False)       # e.g., Breakfast, Dessert, Main Course
    
    # ═══ TIME TRACKING FIELDS ═══
    # All time values stored in minutes
    prep_time = db.Column(db.Integer, nullable=False)     # Preparation time
    cook_time = db.Column(db.Integer, nullable=False)     # Cooking time  
    total_time = db.Column(db.Integer, nullable=False)    # prep_time + cook_time (calculated)
    
    # Number of servings this recipe makes
    serving_size = db.Column(db.Integer, nullable=False)
    
    # Detailed cooking instructions/steps
    preparation_notes = db.Column(db.Text, nullable=True)
    
    # ═══ AUDIT TRAIL TIMESTAMPS ═══
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ═══════════════════════════════════════════════════════════════════════════
    # OOP RELATIONSHIPS - Defining connections to other models
    # ═══════════════════════════════════════════════════════════════════════════
    
    # ONE-TO-MANY: Recipe has many ingredients
    # 'lazy=joined' loads ingredients automatically when recipe is loaded (EAGER LOADING)
    # 'cascade=all, delete-orphan' implements TRANSACTIONAL INTEGRITY:
    #   - When recipe is deleted, all its ingredients are automatically deleted
    #   - When ingredient is removed from recipe, it's deleted from database
    # 'order_by' ensures ingredients are returned in the correct order
    # Used in: backend/routes/recipes.py for displaying recipe details (READ operations)
    ingredients = db.relationship('Ingredient', backref='recipe', lazy='joined',
                                  cascade='all, delete-orphan',
                                  order_by='Ingredient.order')
    
    # ONE-TO-MANY: Recipe has many comments
    # 'lazy=dynamic' returns a query object for PERFORMANCE (doesn't load all comments immediately)
    # 'cascade=all, delete-orphan' means deleting recipe deletes all comments
    # Used in: backend/routes/comments.py for CRUD operations on comments
    comments = db.relationship('Comment', backref='recipe', lazy='dynamic',
                               cascade='all, delete-orphan')
    
    # ONE-TO-MANY: Recipe has many ratings
    # Used in: backend/routes/ratings.py for CRUD operations on ratings
    # Used in: average_rating() and ratings_count() methods below
    ratings = db.relationship('Rating', backref='recipe', lazy='dynamic',
                              cascade='all, delete-orphan')

    # ═══════════════════════════════════════════════════════════════════════════
    # DATABASE OPTIMIZATIONS - Indexes for faster queries
    # ═══════════════════════════════════════════════════════════════════════════
    # __table_args__ defines additional table-level configurations
    # These COMPOSITE INDEXES improve query performance for common searches
    __table_args__ = (
        # Index on (user_id, created_at) speeds up "get user's recipes sorted by date"
        # Used in: backend/routes/auth.py my_recipes() and backend/routes/recipes.py
        db.Index('ix_recipes_user_created', 'user_id', 'created_at'),
        
        # Index on title enables fast text searching by recipe name
        # Used in: Future search functionality
        db.Index('ix_recipes_title', 'title'),
    )

    # ═══════════════════════════════════════════════════════════════════════════
    # OOP METHODS - Business Logic and Data Aggregation
    # ═══════════════════════════════════════════════════════════════════════════
    
    def average_rating(self):
        """
        Calculates average rating for this recipe using SQL AGGREGATE FUNCTION
        
        This demonstrates:
        - DATABASE TRANSACTIONS: Executes SQL query within current session
        - AGGREGATE FUNCTIONS: Uses SQL AVG() function for calculation
        - QUERY OPTIMIZATION: Calculates on database side instead of loading all ratings
        
        Used in: to_dict() method to include rating in API responses
        Connects to: backend/routes/recipes.py (READ operations)
        Connects to: backend/routes/ratings.py (displays updated average after rating)
        
        Returns: Float rounded to 1 decimal place, or 0 if no ratings exist
        """
        # db.session.query() creates a SQL SELECT query
        # db.func.avg() is SQL AVG() aggregate function
        # .filter() adds WHERE clause to query only ratings for this recipe
        # .scalar() returns single value instead of result set
        avg = db.session.query(db.func.avg(Rating.rating)).filter(
            Rating.recipe_id == self.id
        ).scalar()
        return round(float(avg), 1) if avg else 0

    def ratings_count(self):
        """
        Counts total number of ratings for this recipe
        
        This demonstrates:
        - OOP ENCAPSULATION: Hides SQL complexity behind simple method
        - LAZY EVALUATION: Uses dynamic relationship to count without loading records
        
        Used in: to_dict() method to show rating count in API responses
        Connects to: backend/routes/ratings.py for displaying rating statistics
        
        Returns: Integer count of ratings
        """
        # Uses the 'ratings' relationship defined above
        # .count() executes SQL COUNT(*) query - efficient for large datasets
        return self.ratings.count()

    def to_dict(self, include_ingredients=False, include_user=True):
        """
        OOP ABSTRACTION: Converts Recipe model to JSON-serializable dictionary
        
        This implements the DATA TRANSFER OBJECT (DTO) pattern
        Provides flexible serialization with optional related data inclusion
        
        Parameters:
        - include_ingredients: If True, loads and includes ingredient list
        - include_user: If True, includes creator's user information
        
        This method is called in:
        - backend/routes/recipes.py: All CRUD operations (index, show, store, update)
        - backend/routes/auth.py: my_recipes() endpoint
        - backend/routes/saved_recipes.py: Listing saved recipes
        
        Returns: Dictionary ready for JSON API response
        """
        # Build base recipe data dictionary
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'short_description': self.short_description,
            'image': self.image,  # Relative path, served by backend/app.py serve_upload()
            'cuisine_type': self.cuisine_type,
            'category': self.category,
            'prep_time': self.prep_time,
            'cook_time': self.cook_time,
            'total_time': self.total_time,
            'serving_size': self.serving_size,
            'preparation_notes': self.preparation_notes,
            # Calls methods defined above to calculate dynamic values
            'average_rating': self.average_rating(),  # Executes SQL query
            'ratings_count': self.ratings_count(),     # Executes SQL query
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None,
            'updated_at': self.updated_at.isoformat() + 'Z' if self.updated_at else None,
        }
        
        # Conditionally include user data (demonstrates OPTIONAL EAGER LOADING)
        if include_user and self.user:
            # Calls User.to_dict() - demonstrates OOP METHOD CHAINING
            data['user'] = self.user.to_dict()
        elif include_user:
            data['user'] = None  # User was deleted (SET NULL foreign key)
            
        # Conditionally include ingredients (demonstrates RELATIONSHIP TRAVERSAL)
        if include_ingredients:
            # List comprehension calling to_dict() on each ingredient
            # This demonstrates OOP POLYMORPHISM - each model has its own to_dict()
            data['ingredients'] = [i.to_dict() for i in self.ingredients]
            
        return data


# ═══════════════════════════════════════════════════════════════════════════
# INGREDIENT MODEL CLASS - Child Entity with Ordered List Pattern
# ═══════════════════════════════════════════════════════════════════════════
# This class demonstrates:
# 1. OOP COMPOSITION: Ingredient is part of Recipe (cannot exist independently)
# 2. CASCADE DELETE: When recipe is deleted, ingredients are automatically deleted
# 3. ORDERED RELATIONSHIPS: Maintains display order for ingredients
# 4. OPTIONAL FIELDS: substitution_option and allergen_info can be null
#
# Connects to:
# - backend/routes/recipes.py: Created, updated, and deleted with Recipe (CREATE, UPDATE, DELETE)
# - Recipe model: Through 'recipe' backref relationship
# ═══════════════════════════════════════════════════════════════════════════

class Ingredient(db.Model):
    """
    Ingredient Model - Represents individual ingredients in a recipe
    
    This demonstrates PARENT-CHILD RELATIONSHIP with CASCADE operations
    Ingredients are tightly coupled to recipes (composition over inheritance)
    """
    
    # Define the PostgreSQL table name for this model
    __tablename__ = 'ingredients'

    # ═══ PRIMARY KEY ═══
    id = db.Column(db.Integer, primary_key=True)
    
    # ═══ FOREIGN KEY (MANY-TO-ONE relationship with Recipe) ═══
    # 'CASCADE' delete means when recipe is deleted, all its ingredients are deleted too
    # This enforces REFERENTIAL INTEGRITY at the database level
    # Connects to: Recipe.ingredients relationship (parent-child bond)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id', ondelete='CASCADE'), nullable=False)
    
    # ═══ INGREDIENT INFORMATION FIELDS ═══
    # Ingredient name (e.g., "All-purpose flour", "Chicken breast")
    name = db.Column(db.String(255), nullable=False)
    
    # Measurement/quantity (e.g., "2 cups", "500g", "1 tablespoon")
    measurement = db.Column(db.String(100), nullable=False)
    
    # Optional: Alternative ingredient that can be used instead
    # Example: "Can substitute with coconut oil" 
    substitution_option = db.Column(db.String(255), nullable=True)
    
    # Optional: Allergen warnings (e.g., "Contains gluten", "Contains nuts")
    allergen_info = db.Column(db.String(255), nullable=True)
    
    # Display order - maintains the sequence ingredients should appear
    # Used in: Recipe.ingredients relationship with order_by='Ingredient.order'
    # This ensures ingredients are displayed in the order the recipe creator intended
    order = db.Column(db.Integer, default=0)
    
    # ═══ AUDIT TRAIL TIMESTAMPS ═══
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ═══════════════════════════════════════════════════════════════════════════
    # OOP METHODS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def to_dict(self):
        """
        OOP ABSTRACTION: Converts Ingredient to JSON-serializable dictionary
        
        Used in: Recipe.to_dict() when include_ingredients=True
        Connects to: backend/routes/recipes.py for displaying recipe details
        
        Returns: Dictionary for JSON API response
        """
        return {
            'id': self.id,
            'recipe_id': self.recipe_id,
            'name': self.name,
            'measurement': self.measurement,
            'substitution_option': self.substitution_option,
            'allergen_info': self.allergen_info,
            'order': self.order,
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None,
            'updated_at': self.updated_at.isoformat() + 'Z' if self.updated_at else None,
        }


# ═══════════════════════════════════════════════════════════════════════════
# COMMENT MODEL CLASS - Demonstrates Self-Referential Relationships
# ═══════════════════════════════════════════════════════════════════════════
# This class demonstrates:
# 1. SELF-REFERENTIAL RELATIONSHIP: Comment can reply to another Comment
# 2. HIERARCHICAL DATA: Parent-child structure for nested comments  
# 3. CASCADE DELETE: Deleting recipe or parent comment deletes all related comments
# 4. COMPOSITE INDEXES: Optimizes queries for recipe comments
#
# Connects to:
# - backend/routes/comments.py: Full CRUD operations (CREATE, READ, UPDATE, DELETE)
# - Recipe model: Comments belong to recipes
# - User model: Comments are written by users (author relationship)
# ═══════════════════════════════════════════════════════════════════════════

class Comment(db.Model):
    """
    Comment Model - Represents user comments on recipes with nested reply support
    
    This demonstrates TREE STRUCTURE in relational database using adjacency list pattern
    Each comment can have a parent_id pointing to another comment (for replies)
    """
    
    # Define the PostgreSQL table name for this model
    __tablename__ = 'comments'

    # ═══ PRIMARY KEY ═══
    id = db.Column(db.Integer, primary_key=True)
    
    # ═══ FOREIGN KEYS - Multiple MANY-TO-ONE relationships ═══
    
    # Links comment to its recipe - CASCADE delete removes all comments when recipe is deleted
    # This enforces TRANSACTIONAL INTEGRITY (comments cannot exist without their recipe)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id', ondelete='CASCADE'), nullable=False)
    
    # Links comment to its author - SET NULL preserves comment if user account is deleted
    # This demonstrates SOFT DELETE pattern for user data
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    
    # ═══ SELF-REFERENTIAL FOREIGN KEY (Tree Structure) ═══
    # Links comment to parent comment for nested replies
    # CASCADE delete means deleting a comment also deletes all its replies
    # Null parent_id indicates this is a top-level comment
    # This demonstrates RECURSIVE RELATIONSHIP (a comment can reference another comment)
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id', ondelete='CASCADE'), nullable=True)
    
    # ═══ COMMENT DATA ═══
    # The actual comment text content
    comment = db.Column(db.Text, nullable=False)
    
    # ═══ AUDIT TRAIL TIMESTAMPS ═══
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ═══════════════════════════════════════════════════════════════════════════
    # OOP SELF-REFERENTIAL RELATIONSHIP
    # ═══════════════════════════════════════════════════════════════════════════
    # This demonstrates BIDIRECTIONAL NAVIGATION in tree structures
    # - comment.replies gets all child comments (replies to this comment)
    # - comment.parent gets the parent comment (what this comment is replying to)
    
    # ONE-TO-MANY with self: One comment can have many replies
    # 'remote_side=[id]' tells SQLAlchemy which side is the parent (fixes ambiguity)
    # 'lazy=joined' eagerly loads replies with the comment (PERFORMANCE: avoids N+1 queries)
    # 'order_by' ensures replies are chronologically ordered
    # Used in: backend/routes/comments.py for displaying nested comment threads
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]),
                              lazy='joined', order_by='Comment.created_at.asc()')

    # ═══════════════════════════════════════════════════════════════════════════
    # DATABASE OPTIMIZATIONS - Composite Indexes
    # ═══════════════════════════════════════════════════════════════════════════
    __table_args__ = (
        # Index on (recipe_id, created_at) speeds up "get recipe comments sorted by date"
        # Used in: backend/routes/comments.py index() to fetch comments for a recipe
        db.Index('ix_comments_recipe_created', 'recipe_id', 'created_at'),
        
        # Index on parent_id speeds up finding all replies to a comment
        # Used when loading nested comment structure
        db.Index('ix_comments_parent', 'parent_id'),
    )

    # ═══════════════════════════════════════════════════════════════════════════
    # OOP METHODS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def to_dict(self, include_replies=False):
        """
        OOP ABSTRACTION: Converts Comment to JSON with optional nested replies
        
        This demonstrates RECURSIVE SERIALIZATION for tree structures
        When include_replies=True, it includes nested comment replies
        But replies don't include their own replies (prevents infinite recursion)
        
        Parameters:
        - include_replies: If True, includes nested reply comments
        
        Used in:
        - backend/routes/comments.py: index() with include_replies=True for full threads
        - backend/routes/comments.py: store(), update() with include_replies=False for single comments
        
        Returns: Dictionary for JSON API response
        """
        data = {
            'id': self.id,
            'recipe_id': self.recipe_id,
            'user_id': self.user_id,
            'parent_id': self.parent_id,  # null = top-level comment
            'comment': self.comment,
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None,
            'updated_at': self.updated_at.isoformat() + 'Z' if self.updated_at else None,
            # Include commenter's basic info (relationship traversal through self.user)
            'user': {
                'id': self.user.id,
                'name': self.user.name,
            } if self.user else None,  # Handle deleted user accounts
        }
        
        # Conditionally include nested replies (demonstrates RECURSIVE DATA STRUCTURE)
        if include_replies:
            # List comprehension with recursive call to to_dict()
            # Note: include_replies=False prevents infinite recursion (only 2 levels deep)
            # This creates a parent-child hierarchy in the JSON response
            data['replies'] = [r.to_dict(include_replies=False) for r in self.replies]
            
        return data


# ═══════════════════════════════════════════════════════════════════════════
# RATING MODEL CLASS - Implements One Vote Per User Pattern
# ═══════════════════════════════════════════════════════════════════════════
# This class demonstrates:
# 1. COMPOSITE UNIQUE CONSTRAINT: One user can only rate a recipe once
# 2. TRANSACTIONAL INTEGRITY: Ensures data consistency with constraints
# 3. AGGREGATE QUERIES: Used by Recipe.average_rating() for calculations
# 4. CASCADE DELETE: Ratings are removed when recipe is deleted
#
# Connects to:
# - backend/routes/ratings.py: Full CRUD operations (CREATE, READ, UPDATE, DELETE)
# - Recipe model: Used in average_rating() and ratings_count() methods
# - User model: Links ratings to users (prevents self-rating)
# ═══════════════════════════════════════════════════════════════════════════

class Rating(db.Model):
    """
    Rating Model - Represents user ratings (1-5 stars) for recipes
    
    This demonstrates CONSTRAINT-BASED DATA INTEGRITY:
    - Each user can only rate a recipe once (unique constraint)
    - Rating must be between 1-5 (enforced in backend/routes/ratings.py validation)
    """
    
    # Define the PostgreSQL table name for this model
    __tablename__ = 'ratings'

    # ═══ PRIMARY KEY ═══
    id = db.Column(db.Integer, primary_key=True)
    
    # ═══ FOREIGN KEYS - Composite relationship (recipe + user) ═══
    
    # Links rating to its recipe - CASCADE delete removes ratings when recipe is deleted
    # This maintains REFERENTIAL INTEGRITY (ratings cannot exist without their recipe)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id', ondelete='CASCADE'), nullable=False)
    
    # Links rating to the user who gave it - SET NULL preserves rating if user is deleted
    # Allows historical rating data to remain even after user account removal
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    
    # ═══ RATING DATA ═══
    # Rating value: 1-5 stars (validated in backend/routes/ratings.py)
    # SmallInteger is more efficient than Integer for small number ranges
    rating = db.Column(db.SmallInteger, nullable=False)
    
    # ═══ AUDIT TRAIL TIMESTAMPS ═══
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Updated when user changes their rating (UPDATE operation)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ═══════════════════════════════════════════════════════════════════════════
    # DATABASE CONSTRAINTS AND INDEXES
    # ═══════════════════════════════════════════════════════════════════════════
    __table_args__ = (
        # ═══ UNIQUE CONSTRAINT - Implements Business Rule ═══
        # Ensures one user can only rate a recipe once
        # This is enforced at DATABASE LEVEL for data integrity
        # If violated, database raises IntegrityError (caught in backend/routes/ratings.py)
        # The constraint name 'uq_recipe_user_rating' helps identify errors
        db.UniqueConstraint('recipe_id', 'user_id', name='uq_recipe_user_rating'),
        
        # ═══ INDEX - Performance Optimization ═══
        # Speeds up queries for "get all ratings for a recipe"
        # Used in: Recipe.average_rating() and Recipe.ratings_count()
        # Also used in: backend/routes/ratings.py for checking existing ratings
        db.Index('ix_ratings_recipe', 'recipe_id'),
    )

    # ═══════════════════════════════════════════════════════════════════════════
    # OOP METHODS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def to_dict(self):
        """
        OOP ABSTRACTION: Converts Rating to JSON-serializable dictionary
        
        Used in: backend/routes/ratings.py for API responses after CREATE/UPDATE
        
        Returns: Dictionary for JSON API response
        """
        return {
            'id': self.id,
            'recipe_id': self.recipe_id,
            'user_id': self.user_id,
            'rating': self.rating,  # 1-5 star value
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None,
            'updated_at': self.updated_at.isoformat() + 'Z' if self.updated_at else None,
        }


# ═══════════════════════════════════════════════════════════════════════════
# UNUSED MODELS (Category and Product)
# ═══════════════════════════════════════════════════════════════════════════
# Note: The following models (Category and Product) appear to be from a different
# feature set and are not currently used in the ProCook application.
# They may be for future e-commerce functionality or leftover from template code.
# ═══════════════════════════════════════════════════════════════════════════
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('recipe_id', 'user_id', name='uq_recipe_user_rating'),
        db.Index('ix_ratings_recipe', 'recipe_id'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'recipe_id': self.recipe_id,
            'user_id': self.user_id,
            'rating': self.rating,
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None,
            'updated_at': self.updated_at.isoformat() + 'Z' if self.updated_at else None,
        }


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    icon = db.Column(db.String(255), nullable=True)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    products = db.relationship('Product', backref='category', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'icon': self.icon,
            'order': self.order,
        }


class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    features = db.Column(db.Text, nullable=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    sale_price = db.Column(db.Numeric(10, 2), nullable=True)
    sku = db.Column(db.String(255), unique=True, nullable=False)
    stock = db.Column(db.Integer, default=0)
    image = db.Column(db.String(255), nullable=True)
    is_featured = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'category_id': self.category_id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'features': self.features,
            'price': float(self.price) if self.price else 0,
            'sale_price': float(self.sale_price) if self.sale_price else None,
            'sku': self.sku,
            'stock': self.stock,
            'image': self.image,
            'is_featured': self.is_featured,
            'is_active': self.is_active,
            'category': self.category.to_dict() if self.category else None,
        }
