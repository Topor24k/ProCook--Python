import React, { useState, useEffect } from 'react';
import { IoBookmark, IoBookmarkOutline } from 'react-icons/io5';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';

export default function SaveButton({ recipeId, size = 'medium', showLabel = true, onSaveChange }) {
    const { user } = useAuth();
    const [isSaved, setIsSaved] = useState(false);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (user) {
            checkSavedStatus();
        }
    }, [recipeId, user]);

    const checkSavedStatus = async () => {
        try {
            const response = await api.get(`/recipes/${recipeId}/saved`);
            setIsSaved(response.data.data.isSaved);
        } catch (error) {
            console.error('Error checking saved status:', error);
        }
    };

    const handleToggleSave = async () => {
        if (!user) {
            alert('Please login to save recipes');
            return;
        }

        if (loading) return;

        setLoading(true);
        try {
            const response = await api.post(`/recipes/${recipeId}/save`);
            const newStatus = response.data.data.isSaved;
            setIsSaved(newStatus);
            
            if (onSaveChange) {
                onSaveChange(newStatus);
            }
        } catch (error) {
            console.error('Error toggling save:', error);
            alert('Failed to save recipe. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const sizeClasses = {
        small: 'text-lg',
        medium: 'text-xl',
        large: 'text-2xl'
    };

    if (!user) {
        return null; // Don't show save button if not logged in
    }

    return (
        <button
            className={`save-button ${isSaved ? 'saved' : ''} ${sizeClasses[size]}`}
            onClick={handleToggleSave}
            disabled={loading}
            title={isSaved ? 'Unsave recipe' : 'Save recipe'}
        >
            {isSaved ? (
                <IoBookmark className="save-icon saved" />
            ) : (
                <IoBookmarkOutline className="save-icon" />
            )}
            {showLabel && (
                <span className="save-label">
                    {isSaved ? 'Saved' : 'Save'}
                </span>
            )}
        </button>
    );
}
