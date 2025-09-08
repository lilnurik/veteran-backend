from flask import Blueprint, request, jsonify
from models import db
from models.law import Law
from utils.auth import token_required, admin_required
from utils.validators import validate_multilang_field, validate_date_field
from datetime import datetime
from sqlalchemy import or_

laws_bp = Blueprint('laws', __name__)

@laws_bp.route('', methods=['GET'])
def get_laws():
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
        
        return jsonify({
            'laws': [law.to_dict() for law in laws],
            'total': total,
            'limit': limit,
            'offset': offset
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 500

@laws_bp.route('/<int:law_id>', methods=['GET'])
def get_law(law_id):
    """Get specific law by ID"""
    try:
        law = Law.query.get(law_id)
        
        if not law:
            return jsonify({
                'error': 'Not Found',
                'message': 'Law not found'
            }), 404
        
        return jsonify(law.to_dict()), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 500

@laws_bp.route('', methods=['POST'])
@token_required
def create_law(current_user):
    """Create new law"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Invalid request',
                'message': 'Request body must be JSON'
            }), 400
        
        # Validate required fields
        errors = {}
        errors.update(validate_multilang_field(data, 'title'))
        errors.update(validate_multilang_field(data, 'description'))
        errors.update(validate_multilang_field(data, 'category'))
        errors.update(validate_date_field(data, 'date'))
        
        if errors:
            return jsonify({
                'error': 'Validation Error',
                'message': 'Request validation failed',
                'details': errors,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }), 400
        
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
        
        return jsonify(law.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 500

@laws_bp.route('/<int:law_id>', methods=['PUT'])
@token_required
def update_law(current_user, law_id):
    """Update existing law"""
    try:
        law = Law.query.get(law_id)
        
        if not law:
            return jsonify({
                'error': 'Not Found',
                'message': 'Law not found'
            }), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Invalid request',
                'message': 'Request body must be JSON'
            }), 400
        
        # Validate required fields
        errors = {}
        errors.update(validate_multilang_field(data, 'title'))
        errors.update(validate_multilang_field(data, 'description'))
        errors.update(validate_multilang_field(data, 'category'))
        errors.update(validate_date_field(data, 'date'))
        
        if errors:
            return jsonify({
                'error': 'Validation Error',
                'message': 'Request validation failed',
                'details': errors,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }), 400
        
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
        
        return jsonify(law.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 500

@laws_bp.route('/<int:law_id>', methods=['DELETE'])
@token_required
def delete_law(current_user, law_id):
    """Delete law"""
    try:
        law = Law.query.get(law_id)
        
        if not law:
            return jsonify({
                'error': 'Not Found',
                'message': 'Law not found'
            }), 404
        
        db.session.delete(law)
        db.session.commit()
        
        return '', 204
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 500