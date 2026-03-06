# ═══════════════════════════════════════════════════════════════════════════
# COMMENT ROUTES - CRUD Operations for Recipe Comments
# ═══════════════════════════════════════════════════════════════════════════
# This file demonstrates:
# 1. FULL CRUD: CREATE (store), READ (index), UPDATE (update), DELETE (destroy)
# 2. NESTED RESOURCES: Comments belong to specific recipes
# 3. HIERARCHICAL DATA: Parent-child comment structure (replies)
# 4. AUTHORIZATION: Users can only edit/delete their own comments
# 5. TRANSACTIONAL OPERATIONS: Database commits with rollback on error
#
# Connects to:
# - backend/models.py: Comment and Recipe models (self-referential relationship)
# - backend/app.py: Registered as comments_bp with /api/recipes prefix
# ═══════════════════════════════════════════════════════════════════════════

# Import Flask utilities for request/response handling
from flask import Blueprint, request, jsonify

# Import Flask-Login for authentication and authorization
from flask_login import login_required, current_user

# Import database models
# Connects to: backend/models.py for Comment and Recipe classes
from backend.models import db, Comment, Recipe

# Create Blueprint - groups comment-related routes
# Registered in: backend/app.py with url_prefix='/api/recipes'
comments_bp = Blueprint('comments', __name__)


# ═══════════════════════════════════════════════════════════════════════════
# READ OPERATION: Get All Comments for a Recipe
# ═══════════════════════════════════════════════════════════════════════════
# CRUD: READ - Retrieves comments with nested replies
# HTTP Method: GET
# URL: /api/recipes/<recipe_id>/comments
# Authentication: Not required (public)
# Demonstrates: SELF-REFERENTIAL RELATIONSHIPS, RECURSIVE DATA
# ═══════════════════════════════════════════════════════════════════════════

@comments_bp.route('/<int:recipe_id>/comments', methods=['GET'])
def index(recipe_id):
    """
    READ Operation: Fetch all comments for a recipe
    
    This demonstrates:
    - HIERARCHICAL DATA: Parent comments with nested replies
    - OOP RELATIONSHIP: Comment.replies (self-referential)
    - FILTERING: Only parent comments (parent_id=None)
    - RECURSIVE SERIALIZATION: to_dict(include_replies=True)
    
    Process:
    1. Verify recipe exists
    2. Query only parent comments (no parent_id)
    3. Order by newest first
    4. Serialize with nested replies
    
    Returns: JSON array of comments with nested replies
    """
    try:
        recipe = Recipe.query.get(recipe_id)
        if not recipe:
            return jsonify({
                'success': False,
                'message': 'Recipe not found.'
            }), 404

        # Get only parent comments with their replies
        comments = Comment.query.filter_by(
            recipe_id=recipe_id,
            parent_id=None
        ).order_by(Comment.created_at.desc()).all()

        data = [c.to_dict(include_replies=True) for c in comments]

        return jsonify({
            'success': True,
            'data': data,
            'count': len(data)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Failed to fetch comments.'
        }), 500


# ═══════════════════════════════════════════════════════════════════════════
# CREATE OPERATION: Add Comment or Reply
# ═══════════════════════════════════════════════════════════════════════════
# CRUD: CREATE - Inserts new comment or reply
# HTTP Method: POST
# URL: /api/recipes/<recipe_id>/comments
# Authentication: Required (@login_required)
# Demonstrates: TRANSACTIONAL INSERT, HIERARCHICAL DATA
# ═══════════════════════════════════════════════════════════════════════════

@comments_bp.route('/<int:recipe_id>/comments', methods=['POST'])
@login_required  # Must be logged in to comment
def store(recipe_id):
    """
    CREATE Operation: Add comment or reply to recipe
    
    This demonstrates:
    - TRANSACTIONAL INSERT: Creates new Comment record
    - HIERARCHICAL DATA: Optional parent_id for replies
    - VALIDATION: Verifies parent comment exists if replying
    - ROLLBACK ON ERROR: Maintains data integrity
    
    Process:
    1. Verify recipe exists
    2. Validate comment text
    3. If parent_id provided, verify parent exists
    4. Create Comment object
    5. COMMIT transaction (INSERT)
    
    Request Body: { "comment": "text", "parent_id": optional }
    
    Returns: JSON with created comment
    """
    try:
        recipe = Recipe.query.get(recipe_id)
        if not recipe:
            return jsonify({
                'success': False,
                'message': 'Recipe not found.'
            }), 404

        data = request.get_json()
        errors = {}

        comment_text = (data.get('comment') or '').strip()
        if not comment_text or len(comment_text) < 1:
            errors['comment'] = ['Comment text is required.']
        elif len(comment_text) > 1000:
            errors['comment'] = ['Comment cannot exceed 1000 characters.']

        parent_id = data.get('parent_id')
        if parent_id is not None:
            parent = Comment.query.filter_by(id=parent_id, recipe_id=recipe_id).first()
            if not parent:
                return jsonify({
                    'success': False,
                    'message': 'Invalid parent comment.'
                }), 422

        if errors:
            return jsonify({
                'success': False,
                'message': 'Validation failed.',
                'errors': errors
            }), 422

        comment = Comment(
            recipe_id=recipe_id,
            user_id=current_user.id,
            parent_id=parent_id,
            comment=comment_text,
        )
        db.session.add(comment)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Comment added successfully.',
            'data': comment.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Failed to add comment.'
        }), 500


