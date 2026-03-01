import React, { useState, useEffect, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useAuthGuard } from '../hooks/useAuthGuard';
import AuthPrompt from '../components/AuthPrompt';
import RatingStars from '../components/RatingStars';
import SaveButton from '../components/SaveButton';
import {
    IoBookOutline,
    IoCreateOutline,
    IoHeartOutline,
    IoTimeOutline,
    IoRestaurantOutline,
    IoPersonOutline,
    IoArrowForwardOutline,
    IoSearchOutline,
    IoTrendingUpOutline,
    IoLockClosedOutline
} from 'react-icons/io5';

export default function Home() {
    const [allRecipes, setAllRecipes] = useState([]);
    const [displayedRecipes, setDisplayedRecipes] = useState([]);
    const [loading, setLoading] = useState(true);
    const [currentIndex, setCurrentIndex] = useState(0);
    const { isAuthenticated } = useAuth();
    const { requireAuth, showAuthPrompt, hideAuthPrompt } = useAuthGuard();
    const navigate = useNavigate();

    // Fetch all recipes
    const fetchRecipes = useCallback(async () => {
        try {
            const response = await api.get('/recipes');
            const recipes = response.data.data || response.data;
            setAllRecipes(recipes);
            // Set initial 3 recipes
            setDisplayedRecipes(recipes.slice(0, 3));
        } catch (error) {
            console.error('Error fetching recipes:', error);
        } finally {
            setLoading(false);
        }
    }, []);

    // Rotate recipes every 5 minutes (300,000 milliseconds)
    const rotateRecipes = useCallback(() => {
        if (allRecipes.length > 3) {
            setCurrentIndex(prevIndex => {
                const nextIndex = (prevIndex + 3) % allRecipes.length;
                const nextRecipes = [];
                
                // Get 3 recipes starting from nextIndex, wrapping around if needed
                for (let i = 0; i < 3; i++) {
                    const recipeIndex = (nextIndex + i) % allRecipes.length;
                    nextRecipes.push(allRecipes[recipeIndex]);
                }
                
                setDisplayedRecipes(nextRecipes);
                return nextIndex;
            });
        }
    }, [allRecipes]);

    const handleRecipeClick = (e, recipeId) => {
        e.preventDefault();
        requireAuth(
            () => navigate(`/recipes/${recipeId}`),
            "Please register or login to view full recipe details"
        );
    };

    useEffect(() => {
        fetchRecipes();
    }, [fetchRecipes]);

    // Set up rotation interval
    useEffect(() => {
        if (allRecipes.length > 3) {
            const interval = setInterval(rotateRecipes, 300000); // 5 minutes
            return () => clearInterval(interval);
        }
    }, [rotateRecipes, allRecipes.length]);

    return (
        <div className="home-page">
            {/* Hero Section */}
            <section className="hero-section">
                <div className="hero-content">
                    <h1 className="hero-title">
                        Discover Delicious<br />
                        <span className="gradient-text">Recipes</span>
                    </h1>
                    <p className="hero-subtitle">
                        Join our community of food lovers. Share your culinary creations
                        and discover amazing recipes from around the world.
                    </p>
                    <div className="hero-actions">
                        <Link to="/recipes" className="btn-hero-primary">
                            <IoSearchOutline style={{ fontSize: '1.3rem' }} />
                            Browse Recipes
                        </Link>
                        {isAuthenticated ? (
                            <Link to="/recipes/create" className="btn-hero-secondary">
                                <IoCreateOutline style={{ fontSize: '1.3rem' }} />
                                Create Recipe
                            </Link>
                        ) : (
                            <button 
                                onClick={() => requireAuth(null, "Join our community to share your culinary creations!")}
                                className="btn-hero-secondary"
                            >
                                <IoPersonOutline style={{ fontSize: '1.3rem' }} />
                                Share Your Recipe
                            </button>
                        )}
                    </div>
                </div>
            </section>

            {/* Features Section */}
            <section className="features-section">
                <div className="features-grid">
                    <div className="feature-card">
                        <div className="feature-icon">
                            <IoBookOutline style={{ fontSize: '4rem', color: 'var(--primary)' }} />
                        </div>
                        <h3>Browse Recipes</h3>
                        <p>Explore thousands of recipes from cuisines around the world. Find the perfect dish for any occasion.</p>
                    </div>
                    <div className="feature-card">
                        <div className="feature-icon">
                            <IoCreateOutline style={{ fontSize: '4rem', color: 'var(--accent)' }} />
                        </div>
                        <h3>Create & Share</h3>
                        <p>Share your favorite recipes with the community and inspire others with your culinary creativity.</p>
                    </div>
                    <div className="feature-card">
                        <div className="feature-icon">
                            <IoHeartOutline style={{ fontSize: '4rem', color: '#E74C3C' }} />
                        </div>
                        <h3>Save Favorites</h3>
                        <p>Keep track of recipes you love and want to cook again. Build your personal collection.</p>
                    </div>
                </div>
            </section>

            {/* Latest Recipes Section */}
            <section className="latest-recipes-section">
                <div className="section-header">
                    <h2 className="section-title">
                        <IoTrendingUpOutline style={{ fontSize: '2.5rem', marginRight: '0.5rem', verticalAlign: 'middle', color: 'var(--primary)' }} />
                        Latest Recipes
                    </h2>
                    <Link to="/recipes" className="view-all-link">
                        View All <IoArrowForwardOutline style={{ fontSize: '1.2rem' }} />
                    </Link>
                </div>

                {loading ? (
                    <div className="loading-state">
                        <div className="spinner"></div>
                        <p>Loading delicious recipes...</p>
                    </div>
                ) : allRecipes.length === 0 ? (
                    <div className="empty-state">
                        <div className="empty-state-icon">
                            <IoRestaurantOutline />
                        </div>
                        <h3 className="empty-state-title">No Recipes Yet</h3>
                        <p className="empty-state-description">
                            Be the first to share a recipe with our community!
                        </p>
                        {isAuthenticated && (
                            <Link to="/recipes/create" className="btn-primary">
                                <IoCreateOutline style={{ fontSize: '1.2rem' }} />
                                Create First Recipe
                            </Link>
                        )}
                    </div>
                ) : (
                    <div className="recipes-grid">
                        {displayedRecipes.map(recipe => (
                            <div 
                                key={recipe.id}
                                className="recipe-card"
                                onClick={(e) => handleRecipeClick(e, recipe.id)}
                                style={{ cursor: 'pointer' }}
                            >
                                <div className="recipe-image">
                                    {recipe.image ? (
                                        <img 
                                            src={`${import.meta.env.VITE_API_BASE_URL || ''}/uploads/${recipe.image}`} 
                                            alt={recipe.title}
                                            onError={(e) => {
                                                e.target.style.display = 'none';
                                                e.target.parentElement.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
                                            }}
                                        />
                                    ) : null}
                                    <div className="recipe-badge">{recipe.cuisine_type}</div>
                                    <div className="recipe-overlay">
                                        <span className="view-recipe">View Recipe</span>
                                    </div>
                                </div>
                                <div className="recipe-content">
                                    <div className="recipe-card-header">
                                        <h3 className="recipe-title">{recipe.title}</h3>
                                        <div onClick={(e) => e.preventDefault()} className="recipe-card-save">
                                            <SaveButton recipeId={recipe.id} size="small" showLabel={false} />
                                        </div>
                                    </div>
                                    <p className="recipe-description">
                                        {recipe.short_description?.substring(0, 100)}
                                        {recipe.short_description?.length > 100 && '...'}
                                    </p>
                                    <div className="recipe-meta">
                                        <span className="meta-item">
                                            <IoTimeOutline className="meta-icon" style={{ fontSize: '1.2rem' }} />
                                            {recipe.total_time} min
                                        </span>
                                        <span className="meta-item">
                                            <IoRestaurantOutline className="meta-icon" style={{ fontSize: '1.2rem' }} />
                                            {recipe.serving_size} servings
                                        </span>
                                    </div>
                                    <div className="recipe-footer">
                                        <div className="recipe-author">
                                            <IoPersonOutline style={{ fontSize: '1.1rem' }} />
                                            {recipe.user?.name || 'Anonymous'}
                                        </div>
                                        <div className="recipe-card-rating">
                                            <RatingStars recipeId={recipe.id} size="small" showCount={false} interactive={false} />
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
                
                {/* Show rotation indicator if there are more than 3 recipes */}
                {allRecipes.length > 3 && (
                    <div className="recipes-rotation-info">
                        <p style={{ textAlign: 'center', color: 'var(--gray-600)', margin: '1rem 0' }}>
                            Showing 3 of {allRecipes.length} recipes • Recipes rotate every 5 minutes
                        </p>
                    </div>
                )}
            </section>

            {/* CTA Section */}
            {!isAuthenticated && (
                <section className="cta-section">
                    <div className="cta-content">
                        <h2 className="cta-title">Ready to Start Cooking?</h2>
                        <p className="cta-description">
                            Join our community today and share your culinary masterpieces
                        </p>
                        <Link to="/register" className="btn-cta">
                            <IoPersonOutline style={{ fontSize: '1.3rem' }} />
                            Sign Up Free
                        </Link>
                    </div>
                </section>
            )}
            
            {/* Auth Prompt Modal */}
            <AuthPrompt 
                isOpen={showAuthPrompt}
                onClose={hideAuthPrompt}
            />
        </div>
    );
}
