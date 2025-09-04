from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from models import db
from models.user import User
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)

# Simple token blacklist (in production, use Redis or database)
blacklisted_tokens = set()

@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user and return JWT token"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Invalid request',
                'message': 'Request body must be JSON'
            }), 400
        
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({
                'error': 'Validation Error',
                'message': 'Username and password are required'
            }), 400
        
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            return jsonify({
                'error': 'Invalid credentials',
                'message': 'Username or password is incorrect'
            }), 401
        
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'token': access_token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Deactivate current JWT token"""
    try:
        jti = get_jwt()['jti']  # JWT ID
        blacklisted_tokens.add(jti)
        return '', 204
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 500

@auth_bp.route('/verify', methods=['GET'])
@jwt_required()
def verify():
    """Verify JWT token validity"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({
                'error': 'Invalid token',
                'message': 'User not found'
            }), 401
        
        return jsonify({
            'valid': True,
            'user': current_user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Authentication failed',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 401

# JWT token blacklist checker
def check_if_token_revoked(jwt_header, jwt_payload):
    """Check if token is in blacklist"""
    jti = jwt_payload['jti']
    return jti in blacklisted_tokens