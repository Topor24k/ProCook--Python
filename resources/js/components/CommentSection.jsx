import React, { useState, useEffect } from 'react';
import { 
    IoPersonCircleOutline, 
    IoChatbubbleOutline,
    IoCreateOutline,
    IoTrashOutline,
    IoSendOutline,
    IoCloseOutline,
    IoReturnDownForwardOutline
} from 'react-icons/io5';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';

export default function CommentSection({ recipeId }) {
    const { user } = useAuth();
    const [comments, setComments] = useState([]);
    const [newComment, setNewComment] = useState('');
    const [editingCommentId, setEditingCommentId] = useState(null);
    const [editingText, setEditingText] = useState('');
    const [replyingToId, setReplyingToId] = useState(null);
    const [replyText, setReplyText] = useState('');
    const [loading, setLoading] = useState(false);
    const [submitting, setSubmitting] = useState(false);

    useEffect(() => {
        fetchComments();
    }, [recipeId]);

    const fetchComments = async () => {
        setLoading(true);
        try {
            const response = await api.get(`/recipes/${recipeId}/comments`);
            setComments(response.data.data || []);
        } catch (error) {
            console.error('Error fetching comments:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleSubmitComment = async (e, parentId = null) => {
        e.preventDefault();
        
        if (!user) {
            alert('Please login to comment');
            return;
        }

        const commentText = parentId ? replyText : newComment;
        if (!commentText.trim()) return;

        setSubmitting(true);
        try {
            const payload = {
                comment: commentText.trim()
            };
            
            if (parentId) {
                payload.parent_id = parentId;
            }

            const response = await api.post(`/recipes/${recipeId}/comments`, payload);
            
            if (parentId) {
                // Add reply to parent comment's replies array
                setComments(comments.map(c => {
                    if (c.id === parentId) {
                        return {
                            ...c,
                            replies: [...(c.replies || []), response.data.data]
                        };
                    }
                    return c;
                }));
                setReplyText('');
                setReplyingToId(null);
            } else {
                // Add new top-level comment
                setComments([response.data.data, ...comments]);
                setNewComment('');
            }
        } catch (error) {
            console.error('Error submitting comment:', error);
            alert('Failed to post comment. Please try again.');
        } finally {
            setSubmitting(false);
        }
    };

    const handleEditComment = async (commentId, isReply = false, parentId = null) => {
        if (!editingText.trim()) return;

        setSubmitting(true);
        try {
            const response = await api.put(`/recipes/${recipeId}/comments/${commentId}`, {
                comment: editingText.trim()
            });
            
            if (isReply && parentId) {
                // Update reply in parent comment
                setComments(comments.map(c => {
                    if (c.id === parentId) {
                        return {
                            ...c,
                            replies: c.replies.map(r => 
                                r.id === commentId ? response.data.data : r
                            )
                        };
                    }
                    return c;
                }));
            } else {
                // Update top-level comment
                setComments(comments.map(c => 
                    c.id === commentId ? { ...response.data.data, replies: c.replies } : c
                ));
            }
            
            setEditingCommentId(null);
            setEditingText('');
        } catch (error) {
            console.error('Error updating comment:', error);
            alert('Failed to update comment. Please try again.');
        } finally {
            setSubmitting(false);
        }
    };

    const handleDeleteComment = async (commentId, isReply = false, parentId = null) => {
        if (!confirm('Are you sure you want to delete this comment?')) return;

        try {
            await api.delete(`/recipes/${recipeId}/comments/${commentId}`);
            
            if (isReply && parentId) {
                // Remove reply from parent comment
                setComments(comments.map(c => {
                    if (c.id === parentId) {
                        return {
                            ...c,
                            replies: c.replies.filter(r => r.id !== commentId)
                        };
                    }
                    return c;
                }));
            } else {
                // Remove top-level comment
                setComments(comments.filter(c => c.id !== commentId));
            }
        } catch (error) {
            console.error('Error deleting comment:', error);
            alert('Failed to delete comment. Please try again.');
        }
    };

    const startEdit = (comment) => {
        setEditingCommentId(comment.id);
        setEditingText(comment.comment);
    };

    const cancelEdit = () => {
        setEditingCommentId(null);
        setEditingText('');
    };

    const startReply = (commentId) => {
        setReplyingToId(commentId);
        setReplyText('');
    };

    const cancelReply = () => {
        setReplyingToId(null);
        setReplyText('');
    };

    const formatDate = (dateString) => {
        const date = new Date(dateString);
        const now = new Date();
        const diffInSeconds = Math.floor((now - date) / 1000);

        if (diffInSeconds < 60) return 'Just now';
        if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} minutes ago`;
        if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} hours ago`;
        if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)} days ago`;
        
        return date.toLocaleDateString('en-US', { 
            month: 'short', 
            day: 'numeric', 
            year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined 
        });
    };

    const renderComment = (comment, isReply = false, parentId = null) => {
        const isEditing = editingCommentId === comment.id;
        const isReplying = replyingToId === comment.id;

        return (
            <div key={comment.id} className={`comment-item ${isReply ? 'comment-reply' : ''}`}>
                <div className="comment-header">
                    <div className="comment-author">
                        <IoPersonCircleOutline className="comment-avatar" />
                        <div className="comment-meta">
                            <span className="comment-author-name">
                                {comment.user?.name || 'Anonymous'}
                            </span>
                            <span className="comment-date">
                                {formatDate(comment.created_at)}
                            </span>
                        </div>
                    </div>
                    
                    {user && user.id === comment.user_id && (
                        <div className="comment-actions">
                            {!isEditing && (
                                <>
                                    <button
                                        onClick={() => startEdit(comment)}
                                        className="btn-comment-action"
                                        title="Edit comment"
                                    >
                                        <IoCreateOutline />
                                    </button>
                                    <button
                                        onClick={() => handleDeleteComment(comment.id, isReply, parentId)}
                                        className="btn-comment-action delete"
                                        title="Delete comment"
                                    >
                                        <IoTrashOutline />
                                    </button>
                                </>
                            )}
                        </div>
                    )}
                </div>

                {isEditing ? (
                    <div className="comment-edit-form">
                        <textarea
                            value={editingText}
                            onChange={(e) => setEditingText(e.target.value)}
                            className="comment-input"
                            rows="3"
                            maxLength="1000"
                            disabled={submitting}
                        />
                        <div className="comment-edit-actions">
                            <button
                                onClick={cancelEdit}
                                className="btn-cancel"
                                disabled={submitting}
                            >
                                <IoCloseOutline style={{ fontSize: '1.1rem' }} />
                                Cancel
                            </button>
                            <button
                                onClick={() => handleEditComment(comment.id, isReply, parentId)}
                                className="btn-save"
                                disabled={!editingText.trim() || submitting}
                            >
                                <IoSendOutline style={{ fontSize: '1.1rem' }} />
                                Save
                            </button>
                        </div>
                    </div>
                ) : (
                    <>
                        <p className="comment-text">{comment.comment}</p>
                        
                        {/* Reply button for top-level comments only */}
                        {!isReply && user && (
                            <button
                                onClick={() => startReply(comment.id)}
                                className="btn-reply"
                                disabled={submitting}
                            >
                                <IoReturnDownForwardOutline style={{ fontSize: '0.9rem' }} />
                                Reply
                            </button>
                        )}
                    </>
                )}

                {/* Reply Form */}
                {isReplying && user && (
                    <form onSubmit={(e) => handleSubmitComment(e, comment.id)} className="reply-form">
                        <div className="comment-input-wrapper">
                            <IoPersonCircleOutline className="user-avatar-icon" />
                            <textarea
                                value={replyText}
                                onChange={(e) => setReplyText(e.target.value)}
                                placeholder={`Reply to ${comment.user?.name || 'Anonymous'}...`}
                                className="comment-input"
                                rows="2"
                                maxLength="1000"
                                disabled={submitting}
                                autoFocus
                            />
                        </div>
                        <div className="comment-form-actions">
                            <button
                                type="button"
                                onClick={cancelReply}
                                className="btn-cancel"
                                disabled={submitting}
                            >
                                Cancel
                            </button>
                            <button
                                type="submit"
                                className="btn-comment-submit"
                                disabled={!replyText.trim() || submitting}
                            >
                                <IoSendOutline style={{ fontSize: '1.1rem' }} />
                                Post Reply
                            </button>
                        </div>
                    </form>
                )}

                {/* Display Replies */}
                {!isReply && comment.replies && comment.replies.length > 0 && (
                    <div className="comment-replies">
                        {comment.replies.map(reply => renderComment(reply, true, comment.id))}
                    </div>
                )}
            </div>
        );
    };

    return (
        <div className="comment-section">
            <h3 className="comment-section-title">
                <IoChatbubbleOutline style={{ fontSize: '1.5rem' }} />
                Comments ({comments.reduce((total, c) => total + 1 + (c.replies?.length || 0), 0)})
            </h3>

            {/* Add Comment Form */}
            {user ? (
                <form onSubmit={handleSubmitComment} className="comment-form">
                    <div className="comment-input-wrapper">
                        <IoPersonCircleOutline className="user-avatar-icon" />
                        <textarea
                            value={newComment}
                            onChange={(e) => setNewComment(e.target.value)}
                            placeholder="Write a comment..."
                            className="comment-input"
                            rows="3"
                            maxLength="1000"
                            disabled={submitting}
                        />
                    </div>
                    <div className="comment-form-actions">
                        <span className="comment-char-count">
                            {newComment.length}/1000
                        </span>
                        <button
                            type="submit"
                            className="btn-comment-submit"
                            disabled={!newComment.trim() || submitting}
                        >
                            <IoSendOutline style={{ fontSize: '1.1rem' }} />
                            Post Comment
                        </button>
                    </div>
                </form>
            ) : (
                <div className="comment-login-prompt">
                    <IoPersonCircleOutline style={{ fontSize: '2rem' }} />
                    <p>Please login to comment on this recipe</p>
                </div>
            )}

            {/* Comments List */}
            {loading ? (
                <div className="comments-loading">
                    <div className="spinner"></div>
                    <p>Loading comments...</p>
                </div>
            ) : comments.length === 0 ? (
                <div className="comments-empty">
                    <IoChatbubbleOutline style={{ fontSize: '3rem', color: 'var(--gray-400)' }} />
                    <p>No comments yet. Be the first to comment!</p>
                </div>
            ) : (
                <div className="comments-list">
                    {comments.map(comment => renderComment(comment))}
                </div>
            )}
        </div>
    );
}
