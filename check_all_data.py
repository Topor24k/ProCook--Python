"""Check all database tables"""
from backend.app import create_app
from backend.models import db, Recipe, User, Ingredient, Comment, Rating, SavedRecipe

app = create_app()

with app.app_context():
    print('=== ALL DATA IN DATABASE ===\n')
    
    # Check all tables
    users = User.query.all()
    recipes = Recipe.query.all()
    ingredients = Ingredient.query.all()
    comments = Comment.query.all()
    ratings = Rating.query.all()
    saved = SavedRecipe.query.all()
    
    print(f'Users: {len(users)}')
    print(f'Recipes: {len(recipes)}')
    print(f'Ingredients: {len(ingredients)}')
    print(f'Comments: {len(comments)}')
    print(f'Ratings: {len(ratings)}')
    print(f'Saved Recipes: {len(saved)}')
    
    if users:
        print('\n--- USERS ---')
        for u in users:
            print(f'  ID: {u.id} | Name: {u.name} | Email: {u.email}')
    
    if recipes:
        print('\n--- RECIPES ---')
        for r in recipes:
            print(f'  ID: {r.id} | Title: {r.title} | User: {r.user_id}')
