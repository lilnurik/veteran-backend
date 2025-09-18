from flask import request, send_from_directory
from flask_restx import Resource
from models import db
from models.file import File
from utils.auth import token_required
from utils.validators import allowed_file
from datetime import datetime
import os
import uuid
from api_config import files_ns, file_model, files_response_model, error_model


@files_ns.route('/upload')
class FileUploadResource(Resource):
    @files_ns.response(201, 'File uploaded successfully', file_model)
    @files_ns.response(400, 'Invalid file', error_model)
    @files_ns.response(401, 'Unauthorized', error_model)
    @files_ns.doc(security='Bearer')
    @token_required
    def post(self, current_user):
        """Upload file (PDF or image)"""
        return {"message": "Not implemented yet"}, 501


@files_ns.route('')
class FilesListResource(Resource):
    @files_ns.response(200, 'Files retrieved successfully', files_response_model)
    @files_ns.response(401, 'Unauthorized', error_model)
    @files_ns.param('type', 'Filter by file type (pdf/image)', type='string')
    @files_ns.param('category', 'Filter by category', type='string')
    @files_ns.param('limit', 'Number of results (default: 50)', type='integer', default=50)
    @files_ns.param('offset', 'Offset for pagination (default: 0)', type='integer', default=0)
    @files_ns.doc(security='Bearer')
    @token_required  
    def get(self, current_user):
        """Get list of uploaded files"""
        return {"files": [], "total": 0, "limit": 50, "offset": 0}


@files_ns.route('/<file_id>')
class FileResource(Resource):
    @files_ns.response(200, 'File metadata retrieved successfully', file_model)
    @files_ns.response(404, 'File not found', error_model)
    def get(self, file_id):
        """Get file metadata by ID"""
        return {"message": "Not implemented yet"}, 501
    
    @files_ns.response(204, 'File deleted successfully')
    @files_ns.response(404, 'File not found', error_model)
    @files_ns.response(401, 'Unauthorized', error_model)
    @files_ns.doc(security='Bearer')
    @token_required
    def delete(self, current_user, file_id):
        """Delete file and its metadata"""
        return {"message": "Not implemented yet"}, 501


@files_ns.route('/uploads/<filename>')
class UploadedFileResource(Resource):
    def get(self, filename):
        """Serve uploaded files"""
        upload_dir = os.path.join(os.getcwd(), 'uploads')
        return send_from_directory(upload_dir, filename)