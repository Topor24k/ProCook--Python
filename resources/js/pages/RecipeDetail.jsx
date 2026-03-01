import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useAuthGuard } from '../hooks/useAuthGuard';
import AuthPrompt from '../components/AuthPrompt';
import api from '../services/api';
import RatingStars from '../components/RatingStars';
import SaveButton from '../components/SaveButton';
import CommentSection from '../components/CommentSection';
import {
    IoTimeOutline,
    IoRestaurantOutline,
    IoFlameOutline,
    IoTimerOutline,
    IoArrowBackOutline,
    IoCreateOutline,
    IoTrashOutline,
    IoCheckmarkCircleOutline,
    IoWarningOutline,
    IoInformationCircleOutline,
    IoChevronForwardOutline,
    IoLockClosedOutline,
    IoPersonAddOutline,
    IoLogInOutline
} from 'react-icons/io5';

export default function RecipeDetail() {
    const { id } = useParams();
    const { user, isAuthenticated } = useAuth();
    const { requireAuth, showAuthPrompt, hideAuthPrompt } = useAuthGuard();
    const navigate = useNavigate();
    const [recipe, setRecipe] = useState(null);
    const [loading, setLoading] = useState(true);
    const [showAuthRequired, setShowAuthRequired] = useState(false);

    useEffect(() => {
        // Check authentication first
        if (!isAuthenticated) {
            setShowAuthRequired(true);
            setLoading(false);
            return;
        }
        fetchRecipe();
    }, [id, isAuthenticated]);

    const fetchRecipe = async () => {
        try {
            const response = await api.get(`/recipes/${id}`);
            // Handle new API response format with success/data wrapper
            setRecipe(response.data.data || response.data);
        } catch (error) {
            console.error('Error:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async () => {
        if (confirm('Are you sure you want to delete this recipe?')) {
            try {
                await api.delete(`/recipes/${id}`);
                navigate('/recipes');
            } catch (error) {
                alert('Error deleting recipe');
            }
        }
    };

    if (loading) {
        return (
            <div className="recipe-detail-page">
                <div className="recipe-detail-container">
                    <div className="loading-state">
                        <div className="spinner"></div>
                        <p>Loading recipe...</p>
                    </div>
                </div>
            </div>
        );
    }

    // Show authentication required message for unauthenticated users
    if (showAuthRequired) {
        return (
            <div className="recipe-detail-page">
                <div className="recipe-detail-container">
                    <div className="auth-required-state" style={{ 
                        textAlign: 'center', 
                        padding: '4rem 2rem',
                        background: 'var(--white)',
                        borderRadius: 'var(--radius-lg)',
                        boxShadow: 'var(--shadow-md)',
                        margin: '2rem 0'
                    }}>
                        <div style={{ marginBottom: '2rem' }}>
                            <IoLockClosedOutline style={{ fontSize: '4rem', color: 'var(--primary)' }} />
                        </div>
                        <h2 style={{ color: 'var(--dark)', marginBottom: '1rem' }}>Authentication Required</h2>
                        <p style={{ color: 'var(--gray-700)', marginBottom: '2rem', fontSize: '1.1rem' }}>
                            Please register or login to view detailed recipe information.
                        </p>
                        <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
                            <Link to="/register" className="btn-primary">
                                <IoPersonAddOutline style={{ fontSize: '1.2rem' }} />
                                Register Now
                            </Link>
                            <Link to="/login" className="btn-secondary">
                                <IoLogInOutline style={{ fontSize: '1.2rem' }} />
                                Login
                            </Link>
                        </div>
                        <p style={{ fontSize: '0.9rem', color: 'var(--gray-600)', marginTop: '2rem' }}>
                            Join our community to access all features and share your culinary creations!
                        </p>
                    </div>
                    
                    {/* Auth Prompt Modal */}
                    <AuthPrompt 
                        isOpen={showAuthPrompt}
                        onClose={hideAuthPrompt}
                    />
                </div>
            </div>
        );
    }

    if (!recipe) {
        return (
            <div className="recipe-detail-page">
                <div className="recipe-detail-container">
                    <div className="empty-state">
                        <div className="empty-state-icon">
                            <IoWarningOutline />
                        </div>
                        <h3 className="empty-state-title">Recipe Not Found</h3>
                        <p className="empty-state-description">
                            The recipe you're looking for doesn't exist or has been removed.
                        </p>
                        <Link to="/recipes" className="btn-primary">
                            <IoArrowBackOutline style={{ fontSize: '1.2rem' }} />
                            Back to Recipes
                        </Link>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="recipe-detail-page">
            <div className="recipe-detail-container">
                {/* Breadcrumb */}
                <div className="breadcrumb">
                    <Link to="/">Home</Link>
                    <IoChevronForwardOutline className="breadcrumb-separator" />
                    <Link to="/recipes">Recipes</Link>
                    <IoChevronForwardOutline className="breadcrumb-separator" />
                    <span style={{ color: 'var(--dark)' }}>{recipe.title}</span>
                </div>

                {/* Recipe Image */}
                {recipe.image && (
                    <div className="recipe-detail-image-container">
                        <img 
                            src={`${import.meta.env.VITE_API_BASE_URL || ''}/uploads/${recipe.image}`} 
                            alt={recipe.title}
                            className="recipe-detail-image"
                        />
                    </div>
                )}

                {/* Recipe Header Card */}
                <div className="recipe-header-card">
                    <div className="recipe-categories">
                        <span className="category-badge category-badge-primary">
                            {recipe.cuisine_type}
                        </span>
                        <span className="category-badge category-badge-secondary">
                            {recipe.category}
                        </span>
                    </div>
                    
                    <h1 className="recipe-detail-title">{recipe.title}</h1>
                    <p className="recipe-detail-description">{recipe.short_description}</p>
                    
                    <div className="recipe-stats">
                        <div className="stat-item">
                            <div className="stat-icon">
                                <IoTimeOutline style={{ color: 'var(--primary)' }} />
                            </div>
                            <div className="stat-label">PREP TIME</div>
                            <div className="stat-value">{recipe.prep_time} min</div>
                        </div>
                        <div className="stat-item">
                            <div className="stat-icon">
                                <IoFlameOutline style={{ color: 'var(--danger)' }} />
                            </div>
                            <div className="stat-label">COOK TIME</div>
                            <div className="stat-value">{recipe.cook_time} min</div>
                        </div>
                        <div className="stat-item">
                            <div className="stat-icon">
                                <IoTimerOutline style={{ color: 'var(--accent)' }} />
                            </div>
                            <div className="stat-label">TOTAL TIME</div>
                            <div className="stat-value">{recipe.total_time} min</div>
                        </div>
                        <div className="stat-item">
                            <div className="stat-icon">
                                <IoRestaurantOutline style={{ color: 'var(--info)' }} />
                            </div>
                            <div className="stat-label">SERVINGS</div>
                            <div className="stat-value">{recipe.serving_size}</div>
                        </div>
                    </div>

                    {/* Rating and Save Section */}
                    <div className="recipe-interactions">
                        <div className="recipe-rating">
                            <RatingStars recipeId={recipe.id} size="large" interactive={true} />
                        </div>
                        <SaveButton recipeId={recipe.id} size="large" showLabel={true} />
                    </div>

                    {user && recipe.user_id === user.id && (
                        <div className="recipe-actions">
                            <Link to={`/recipes/${recipe.id}/edit`} className="btn-secondary">
                                <IoCreateOutline style={{ fontSize: '1.2rem' }} />
                                Edit Recipe
                            </Link>
                            <button 
                                onClick={handleDelete} 
                                className="btn-secondary" 
                                style={{ 
                                    background: 'var(--danger)', 
                                    color: 'white', 
                                    borderColor: 'var(--danger)' 
                                }}
                            >
                                <IoTrashOutline style={{ fontSize: '1.2rem' }} />
                                Delete Recipe
                            </button>
                        </div>
                    )}
                </div>

                {/* Ingredients Section */}
                {recipe.ingredients && recipe.ingredients.length > 0 && (
                    <div className="section-card">
                        <h2 className="section-card-title">Ingredients</h2>
                        <div className="ingredients-list">
                            {recipe.ingredients.map((ingredient, index) => (
                                <div key={index} className="ingredient-item">
                                    <IoCheckmarkCircleOutline className="ingredient-check" />
                                    <div className="ingredient-details">
                                        <div className="ingredient-name">
                                            {ingredient.measurement} {ingredient.name}
                                        </div>
                                        {ingredient.substitution_option && (
                                            <div className="ingredient-note">
                                                <IoInformationCircleOutline style={{ color: 'var(--info)', fontSize: '1rem' }} />
                                                Substitute: {ingredient.substitution_option}
                                            </div>
                                        )}
                                        {ingredient.allergen_info && (
                                            <div className="ingredient-note" style={{ color: 'var(--danger)' }}>
                                                <IoWarningOutline style={{ color: 'var(--danger)', fontSize: '1rem' }} />
                                                Allergen: {ingredient.allergen_info}
                                            </div>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Preparation Section */}
                <div className="section-card">
                    <h2 className="section-card-title">Preparation Instructions</h2>
                    <div className="preparation-content">{recipe.preparation_notes}</div>
                </div>

                {/* Comment Section */}
                <CommentSection recipeId={recipe.id} />

                {/* Back Link */}
                <Link to="/recipes" className="back-link">
                    <IoArrowBackOutline style={{ fontSize: '1.2rem' }} />
                    Back to All Recipes
                </Link>
                
                {/* Auth Prompt Modal */}
                <AuthPrompt 
                    isOpen={showAuthPrompt}
                    onClose={hideAuthPrompt}
                />
            </div>
        </div>
    );
}
