import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';

const TABS = [
    { id: 'overview', label: 'Overview' },
    { id: 'security', label: 'Security' },
    { id: 'danger', label: 'Danger Zone' },
];

export default function Profile() {
    const { user, logout, clearUser, isAuthenticated } = useAuth();
    const navigate = useNavigate();

    // Profile data
    const [profile, setProfile] = useState(null);
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);

    // Active tab
    const [activeTab, setActiveTab] = useState('overview');

    // Edit mode
    const [editing, setEditing] = useState(false);
    const [editForm, setEditForm] = useState({ name: '', email: '' });
    const [editErrors, setEditErrors] = useState({});
    const [editLoading, setEditLoading] = useState(false);
    const [editSuccess, setEditSuccess] = useState(false);

    // Change password
    const [showPasswordForm, setShowPasswordForm] = useState(false);
    const [passwordForm, setPasswordForm] = useState({
        current_password: '',
        password: '',
        password_confirmation: ''
    });
    const [passwordErrors, setPasswordErrors] = useState({});
    const [passwordLoading, setPasswordLoading] = useState(false);
    const [passwordSuccess, setPasswordSuccess] = useState(false);

    // Delete account modal
    const [showDeleteModal, setShowDeleteModal] = useState(false);
    const [deleteMode, setDeleteMode] = useState('');
    const [deletePassword, setDeletePassword] = useState('');
    const [deleteErrors, setDeleteErrors] = useState({});
    const [deleteLoading, setDeleteLoading] = useState(false);

    useEffect(() => {
        if (!isAuthenticated) {
            navigate('/login');
            return;
        }
        fetchProfile();
    }, [isAuthenticated]);

    const fetchProfile = async () => {
        try {
            const response = await api.get('/profile');
            setProfile(response.data.data.user);
            setStats(response.data.data.stats);
            setEditForm({
                name: response.data.data.user.name,
                email: response.data.data.user.email
            });
        } catch (error) {
            console.error('Error fetching profile:', error);
        } finally {
            setLoading(false);
        }
    };

    // --- Edit Profile ---
    const handleEditSubmit = async (e) => {
        e.preventDefault();
        setEditErrors({});
        setEditLoading(true);
        setEditSuccess(false);

        try {
            const response = await api.put('/profile', editForm);
            setProfile(response.data.data);
            setEditing(false);
            setEditSuccess(true);
            setTimeout(() => setEditSuccess(false), 3000);
        } catch (err) {
            setEditErrors(err.response?.data?.errors || { error: ['Failed to update profile.'] });
        } finally {
            setEditLoading(false);
        }
    };

    const cancelEdit = () => {
        setEditing(false);
        setEditErrors({});
        setEditForm({ name: profile.name, email: profile.email });
    };

    // --- Change Password ---
    const handlePasswordSubmit = async (e) => {
        e.preventDefault();
        setPasswordErrors({});
        setPasswordLoading(true);
        setPasswordSuccess(false);

        try {
            await api.put('/profile/password', passwordForm);
            setPasswordSuccess(true);
            setPasswordForm({ current_password: '', password: '', password_confirmation: '' });
            setTimeout(() => {
                setPasswordSuccess(false);
                setShowPasswordForm(false);
            }, 3000);
        } catch (err) {
            setPasswordErrors(err.response?.data?.errors || { error: ['Failed to change password.'] });
        } finally {
            setPasswordLoading(false);
        }
    };

    // --- Delete Account ---
    const openDeleteModal = (mode) => {
        setDeleteMode(mode);
        setDeletePassword('');
        setDeleteErrors({});
        setShowDeleteModal(true);
    };

    const handleDeleteAccount = async () => {
        setDeleteErrors({});
        setDeleteLoading(true);

        try {
            await api.delete('/profile', {
                data: {
                    password: deletePassword,
                    mode: deleteMode
                }
            });
            setShowDeleteModal(false);
            clearUser();
            navigate('/', { replace: true });
        } catch (err) {
            setDeleteErrors(err.response?.data?.errors || { password: [err.response?.data?.message || 'Failed to delete account.'] });
        } finally {
            setDeleteLoading(false);
        }
    };

    // --- Helpers ---
    const getInitials = (name) => {
        if (!name) return '?';
        return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
    };

    const memberSince = profile?.created_at
        ? new Date(profile.created_at).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
        : '—';

    const totalContributions = stats
        ? stats.recipes_count + stats.comments_count + stats.ratings_count
        : 0;

    // --- Loading skeleton ---
    if (loading) {
        return (
            <div className="profile-page">
                <div className="profile-cover">
                    <div className="profile-cover-gradient"></div>
                    <div className="profile-cover-content container">
                        <div className="profile-identity">
                            <div className="profile-avatar profile-skeleton-avatar">&nbsp;</div>
                            <div className="profile-headline">
                                <div className="skeleton-line skeleton-w200 skeleton-h24"></div>
                                <div className="skeleton-line skeleton-w160 skeleton-h14"></div>
                                <div className="skeleton-line skeleton-w120 skeleton-h12"></div>
                            </div>
                        </div>
                    </div>
                </div>
                <div className="profile-body container">
                    <div className="profile-skeleton-cards">
                        <div className="profile-card skeleton-card"></div>
                        <div className="profile-card skeleton-card"></div>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="profile-page">

            {/* ════════════ Cover Header ════════════ */}
            <div className="profile-cover">
                <div className="profile-cover-gradient"></div>
                <div className="profile-cover-pattern"></div>
                <div className="profile-cover-content container">
                    <div className="profile-identity">
                        <div className="profile-avatar-wrapper">
                            <div className="profile-avatar">
                                {getInitials(profile?.name)}
                            </div>
                            <div className="profile-avatar-ring"></div>
                        </div>
                        <div className="profile-headline">
                            <h1 className="profile-name">{profile?.name}</h1>
                            <p className="profile-email">{profile?.email}</p>
                            <p className="profile-joined">Member since {memberSince}</p>
                        </div>
                    </div>

                    {/* Stats Bar */}
                    {stats && (
                        <div className="profile-stats-bar">
                            <div className="profile-stat-item">
                                <span className="profile-stat-num">{stats.recipes_count}</span>
                                <span className="profile-stat-label">Recipes</span>
                            </div>
                            <div className="profile-stat-divider"></div>
                            <div className="profile-stat-item">
                                <span className="profile-stat-num">{stats.comments_count}</span>
                                <span className="profile-stat-label">Comments</span>
                            </div>
                            <div className="profile-stat-divider"></div>
                            <div className="profile-stat-item">
                                <span className="profile-stat-num">{stats.ratings_count}</span>
                                <span className="profile-stat-label">Ratings</span>
                            </div>
                            <div className="profile-stat-divider"></div>
                            <div className="profile-stat-item">
                                <span className="profile-stat-num">{stats.saved_count}</span>
                                <span className="profile-stat-label">Saved</span>
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {/* ════════════ Tab Navigation ════════════ */}
            <div className="profile-tabs-wrapper">
                <div className="profile-tabs container">
                    {TABS.map(tab => (
                        <button
                            key={tab.id}
                            className={`profile-tab ${activeTab === tab.id ? 'profile-tab--active' : ''} ${tab.id === 'danger' ? 'profile-tab--danger' : ''}`}
                            onClick={() => setActiveTab(tab.id)}
                        >
                            {tab.label}
                        </button>
                    ))}
                </div>
            </div>

            {/* ════════════ Content Body ════════════ */}
            <div className="profile-body container">

                {/* Success toast */}
                {editSuccess && (
                    <div className="profile-toast profile-toast--success">
                        <span className="profile-toast-dot"></span>
                        Profile updated successfully!
                    </div>
                )}

                <div className="profile-grid">

                    {/* ──── Left Sidebar ──── */}
                    <div className="profile-sidebar">
                        {/* Activity Summary Card */}
                        <div className="profile-card profile-card--activity">
                            <div className="profile-card-header">
                                <h2>Activity</h2>
                            </div>
                            <div className="activity-summary">
                                <div className="activity-total">
                                    <span className="activity-total-num">{totalContributions}</span>
                                    <span className="activity-total-label">Total contributions</span>
                                </div>
                                <div className="activity-bars">
                                    {stats && [
                                        { label: 'Recipes', count: stats.recipes_count, color: 'var(--primary)' },
                                        { label: 'Comments', count: stats.comments_count, color: 'var(--info)' },
                                        { label: 'Ratings', count: stats.ratings_count, color: 'var(--accent)' },
                                        { label: 'Saved', count: stats.saved_count, color: 'var(--warning)' },
                                    ].map(item => (
                                        <div className="activity-bar-row" key={item.label}>
                                            <div className="activity-bar-header">
                                                <span className="activity-bar-label">{item.label}</span>
                                                <span className="activity-bar-count">{item.count}</span>
                                            </div>
                                            <div className="activity-bar-track">
                                                <div
                                                    className="activity-bar-fill"
                                                    style={{
                                                        width: totalContributions > 0
                                                            ? `${Math.max((item.count / Math.max(totalContributions, 1)) * 100, item.count > 0 ? 6 : 0)}%`
                                                            : '0%',
                                                        backgroundColor: item.color
                                                    }}
                                                ></div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* ──── Right Main ──── */}
                    <div className="profile-main">

                        {/* ▸ Overview Tab */}
                        {activeTab === 'overview' && (
                            <div className="profile-tab-content">
                                <div className="profile-card">
                                    <div className="profile-card-header">
                                        <h2>Account Information</h2>
                                        {!editing && (
                                            <button className="btn-secondary btn-sm" onClick={() => setEditing(true)}>
                                                Edit Profile
                                            </button>
                                        )}
                                    </div>

                                    {editing ? (
                                        <form onSubmit={handleEditSubmit} className="profile-edit-form">
                                            <div className="form-group">
                                                <label className="form-label">Full Name</label>
                                                <input
                                                    type="text"
                                                    className="form-input"
                                                    value={editForm.name}
                                                    onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
                                                    placeholder="Enter your full name"
                                                    required
                                                />
                                                {editErrors.name && <div className="error-message">{editErrors.name[0]}</div>}
                                            </div>

                                            <div className="form-group">
                                                <label className="form-label">Email Address</label>
                                                <input
                                                    type="email"
                                                    className="form-input"
                                                    value={editForm.email}
                                                    onChange={(e) => setEditForm({ ...editForm, email: e.target.value })}
                                                    placeholder="your@email.com"
                                                    required
                                                />
                                                {editErrors.email && <div className="error-message">{editErrors.email[0]}</div>}
                                            </div>

                                            <div className="profile-edit-actions">
                                                <button type="submit" className="btn-primary" disabled={editLoading}>
                                                    {editLoading ? 'Saving...' : 'Save Changes'}
                                                </button>
                                                <button type="button" className="btn-secondary" onClick={cancelEdit}>
                                                    Cancel
                                                </button>
                                            </div>
                                        </form>
                                    ) : (
                                        <div className="profile-info-grid">
                                            <div className="profile-info-item">
                                                <span className="profile-info-label">Name</span>
                                                <span className="profile-info-value">{profile?.name}</span>
                                            </div>
                                            <div className="profile-info-item">
                                                <span className="profile-info-label">Email</span>
                                                <span className="profile-info-value">{profile?.email}</span>
                                            </div>
                                            <div className="profile-info-item">
                                                <span className="profile-info-label">Member Since</span>
                                                <span className="profile-info-value">{memberSince}</span>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </div>
                        )}

                        {/* ▸ Security Tab */}
                        {activeTab === 'security' && (
                            <div className="profile-tab-content">
                                <div className="profile-card">
                                    <div className="profile-card-header">
                                        <h2>Password</h2>
                                        {!showPasswordForm && (
                                            <button className="btn-secondary btn-sm" onClick={() => setShowPasswordForm(true)}>
                                                Change Password
                                            </button>
                                        )}
                                    </div>

                                    {passwordSuccess && (
                                        <div className="profile-toast profile-toast--success" style={{ position: 'relative', marginBottom: '1rem' }}>
                                            <span className="profile-toast-dot"></span>
                                            Password changed successfully!
                                        </div>
                                    )}

                                    {showPasswordForm ? (
                                        <form onSubmit={handlePasswordSubmit} className="profile-edit-form">
                                            <div className="form-group">
                                                <label className="form-label">Current Password</label>
                                                <input
                                                    type="password"
                                                    className="form-input"
                                                    value={passwordForm.current_password}
                                                    onChange={(e) => setPasswordForm({ ...passwordForm, current_password: e.target.value })}
                                                    placeholder="Enter current password"
                                                    required
                                                />
                                                {passwordErrors.current_password && <div className="error-message">{passwordErrors.current_password[0]}</div>}
                                            </div>

                                            <div className="form-group">
                                                <label className="form-label">New Password</label>
                                                <input
                                                    type="password"
                                                    className="form-input"
                                                    value={passwordForm.password}
                                                    onChange={(e) => setPasswordForm({ ...passwordForm, password: e.target.value })}
                                                    placeholder="Minimum 8 characters"
                                                    required
                                                />
                                                {passwordErrors.password && <div className="error-message">{passwordErrors.password[0]}</div>}
                                            </div>

                                            <div className="form-group">
                                                <label className="form-label">Confirm New Password</label>
                                                <input
                                                    type="password"
                                                    className="form-input"
                                                    value={passwordForm.password_confirmation}
                                                    onChange={(e) => setPasswordForm({ ...passwordForm, password_confirmation: e.target.value })}
                                                    placeholder="Re-enter new password"
                                                    required
                                                />
                                            </div>

                                            <div className="profile-edit-actions">
                                                <button type="submit" className="btn-primary" disabled={passwordLoading}>
                                                    {passwordLoading ? 'Changing...' : 'Change Password'}
                                                </button>
                                                <button type="button" className="btn-secondary" onClick={() => {
                                                    setShowPasswordForm(false);
                                                    setPasswordErrors({});
                                                    setPasswordForm({ current_password: '', password: '', password_confirmation: '' });
                                                }}>
                                                    Cancel
                                                </button>
                                            </div>
                                        </form>
                                    ) : !passwordSuccess ? (
                                        <div className="security-info">
                                            <p className="profile-card-hint">
                                                Keep your account safe by using a strong, unique password that you don't use on other sites.
                                            </p>
                                            <div className="security-checklist">
                                                <div className="security-check-item">
                                                    <span className="security-check-icon">&#10003;</span>
                                                    <span>Use at least 8 characters</span>
                                                </div>
                                                <div className="security-check-item">
                                                    <span className="security-check-icon">&#10003;</span>
                                                    <span>Include uppercase and lowercase letters</span>
                                                </div>
                                                <div className="security-check-item">
                                                    <span className="security-check-icon">&#10003;</span>
                                                    <span>Add numbers and special characters</span>
                                                </div>
                                            </div>
                                        </div>
                                    ) : null}
                                </div>
                            </div>
                        )}

                        {/* ▸ Danger Zone Tab */}
                        {activeTab === 'danger' && (
                            <div className="profile-tab-content">
                                <div className="profile-card danger-zone">
                                    <div className="profile-card-header">
                                        <h2>Delete Your Account</h2>
                                    </div>

                                    <p className="danger-description">
                                        Deleting your account is permanent and cannot be undone. Please review the options below carefully before proceeding.
                                    </p>

                                    <div className="delete-options">
                                        <div className="delete-option-card delete-option-card--destructive">
                                            <div className="delete-option-badge delete-option-badge--red">Permanent</div>
                                            <h3>Delete Everything</h3>
                                            <p>
                                                Remove your account and <strong>all associated content</strong> — recipes, comments, ratings, and saved items.
                                            </p>
                                            {stats && (
                                                <div className="delete-impact">
                                                    <span>{stats.recipes_count} recipes</span>
                                                    <span>{stats.comments_count} comments</span>
                                                    <span>{stats.ratings_count} ratings</span>
                                                    <span>{stats.saved_count} saved</span>
                                                </div>
                                            )}
                                            <button className="btn-danger" onClick={() => openDeleteModal('delete_all')}>
                                                Delete Account &amp; All Data
                                            </button>
                                        </div>

                                        <div className="delete-option-card delete-option-card--soft">
                                            <div className="delete-option-badge delete-option-badge--amber">Partial</div>
                                            <h3>Delete Account Only</h3>
                                            <p>
                                                Remove your account but <strong>preserve your content</strong> for the community. Items will appear as from a deleted user.
                                            </p>
                                            <button className="btn-warning" onClick={() => openDeleteModal('keep_data')}>
                                                Delete Account Only
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}

                    </div>
                </div>
            </div>

            {/* ════════════ Delete Modal ════════════ */}
            {showDeleteModal && (
                <div className="modal-overlay" onClick={() => !deleteLoading && setShowDeleteModal(false)}>
                    <div className="modal-content profile-delete-modal" onClick={(e) => e.stopPropagation()}>
                        <button
                            className="modal-close"
                            onClick={() => !deleteLoading && setShowDeleteModal(false)}
                        >
                            &times;
                        </button>

                        <div className={`profile-modal-icon ${deleteMode === 'delete_all' ? 'profile-modal-icon--red' : 'profile-modal-icon--amber'}`}>
                            {deleteMode === 'delete_all' ? '!!' : '!'}
                        </div>

                        <h2 className="modal-title">
                            {deleteMode === 'delete_all' ? 'Delete Account & All Data?' : 'Delete Account Only?'}
                        </h2>

                        <p className="modal-message">
                            {deleteMode === 'delete_all'
                                ? 'This will permanently destroy your account and every piece of content you created — recipes, comments, ratings, and saved items. This cannot be reversed.'
                                : 'Your account will be permanently deleted. Your content (recipes, comments, ratings) will remain visible but shown as from a deleted user.'
                            }
                        </p>

                        <div className="form-group" style={{ textAlign: 'left', width: '100%' }}>
                            <label className="form-label">Type your password to confirm</label>
                            <input
                                type="password"
                                className="form-input"
                                value={deletePassword}
                                onChange={(e) => setDeletePassword(e.target.value)}
                                placeholder="Enter your password"
                                required
                            />
                            {deleteErrors.password && <div className="error-message">{deleteErrors.password[0]}</div>}
                        </div>

                        <div className="modal-actions" style={{ marginTop: '1.5rem' }}>
                            <button
                                className="btn-secondary"
                                onClick={() => setShowDeleteModal(false)}
                                disabled={deleteLoading}
                            >
                                Cancel
                            </button>
                            <button
                                className={deleteMode === 'delete_all' ? 'btn-danger' : 'btn-warning'}
                                onClick={handleDeleteAccount}
                                disabled={deleteLoading || !deletePassword}
                            >
                                {deleteLoading ? 'Deleting...' : 'Confirm Delete'}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
