import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useAuthGuard } from '../hooks/useAuthGuard';
import AuthPrompt from '../components/AuthPrompt';
import RatingStars from '../components/RatingStars';
import SaveButton from '../components/SaveButton';
import {
    IoTimeOutline,
    IoRestaurantOutline,
    IoPersonOutline,
    IoSearchOutline,
    IoFilterOutline,
    IoAddCircleOutline,
    IoGridOutline
} from 'react-icons/io5';

export default function Recipes() {
    const [recipes, setRecipes] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [filterCuisine, setFilterCuisine] = useState('');
    const { isAuthenticated } = useAuth();
    const { requireAuth, showAuthPrompt, hideAuthPrompt } = useAuthGuard();
    const navigate = useNavigate();

    useEffect(() => {
        fetchRecipes();
    }, []);

    const fetchRecipes = async () => {
        try {
            const response = await api.get('/recipes');
            setRecipes(response.data.data || response.data);
        } catch (error) {
            console.error('Error:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleRecipeClick = (e, recipeId) => {
        e.preventDefault();
        requireAuth(
            () => navigate(`/recipes/${recipeId}`),
            "Please register or login to view full recipe details"
        );
    };

    const handleShareRecipeClick = (e) => {
        e.preventDefault();
        requireAuth(
            () => navigate('/recipes/create'),
            "Join our community to share your culinary creations!"
        );
    };

    const cuisineTypes = [...new Set(recipes.map(r => r.cuisine_type))].filter(Boolean);

    const filteredRecipes = recipes.filter(recipe => {
        const matchesSearch = recipe.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                             recipe.short_description?.toLowerCase().includes(searchTerm.toLowerCase());
        const matchesCuisine = !filterCuisine || recipe.cuisine_type === filterCuisine;
        return matchesSearch && matchesCuisine;
    });

    if (loading) {
        return (
            <div className="recipes-page container">
                <div className="loading-state">
                    <div className="spinner"></div>
                    <p>Loading recipes...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="recipes-page container">
            {/* Page Header */}
            <div className="page-header">
                <h1 className="page-title">
                    <IoGridOutline style={{ fontSize: '3rem', marginRight: '1rem', verticalAlign: 'middle', color: 'var(--primary)' }} />
                    Recipe Collection
                </h1>
                <p className="page-subtitle">
                    Discover delicious recipes from our community of passionate cooks
                </p>
                {isAuthenticated ? (
                    <Link to="/recipes/create" className="btn-primary" style={{ marginTop: '1.5rem' }}>
                        <IoAddCircleOutline style={{ fontSize: '1.3rem' }} />
                        Share Your Recipe
                    </Link>
                ) : (
                    <button 
                        onClick={handleShareRecipeClick}
                        className="btn-primary" 
                        style={{ marginTop: '1.5rem' }}
                    >
                        <IoAddCircleOutline style={{ fontSize: '1.3rem' }} />
                        Share Your Recipe
                    </button>
                )}
            </div>

            {/* Search & Filter Bar */}
            <div className="search-filter-bar">
                <div style={{ position: 'relative', flex: 1, minWidth: '250px' }}>
                    <IoSearchOutline style={{
                        position: 'absolute',
                        left: '1rem',
                        top: '50%',
                        transform: 'translateY(-50%)',
                        fontSize: '1.3rem',
                        color: 'var(--gray-500)',
                        pointerEvents: 'none'
                    }} />
                    <input
                        type="text"
                        className="search-input"
                        placeholder="Search recipes..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        style={{ paddingLeft: '3rem' }}
                    />
                </div>
                
                <div style={{ position: 'relative' }}>
                    <IoFilterOutline style={{
                        position: 'absolute',
                        left: '1rem',
                        top: '50%',
                        transform: 'translateY(-50%)',
                        fontSize: '1.2rem',
                        color: 'var(--gray-500)',
                        pointerEvents: 'none'
                    }} />
                    <select
                        className="filter-select"
                        value={filterCuisine}
                        onChange={(e) => setFilterCuisine(e.target.value)}
                        style={{ paddingLeft: '3rem', minWidth: '200px' }}
                    >
                        <option value="">All Cuisines</option>
                        {cuisineTypes.map(cuisine => (
                            <option key={cuisine} value={cuisine}>{cuisine}</option>
                        ))}
                    </select>
                </div>

                <div style={{ fontSize: '0.9rem', color: 'var(--gray-600)', fontWeight: '500', whiteSpace: 'nowrap' }}>
                    {filteredRecipes.length} recipe{filteredRecipes.length !== 1 ? 's' : ''} found
                </div>
            </div>

            {/* Recipes Grid */}
            {filteredRecipes.length === 0 ? (
                <div className="empty-state">
                    <div className="empty-state-icon">
                        <IoRestaurantOutline />
                    </div>
                    <h3 className="empty-state-title">No Recipes Found</h3>
                    <p className="empty-state-description">
                        Try adjusting your search or filters to find what you're looking for.
                    </p>
                </div>
            ) : (
                <div className="recipes-grid">
                    {filteredRecipes.map(recipe => (
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
                                    {recipe.short_description}
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
            
            {/* Auth Prompt Modal */}
            <AuthPrompt 
                isOpen={showAuthPrompt}
                onClose={hideAuthPrompt}
            />
        </div>
    );
}
