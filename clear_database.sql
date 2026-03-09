-- Clear all data from ProCook database
-- Run this in pgAdmin4 Query Tool

-- Disable foreign key checks temporarily
SET session_replication_role = 'replica';

-- Delete all data from tables (in correct order due to foreign keys)
TRUNCATE TABLE saved_recipes CASCADE;
TRUNCATE TABLE ratings CASCADE;
TRUNCATE TABLE comments CASCADE;
TRUNCATE TABLE ingredients CASCADE;
TRUNCATE TABLE recipes CASCADE;
TRUNCATE TABLE users CASCADE;

-- Re-enable foreign key checks
SET session_replication_role = 'origin';

-- Verify all tables are empty
SELECT 'users' as table_name, COUNT(*) as records FROM users
UNION ALL
SELECT 'recipes', COUNT(*) FROM recipes
UNION ALL
SELECT 'ingredients', COUNT(*) FROM ingredients
UNION ALL
SELECT 'comments', COUNT(*) FROM comments
UNION ALL
SELECT 'ratings', COUNT(*) FROM ratings
UNION ALL
SELECT 'saved_recipes', COUNT(*) FROM saved_recipes;

SELECT 'All data cleared successfully!' as status;
