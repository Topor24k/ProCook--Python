from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# CRUD: Many-to-many relationship table - stores which users saved which recipes
saved_recipes = db.Table(
    'saved_recipes',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
    db.Column('recipe_id', db.Integer, db.ForeignKey('recipes.id', ondelete='CASCADE'), nullable=False),
    db.Column('created_at', db.DateTime, default=datetime.utcnow),
    db.Column('updated_at', db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow),
    db.UniqueConstraint('user_id', 'recipe_id', name='uq_user_recipe_saved'),
)


# OOP: User class inherits from UserMixin (authentication methods) and db.Model (database ORM)
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    email_verified_at = db.Column(db.DateTime, nullable=True)
    password = db.Column(db.String(255), nullable=False)
    remember_token = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # OOP: One-to-many relationships - User has many recipes, comments, and ratings
    recipes = db.relationship('Recipe', backref='user', lazy='dynamic', foreign_keys='Recipe.user_id')
    comments = db.relationship('Comment', backref='user', lazy='dynamic', foreign_keys='Comment.user_id')
    ratings = db.relationship('Rating', backref='user', lazy='dynamic', foreign_keys='Rating.user_id')
    
    # OOP: Many-to-many relationship - User can save many recipes through saved_recipes table
    saved = db.relationship('Recipe', secondary=saved_recipes, lazy='dynamic',
                            backref=db.backref('saved_by', lazy='dynamic'))

    # OOP Encapsulation: hashes password securely instead of storing plain text
    def set_password(self, password):
        self.password = generate_password_hash(password)

    # OOP Encapsulation: verifies password against stored hash
    def check_password(self, password):
        return check_password_hash(self.password, password)

    # OOP Abstraction: converts User object to dictionary for JSON API responses
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None,
            'updated_at': self.updated_at.isoformat() + 'Z' if self.updated_at else None,
        }


# OOP: Recipe class maps to recipes database table
class Recipe(db.Model):
    __tablename__ = 'recipes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    title = db.Column(db.String(255), nullable=False)
    short_description = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(255), nullable=True)
    cuisine_type = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    prep_time = db.Column(db.Integer, nullable=False)
    cook_time = db.Column(db.Integer, nullable=False)
    total_time = db.Column(db.Integer, nullable=False)
    serving_size = db.Column(db.Integer, nullable=False)
    preparation_notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # OOP: One-to-many relationships - Recipe has many ingredients, comments, and ratings
    # CASCADE delete ensures child records are deleted when recipe is deleted
    ingredients = db.relationship('Ingredient', backref='recipe', lazy='joined',
                                  cascade='all, delete-orphan', order_by='Ingredient.order')
    comments = db.relationship('Comment', backref='recipe', lazy='dynamic', cascade='all, delete-orphan')
    ratings = db.relationship('Rating', backref='recipe', lazy='dynamic', cascade='all, delete-orphan')

    __table_args__ = (
        db.Index('ix_recipes_user_created', 'user_id', 'created_at'),
        db.Index('ix_recipes_title', 'title'),
    )

    # CRUD READ: calculates average rating using SQL aggregate function
    def average_rating(self):
        avg = db.session.query(db.func.avg(Rating.rating)).filter(Rating.recipe_id == self.id).scalar()
        return round(float(avg), 1) if avg else 0

    # CRUD READ: counts total ratings for this recipe
    def ratings_count(self):
        return self.ratings.count()

    # OOP Abstraction: converts Recipe object to dictionary for JSON API responses
    def to_dict(self, include_ingredients=False, include_user=True):
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'short_description': self.short_description,
            'image': self.image,
            'cuisine_type': self.cuisine_type,
            'category': self.category,
            'prep_time': self.prep_time,
            'cook_time': self.cook_time,
            'total_time': self.total_time,
            'serving_size': self.serving_size,
            'preparation_notes': self.preparation_notes,
            'average_rating': self.average_rating(),
            'ratings_count': self.ratings_count(),
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None,
            'updated_at': self.updated_at.isoformat() + 'Z' if self.updated_at else None,
        }
        
        # OOP: optionally loads related user data through relationship
        if include_user and self.user:
            data['user'] = self.user.to_dict()
        elif include_user:
            data['user'] = None
            
        # OOP: optionally loads related ingredients through relationship
        if include_ingredients:
            data['ingredients'] = [i.to_dict() for i in self.ingredients]
            
        return data


# OOP: Ingredient class represents child entity of Recipe with CASCADE delete
class Ingredient(db.Model):
    __tablename__ = 'ingredients'

    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    measurement = db.Column(db.String(100), nullable=False)
    substitution_option = db.Column(db.String(255), nullable=True)
    allergen_info = db.Column(db.String(255), nullable=True)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # OOP Abstraction: converts Ingredient object to dictionary for JSON API responses
    def to_dict(self):
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


# OOP: Comment class with self-referential relationship for nested replies
class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id', ondelete='CASCADE'), nullable=True)  # Self-referential for replies
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # OOP: Self-referential one-to-many relationship - Comment can have many replies
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]),
                              lazy='joined', order_by='Comment.created_at.asc()')

    __table_args__ = (
        db.Index('ix_comments_recipe_created', 'recipe_id', 'created_at'),
        db.Index('ix_comments_parent', 'parent_id'),
    )

    # OOP Abstraction: converts Comment object to dictionary with optional nested replies
    def to_dict(self, include_replies=False):
        data = {
            'id': self.id,
            'recipe_id': self.recipe_id,
            'user_id': self.user_id,
            'parent_id': self.parent_id,
            'comment': self.comment,
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None,
            'updated_at': self.updated_at.isoformat() + 'Z' if self.updated_at else None,
            'user': {'id': self.user.id, 'name': self.user.name} if self.user else None,
        }
        
        # OOP: recursively includes nested replies through relationship
        if include_replies:
            data['replies'] = [r.to_dict(include_replies=False) for r in self.replies]
            
        return data


# OOP: Rating class with unique constraint to prevent duplicate ratings
class Rating(db.Model):
    __tablename__ = 'ratings'

    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    rating = db.Column(db.SmallInteger, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # CRUD: ensures one user can only rate a recipe once
    __table_args__ = (
        db.UniqueConstraint('recipe_id', 'user_id', name='uq_recipe_user_rating'),
        db.Index('ix_ratings_recipe', 'recipe_id'),
    )

    # OOP Abstraction: converts Rating object to dictionary for JSON API responses
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
            'price': float(self.price),
            'sale_price': float(self.sale_price) if self.sale_price else None,
            'sku': self.sku,
            'stock': self.stock,
            'image': self.image,
            'is_featured': self.is_featured,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None,
            'updated_at': self.updated_at.isoformat() + 'Z' if self.updated_at else None,
        }
