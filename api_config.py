"""
Flask-RESTX API configuration and shared models for Swagger documentation
"""
from flask_restx import Api, Namespace, fields

# Initialize Flask-RESTX API
api = Api(
    version='1.0.0',
    title='Veterans Association API',
    description='API для Ассоциации Ветеранов - управление законами, новостями, поиск сослуживцев и файлы',
    doc='/docs/',
    prefix='/api',
    authorizations={
        'Bearer': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'JWT Authorization header. Example: "Bearer {token}"'
        }
    },
    security='Bearer'
)

# Define namespaces
auth_ns = Namespace('auth', description='Authentication operations')
laws_ns = Namespace('laws', description='Laws management operations')  
news_ns = Namespace('news', description='News management operations')
comrades_ns = Namespace('comrades', description='Comrades search operations')
files_ns = Namespace('files', description='File management operations')

# Add namespaces to API
api.add_namespace(auth_ns, path='/auth')
api.add_namespace(laws_ns, path='/laws')
api.add_namespace(news_ns, path='/news') 
api.add_namespace(comrades_ns, path='/comrades')
api.add_namespace(files_ns, path='/files')

# Shared models
multilang_text = api.model('MultiLangText', {
    'ru': fields.String(required=True, description='Russian text'),
    'uz': fields.String(required=True, description='Uzbek text'), 
    'en': fields.String(required=True, description='English text')
})

error_model = api.model('Error', {
    'error': fields.String(required=True, description='Error type'),
    'message': fields.String(required=True, description='Error message'),
    'details': fields.Raw(description='Additional error details'),
    'timestamp': fields.DateTime(required=True, description='Error timestamp')
})

validation_error_model = api.model('ValidationError', {
    'error': fields.String(required=True, description='Error type'),
    'message': fields.String(required=True, description='Error message'), 
    'details': fields.Raw(required=True, description='Validation error details'),
    'timestamp': fields.DateTime(required=True, description='Error timestamp')
})

# Authentication models
login_model = api.model('LoginRequest', {
    'username': fields.String(required=True, description='Username'),
    'password': fields.String(required=True, description='Password')
})

login_response_model = api.model('LoginResponse', {
    'token': fields.String(required=True, description='JWT access token'),
    'user': fields.Raw(required=True, description='User information')
})

token_verify_model = api.model('TokenVerifyResponse', {
    'valid': fields.Boolean(required=True, description='Token validity status'),
    'user': fields.Raw(required=True, description='User information')
})

# Law models
law_model = api.model('Law', {
    'id': fields.Integer(description='Law ID'),
    'title': fields.Nested(multilang_text, required=True, description='Law title'),
    'description': fields.Nested(multilang_text, required=True, description='Law description'),
    'category': fields.Nested(multilang_text, required=True, description='Law category'),
    'date': fields.Date(required=True, description='Law date'),
    'pdfUrl': fields.String(description='PDF file URL'),
    'createdAt': fields.DateTime(description='Creation timestamp'),
    'updatedAt': fields.DateTime(description='Last update timestamp')
})

law_create_model = api.model('LawCreateRequest', {
    'title': fields.Nested(multilang_text, required=True, description='Law title'),
    'description': fields.Nested(multilang_text, required=True, description='Law description'),
    'category': fields.Nested(multilang_text, required=True, description='Law category'),
    'date': fields.Date(required=True, description='Law date (YYYY-MM-DD)'),
    'pdfUrl': fields.String(description='PDF file URL')
})

laws_response_model = api.model('LawsResponse', {
    'laws': fields.List(fields.Nested(law_model), description='List of laws'),
    'total': fields.Integer(description='Total number of laws'),
    'limit': fields.Integer(description='Results limit'),
    'offset': fields.Integer(description='Results offset')
})

# News models  
news_model = api.model('News', {
    'id': fields.Integer(description='News ID'),
    'title': fields.Nested(multilang_text, required=True, description='News title'),
    'content': fields.Nested(multilang_text, required=True, description='News content'),
    'summary': fields.Nested(multilang_text, required=True, description='News summary'),
    'date': fields.Date(required=True, description='News date'),
    'imageUrl': fields.String(description='Image URL'),
    'createdAt': fields.DateTime(description='Creation timestamp'),
    'updatedAt': fields.DateTime(description='Last update timestamp')
})

news_create_model = api.model('NewsCreateRequest', {
    'title': fields.Nested(multilang_text, required=True, description='News title'),
    'content': fields.Nested(multilang_text, required=True, description='News content'),
    'summary': fields.Nested(multilang_text, required=True, description='News summary'),
    'date': fields.Date(required=True, description='News date (YYYY-MM-DD)'),
    'imageUrl': fields.String(description='Image URL')
})

news_response_model = api.model('NewsResponse', {
    'news': fields.List(fields.Nested(news_model), description='List of news'),
    'total': fields.Integer(description='Total number of news'),
    'limit': fields.Integer(description='Results limit'),
    'offset': fields.Integer(description='Results offset')
})

# Comrade models
comrade_model = api.model('Comrade', {
    'id': fields.Integer(description='Comrade ID'),
    'firstName': fields.String(required=True, description='First name'),
    'lastName': fields.String(required=True, description='Last name'),
    'middleName': fields.String(description='Middle name'),
    'unit': fields.String(required=True, description='Military unit'),
    'region': fields.String(required=True, description='Service region'),
    'yearOfServiceFrom': fields.Integer(required=True, description='Service start year'),
    'yearOfServiceTo': fields.Integer(description='Service end year'),
    'rank': fields.String(description='Military rank'),
    'photoUrl': fields.String(description='Photo URL'),
    'contactInfo': fields.Raw(description='Contact information'),
    'additionalInfo': fields.String(description='Additional information'),
    'isVerified': fields.Boolean(description='Verification status'),
    'createdAt': fields.DateTime(description='Creation timestamp'),
    'updatedAt': fields.DateTime(description='Last update timestamp')
})

comrade_create_model = api.model('ComradeCreateRequest', {
    'firstName': fields.String(required=True, description='First name'),
    'lastName': fields.String(required=True, description='Last name'),
    'middleName': fields.String(description='Middle name'),
    'unit': fields.String(required=True, description='Military unit'),
    'region': fields.String(required=True, description='Service region'),
    'yearOfServiceFrom': fields.Integer(required=True, description='Service start year'),
    'yearOfServiceTo': fields.Integer(description='Service end year'),
    'rank': fields.String(description='Military rank'),
    'photoUrl': fields.String(description='Photo URL'),
    'contactInfo': fields.Raw(description='Contact information'),
    'additionalInfo': fields.String(description='Additional information')
})

comrades_response_model = api.model('ComradesResponse', {
    'comrades': fields.List(fields.Nested(comrade_model), description='List of comrades'),
    'total': fields.Integer(description='Total number of comrades'),
    'limit': fields.Integer(description='Results limit'),
    'offset': fields.Integer(description='Results offset')
})

# File models
file_model = api.model('File', {
    'id': fields.String(description='File ID'),
    'filename': fields.String(description='File name'),
    'originalName': fields.String(description='Original file name'),
    'url': fields.String(description='File URL'),
    'fileType': fields.String(description='File type (pdf/image)'),
    'category': fields.String(description='File category'),
    'size': fields.Integer(description='File size in bytes'),
    'uploadedAt': fields.DateTime(description='Upload timestamp')
})

files_response_model = api.model('FilesResponse', {
    'files': fields.List(fields.Nested(file_model), description='List of files'),
    'total': fields.Integer(description='Total number of files'),
    'limit': fields.Integer(description='Results limit'),
    'offset': fields.Integer(description='Results offset')
})