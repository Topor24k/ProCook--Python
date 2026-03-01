"""Database seeder – creates tables and optionally adds sample data."""
from backend.app import create_app
from backend.models import db, User, Recipe, Ingredient, Category

app = create_app()


def create_tables():
    """Create all database tables."""
    with app.app_context():
        db.create_all()
        print("✓ All database tables created successfully.")


def seed_sample_data():
    """Insert sample data for development."""
    with app.app_context():
        # Check if data already exists
        if User.query.first():
            print("⚠ Database already has data. Skipping seed.")
            return

        # Create a sample user
        user = User(name='Demo User', email='demo@procook.com')
        user.set_password('Password123')
        db.session.add(user)
        db.session.flush()

        # Create sample recipes
        recipes_data = [
            {
                'title': 'Classic Spaghetti Carbonara',
                'short_description': 'A traditional Italian pasta dish made with eggs, cheese, pancetta, and pepper.',
                'cuisine_type': 'Italian',
                'category': 'Pasta',
                'prep_time': 15,
                'cook_time': 20,
                'serving_size': 4,
                'preparation_notes': 'Cook the spaghetti according to package directions. While the pasta cooks, prepare the sauce by whisking together eggs, grated Pecorino Romano, and black pepper. Cook the pancetta until crispy. Drain the pasta, reserving some pasta water. Combine the hot pasta with the pancetta, then quickly toss with the egg mixture off heat. The residual heat will cook the eggs into a creamy sauce. Add pasta water as needed for consistency.',
                'ingredients': [
                    {'name': 'Spaghetti', 'measurement': '400g'},
                    {'name': 'Pancetta', 'measurement': '200g'},
                    {'name': 'Eggs', 'measurement': '4 large'},
                    {'name': 'Pecorino Romano', 'measurement': '100g, grated'},
                    {'name': 'Black Pepper', 'measurement': '2 tsp, freshly ground'},
                ]
            },
            {
                'title': 'Thai Green Curry',
                'short_description': 'Aromatic and spicy Thai curry with coconut milk, vegetables, and your choice of protein.',
                'cuisine_type': 'Thai',
                'category': 'Curry',
                'prep_time': 20,
                'cook_time': 25,
                'serving_size': 4,
                'preparation_notes': 'Heat oil in a wok. Fry the green curry paste for 2 minutes until fragrant. Add coconut milk and bring to a simmer. Add chicken and cook until done. Add bamboo shoots, bell peppers, and Thai basil. Season with fish sauce, sugar, and lime juice. Serve over steamed jasmine rice.',
                'ingredients': [
                    {'name': 'Green Curry Paste', 'measurement': '3 tbsp'},
                    {'name': 'Coconut Milk', 'measurement': '400ml'},
                    {'name': 'Chicken Breast', 'measurement': '500g, sliced'},
                    {'name': 'Thai Basil', 'measurement': '1 cup'},
                    {'name': 'Fish Sauce', 'measurement': '2 tbsp'},
                    {'name': 'Jasmine Rice', 'measurement': '2 cups'},
                ]
            },
        ]

        for r_data in recipes_data:
            ingredients = r_data.pop('ingredients')
            recipe = Recipe(
                user_id=user.id,
                total_time=r_data['prep_time'] + r_data['cook_time'],
                **r_data
            )
            db.session.add(recipe)
            db.session.flush()

            for i, ing in enumerate(ingredients):
                db.session.add(Ingredient(
                    recipe_id=recipe.id,
                    name=ing['name'],
                    measurement=ing['measurement'],
                    order=i + 1,
                ))

        db.session.commit()
        print("✓ Sample data seeded successfully.")
        print("  Demo account: demo@procook.com / Password123")


if __name__ == '__main__':
    create_tables()
    seed_sample_data()
