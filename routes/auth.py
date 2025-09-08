from flask import request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from flask_restx import Resource
from models import db
from models.user import User
from datetime import datetime, timedelta
from api_config import auth_ns, login_model, login_response_model, token_verify_model, error_model

# Simple token blacklist (in production, use Redis or database)
blacklisted_tokens = set()


@auth_ns.route('/login')
class LoginResource(Resource):
    @auth_ns.expect(login_model, validate=True)
    @auth_ns.response(200, 'Login successful', login_response_model)
    @auth_ns.response(400, 'Validation error', error_model)
    @auth_ns.response(401, 'Invalid credentials', error_model)
    @auth_ns.response(500, 'Internal server error', error_model)
    @auth_ns.doc(description='Authenticate user and return JWT token')
    def post(self):
        """Authenticate user and return JWT token"""
        try:
            data = request.get_json()
            
            if not data:
                auth_ns.abort(400, 'Request body must be JSON', error='Invalid request')
            
            username = data.get('username')
            password = data.get('password')
            
            if not username or not password:
                auth_ns.abort(400, 'Username and password are required', error='Validation Error')
            
            user = User.query.filter_by(username=username).first()
            
            if not user or not user.check_password(password):
                auth_ns.abort(401, 'Username or password is incorrect', error='Invalid credentials')
            
            access_token = create_access_token(identity=user.id)
            
            return {
                'token': access_token,
                'user': user.to_dict()
            }, 200
            
        except Exception as e:
            auth_ns.abort(500, f'Internal server error: {str(e)}', error='Internal Server Error')


@auth_ns.route('/logout')
class LogoutResource(Resource):
    @auth_ns.response(204, 'Logout successful')
    @auth_ns.response(401, 'Unauthorized', error_model)
    @auth_ns.response(500, 'Internal server error', error_model)
    @auth_ns.doc(description='Deactivate current JWT token', security='Bearer')
    @jwt_required()
    def post(self):
        """Deactivate current JWT token"""
        try:
            jti = get_jwt()['jti']  # JWT ID
            blacklisted_tokens.add(jti)
            return '', 204
        except Exception as e:
            auth_ns.abort(500, f'Internal server error: {str(e)}', error='Internal Server Error')


@auth_ns.route('/verify')
class VerifyResource(Resource):
    @auth_ns.response(200, 'Token is valid', token_verify_model)
    @auth_ns.response(401, 'Unauthorized', error_model)
    @auth_ns.doc(description='Verify JWT token validity', security='Bearer')
    @jwt_required()
    def get(self):
        """Verify JWT token validity"""
        try:
            current_user_id = get_jwt_identity()
            current_user = User.query.get(current_user_id)
            
            if not current_user:
                auth_ns.abort(401, 'User not found', error='Invalid token')
            
            return {
                'valid': True,
                'user': current_user.to_dict()
            }, 200
            
        except Exception as e:
            auth_ns.abort(401, f'Authentication failed: {str(e)}', error='Authentication failed')

# JWT token blacklist checker
def check_if_token_revoked(jwt_header, jwt_payload):
    """Check if token is in blacklist"""
    jti = jwt_payload['jti']
    return jti in blacklisted_tokens