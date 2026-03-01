import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import ImageCropper from '../components/ImageCropper';
import {
    IoCreateOutline,
    IoAddCircleOutline,
    IoTrashOutline,
    IoArrowBackOutline,
    IoCheckmarkCircleOutline,
    IoRestaurantOutline,
    IoTimeOutline,
    IoImageOutline,
    IoCloseCircleOutline
} from 'react-icons/io5';

export default function RecipeCreate() {
    const { user } = useAuth();
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        title: '',
        short_description: '',
        cuisine_type: '',
        category: '',
        prep_time: '',
        cook_time: '',
        serving_size: '',
        preparation_notes: '',
        ingredients: [{ name: '', measurement: '', substitution_option: '', allergen_info: '' }]
    });
    const [image, setImage] = useState(null);
    const [imagePreview, setImagePreview] = useState(null);
    const [showCropper, setShowCropper] = useState(false);
    const [imageToCrop, setImageToCrop] = useState(null);
    const [originalFileName, setOriginalFileName] = useState('');
    const [errors, setErrors] = useState({});
    const [loading, setLoading] = useState(false);

    if (!user) {
        navigate('/login');
        return null;
    }

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            const formDataToSend = new FormData();
            
            // Append all form fields
            Object.keys(formData).forEach(key => {
                if (key === 'ingredients') {
                    formDataToSend.append(key, JSON.stringify(formData[key]));
                } else {
                    formDataToSend.append(key, formData[key]);
                }
            });
            
            // Append image if exists
            if (image) {
                formDataToSend.append('image', image);
            }
            
            await api.post('/recipes', formDataToSend, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            navigate('/recipes/my-recipes');
        } catch (error) {
            setErrors(error.response?.data?.errors || {});
        } finally {
            setLoading(false);
        }
    };

    const addIngredient = () => {
        setFormData({
            ...formData,
            ingredients: [...formData.ingredients, { name: '', measurement: '', substitution_option: '', allergen_info: '' }]
        });
    };

    const removeIngredient = (index) => {
        const newIngredients = formData.ingredients.filter((_, i) => i !== index);
        setFormData({ ...formData, ingredients: newIngredients });
    };

    const handleImageChange = (e) => {
        const file = e.target.files[0];
        if (file) {
            if (file.size > 5242880) { // 5MB in bytes
                setErrors({ ...errors, image: ['Image size cannot exceed 5MB.'] });
                return;
            }
            
            setOriginalFileName(file.name);
            const reader = new FileReader();
            reader.onloadend = () => {
                setImageToCrop(reader.result);
                setShowCropper(true);
            };
            reader.readAsDataURL(file);
            
            // Clear image error if exists
            if (errors.image) {
                const newErrors = { ...errors };
                delete newErrors.image;
                setErrors(newErrors);
            }
        }
    };

    const handleCropComplete = (croppedBlob) => {
        // Convert blob to file
        const croppedFile = new File([croppedBlob], originalFileName || 'recipe-image.jpg', {
            type: 'image/jpeg',
            lastModified: Date.now()
        });
        
        setImage(croppedFile);
        
        // Create preview URL from blob
        const previewUrl = URL.createObjectURL(croppedBlob);
        setImagePreview(previewUrl);
        
        setShowCropper(false);
        setImageToCrop(null);
    };

    const handleCropCancel = () => {
        setShowCropper(false);
        setImageToCrop(null);
        // Clear the file input
        const fileInput = document.getElementById('recipe-image');
        if (fileInput) fileInput.value = '';
    };

    const removeImage = () => {
        setImage(null);
        setImagePreview(null);
        setImageToCrop(null);
        // Clear the file input
        const fileInput = document.getElementById('recipe-image');
        if (fileInput) fileInput.value = '';
    };

    return (
        <div className="form-page" style={{ alignItems: 'flex-start', paddingTop: 'var(--space-2xl)' }}>
            <div className="form-container wide">
                <div style={{ textAlign: 'center', marginBottom: '2.5rem' }}>
                    <IoCreateOutline style={{ fontSize: '4rem', color: 'var(--primary)', marginBottom: '1rem' }} />
                    <h1 className="form-title">Share Your Recipe</h1>
                    <p className="form-subtitle">Create a new recipe and share it with the community</p>
                </div>
                
                <form onSubmit={handleSubmit}>
                    {/* Basic Information */}
                    <div className="form-group">
                        <label className="form-label">Recipe Title *</label>
                        <input
                            type="text"
                            className="form-input"
                            value={formData.title}
                            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                            placeholder="e.g., Chicken Adobo"
                            required
                        />
                        {errors.title && <div className="error-message">{errors.title[0]}</div>}
                    </div>

                    <div className="form-group">
                        <label className="form-label">Short Description *</label>
                        <textarea
                            className="form-textarea"
                            value={formData.short_description}
                            onChange={(e) => setFormData({ ...formData, short_description: e.target.value })}
                            placeholder="A savory and tangy dish that's perfect for family meals..."
                            rows="3"
                            required
                        />
                    </div>

                    {/* Image Upload Section */}
                    <div className="form-group">
                        <label className="form-label">
                            <IoImageOutline style={{ fontSize: '1.1rem', marginRight: '0.5rem', verticalAlign: 'middle' }} />
                            Recipe Image
                        </label>
                        <div className="image-upload-container">
                            {!imagePreview ? (
                                <label htmlFor="recipe-image" className="image-upload-label">
                                    <IoImageOutline style={{ fontSize: '3rem', color: 'var(--gray-400)' }} />
                                    <span style={{ marginTop: '0.5rem', color: 'var(--gray-600)' }}>Click to upload recipe image</span>
                                    <span style={{ fontSize: '0.85rem', color: 'var(--gray-500)' }}>PNG, JPG, GIF, WEBP up to 5MB</span>
                                </label>
                            ) : (
                                <div className="image-preview-container">
                                    <img src={imagePreview} alt="Recipe preview" className="image-preview" />
                                    <button 
                                        type="button" 
                                        onClick={removeImage}
                                        className="image-remove-btn"
                                    >
                                        <IoCloseCircleOutline />
                                    </button>
                                </div>
                            )}
                            <input
                                id="recipe-image"
                                type="file"
                                accept="image/*"
                                onChange={handleImageChange}
                                style={{ display: 'none' }}
                            />
                        </div>
                        {errors.image && <div className="error-message">{errors.image[0]}</div>}
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 'var(--space-lg)' }}>
                        <div className="form-group">
                            <label className="form-label">Cuisine Type *</label>
                            <input
                                type="text"
                                className="form-input"
                                value={formData.cuisine_type}
                                onChange={(e) => setFormData({ ...formData, cuisine_type: e.target.value })}
                                placeholder="e.g., Filipino"
                                required
                            />
                        </div>
                        <div className="form-group">
                            <label className="form-label">Category *</label>
                            <input
                                type="text"
                                className="form-input"
                                value={formData.category}
                                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                                placeholder="e.g., Ulam (Main Dish)"
                                required
                            />
                        </div>
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: 'var(--space-lg)' }}>
                        <div className="form-group">
                            <label className="form-label">
                                <IoTimeOutline style={{ fontSize: '1.1rem', marginRight: '0.5rem', verticalAlign: 'middle' }} />
                                Prep Time (min) *
                            </label>
                            <input
                                type="number"
                                className="form-input"
                                value={formData.prep_time}
                                onChange={(e) => setFormData({ ...formData, prep_time: e.target.value })}
                                placeholder="15"
                                required
                            />
                        </div>
                        <div className="form-group">
                            <label className="form-label">
                                <IoTimeOutline style={{ fontSize: '1.1rem', marginRight: '0.5rem', verticalAlign: 'middle' }} />
                                Cook Time (min) *
                            </label>
                            <input
                                type="number"
                                className="form-input"
                                value={formData.cook_time}
                                onChange={(e) => setFormData({ ...formData, cook_time: e.target.value })}
                                placeholder="30"
                                required
                            />
                        </div>
                        <div className="form-group">
                            <label className="form-label">
                                <IoRestaurantOutline style={{ fontSize: '1.1rem', marginRight: '0.5rem', verticalAlign: 'middle' }} />
                                Servings *
                            </label>
                            <input
                                type="number"
                                className="form-input"
                                value={formData.serving_size}
                                onChange={(e) => setFormData({ ...formData, serving_size: e.target.value })}
                                placeholder="4"
                                required
                            />
                        </div>
                    </div>

                    {/* Ingredients Section */}
                    <div style={{ 
                        marginTop: 'var(--space-2xl)', 
                        padding: 'var(--space-xl)', 
                        background: 'var(--gray-100)', 
                        borderRadius: 'var(--radius-md)' 
                    }}>
                        <h3 style={{ 
                            fontSize: '1.5rem', 
                            marginBottom: 'var(--space-lg)',
                            display: 'flex',
                            alignItems: 'center',
                            gap: 'var(--space-sm)'
                        }}>
                            <IoRestaurantOutline style={{ color: 'var(--primary)' }} />
                            Ingredients
                        </h3>
                        {formData.ingredients.map((ingredient, index) => (
                            <div key={index} style={{ 
                                background: 'var(--white)', 
                                padding: 'var(--space-lg)', 
                                borderRadius: 'var(--radius-md)', 
                                marginBottom: 'var(--space-md)',
                                border: '2px solid var(--gray-200)'
                            }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-md)' }}>
                                    <span style={{ fontWeight: '600', color: 'var(--gray-700)' }}>Ingredient {index + 1}</span>
                                    {formData.ingredients.length > 1 && (
                                        <button 
                                            type="button" 
                                            onClick={() => removeIngredient(index)}
                                            style={{
                                                background: 'transparent',
                                                border: 'none',
                                                color: 'var(--danger)',
                                                cursor: 'pointer',
                                                padding: '0.5rem',
                                                display: 'flex',
                                                alignItems: 'center',
                                                gap: '0.25rem',
                                                fontSize: '0.9rem'
                                            }}
                                        >
                                            <IoTrashOutline style={{ fontSize: '1.2rem' }} />
                                            Remove
                                        </button>
                                    )}
                                </div>
                                <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 'var(--space-md)' }}>
                                    <div className="form-group" style={{ marginBottom: 0 }}>
                                        <label className="form-label">Ingredient Name *</label>
                                        <input
                                            type="text"
                                            className="form-input"
                                            value={ingredient.name}
                                            onChange={(e) => {
                                                const newIngredients = [...formData.ingredients];
                                                newIngredients[index].name = e.target.value;
                                                setFormData({ ...formData, ingredients: newIngredients });
                                            }}
                                            placeholder="e.g., Soy Sauce (Toyo)"
                                            required
                                        />
                                    </div>
                                    <div className="form-group" style={{ marginBottom: 0 }}>
                                        <label className="form-label">Measurement *</label>
                                        <input
                                            type="text"
                                            className="form-input"
                                            value={ingredient.measurement}
                                            onChange={(e) => {
                                                const newIngredients = [...formData.ingredients];
                                                newIngredients[index].measurement = e.target.value;
                                                setFormData({ ...formData, ingredients: newIngredients });
                                            }}
                                            placeholder="e.g., 1/2 cup"
                                            required
                                        />
                                    </div>
                                </div>
                            </div>
                        ))}
                        <button 
                            type="button" 
                            onClick={addIngredient} 
                            className="btn-secondary"
                            style={{ width: '100%' }}
                        >
                            <IoAddCircleOutline style={{ fontSize: '1.3rem' }} />
                            Add Ingredient
                        </button>
                    </div>

                    {/* Preparation Instructions */}
                    <div className="form-group">
                        <label className="form-label">Preparation Instructions</label>
                        <textarea
                            className="form-textarea"
                            value={formData.preparation_notes}
                            onChange={(e) => setFormData({ ...formData, preparation_notes: e.target.value })}
                            rows="12"
                            placeholder="Step-by-step instructions (e.g., 1. Marinate chicken with toyo and suka for 30 minutes. 2. Sauté garlic in hot oil until golden brown...)"
                            style={{ minHeight: '250px' }}
                        />
                    </div>

                    {/* Action Buttons */}
                    <div className="form-actions">
                        <button 
                            type="button" 
                            onClick={() => navigate('/recipes')} 
                            className="btn-form-cancel"
                        >
                            <IoArrowBackOutline />
                            <span>Cancel</span>
                        </button>
                        <button 
                            type="submit" 
                            className="btn-form-submit" 
                            disabled={loading}
                        >
                            <IoCheckmarkCircleOutline />
                            <span>{loading ? 'Publishing...' : 'Publish Recipe'}</span>
                        </button>
                    </div>
                </form>
            </div>

            {/* Image Cropper Modal */}
            {showCropper && imageToCrop && (
                <ImageCropper
                    image={imageToCrop}
                    onCropComplete={handleCropComplete}
                    onCancel={handleCropCancel}
                />
            )}
        </div>
    );
}
