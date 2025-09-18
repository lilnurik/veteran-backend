from flask import Blueprint, request, jsonify
from models import db
from models.comrade import Comrade
from utils.auth import token_required
from utils.validators import validate_contact_info, validate_year_range
from utils.excel_parser import ComradeExcelParser
from datetime import datetime
from sqlalchemy import or_, and_
import os

comrades_bp = Blueprint('comrades', __name__)

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


@comrades_bp.route('/bulk-import', methods=['POST'])
@token_required
def bulk_import_comrades(current_user):
    """Import comrades from Excel file"""
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({
                'error': 'No file provided',
                'message': 'Excel file is required for bulk import'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'error': 'No file selected',
                'message': 'Please select an Excel file'
            }), 400
        
        # Validate file extension
        if not file.filename.lower().endswith(('.xlsx', '.xls')):
            return jsonify({
                'error': 'Invalid file format',
                'message': 'Only Excel files (.xlsx, .xls) are supported'
            }), 400
        
        # Save uploaded file temporarily
        upload_dir = '/tmp'
        os.makedirs(upload_dir, exist_ok=True)
        temp_filename = f"comrades_import_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.xlsx"
        temp_filepath = os.path.join(upload_dir, temp_filename)
        
        try:
            file.save(temp_filepath)
            
            # Parse Excel file
            parser = ComradeExcelParser()
            comrades_data, errors, warnings = parser.parse_excel_file(temp_filepath)
            
            if errors:
                return jsonify({
                    'error': 'Import validation failed',
                    'message': 'Найдены ошибки в файле',
                    'details': {
                        'errors': errors,
                        'warnings': warnings
                    },
                    'timestamp': datetime.utcnow().isoformat() + 'Z'
                }), 400
            
            # Import comrades to database
            imported_count = 0
            skipped_count = 0
            import_errors = []
            
            for i, comrade_data in enumerate(comrades_data):
                try:
                    # Additional validation using existing validators
                    validation_errors = {}
                    
                    # Validate year range
                    year_from = comrade_data['yearOfServiceFrom']
                    year_to = comrade_data.get('yearOfServiceTo')
                    if year_from:
                        validation_errors.update(validate_year_range(year_from, year_to))
                    
                    # Validate contact info if present
                    if 'contactInfo' in comrade_data:
                        validation_errors.update(validate_contact_info(comrade_data['contactInfo']))
                    
                    if validation_errors:
                        import_errors.append(f"Строка {i + 1}: {', '.join(validation_errors.values())}")
                        skipped_count += 1
                        continue
                    
                    # Check for duplicates (same first name, last name, unit)
                    existing = Comrade.query.filter_by(
                        first_name=comrade_data['firstName'],
                        last_name=comrade_data['lastName'],
                        unit=comrade_data['unit']
                    ).first()
                    
                    if existing:
                        import_errors.append(f"Строка {i + 1}: Сослуживец уже существует ({comrade_data['firstName']} {comrade_data['lastName']}, {comrade_data['unit']})")
                        skipped_count += 1
                        continue
                    
                    # Create new comrade
                    try:
                        comrade = Comrade(
                            first_name=comrade_data['firstName'],
                            last_name=comrade_data['lastName'],
                            middle_name=comrade_data.get('middleName'),
                            unit=comrade_data['unit'],
                            region=comrade_data['region'],
                            year_of_service_from=comrade_data['yearOfServiceFrom'],
                            year_of_service_to=comrade_data.get('yearOfServiceTo'),
                            rank=comrade_data.get('rank'),
                            additional_info=comrade_data.get('additionalInfo')
                        )
                        
                        # Set contact info if provided
                        if 'contactInfo' in comrade_data:
                            comrade.set_contact_info(comrade_data['contactInfo'])
                        
                        db.session.add(comrade)
                        imported_count += 1
                        
                    except Exception as db_error:
                        import_errors.append(f"Строка {i + 1}: Database error - {str(db_error)}")
                        skipped_count += 1
                    
                except Exception as e:
                    import_errors.append(f"Строка {i + 1}: General error - {str(e)}")
                    skipped_count += 1
            
            # Commit all changes
            if imported_count > 0:
                db.session.commit()
            
            response_data = {
                'success': True,
                'message': f'Импорт завершен. Импортировано: {imported_count}, пропущено: {skipped_count}',
                'statistics': {
                    'imported': imported_count,
                    'skipped': skipped_count,
                    'total_processed': len(comrades_data)
                },
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
            
            if warnings:
                response_data['warnings'] = warnings
            
            if import_errors:
                response_data['import_errors'] = import_errors
            
            return jsonify(response_data), 200
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_filepath):
                os.remove(temp_filepath)
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 500


@comrades_bp.route('/bulk-import/sample', methods=['GET'])
@token_required
def download_sample_excel(current_user):
    """Download sample Excel file for bulk import"""
    try:
        # Create sample file
        sample_dir = '/tmp'
        os.makedirs(sample_dir, exist_ok=True)
        sample_filename = f"sample_comrades_import_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.xlsx"
        sample_filepath = os.path.join(sample_dir, sample_filename)
        
        parser = ComradeExcelParser()
        parser.create_sample_excel(sample_filepath)
        
        return jsonify({
            'message': 'Sample file created successfully',
            'download_instructions': 'Use the file path provided to download the sample Excel file',
            'file_path': sample_filepath,
            'columns': {
                'required': parser.REQUIRED_COLUMNS,
                'optional': parser.OPTIONAL_COLUMNS
            },
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 500