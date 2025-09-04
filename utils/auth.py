from functools import wraps
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.user import User

def token_required(f):
    """Decorator for routes that require authentication"""
    @wraps(f)
    @jwt_required()
    def decorated(*args, **kwargs):
        try:
            current_user_id = get_jwt_identity()
            current_user = User.query.get(current_user_id)
            
            if not current_user:
                return jsonify({
                    'error': 'Invalid token',
                    'message': 'User not found'
                }), 401
            
            return f(current_user, *args, **kwargs)
        except Exception as e:
            return jsonify({
                'error': 'Authentication failed',
                'message': str(e)
            }), 401
    
    return decorated

def admin_required(f):
    """Decorator for routes that require admin privileges"""
    @wraps(f)
    @jwt_required()
    def decorated(*args, **kwargs):
        try:
            current_user_id = get_jwt_identity()
            current_user = User.query.get(current_user_id)
            
            if not current_user:
                return jsonify({
                    'error': 'Invalid token',
                    'message': 'User not found'
                }), 401
            
            if current_user.role != 'admin':
                return jsonify({
                    'error': 'Access denied',
                    'message': 'Admin privileges required'
                }), 403
            
            return f(current_user, *args, **kwargs)
        except Exception as e:
            return jsonify({
                'error': 'Authentication failed',
                'message': str(e)
            }), 401
    
    return decorated