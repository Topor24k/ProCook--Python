import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import {
    IoPersonAddOutline,
    IoLogInOutline,
    IoCloseOutline,
    IoLockClosedOutline
} from 'react-icons/io5';

export default function AuthPrompt({ isOpen, onClose }) {
    if (!isOpen) return null;

    return (
        <div className="auth-prompt-overlay" onClick={onClose}>
            <div className="auth-prompt-modal" onClick={(e) => e.stopPropagation()}>
                <button className="auth-prompt-close" onClick={onClose}>
                    <IoCloseOutline />
                </button>
                
                <div className="auth-prompt-content">
                    <div className="auth-prompt-icon">
                        <IoLockClosedOutline />
                    </div>
                    
                    <h2 className="auth-prompt-title">Authentication Required</h2>
                    
                    <div className="auth-prompt-actions">
                        <Link to="/register" className="btn-primary" onClick={onClose}>
                            <IoPersonAddOutline style={{ fontSize: '1.1rem' }} />
                            Sign Up
                        </Link>
                        <Link to="/login" className="btn-secondary" onClick={onClose}>
                            <IoLogInOutline style={{ fontSize: '1.1rem' }} />
                            Login
                        </Link>
                    </div>
                    
                    <p className="auth-prompt-note">
                        Join our community to access all features and share your culinary creations!
                    </p>
                </div>
            </div>
        </div>
    );
}