from flask import Blueprint, request, jsonify
from models import db
from models.news import News
from utils.auth import token_required
from utils.validators import validate_multilang_field, validate_date_field
from datetime import datetime
from sqlalchemy import or_, desc, asc

news_bp = Blueprint('news', __name__)

@news_bp.route('', methods=['GET'])
def get_news():
    """Get all news with optional filtering and sorting"""
    try:
        # Get query parameters
        search = request.args.get('search')
        date_from = request.args.get('dateFrom')
        date_to = request.args.get('dateTo')
        limit = int(request.args.get('limit', 20))
        offset = int(request.args.get('offset', 0))
        sort_by = request.args.get('sortBy', 'date')
        sort_order = request.args.get('sortOrder', 'desc')
        
        # Build query
        query = News.query
        
        # Apply search filter
        if search:
            query = query.filter(
                or_(
                    News.title_ru.ilike(f'%{search}%'),
                    News.title_uz.ilike(f'%{search}%'),
                    News.title_en.ilike(f'%{search}%'),
                    News.content_ru.ilike(f'%{search}%'),
                    News.content_uz.ilike(f'%{search}%'),
                    News.content_en.ilike(f'%{search}%')
                )
            )
        
        # Apply date filters
        if date_from:
            try:
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
                query = query.filter(News.date >= date_from_obj)
            except ValueError:
                return jsonify({
                    'error': 'Invalid dateFrom format',
                    'message': 'Date must be in YYYY-MM-DD format'
                }), 400
        
        if date_to:
            try:
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
                query = query.filter(News.date <= date_to_obj)
            except ValueError:
                return jsonify({
                    'error': 'Invalid dateTo format',
                    'message': 'Date must be in YYYY-MM-DD format'
                }), 400
        
        # Apply sorting
        if sort_by == 'title':
            if sort_order == 'asc':
                query = query.order_by(asc(News.title_ru))
            else:
                query = query.order_by(desc(News.title_ru))
        else:  # sort by date (default)
            if sort_order == 'asc':
                query = query.order_by(asc(News.date))
            else:
                query = query.order_by(desc(News.date))
        
        # Get total count
        total = query.count()
        
        # Apply pagination and get results
        news_items = query.offset(offset).limit(limit).all()
        
        return jsonify({
            'news': [news.to_dict() for news in news_items],
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

@news_bp.route('/<int:news_id>', methods=['GET'])
def get_news_item(news_id):
    """Get specific news by ID"""
    try:
        news = News.query.get(news_id)
        
        if not news:
            return jsonify({
                'error': 'Not Found',
                'message': 'News not found'
            }), 404
        
        return jsonify(news.to_dict()), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 500

@news_bp.route('', methods=['POST'])
@token_required
def create_news(current_user):
    """Create new news"""
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
        errors.update(validate_multilang_field(data, 'content'))
        errors.update(validate_multilang_field(data, 'summary'))
        errors.update(validate_date_field(data, 'date'))
        
        if errors:
            return jsonify({
                'error': 'Validation Error',
                'message': 'Request validation failed',
                'details': errors,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }), 400
        
        # Create new news
        news = News(
            title_ru=data['title']['ru'],
            title_uz=data['title']['uz'],
            title_en=data['title']['en'],
            content_ru=data['content']['ru'],
            content_uz=data['content']['uz'],
            content_en=data['content']['en'],
            summary_ru=data['summary']['ru'],
            summary_uz=data['summary']['uz'],
            summary_en=data['summary']['en'],
            date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
            image_url=data.get('imageUrl')
        )
        
        db.session.add(news)
        db.session.commit()
        
        return jsonify(news.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 500

@news_bp.route('/<int:news_id>', methods=['PUT'])
@token_required
def update_news(current_user, news_id):
    """Update existing news"""
    try:
        news = News.query.get(news_id)
        
        if not news:
            return jsonify({
                'error': 'Not Found',
                'message': 'News not found'
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
        errors.update(validate_multilang_field(data, 'content'))
        errors.update(validate_multilang_field(data, 'summary'))
        errors.update(validate_date_field(data, 'date'))
        
        if errors:
            return jsonify({
                'error': 'Validation Error',
                'message': 'Request validation failed',
                'details': errors,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }), 400
        
        # Update news
        news.title_ru = data['title']['ru']
        news.title_uz = data['title']['uz']
        news.title_en = data['title']['en']
        news.content_ru = data['content']['ru']
        news.content_uz = data['content']['uz']
        news.content_en = data['content']['en']
        news.summary_ru = data['summary']['ru']
        news.summary_uz = data['summary']['uz']
        news.summary_en = data['summary']['en']
        news.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        news.image_url = data.get('imageUrl')
        news.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify(news.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 500

@news_bp.route('/<int:news_id>', methods=['DELETE'])
@token_required
def delete_news(current_user, news_id):
    """Delete news"""
    try:
        news = News.query.get(news_id)
        
        if not news:
            return jsonify({
                'error': 'Not Found',
                'message': 'News not found'
            }), 404
        
        db.session.delete(news)
        db.session.commit()
        
        return '', 204
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 500