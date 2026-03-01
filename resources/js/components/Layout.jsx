import React, { useState } from 'react';
import { Link, Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
    IoRestaurantOutline, 
    IoHomeOutline, 
    IoBookOutline, 
    IoAddCircleOutline,
    IoLogOutOutline,
    IoLogInOutline,
    IoPersonAddOutline,
    IoPersonOutline,
    IoHeartOutline,
    IoBookmarkOutline,
    IoMailOutline,
    IoLogoFacebook,
    IoLogoTwitter,
    IoLogoInstagram,
    IoChevronDownOutline,
    IoInformationCircleOutline,
    IoDocumentTextOutline,
    IoShieldCheckmarkOutline,
    IoHelpCircleOutline
} from 'react-icons/io5';

export default function Layout() {
    const { user, logout, isAuthenticated } = useAuth();
    const navigate = useNavigate();
    const [contactDropdownOpen, setContactDropdownOpen] = useState(false);
    const [userDropdownOpen, setUserDropdownOpen] = useState(false);

    const handleLogout = async () => {
        await logout();
        navigate('/');
        setUserDropdownOpen(false);
    };

    return (
        <div className="app-container">
            {/* Premium Header */}
            <header className="modern-header">
                <div className="header-content">
                    <Link to="/" className="logo">
                        <IoRestaurantOutline className="logo-icon" />
                        <span className="logo-text">ProCook</span>
                    </Link>

                    <nav className="main-nav">
                        <Link to="/" className="nav-link">
                            <IoHomeOutline style={{ fontSize: '1.2rem' }} />
                            <span>Home</span>
                        </Link>
                        <Link to="/recipes" className="nav-link">
                            <IoBookOutline style={{ fontSize: '1.2rem' }} />
                            <span>Recipes</span>
                        </Link>
                        <Link to="/about" className="nav-link">
                            <IoInformationCircleOutline style={{ fontSize: '1.2rem' }} />
                            <span>About Us</span>
                        </Link>
                        <div 
                            className="nav-dropdown"
                            onMouseEnter={() => setContactDropdownOpen(true)}
                            onMouseLeave={() => setContactDropdownOpen(false)}
                        >
                            <button className="nav-link dropdown-toggle">
                                <IoMailOutline style={{ fontSize: '1.2rem' }} />
                                <span>Contact</span>
                                <IoChevronDownOutline style={{ fontSize: '0.9rem' }} />
                            </button>
                            {contactDropdownOpen && (
                                <div className="dropdown-menu">
                                    <a href="#terms" className="dropdown-item">
                                        <IoDocumentTextOutline /> Terms of Service
                                    </a>
                                    <a href="#privacy" className="dropdown-item">
                                        <IoShieldCheckmarkOutline /> Privacy Policy
                                    </a>
                                    <a href="#help" className="dropdown-item">
                                        <IoHelpCircleOutline /> Help Center
                                    </a>
                                </div>
                            )}
                        </div>
                        {isAuthenticated && (
                            <Link to="/recipes/my-recipes" className="nav-link">
                                <IoHeartOutline style={{ fontSize: '1.2rem' }} />
                                <span>My Recipes</span>
                            </Link>
                        )}
                    </nav>

                    <div className="auth-actions">
                        {isAuthenticated ? (
                            <div 
                                className="user-dropdown"
                                onMouseEnter={() => setUserDropdownOpen(true)}
                                onMouseLeave={() => setUserDropdownOpen(false)}
                            >
                                <button className="user-button">
                                    <IoPersonOutline style={{ fontSize: '1.1rem', marginRight: '0.25rem' }} />
                                    {user?.name}
                                    <IoChevronDownOutline style={{ fontSize: '0.9rem', marginLeft: '0.25rem' }} />
                                </button>
                                {userDropdownOpen && (
                                    <div className="dropdown-menu user-menu-dropdown">
                                        <Link to="/profile" className="dropdown-item" onClick={() => setUserDropdownOpen(false)}>
                                            <IoPersonOutline /> My Profile
                                        </Link>
                                        <Link to="/recipes/my-recipes" className="dropdown-item" onClick={() => setUserDropdownOpen(false)}>
                                            <IoHeartOutline /> My Recipes
                                        </Link>
                                        <Link to="/recipes/saved" className="dropdown-item" onClick={() => setUserDropdownOpen(false)}>
                                            <IoBookmarkOutline /> Saved Recipes
                                        </Link>
                                        <Link to="/recipes/create" className="dropdown-item" onClick={() => setUserDropdownOpen(false)}>
                                            <IoAddCircleOutline /> Create Recipe
                                        </Link>
                                        <button onClick={handleLogout} className="dropdown-item logout-item">
                                            <IoLogOutOutline /> Logout
                                        </button>
                                    </div>
                                )}
                            </div>
                        ) : (
                            <>
                                <Link to="/login" className="btn-secondary">
                                    <IoLogInOutline style={{ fontSize: '1.1rem' }} />
                                    Login
                                </Link>
                                <Link to="/register" className="btn-primary">
                                    <IoPersonAddOutline style={{ fontSize: '1.1rem' }} />
                                    Sign Up
                                </Link>
                            </>
                        )}
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="main-content">
                <Outlet />
            </main>

            {/* Premium Footer */}
            <footer className="modern-footer">
                <div className="footer-content">
                    <div className="footer-section">
                        <h3>
                            <IoRestaurantOutline style={{ fontSize: '1.8rem', marginBottom: '0.5rem' }} />
                            ProCook
                        </h3>
                        <p>Discover, create, and share amazing recipes with food lovers worldwide. Join our community of passionate cooks and culinary enthusiasts.</p>
                        <div style={{ display: 'flex', gap: '1rem', marginTop: '1.5rem' }}>
                            <a href="#" style={{ fontSize: '1.5rem', display: 'inline' }}>
                                <IoLogoFacebook />
                            </a>
                            <a href="#" style={{ fontSize: '1.5rem', display: 'inline' }}>
                                <IoLogoTwitter />
                            </a>
                            <a href="#" style={{ fontSize: '1.5rem', display: 'inline' }}>
                                <IoLogoInstagram />
                            </a>
                        </div>
                    </div>
                    <div className="footer-section">
                        <h4>Quick Links</h4>
                        <Link to="/recipes">Browse Recipes</Link>
                        <Link to="/recipes/create">Create Recipe</Link>
                        {isAuthenticated && <Link to="/recipes/my-recipes">My Recipes</Link>}
                        <a href="#">Recipe Collections</a>
                        <a href="#">Popular</a>
                    </div>
                    <div className="footer-section">
                        <h4>Community</h4>
                        <Link to="/about">About Us</Link>
                        <a href="#">Contact</a>
                        <a href="#">Terms of Service</a>
                        <a href="#">Privacy Policy</a>
                        <a href="#">Help Center</a>
                    </div>
                    <div className="footer-section">
                        <h4>Newsletter</h4>
                        <p style={{ fontSize: '0.9rem', marginBottom: '1rem' }}>
                            Stay updated with the latest recipes and culinary tips!
                        </p>
                        <div style={{ display: 'flex', gap: '0.5rem' }}>
                            <input 
                                type="email" 
                                placeholder="Your email" 
                                style={{
                                    flex: 1,
                                    padding: '0.625rem 0.875rem',
                                    borderRadius: '6px',
                                    border: '1px solid var(--gray-700)',
                                    background: 'var(--gray-800)',
                                    color: 'var(--gray-300)',
                                    fontSize: '0.875rem'
                                }}
                            />
                            <button style={{
                                padding: '0.625rem 1rem',
                                borderRadius: '6px',
                                border: 'none',
                                background: 'var(--primary)',
                                color: 'white',
                                cursor: 'pointer',
                                fontWeight: '600'
                            }}>
                                <IoMailOutline style={{ fontSize: '1.2rem' }} />
                            </button>
                        </div>
                    </div>
                </div>
                <div className="footer-bottom">
                    <p>&copy; 2026 ProCook. All rights reserved. Made with <IoHeartOutline style={{ display: 'inline', verticalAlign: 'middle', color: 'var(--primary)' }} /> for food lovers.</p>
                </div>
            </footer>
        </div>
    );
}
