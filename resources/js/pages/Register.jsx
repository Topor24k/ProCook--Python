import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
    IoPersonOutline, 
    IoMailOutline, 
    IoLockClosedOutline, 
    IoPersonAddOutline,
    IoRestaurantOutline,
    IoCheckmarkCircleOutline
} from 'react-icons/io5';

export default function Register() {
    const { register } = useAuth();
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        password: '',
        password_confirmation: ''
    });
    const [errors, setErrors] = useState({});
    const [loading, setLoading] = useState(false);
    const [success, setSuccess] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setErrors({});
        setLoading(true);
        setSuccess(false);

        try {
            await register(formData.name, formData.email, formData.password, formData.password_confirmation);
            setSuccess(true);
            
            // Show success message for 2 seconds before redirecting
            setTimeout(() => {
                navigate('/');
            }, 2000);
        } catch (err) {
            setErrors(err.response?.data?.errors || { error: ['Registration failed'] });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="form-page">
            <div className="form-container">
                <div style={{ textAlign: 'center', marginBottom: '2.5rem' }}>
                    <IoRestaurantOutline style={{ fontSize: '4rem', color: 'var(--primary)', marginBottom: '1rem' }} />
                    <h1 className="form-title">Join ProCook</h1>
                    <p className="form-subtitle">Create your account and start cooking</p>
                </div>

                {success && (
                    <div className="success-message">
                        <IoCheckmarkCircleOutline style={{ fontSize: '1.5rem', marginRight: '0.5rem' }} />
                        <div>
                            <strong>Account Created Successfully!</strong>
                            <p style={{ marginTop: '0.25rem', fontSize: '0.9rem' }}>Welcome to ProCook! Redirecting you to home...</p>
                        </div>
                    </div>
                )}

                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label className="form-label">
                            <IoPersonOutline style={{ fontSize: '1.1rem', marginRight: '0.5rem', verticalAlign: 'middle' }} />
                            Full Name
                        </label>
                        <input
                            type="text"
                            className="form-input"
                            value={formData.name}
                            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                            placeholder="Enter your full name"
                            required
                        />
                        {errors.name && <div className="error-message">{errors.name[0]}</div>}
                    </div>

                    <div className="form-group">
                        <label className="form-label">
                            <IoMailOutline style={{ fontSize: '1.1rem', marginRight: '0.5rem', verticalAlign: 'middle' }} />
                            Email Address
                        </label>
                        <input
                            type="email"
                            className="form-input"
                            value={formData.email}
                            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                            placeholder="your@email.com"
                            required
                        />
                        {errors.email && <div className="error-message">{errors.email[0]}</div>}
                    </div>

                    <div className="form-group">
                        <label className="form-label">
                            <IoLockClosedOutline style={{ fontSize: '1.1rem', marginRight: '0.5rem', verticalAlign: 'middle' }} />
                            Password
                        </label>
                        <input
                            type="password"
                            className="form-input"
                            value={formData.password}
                            onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                            placeholder="Minimum 8 characters"
                            required
                        />
                        {errors.password && <div className="error-message">{errors.password[0]}</div>}
                    </div>

                    <div className="form-group">
                        <label className="form-label">
                            <IoLockClosedOutline style={{ fontSize: '1.1rem', marginRight: '0.5rem', verticalAlign: 'middle' }} />
                            Confirm Password
                        </label>
                        <input
                            type="password"
                            className="form-input"
                            value={formData.password_confirmation}
                            onChange={(e) => setFormData({ ...formData, password_confirmation: e.target.value })}
                            placeholder="Re-enter your password"
                            required
                        />
                    </div>

                    <button type="submit" className="form-button" disabled={loading}>
                        <IoPersonAddOutline style={{ fontSize: '1.3rem' }} />
                        {loading ? 'Creating Account...' : 'Create Account'}
                    </button>
                </form>

                <div className="form-link">
                    <p>
                        Already have an account? <Link to="/login">Login here</Link>
                    </p>
                </div>
            </div>
        </div>
    );
}
