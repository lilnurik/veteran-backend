from flask import request
from flask_restx import Resource
from models import db
from models.law import Law
from utils.auth import token_required, admin_required
from utils.validators import validate_multilang_field, validate_date_field
from datetime import datetime
from sqlalchemy import or_
from api_config import laws_ns, law_model, law_create_model, laws_response_model, error_model, validation_error_model

@laws_ns.route('')
class LawsResource(Resource):
    @laws_ns.response(200, 'Laws retrieved successfully', laws_response_model)
    @laws_ns.response(500, 'Internal server error', error_model)
    @laws_ns.param('category', 'Filter by category', type='string')
    @laws_ns.param('search', 'Search in title and description', type='string')
    @laws_ns.param('limit', 'Number of results (default: 50)', type='integer', default=50)
    @laws_ns.param('offset', 'Offset for pagination (default: 0)', type='integer', default=0)
    @laws_ns.doc(description='Get all laws with optional filtering and pagination')
    def get(self):
        """Get all laws with optional filtering"""
        try:
            # Get query parameters
            category = request.args.get('category')
            search = request.args.get('search')
            limit = int(request.args.get('limit', 50))
            offset = int(request.args.get('offset', 0))
            
            # Build query
            query = Law.query
            
            # Apply category filter
            if category:
                query = query.filter(
                    or_(
                        Law.category_ru.ilike(f'%{category}%'),
                        Law.category_uz.ilike(f'%{category}%'),
                        Law.category_en.ilike(f'%{category}%')
                    )
                )
            
            # Apply search filter
            if search:
                query = query.filter(
                    or_(
                        Law.title_ru.ilike(f'%{search}%'),
                        Law.title_uz.ilike(f'%{search}%'),
                        Law.title_en.ilike(f'%{search}%'),
                        Law.description_ru.ilike(f'%{search}%'),
                        Law.description_uz.ilike(f'%{search}%'),
                        Law.description_en.ilike(f'%{search}%')
                    )
                )
            
            # Get total count
            total = query.count()
            
            # Apply pagination and get results
            laws = query.order_by(Law.date.desc()).offset(offset).limit(limit).all()
            
            return {
                'laws': [law.to_dict() for law in laws],
                'total': total,
                'limit': limit,
                'offset': offset
            }, 200
            
        except Exception as e:
            laws_ns.abort(500, f'Internal server error: {str(e)}', error='Internal Server Error')
    
    @laws_ns.expect(law_create_model, validate=True)
    @laws_ns.response(201, 'Law created successfully', law_model)
    @laws_ns.response(400, 'Validation error', validation_error_model)
    @laws_ns.response(401, 'Unauthorized', error_model)
    @laws_ns.response(500, 'Internal server error', error_model)
    @laws_ns.doc(description='Create new law', security='Bearer')
    @token_required
    def post(self, current_user):
        """Create new law"""
        try:
            data = request.get_json()
            
            if not data:
                laws_ns.abort(400, 'Request body must be JSON', error='Invalid request')
            
            # Validate required fields
            errors = {}
            errors.update(validate_multilang_field(data, 'title'))
            errors.update(validate_multilang_field(data, 'description'))
            errors.update(validate_multilang_field(data, 'category'))
            errors.update(validate_date_field(data, 'date'))
            
            if errors:
                return {
                    'error': 'Validation Error',
                    'message': 'Request validation failed',
                    'details': errors,
                    'timestamp': datetime.utcnow().isoformat() + 'Z'
                }, 400
            
            # Create new law
            law = Law(
                title_ru=data['title']['ru'],
                title_uz=data['title']['uz'],
                title_en=data['title']['en'],
                description_ru=data['description']['ru'],
                description_uz=data['description']['uz'],
                description_en=data['description']['en'],
                category_ru=data['category']['ru'],
                category_uz=data['category']['uz'],
                category_en=data['category']['en'],
                date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
                pdf_url=data.get('pdfUrl')
            )
            
            db.session.add(law)
            db.session.commit()
            
            return law.to_dict(), 201
            
        except Exception as e:
            db.session.rollback()
            laws_ns.abort(500, f'Internal server error: {str(e)}', error='Internal Server Error')


@laws_ns.route('/<int:law_id>')
class LawResource(Resource):
    @laws_ns.response(200, 'Law retrieved successfully', law_model)
    @laws_ns.response(404, 'Law not found', error_model)
    @laws_ns.response(500, 'Internal server error', error_model)
    @laws_ns.doc(description='Get specific law by ID')
    def get(self, law_id):
        """Get specific law by ID"""
        try:
            law = Law.query.get(law_id)
            
            if not law:
                laws_ns.abort(404, 'Law not found', error='Not Found')
            
            return law.to_dict(), 200
            
        except Exception as e:
            laws_ns.abort(500, f'Internal server error: {str(e)}', error='Internal Server Error')
    
    @laws_ns.expect(law_create_model, validate=True)
    @laws_ns.response(200, 'Law updated successfully', law_model)
    @laws_ns.response(400, 'Validation error', validation_error_model)
    @laws_ns.response(401, 'Unauthorized', error_model)
    @laws_ns.response(404, 'Law not found', error_model)
    @laws_ns.response(500, 'Internal server error', error_model)
    @laws_ns.doc(description='Update existing law', security='Bearer')
    @token_required
    def put(self, current_user, law_id):
        """Update existing law"""
        try:
            law = Law.query.get(law_id)
            
            if not law:
                laws_ns.abort(404, 'Law not found', error='Not Found')
            
            data = request.get_json()
            
            if not data:
                laws_ns.abort(400, 'Request body must be JSON', error='Invalid request')
            
            # Validate required fields
            errors = {}
            errors.update(validate_multilang_field(data, 'title'))
            errors.update(validate_multilang_field(data, 'description'))
            errors.update(validate_multilang_field(data, 'category'))
            errors.update(validate_date_field(data, 'date'))
            
            if errors:
                return {
                    'error': 'Validation Error',
                    'message': 'Request validation failed',
                    'details': errors,
                    'timestamp': datetime.utcnow().isoformat() + 'Z'
                }, 400
            
            # Update law
            law.title_ru = data['title']['ru']
            law.title_uz = data['title']['uz']
            law.title_en = data['title']['en']
            law.description_ru = data['description']['ru']
            law.description_uz = data['description']['uz']
            law.description_en = data['description']['en']
            law.category_ru = data['category']['ru']
            law.category_uz = data['category']['uz']
            law.category_en = data['category']['en']
            law.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
            law.pdf_url = data.get('pdfUrl')
            law.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            return law.to_dict(), 200
            
        except Exception as e:
            db.session.rollback()
            laws_ns.abort(500, f'Internal server error: {str(e)}', error='Internal Server Error')
    
    @laws_ns.response(204, 'Law deleted successfully')
    @laws_ns.response(401, 'Unauthorized', error_model)
    @laws_ns.response(404, 'Law not found', error_model)
    @laws_ns.response(500, 'Internal server error', error_model)
    @laws_ns.doc(description='Delete law', security='Bearer')
    @token_required
    def delete(self, current_user, law_id):
        """Delete law"""
        try:
            law = Law.query.get(law_id)
            
            if not law:
                laws_ns.abort(404, 'Law not found', error='Not Found')
            
            db.session.delete(law)
            db.session.commit()
            
            return '', 204
            
        except Exception as e:
            db.session.rollback()
            laws_ns.abort(500, f'Internal server error: {str(e)}', error='Internal Server Error')