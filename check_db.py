"""Check database content"""
from backend.app import create_app
from backend.models import db, Recipe, User

app = create_app()

with app.app_context():
    print('=== DATABASE CONNECTION ===')
    print(f'Database URI: {app.config["SQLALCHEMY_DATABASE_URI"]}')
    print('\n=== DATABASE CONTENT ===')
    
    users = User.query.all()
    recipes = Recipe.query.all()
    
    print(f'Total Users: {len(users)}')
    print(f'Total Recipes: {len(recipes)}')
    
    if users:
        print('\nUsers:')
        for u in users:
            print(f'  - {u.name} ({u.email})')
    
    if recipes:
        print('\nRecipes:')
        for r in recipes:
            print(f'  - {r.title} by User#{r.user_id}')
