from flask import Blueprint, request, jsonify, url_for, send_from_directory
from werkzeug.utils import secure_filename
from models import db
from models.file import File
from utils.auth import token_required
from utils.validators import allowed_file
from datetime import datetime
import os
import uuid

files_bp = Blueprint('files', __name__)

@files_bp.route('/upload', methods=['POST'])
@token_required
def upload_file(current_user):
    """Upload file (PDF or image)"""
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({
                'error': 'No file provided',
                'message': 'File field is required'
            }), 400
        
        file = request.files['file']
        file_type = request.form.get('type')
        category = request.form.get('category', 'other')
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({
                'error': 'No file selected',
                'message': 'Please select a file'
            }), 400
        
        # Validate file type parameter
        if file_type not in ['pdf', 'image']:
            return jsonify({
                'error': 'Invalid file type',
                'message': 'Type must be either "pdf" or "image"'
            }), 400
        
        # Get allowed extensions based on file type
        if file_type == 'pdf':
            allowed_extensions = {'pdf'}
            max_size = 10 * 1024 * 1024  # 10MB
        else:  # image
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
            max_size = 5 * 1024 * 1024  # 5MB
        
        # Check file extension
        if not allowed_file(file.filename, allowed_extensions):
            return jsonify({
                'error': 'Invalid file format',
                'message': f'Allowed formats for {file_type}: {", ".join(allowed_extensions)}'
            }), 400
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > max_size:
            return jsonify({
                'error': 'File size too large',
                'message': f'Maximum file size for {file_type}: {max_size // (1024*1024)}MB'
            }), 400
        
        # Generate unique filename
        original_filename = secure_filename(file.filename)
        file_extension = original_filename.rsplit('.', 1)[1].lower()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        new_filename = f"{original_filename.rsplit('.', 1)[0]}_{timestamp}.{file_extension}"
        
        # Create upload directory if it doesn't exist
        upload_dir = os.path.join(os.getcwd(), 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file
        file_path = os.path.join(upload_dir, new_filename)
        file.save(file_path)
        
        # Generate URL (in production, use proper domain)
        file_url = url_for('files.get_uploaded_file', filename=new_filename, _external=True)
        
        # Create file record in database
        file_record = File(
            filename=new_filename,
            original_name=original_filename,
            url=file_url,
            file_type=file_type,
            category=category,
            size=file_size
        )
        
        db.session.add(file_record)
        db.session.commit()
        
        return jsonify(file_record.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 500

@files_bp.route('/<file_id>', methods=['GET'])
def get_file_metadata(file_id):
    """Get file metadata by ID"""
    try:
        file_record = File.query.get(file_id)
        
        if not file_record:
            return jsonify({
                'error': 'Not Found',
                'message': 'File not found'
            }), 404
        
        return jsonify(file_record.to_dict()), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 500

@files_bp.route('/<file_id>', methods=['DELETE'])
@token_required
def delete_file(current_user, file_id):
    """Delete file and its metadata"""
    try:
        file_record = File.query.get(file_id)
        
        if not file_record:
            return jsonify({
                'error': 'Not Found',
                'message': 'File not found'
            }), 404
        
        # Delete physical file
        file_path = os.path.join(os.getcwd(), 'uploads', file_record.filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Delete database record
        db.session.delete(file_record)
        db.session.commit()
        
        return '', 204
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 500

@files_bp.route('', methods=['GET'])
@token_required
def get_files(current_user):
    """Get list of uploaded files"""
    try:
        # Get query parameters
        file_type = request.args.get('type')
        category = request.args.get('category')
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        # Build query
        query = File.query
        
        # Apply file type filter
        if file_type:
            if file_type not in ['pdf', 'image']:
                return jsonify({
                    'error': 'Invalid file type',
                    'message': 'Type must be either "pdf" or "image"'
                }), 400
            query = query.filter(File.file_type == file_type)
        
        # Apply category filter
        if category:
            query = query.filter(File.category == category)
        
        # Get total count
        total = query.count()
        
        # Apply pagination and get results
        files = query.order_by(File.uploaded_at.desc()).offset(offset).limit(limit).all()
        
        return jsonify({
            'files': [file.to_dict() for file in files],
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

@files_bp.route('/uploads/<filename>')
def get_uploaded_file(filename):
    """Serve uploaded files"""
    upload_dir = os.path.join(os.getcwd(), 'uploads')
    return send_from_directory(upload_dir, filename)