# ═══════════════════════════════════════════════════════════════════════════
# UPDATE OPERATION: Edit Comment
# ═══════════════════════════════════════════════════════════════════════════
# CRUD: UPDATE - Modifies existing comment text
# HTTP Method: PUT
# URL: /api/recipes/<recipe_id>/comments/<comment_id>
# Authentication: Required (must be comment author)
# Demonstrates: TRANSACTIONAL UPDATE, AUTHORIZATION
# ═══════════════════════════════════════════════════════════════════════════

@comments_bp.route('/<int:recipe_id>/comments/<int:comment_id>', methods=['PUT'])
@login_required  # Must be logged in
def update(recipe_id, comment_id):
    """
    UPDATE Operation: Edit comment text
    
    This demonstrates:
    - TRANSACTIONAL UPDATE: Modifies Comment record
    - AUTHORIZATION: Only comment author can update
    - AUTO-UPDATE: updated_at timestamp automatically set
    - ROLLBACK ON ERROR: Maintains data integrity
    
    Process:
    1. Find comment by ID
    2. Verify ownership (current_user.id == comment.user_id)
    3. Validate new text
    4. Update comment field
    5. COMMIT transaction (UPDATE)
    
    Returns: JSON with updated comment
    """
    try:
        comment = Comment.query.filter_by(id=comment_id, recipe_id=recipe_id).first()
        if not comment:
            return jsonify({
                'success': False,
                'message': 'Comment not found.'
            }), 404

        if comment.user_id != current_user.id:
            return jsonify({
                'success': False,
                'message': 'Unauthorized to update this comment.'
            }), 403

        data = request.get_json()
        comment_text = (data.get('comment') or '').strip()

        if not comment_text or len(comment_text) < 1:
            return jsonify({
                'success': False,
                'message': 'Validation failed.',
                'errors': {'comment': ['Comment text is required.']}
            }), 422
        if len(comment_text) > 1000:
            return jsonify({
                'success': False,
                'message': 'Validation failed.',
                'errors': {'comment': ['Comment cannot exceed 1000 characters.']}
            }), 422

        comment.comment = comment_text
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Comment updated successfully.',
            'data': comment.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Failed to update comment.'
        }), 500


# ═══════════════════════════════════════════════════════════════════════════
# DELETE OPERATION: Remove Comment
# ═══════════════════════════════════════════════════════════════════════════
# CRUD: DELETE - Removes comment and all replies
# HTTP Method: DELETE
# URL: /api/recipes/<recipe_id>/comments/<comment_id>
# Authentication: Required (must be comment author)
# Demonstrates: CASCADE DELETE, AUTHORIZATION
# ═══════════════════════════════════════════════════════════════════════════

@comments_bp.route('/<int:recipe_id>/comments/<int:comment_id>', methods=['DELETE'])
@login_required  # Must be logged in
def destroy(recipe_id, comment_id):
    """
    DELETE Operation: Remove comment and all replies
    
    This demonstrates:
    - TRANSACTIONAL DELETE: Removes Comment from database
    - CASCADE OPERATIONS: Automatically deletes all replies
      (parent_id foreign key with CASCADE delete)
    - AUTHORIZATION: Only comment author can delete
    - ROLLBACK ON ERROR: Maintains data integrity
    
    Process:
    1. Find comment by ID
    2. Verify ownership
    3. Delete comment (CASCADE deletes replies)
    4. COMMIT transaction
    
    Returns: JSON confirmation
    """
    try:
        comment = Comment.query.filter_by(id=comment_id, recipe_id=recipe_id).first()
        if not comment:
            return jsonify({
                'success': False,
                'message': 'Comment not found.'
            }), 404

        if comment.user_id != current_user.id:
            return jsonify({
                'success': False,
                'message': 'Unauthorized to delete this comment.'
            }), 403

        db.session.delete(comment)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Comment deleted successfully.'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Failed to delete comment.'
        }), 500
