import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import {
    IoHeartOutline,
    IoAddCircleOutline,
    IoRestaurantOutline,
    IoTimeOutline,
    IoEyeOutline,
    IoCreateOutline,
    IoBookOutline
} from 'react-icons/io5';

export default function MyRecipes() {
    const { user } = useAuth();
    const navigate = useNavigate();
    const [recipes, setRecipes] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (!user) {
            navigate('/login');
            return;
        }
        fetchMyRecipes();
    }, [user]);

    const fetchMyRecipes = async () => {
        try {
            const response = await api.get('/my-recipes');
            setRecipes(response.data.data || response.data);
        } catch (error) {
            console.error('Error:', error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="recipes-page container">
                <div className="loading-state">
                    <div className="spinner"></div>
                    <p>Loading your recipes...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="recipes-page container">
            <div className="page-header">
                <h1 className="page-title">
                    <IoHeartOutline style={{ fontSize: '3rem', marginRight: '1rem', verticalAlign: 'middle', color: 'var(--primary)' }} />
                    My Recipes
                </h1>
                <p className="page-subtitle">
                    Manage your personal recipe collection
                </p>
                <Link to="/recipes/create" className="btn-primary" style={{ marginTop: '1.5rem' }}>
                    <IoAddCircleOutline style={{ fontSize: '1.3rem' }} />
                    Create New Recipe
                </Link>
            </div>

            {recipes.length === 0 ? (
                <div className="empty-state">
                    <div className="empty-state-icon">
                        <IoBookOutline />
                    </div>
                    <h3 className="empty-state-title">No Recipes Yet</h3>
                    <p className="empty-state-description">
                        Start sharing your culinary creations with the community!
                    </p>
                    <Link to="/recipes/create" className="btn-primary">
                        <IoAddCircleOutline style={{ fontSize: '1.3rem' }} />
                        Create Your First Recipe
                    </Link>
                </div>
            ) : (
                <div className="recipes-grid">
                    {recipes.map(recipe => (
                        <div key={recipe.id} className="recipe-card" style={{ cursor: 'default' }}>
                            <div className="recipe-image">
                                <div className="recipe-badge">{recipe.cuisine_type}</div>
                            </div>
                            <div className="recipe-content">
                                <h3 className="recipe-title">{recipe.title}</h3>
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
                                <div style={{ 
                                    display: 'flex', 
                                    gap: 'var(--space-sm)', 
                                    paddingTop: 'var(--space-md)', 
                                    borderTop: '1px solid var(--gray-200)',
                                    marginTop: 'var(--space-md)'
                                }}>
                                    <Link to={`/recipes/${recipe.id}`} className="btn-secondary" style={{ 
                                        flex: 1, 
                                        padding: '0.625rem', 
                                        textAlign: 'center', 
                                        fontSize: '0.875rem',
                                        textDecoration: 'none'
                                    }}>
                                        <IoEyeOutline style={{ fontSize: '1rem' }} />
                                        View
                                    </Link>
                                    <Link to={`/recipes/${recipe.id}/edit`} className="btn-primary" style={{ 
                                        flex: 1, 
                                        padding: '0.625rem', 
                                        textAlign: 'center', 
                                        fontSize: '0.875rem',
                                        textDecoration: 'none'
                                    }}>
                                        <IoCreateOutline style={{ fontSize: '1rem' }} />
                                        Edit
                                    </Link>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
