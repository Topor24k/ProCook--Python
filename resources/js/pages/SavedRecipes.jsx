import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import RatingStars from '../components/RatingStars';
import SaveButton from '../components/SaveButton';
import {
    IoBookmarkOutline,
    IoBookOutline,
    IoRestaurantOutline,
    IoTimeOutline,
    IoPersonOutline,
    IoHeartOutline
} from 'react-icons/io5';

export default function SavedRecipes() {
    const { user } = useAuth();
    const navigate = useNavigate();
    const [recipes, setRecipes] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (!user) {
            navigate('/login');
            return;
        }
        fetchSavedRecipes();
    }, [user]);

    const fetchSavedRecipes = async () => {
        try {
            const response = await api.get('/saved-recipes');
            setRecipes(response.data.data || response.data);
        } catch (error) {
            console.error('Error:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleRemoveSaved = (recipeId) => {
        setRecipes(recipes.filter(recipe => recipe.id !== recipeId));
    };

    if (loading) {
        return (
            <div className="recipes-page container">
                <div className="loading-state">
                    <div className="spinner"></div>
                    <p>Loading saved recipes...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="recipes-page container">
            <div className="page-header">
                <h1 className="page-title">
                    <IoBookmarkOutline style={{ fontSize: '3rem', marginRight: '1rem', verticalAlign: 'middle', color: 'var(--primary)' }} />
                    Saved Recipes
                </h1>
                <p className="page-subtitle">
                    Your collection of favorite recipes from the community
                </p>
            </div>

            {recipes.length === 0 ? (
                <div className="empty-state">
                    <div className="empty-state-icon">
                        <IoBookOutline />
                    </div>
                    <h3 className="empty-state-title">No Saved Recipes</h3>
                    <p className="empty-state-description">
                        Start exploring recipes and save your favorites to access them easily!
                    </p>
                    <Link to="/recipes" className="btn-primary">
                        <IoHeartOutline style={{ fontSize: '1.3rem' }} />
                        Browse Recipes
                    </Link>
                </div>
            ) : (
                <div className="recipes-grid">
                    {recipes.map(recipe => (
                        <Link 
                            key={recipe.id} 
                            to={`/recipes/${recipe.id}`} 
                            className="recipe-card"
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
                                        <SaveButton 
                                            recipeId={recipe.id} 
                                            size="small" 
                                            showLabel={false}
                                            onSaveChange={(isSaved) => {
                                                if (!isSaved) {
                                                    handleRemoveSaved(recipe.id);
                                                }
                                            }}
                                        />
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
                        </Link>
                    ))}
                </div>
            )}
        </div>
    );
}
