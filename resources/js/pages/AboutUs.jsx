import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
    IoHeartOutline,
    IoPeopleOutline,
    IoRestaurantOutline,
    IoGlobeOutline,
    IoSparklesOutline,
    IoBookOutline,
    IoCreateOutline,
    IoShareSocialOutline,
    IoWarningOutline,
    IoCloseOutline
} from 'react-icons/io5';

export default function AboutUs() {
    const { isAuthenticated } = useAuth();
    const navigate = useNavigate();
    const [showModal, setShowModal] = useState(false);

    const handleJoinCommunity = () => {
        if (isAuthenticated) {
            setShowModal(true);
        } else {
            navigate('/register');
        }
    };

    return (
        <div className="about-us-page">
            {/* Hero Section */}
            <section className="about-hero">
                <div className="container">
                    <div className="about-hero-content">
                        <h1 className="about-title">
                            Welcome to Our <span className="gradient-text">Culinary Community</span>
                        </h1>
                        <p className="about-subtitle">
                            A place built for food lovers from all walks of life
                        </p>
                    </div>
                </div>
            </section>

            {/* Mission Section */}
            <section className="about-mission">
                <div className="container">
                    <div className="mission-content">
                        <div className="mission-icon">
                            <IoHeartOutline />
                        </div>
                        <h2>Our Mission</h2>
                        <p className="lead-text">
                            We believe food is more than just sustenance — it's a language of love, 
                            culture, and creativity that connects us all. Our mission is to create a 
                            welcoming space where everyone can share their culinary journey without 
                            fear of judgment.
                        </p>
                    </div>
                </div>
            </section>

            {/* Values Section */}
            <section className="about-values">
                <div className="container">
                    <h2 className="section-title">What We Stand For</h2>
                    <div className="values-grid">
                        <div className="value-card">
                            <div className="value-icon">
                                <IoCreateOutline />
                            </div>
                            <h3>Creative Expression</h3>
                            <p>
                                Whether you have a unique recipe inspired by family traditions or a 
                                simple favorite dish, this platform allows you to express your culinary 
                                ideas freely and creatively.
                            </p>
                        </div>

                        <div className="value-card">
                            <div className="value-icon">
                                <IoShareSocialOutline />
                            </div>
                            <h3>Share Without Judgment</h3>
                            <p>
                                Every recipe has a story, and every cook has a voice. We've created a 
                                safe space where you can share your passion for food without hesitation 
                                or criticism.
                            </p>
                        </div>

                        <div className="value-card">
                            <div className="value-icon">
                                <IoBookOutline />
                            </div>
                            <h3>Learn & Grow</h3>
                            <p>
                                It's not just about sharing — it's about learning. Explore a diverse range 
                                of dishes and cooking styles from food enthusiasts around the world.
                            </p>
                        </div>

                        <div className="value-card">
                            <div className="value-icon">
                                <IoGlobeOutline />
                            </div>
                            <h3>Global Community</h3>
                            <p>
                                Each post, tip, and recipe is an opportunity to expand your palate, discover 
                                new flavors, and gain inspiration from diverse culinary experiences.
                            </p>
                        </div>

                        <div className="value-card">
                            <div className="value-icon">
                                <IoPeopleOutline />
                            </div>
                            <h3>Supportive Environment</h3>
                            <p>
                                Our goal is to foster a vibrant, supportive community where curiosity meets 
                                creativity, and where every food lover can find a place to belong.
                            </p>
                        </div>

                        <div className="value-card">
                            <div className="value-icon">
                                <IoSparklesOutline />
                            </div>
                            <h3>For Everyone</h3>
                            <p>
                                Whether you're a seasoned chef, a home cook, or someone who simply enjoys 
                                exploring different tastes, this is your space to connect, learn, and grow.
                            </p>
                        </div>
                    </div>
                </div>
            </section>

            {/* Story Section */}
            <section className="about-story">
                <div className="container">
                    <div className="story-grid">
                        <div className="story-image">
                            <img src="/Family.jpg" alt="ProCook Community" className="story-img" />
                        </div>
                        <div className="story-content">
                            <h2>A Place to Belong</h2>
                            <p>
                                The idea behind this website is to create more than just a recipe repository — 
                                we're building a home for food lovers everywhere. A place where you can:
                            </p>
                            <ul className="story-list">
                                <li>
                                    <IoHeartOutline className="list-icon" />
                                    <span>Share recipes inspired by your heritage and personal experiences</span>
                                </li>
                                <li>
                                    <IoGlobeOutline className="list-icon" />
                                    <span>Discover authentic dishes from cultures around the world</span>
                                </li>
                                <li>
                                    <IoPeopleOutline className="list-icon" />
                                    <span>Connect with fellow food enthusiasts who share your passion</span>
                                </li>
                                <li>
                                    <IoBookOutline className="list-icon" />
                                    <span>Learn new techniques and expand your culinary horizons</span>
                                </li>
                                <li>
                                    <IoSparklesOutline className="list-icon" />
                                    <span>Find inspiration for your next kitchen adventure</span>
                                </li>
                            </ul>
                        </div>
                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section className="about-cta">
                <div className="container">
                    <div className="cta-content">
                        <h2>Ready to Join Our Community?</h2>
                        <p>
                            Connect, learn, and grow together through the universal love of food. 
                            Start sharing your culinary journey today.
                        </p>
                        <div className="cta-buttons">
                            <button onClick={handleJoinCommunity} className="btn-hero-primary">
                                <IoPeopleOutline style={{ fontSize: '1.3rem' }} />
                                Join the Community
                            </button>
                            <Link to="/recipes" className="btn-hero-secondary">
                                <IoRestaurantOutline style={{ fontSize: '1.3rem' }} />
                                Explore Recipes
                            </Link>
                        </div>
                    </div>
                </div>
            </section>

            {/* Confirmation Modal */}
            {showModal && (
                <div className="modal-overlay" onClick={() => setShowModal(false)}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <button className="modal-close" onClick={() => setShowModal(false)}>
                            <IoCloseOutline />
                        </button>
                        <div className="modal-icon warning">
                            <IoWarningOutline />
                        </div>
                        <h3 className="modal-title">Already a Member!</h3>
                        <p className="modal-message">
                            You have already made an account. Would you like to create a new one?
                        </p>
                        <div className="modal-actions">
                            <button 
                                className="btn-secondary"
                                onClick={() => setShowModal(false)}
                            >
                                Cancel
                            </button>
                            <button 
                                className="btn-primary"
                                onClick={() => {
                                    setShowModal(false);
                                    navigate('/register');
                                }}
                            >
                                Create New Account
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
