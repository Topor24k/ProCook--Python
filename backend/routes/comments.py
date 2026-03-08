from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from backend.models import db, Comment, Recipe

comments_bp = Blueprint('comments', __name__)


# CRUD READ: fetches all parent comments with nested replies for a recipe
@comments_bp.route('/<int:recipe_id>/comments', methods=['GET'])
def index(recipe_id):
    try:
        recipe = Recipe.query.get(recipe_id)
        if not recipe:
            return jsonify({'success': False, 'message': 'Recipe not found.'}), 404

        # OOP: queries parent comments and uses self-referential relationship to load replies
        comments = Comment.query.filter_by(
            recipe_id=recipe_id,
            parent_id=None
        ).order_by(Comment.created_at.desc()).all()

        data = [c.to_dict(include_replies=True) for c in comments]
        return jsonify({'success': True, 'data': data, 'count': len(data)})
    except Exception as e:
        return jsonify({'success': False, 'message': 'Failed to fetch comments.'}), 500


# CRUD CREATE: inserts new comment or reply into database
@comments_bp.route('/<int:recipe_id>/comments', methods=['POST'])
@login_required
def store(recipe_id):
    try:
        recipe = Recipe.query.get(recipe_id)
        if not recipe:
            return jsonify({'success': False, 'message': 'Recipe not found.'}), 404

        data = request.get_json()
        errors = {}

        comment_text = (data.get('comment') or '').strip()
        if not comment_text or len(comment_text) < 1:
            errors['comment'] = ['Comment text is required.']
        elif len(comment_text) > 1000:
            errors['comment'] = ['Comment cannot exceed 1000 characters.']

        # OOP: validates parent comment exists if creating a reply (self-referential relationship)
        parent_id = data.get('parent_id')
        if parent_id is not None:
            parent = Comment.query.filter_by(id=parent_id, recipe_id=recipe_id).first()
            if not parent:
                return jsonify({'success': False, 'message': 'Invalid parent comment.'}), 422

        if errors:
            return jsonify({'success': False, 'message': 'Validation failed.', 'errors': errors}), 422

        # CRUD CREATE: creates Comment object and adds to database
        comment = Comment(
            recipe_id=recipe_id,
            user_id=current_user.id,
            parent_id=parent_id,
            comment=comment_text,
        )
        db.session.add(comment)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Comment added successfully.', 'data': comment.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Failed to add comment.'}), 500


# CRUD UPDATE: modifies existing comment text
@comments_bp.route('/<int:recipe_id>/comments/<int:comment_id>', methods=['PUT'])
@login_required
def update(recipe_id, comment_id):
    try:
        comment = Comment.query.filter_by(id=comment_id, recipe_id=recipe_id).first()
        if not comment:
            return jsonify({'success': False, 'message': 'Comment not found.'}), 404
        if comment.user_id != current_user.id:
            return jsonify({'success': False, 'message': 'Unauthorized to update this comment.'}), 403

        data = request.get_json()
        comment_text = (data.get('comment') or '').strip()

        if not comment_text or len(comment_text) < 1:
            return jsonify({'success': False, 'message': 'Validation failed.', 'errors': {'comment': ['Comment text is required.']}}), 422
        if len(comment_text) > 1000:
            return jsonify({'success': False, 'message': 'Validation failed.', 'errors': {'comment': ['Comment cannot exceed 1000 characters.']}}), 422

        # CRUD UPDATE: modifies comment field
        comment.comment = comment_text
        db.session.commit()
        return jsonify({'success': True, 'message': 'Comment updated successfully.', 'data': comment.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Failed to update comment.'}), 500


# CRUD DELETE: removes comment from database (CASCADE deletes all replies)
@comments_bp.route('/<int:recipe_id>/comments/<int:comment_id>', methods=['DELETE'])
@login_required
def destroy(recipe_id, comment_id):
    try:
        comment = Comment.query.filter_by(id=comment_id, recipe_id=recipe_id).first()
        if not comment:
            return jsonify({'success': False, 'message': 'Comment not found.'}), 404
        if comment.user_id != current_user.id:
            return jsonify({'success': False, 'message': 'Unauthorized to delete this comment.'}), 403

        # CRUD DELETE: removes comment (CASCADE automatically deletes nested replies)
        db.session.delete(comment)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Comment deleted successfully.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Failed to delete comment.'}), 500
