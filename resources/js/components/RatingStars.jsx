import React, { useState, useEffect } from 'react';
import { IoStar, IoStarOutline } from 'react-icons/io5';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';

export default function RatingStars({ recipeId, recipeOwnerId, size = 'medium', showCount = true, interactive = true }) {
    const { user } = useAuth();
    const [userRating, setUserRating] = useState(null);
    const [averageRating, setAverageRating] = useState(0);
    const [ratingsCount, setRatingsCount] = useState(0);
    const [hoverRating, setHoverRating] = useState(0);
    const [loading, setLoading] = useState(false);
    const [isOwner, setIsOwner] = useState(false);

    useEffect(() => {
        fetchPublicRating();
        if (user) {
            fetchUserRating();
        }
    }, [recipeId, user]);

    const fetchPublicRating = async () => {
        try {
            const response = await api.get(`/recipes/${recipeId}/rating/public`);
            const data = response.data.data;
            setAverageRating(data.averageRating || 0);
            setRatingsCount(data.ratingsCount || 0);
            
            // Check if current user is the recipe owner
            if (user && data.recipeOwnerId === user.id) {
                setIsOwner(true);
            }
        } catch (error) {
            console.error('Error fetching public rating:', error);
        }
    };

    const fetchUserRating = async () => {
        try {
            const response = await api.get(`/recipes/${recipeId}/rating`);
            const data = response.data.data;
            setUserRating(data.userRating);
        } catch (error) {
            console.error('Error fetching user rating:', error);
        }
    };

    const handleRate = async (rating) => {
        if (!interactive || !user || loading || isOwner) return;

        setLoading(true);
        try {
            const response = await api.post(`/recipes/${recipeId}/rating`, { rating });
            const data = response.data.data;
            setUserRating(rating);
            setAverageRating(data.averageRating);
            setRatingsCount(data.ratingsCount);
        } catch (error) {
            console.error('Error submitting rating:', error);
            if (error.response?.status === 403) {
                alert('You cannot rate your own recipe.');
            } else {
                alert('Failed to submit rating. Please try again.');
            }
        } finally {
            setLoading(false);
        }
    };

    const sizeClasses = {
        small: 'text-lg',
        medium: 'text-2xl',
        large: 'text-3xl'
    };

    const displayRating = interactive && user && !isOwner ? (hoverRating || userRating || 0) : averageRating;

    return (
        <div className="rating-stars-container">
            <div 
                className={`rating-stars ${sizeClasses[size]}`}
                onMouseLeave={() => interactive && !isOwner && setHoverRating(0)}
            >
                {[1, 2, 3, 4, 5].map((star) => (
                    <button
                        key={star}
                        className={`star-button ${!interactive || !user || isOwner ? 'non-interactive' : ''}`}
                        onClick={() => handleRate(star)}
                        onMouseEnter={() => interactive && user && !isOwner && setHoverRating(star)}
                        disabled={!interactive || !user || loading || isOwner}
                    >
                        {star <= displayRating ? (
                            <IoStar className="star-filled" />
                        ) : (
                            <IoStarOutline className="star-outline" />
                        )}
                    </button>
                ))}
            </div>
            {showCount && (
                <div className="rating-info">
                    <span className="rating-average">{averageRating.toFixed(1)}</span>
                    <span className="rating-count">({ratingsCount} {ratingsCount === 1 ? 'rating' : 'ratings'})</span>
                </div>
            )}
            {interactive && user && userRating && !isOwner && (
                <div className="user-rating-label">Your rating: {userRating} stars</div>
            )}
        </div>
    );
}
