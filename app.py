from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import datetime, timedelta, timezone
import os

# Import models and database
from models import db, jwt
from models.user import User
from models.law import Law
from models.news import News
from models.comrade import Comrade
from models.file import File

# Import Flask-RESTX API configuration
from api_config import api

# Import routes (they now register with Flask-RESTX namespaces automatically)
from routes.auth import check_if_token_revoked
from routes import laws, news, comrades, files, auth

# Import configuration
from config import Config

def create_app():
    """Application factory"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    CORS(app, 
         origins=app.config['CORS_ORIGINS'],
         allow_headers=app.config['CORS_ALLOW_HEADERS'],
         supports_credentials=app.config['CORS_SUPPORTS_CREDENTIALS'])
    
    # Initialize Flask-RESTX API
    api.init_app(app)
    
    # JWT configuration
    @jwt.token_in_blocklist_loader
    def check_if_token_is_revoked(jwt_header, jwt_payload):
        return check_if_token_revoked(jwt_header, jwt_payload)
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'error': 'Token expired',
            'message': 'The token has expired'
        }), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'error': 'Invalid token',
            'message': 'Token is invalid'
        }), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            'error': 'Authorization token required',
            'message': 'Request does not contain an access token'
        }), 401
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested resource was not found',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'error': 'Method Not Allowed',
            'message': 'The method is not allowed for the requested URL',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 405
    
    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 500
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'version': '1.0.0'
        })
    
    # API info endpoint
    @app.route('/api/info')
    def api_info():
        return jsonify({
            'message': 'Veterans Association API',
            'documentation': '/docs/',
            'version': '1.0.0',
            'endpoints': {
                'authentication': '/api/auth',
                'laws': '/api/laws',
                'news': '/api/news',
                'comrades': '/api/comrades',
                'files': '/api/files'
            }
        })
    
    return app

def init_db(app):
    """Initialize database with sample data"""
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if admin user exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            # Create default admin user
            admin = User(username='admin', password='admin', role='admin')
            db.session.add(admin)
            
            # Create sample law
            sample_law = Law(
                title_ru='Закон о ветеранах',
                title_uz='Veteranlar haqidagi qonun',
                title_en='Veterans Law',
                description_ru='Федеральный закон о ветеранах',
                description_uz='Veteranlar haqidagi federal qonun',
                description_en='Federal Veterans Law',
                category_ru='Федеральный закон',
                category_uz='Federal qonun',
                category_en='Federal Law',
                date=datetime(2023, 1, 15).date(),
                pdf_url='https://example.com/files/law1.pdf'
            )
            db.session.add(sample_law)
            
            # Create sample news
            sample_news = News(
                title_ru='Важная новость',
                title_uz='Muhim yangilik',
                title_en='Important News',
                content_ru='Полный текст новости о важных изменениях в законодательстве для ветеранов.',
                content_uz='Veteranlar uchun qonunchilikdagi muhim o\'zgarishlar haqida yangilik to\'liq matni.',
                content_en='Full news text about important legislative changes for veterans.',
                summary_ru='Краткое описание важных изменений',
                summary_uz='Muhim o\'zgarishlarning qisqacha tavsifi',
                summary_en='Brief description of important changes',
                date=datetime(2024, 1, 15).date(),
                image_url='https://example.com/images/news1.jpg'
            )
            db.session.add(sample_news)
            
            # Create sample comrade
            sample_comrade = Comrade(
                first_name='Иван',
                last_name='Иванов',
                middle_name='Петрович',
                unit='Воинская часть 12345',
                region='Ташкентская область',
                year_of_service_from=1990,
                year_of_service_to=1992,
                rank='Сержант',
                photo_url='https://example.com/photos/person1.jpg',
                additional_info='Служил в танковых войсках',
                is_verified=True
            )
            sample_comrade.set_contact_info({
                'phone': '+998901234567',
                'email': 'ivanov@example.com',
                'address': 'г. Ташкент, ул. Примерная 123'
            })
            db.session.add(sample_comrade)
            
            db.session.commit()
            print("Database initialized with sample data")
            print("Admin credentials: admin/admin")

if __name__ == '__main__':
    app = create_app()
    init_db(app)
    
    # Run the application
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    app.run(host=host, port=port, debug=debug)