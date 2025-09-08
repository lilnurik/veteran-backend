from flask import request
from flask_restx import Resource  
from models import db
from models.comrade import Comrade
from utils.auth import token_required
from utils.validators import validate_contact_info, validate_year_range
from datetime import datetime
from sqlalchemy import or_, and_
from api_config import comrades_ns, comrade_model, comrade_create_model, comrades_response_model, error_model


@comrades_ns.route('')
class ComradesListResource(Resource):
    def get(self):
        """Search comrades with multiple filters"""
        return {"comrades": [], "total": 0, "limit": 50, "offset": 0}
    
    def post(self):
        """Add information about a comrade"""
        return {"message": "Not implemented yet"}, 501


@comrades_ns.route('/<int:comrade_id>')
class ComradeResource(Resource):
    def get(self, comrade_id):
        """Get specific comrade by ID"""
        return {"message": "Not implemented yet"}, 501

@comrades_bp.route('', methods=['GET'])
def search_comrades():
    """Search comrades with multiple filters"""
    try:
        # Get query parameters
        name = request.args.get('name')
        unit = request.args.get('unit')
        region = request.args.get('region')
        year_from = request.args.get('yearFrom')
        year_to = request.args.get('yearTo')
        rank = request.args.get('rank')
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        # Build query
        query = Comrade.query
        
        # Apply name filter (search in first name, last name, middle name)
        if name:
            query = query.filter(
                or_(
                    Comrade.first_name.ilike(f'%{name}%'),
                    Comrade.last_name.ilike(f'%{name}%'),
                    Comrade.middle_name.ilike(f'%{name}%')
                )
            )
        
        # Apply unit filter
        if unit:
            query = query.filter(Comrade.unit.ilike(f'%{unit}%'))
        
        # Apply region filter
        if region:
            query = query.filter(Comrade.region.ilike(f'%{region}%'))
        
        # Apply year range filters
        if year_from:
            try:
                year_from_int = int(year_from)
                query = query.filter(Comrade.year_of_service_from >= year_from_int)
            except ValueError:
                return jsonify({
                    'error': 'Invalid yearFrom',
                    'message': 'yearFrom must be a number'
                }), 400
        
        if year_to:
            try:
                year_to_int = int(year_to)
                query = query.filter(
                    or_(
                        Comrade.year_of_service_to <= year_to_int,
                        Comrade.year_of_service_to.is_(None)
                    )
                )
            except ValueError:
                return jsonify({
                    'error': 'Invalid yearTo',
                    'message': 'yearTo must be a number'
                }), 400
        
        # Apply rank filter
        if rank:
            query = query.filter(Comrade.rank.ilike(f'%{rank}%'))
        
        # Get total count
        total = query.count()
        
        # Apply pagination and get results
        comrades = query.order_by(Comrade.last_name, Comrade.first_name).offset(offset).limit(limit).all()
        
        return jsonify({
            'comrades': [comrade.to_dict() for comrade in comrades],
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

@comrades_bp.route('', methods=['POST'])
def create_comrade():
    """Add information about a comrade"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Invalid request',
                'message': 'Request body must be JSON'
            }), 400
        
        # Validate required fields
        errors = {}
        
        if not data.get('firstName'):
            errors['firstName'] = 'First name is required'
        
        if not data.get('lastName'):
            errors['lastName'] = 'Last name is required'
        
        if not data.get('unit'):
            errors['unit'] = 'Unit is required'
        
        if not data.get('region'):
            errors['region'] = 'Region is required'
        
        if not data.get('yearOfServiceFrom'):
            errors['yearOfServiceFrom'] = 'Year of service from is required'
        
        # Validate year range
        year_from = data.get('yearOfServiceFrom')
        year_to = data.get('yearOfServiceTo')
        
        if year_from:
            try:
                year_from_int = int(year_from)
                year_to_int = int(year_to) if year_to else None
                errors.update(validate_year_range(year_from_int, year_to_int))
            except (ValueError, TypeError):
                errors['yearOfServiceFrom'] = 'Year of service from must be a number'
        
        # Validate contact info if provided
        if 'contactInfo' in data and data['contactInfo']:
            errors.update(validate_contact_info(data['contactInfo']))
        
        if errors:
            return jsonify({
                'error': 'Validation Error',
                'message': 'Request validation failed',
                'details': errors,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }), 400
        
        # Create new comrade
        comrade = Comrade(
            first_name=data['firstName'],
            last_name=data['lastName'],
            middle_name=data.get('middleName'),
            unit=data['unit'],
            region=data['region'],
            year_of_service_from=int(year_from),
            year_of_service_to=int(year_to) if year_to else None,
            rank=data.get('rank'),
            photo_url=data.get('photoUrl'),
            additional_info=data.get('additionalInfo')
        )
        
        # Set contact info if provided
        if 'contactInfo' in data and data['contactInfo']:
            comrade.set_contact_info(data['contactInfo'])
        
        db.session.add(comrade)
        db.session.commit()
        
        return jsonify(comrade.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 500

@comrades_bp.route('/<int:comrade_id>', methods=['GET'])
def get_comrade(comrade_id):
    """Get specific comrade by ID"""
    try:
        comrade = Comrade.query.get(comrade_id)
        
        if not comrade:
            return jsonify({
                'error': 'Not Found',
                'message': 'Comrade not found'
            }), 404
        
        return jsonify(comrade.to_dict()), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 500

@comrades_bp.route('/<int:comrade_id>', methods=['PUT'])
@token_required
def update_comrade(current_user, comrade_id):
    """Update comrade information"""
    try:
        comrade = Comrade.query.get(comrade_id)
        
        if not comrade:
            return jsonify({
                'error': 'Not Found',
                'message': 'Comrade not found'
            }), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Invalid request',
                'message': 'Request body must be JSON'
            }), 400
        
        # Validate required fields
        errors = {}
        
        if not data.get('firstName'):
            errors['firstName'] = 'First name is required'
        
        if not data.get('lastName'):
            errors['lastName'] = 'Last name is required'
        
        if not data.get('unit'):
            errors['unit'] = 'Unit is required'
        
        if not data.get('region'):
            errors['region'] = 'Region is required'
        
        if not data.get('yearOfServiceFrom'):
            errors['yearOfServiceFrom'] = 'Year of service from is required'
        
        # Validate year range
        year_from = data.get('yearOfServiceFrom')
        year_to = data.get('yearOfServiceTo')
        
        if year_from:
            try:
                year_from_int = int(year_from)
                year_to_int = int(year_to) if year_to else None
                errors.update(validate_year_range(year_from_int, year_to_int))
            except (ValueError, TypeError):
                errors['yearOfServiceFrom'] = 'Year of service from must be a number'
        
        # Validate contact info if provided
        if 'contactInfo' in data and data['contactInfo']:
            errors.update(validate_contact_info(data['contactInfo']))
        
        if errors:
            return jsonify({
                'error': 'Validation Error',
                'message': 'Request validation failed',
                'details': errors,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }), 400
        
        # Update comrade
        comrade.first_name = data['firstName']
        comrade.last_name = data['lastName']
        comrade.middle_name = data.get('middleName')
        comrade.unit = data['unit']
        comrade.region = data['region']
        comrade.year_of_service_from = int(year_from)
        comrade.year_of_service_to = int(year_to) if year_to else None
        comrade.rank = data.get('rank')
        comrade.photo_url = data.get('photoUrl')
        comrade.additional_info = data.get('additionalInfo')
        comrade.updated_at = datetime.utcnow()
        
        # Set contact info if provided
        if 'contactInfo' in data and data['contactInfo']:
            comrade.set_contact_info(data['contactInfo'])
        else:
            comrade.contact_info = None
        
        db.session.commit()
        
        return jsonify(comrade.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 500

@comrades_bp.route('/<int:comrade_id>', methods=['DELETE'])
@token_required
def delete_comrade(current_user, comrade_id):
    """Delete comrade information"""
    try:
        comrade = Comrade.query.get(comrade_id)
        
        if not comrade:
            return jsonify({
                'error': 'Not Found',
                'message': 'Comrade not found'
            }), 404
        
        db.session.delete(comrade)
        db.session.commit()
        
        return '', 204
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 500