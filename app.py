from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import datetime, timedelta
import os

# Import models and database
from models import db, jwt
from models.user import User
from models.law import Law
from models.news import News
from models.comrade import Comrade
from models.file import File

# Import routes
from routes.auth import auth_bp, check_if_token_revoked
from routes.laws import laws_bp
from routes.news import news_bp
from routes.comrades import comrades_bp
from routes.files import files_bp

# Import configuration
from config import Config

def create_app():
    """Application factory"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(laws_bp, url_prefix='/api/laws')
    app.register_blueprint(news_bp, url_prefix='/api/news')
    app.register_blueprint(comrades_bp, url_prefix='/api/comrades')
    app.register_blueprint(files_bp, url_prefix='/api/files')
    
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
    
    # Swagger documentation endpoint
    @app.route('/docs/')
    @app.route('/docs')
    def swagger_docs():
        """Simple API Documentation"""
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Veterans Association API Documentation</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
                h2 { color: #34495e; margin-top: 30px; }
                .endpoint { background: #ecf0f1; padding: 15px; margin: 10px 0; border-radius: 5px; }
                .method { display: inline-block; padding: 5px 10px; border-radius: 3px; font-weight: bold; }
                .get { background: #27ae60; color: white; }
                .post { background: #e74c3c; color: white; }
                .put { background: #f39c12; color: white; }
                .delete { background: #e74c3c; color: white; }
                .auth { color: #e67e22; font-weight: bold; }
                code { background: #34495e; color: white; padding: 2px 5px; border-radius: 3px; }
                .json-spec { background: #2c3e50; color: #ecf0f1; padding: 20px; border-radius: 5px; overflow: auto; }
                .btn { background: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Veterans Association API Documentation</h1>
                <p>Complete REST API for managing laws, news, comrades search, and file uploads.</p>
                <p><strong>Base URL:</strong> <code>/api</code></p>
                
                <p><a href="/api/swagger.json" class="btn">View OpenAPI 3.0 Specification</a></p>
                
                <h2>Authentication</h2>
                <div class="endpoint">
                    <span class="method post">POST</span> <code>/auth/login</code>
                    <p>Login with username/password to get JWT token</p>
                </div>
                <div class="endpoint">
                    <span class="method post">POST</span> <code>/auth/logout</code> <span class="auth">[Auth Required]</span>
                    <p>Logout and invalidate token</p>
                </div>
                <div class="endpoint">
                    <span class="method get">GET</span> <code>/auth/verify</code> <span class="auth">[Auth Required]</span>
                    <p>Verify token validity</p>
                </div>

                <h2>Laws Management</h2>
                <div class="endpoint">
                    <span class="method get">GET</span> <code>/laws</code>
                    <p>Get all laws with filtering (category, search, pagination)</p>
                </div>
                <div class="endpoint">
                    <span class="method get">GET</span> <code>/laws/{id}</code>
                    <p>Get specific law by ID</p>
                </div>
                <div class="endpoint">
                    <span class="method post">POST</span> <code>/laws</code> <span class="auth">[Auth Required]</span>
                    <p>Create new law with multilingual support</p>
                </div>
                <div class="endpoint">
                    <span class="method put">PUT</span> <code>/laws/{id}</code> <span class="auth">[Auth Required]</span>
                    <p>Update existing law</p>
                </div>
                <div class="endpoint">
                    <span class="method delete">DELETE</span> <code>/laws/{id}</code> <span class="auth">[Auth Required]</span>
                    <p>Delete law</p>
                </div>

                <h2>News Management</h2>
                <div class="endpoint">
                    <span class="method get">GET</span> <code>/news</code>
                    <p>Get all news with filtering, sorting, and pagination</p>
                </div>
                <div class="endpoint">
                    <span class="method get">GET</span> <code>/news/{id}</code>
                    <p>Get specific news by ID</p>
                </div>
                <div class="endpoint">
                    <span class="method post">POST</span> <code>/news</code> <span class="auth">[Auth Required]</span>
                    <p>Create new news with multilingual support</p>
                </div>
                <div class="endpoint">
                    <span class="method put">PUT</span> <code>/news/{id}</code> <span class="auth">[Auth Required]</span>
                    <p>Update existing news</p>
                </div>
                <div class="endpoint">
                    <span class="method delete">DELETE</span> <code>/news/{id}</code> <span class="auth">[Auth Required]</span>
                    <p>Delete news</p>
                </div>

                <h2>Comrades Search</h2>
                <div class="endpoint">
                    <span class="method get">GET</span> <code>/comrades</code>
                    <p>Search comrades with filters (name, unit, region, years, rank)</p>
                </div>
                <div class="endpoint">
                    <span class="method get">GET</span> <code>/comrades/{id}</code>
                    <p>Get specific comrade by ID</p>
                </div>
                <div class="endpoint">
                    <span class="method post">POST</span> <code>/comrades</code>
                    <p>Add new comrade information</p>
                </div>
                <div class="endpoint">
                    <span class="method put">PUT</span> <code>/comrades/{id}</code> <span class="auth">[Auth Required]</span>
                    <p>Update comrade information</p>
                </div>
                <div class="endpoint">
                    <span class="method delete">DELETE</span> <code>/comrades/{id}</code> <span class="auth">[Auth Required]</span>
                    <p>Delete comrade information</p>
                </div>

                <h2>File Management</h2>
                <div class="endpoint">
                    <span class="method post">POST</span> <code>/files/upload</code> <span class="auth">[Auth Required]</span>
                    <p>Upload PDF or image files</p>
                </div>
                <div class="endpoint">
                    <span class="method get">GET</span> <code>/files</code> <span class="auth">[Auth Required]</span>
                    <p>List uploaded files with filtering</p>
                </div>
                <div class="endpoint">
                    <span class="method get">GET</span> <code>/files/{id}</code>
                    <p>Get file metadata by ID</p>
                </div>
                <div class="endpoint">
                    <span class="method delete">DELETE</span> <code>/files/{id}</code> <span class="auth">[Auth Required]</span>
                    <p>Delete file and metadata</p>
                </div>

                <h2>Example Usage</h2>
                <h3>Login:</h3>
                <pre><code>curl -X POST http://localhost:5000/api/auth/login \\
  -H "Content-Type: application/json" \\
  -d '{"username":"admin","password":"admin"}'</code></pre>

                <h3>Get Laws:</h3>
                <pre><code>curl http://localhost:5000/api/laws?limit=10&category=федеральный</code></pre>

                <h3>Create News (with token):</h3>
                <pre><code>curl -X POST http://localhost:5000/api/news \\
  -H "Authorization: Bearer &lt;token&gt;" \\
  -H "Content-Type: application/json" \\
  -d '{"title": {"ru":"Новость","uz":"Yangilik","en":"News"}, ...}'</code></pre>

                <p><strong>Default Admin:</strong> username: <code>admin</code>, password: <code>admin</code></p>
            </div>
        </body>
        </html>
        '''
    
    @app.route('/api/swagger.json')
    def swagger_json():
        """OpenAPI specification"""
        swagger_spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "Veterans Association API",
                "description": "API для Ассоциации Ветеранов - управление законами, новостями, поиск сослуживцев и файлы",
                "version": "1.0.0"
            },
            "servers": [
                {"url": "/api", "description": "API server"}
            ],
            "components": {
                "securitySchemes": {
                    "Bearer": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT",
                        "description": "JWT token for authentication"
                    }
                },
                "schemas": {
                    "MultiLangText": {
                        "type": "object",
                        "properties": {
                            "ru": {"type": "string", "description": "Russian text"},
                            "uz": {"type": "string", "description": "Uzbek text"},
                            "en": {"type": "string", "description": "English text"}
                        },
                        "required": ["ru", "uz", "en"]
                    },
                    "Law": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "title": {"$ref": "#/components/schemas/MultiLangText"},
                            "description": {"$ref": "#/components/schemas/MultiLangText"},
                            "category": {"$ref": "#/components/schemas/MultiLangText"},
                            "date": {"type": "string", "format": "date"},
                            "pdfUrl": {"type": "string", "nullable": True},
                            "createdAt": {"type": "string", "format": "date-time"},
                            "updatedAt": {"type": "string", "format": "date-time"}
                        }
                    },
                    "News": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "title": {"$ref": "#/components/schemas/MultiLangText"},
                            "content": {"$ref": "#/components/schemas/MultiLangText"},
                            "summary": {"$ref": "#/components/schemas/MultiLangText"},
                            "date": {"type": "string", "format": "date"},
                            "imageUrl": {"type": "string", "nullable": True},
                            "createdAt": {"type": "string", "format": "date-time"},
                            "updatedAt": {"type": "string", "format": "date-time"}
                        }
                    },
                    "Comrade": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "firstName": {"type": "string"},
                            "lastName": {"type": "string"},
                            "middleName": {"type": "string", "nullable": True},
                            "unit": {"type": "string"},
                            "region": {"type": "string"},
                            "yearOfServiceFrom": {"type": "integer"},
                            "yearOfServiceTo": {"type": "integer", "nullable": True},
                            "rank": {"type": "string", "nullable": True},
                            "photoUrl": {"type": "string", "nullable": True},
                            "contactInfo": {"type": "object"},
                            "additionalInfo": {"type": "string", "nullable": True},
                            "isVerified": {"type": "boolean"},
                            "createdAt": {"type": "string", "format": "date-time"},
                            "updatedAt": {"type": "string", "format": "date-time"}
                        }
                    },
                    "LoginRequest": {
                        "type": "object",
                        "properties": {
                            "username": {"type": "string"},
                            "password": {"type": "string"}
                        },
                        "required": ["username", "password"]
                    },
                    "Error": {
                        "type": "object",
                        "properties": {
                            "error": {"type": "string"},
                            "message": {"type": "string"},
                            "timestamp": {"type": "string", "format": "date-time"}
                        }
                    }
                }
            },
            "paths": {
                "/auth/login": {
                    "post": {
                        "tags": ["Authentication"],
                        "summary": "Login user",
                        "description": "Authenticate user and return JWT token",
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/LoginRequest"}
                                }
                            }
                        },
                        "responses": {
                            "200": {
                                "description": "Login successful",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "token": {"type": "string"},
                                                "user": {"type": "object"}
                                            }
                                        }
                                    }
                                }
                            },
                            "401": {
                                "description": "Invalid credentials",
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": "#/components/schemas/Error"}
                                    }
                                }
                            }
                        }
                    }
                },
                "/auth/logout": {
                    "post": {
                        "tags": ["Authentication"],
                        "summary": "Logout user",
                        "description": "Deactivate JWT token",
                        "security": [{"Bearer": []}],
                        "responses": {
                            "204": {"description": "Logout successful"},
                            "401": {"description": "Unauthorized"}
                        }
                    }
                },
                "/auth/verify": {
                    "get": {
                        "tags": ["Authentication"],
                        "summary": "Verify token",
                        "description": "Verify JWT token validity",
                        "security": [{"Bearer": []}],
                        "responses": {
                            "200": {
                                "description": "Token is valid",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "valid": {"type": "boolean"},
                                                "user": {"type": "object"}
                                            }
                                        }
                                    }
                                }
                            },
                            "401": {"description": "Token invalid"}
                        }
                    }
                },
                "/laws": {
                    "get": {
                        "tags": ["Laws"],
                        "summary": "Get all laws",
                        "description": "Get all laws with optional filtering",
                        "parameters": [
                            {"name": "category", "in": "query", "schema": {"type": "string"}, "description": "Filter by category"},
                            {"name": "search", "in": "query", "schema": {"type": "string"}, "description": "Search in title and description"},
                            {"name": "limit", "in": "query", "schema": {"type": "integer", "default": 50}, "description": "Number of results"},
                            {"name": "offset", "in": "query", "schema": {"type": "integer", "default": 0}, "description": "Offset for pagination"}
                        ],
                        "responses": {
                            "200": {
                                "description": "List of laws",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "laws": {"type": "array", "items": {"$ref": "#/components/schemas/Law"}},
                                                "total": {"type": "integer"},
                                                "limit": {"type": "integer"},
                                                "offset": {"type": "integer"}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "post": {
                        "tags": ["Laws"],
                        "summary": "Create law",
                        "description": "Create new law",
                        "security": [{"Bearer": []}],
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "title": {"$ref": "#/components/schemas/MultiLangText"},
                                            "description": {"$ref": "#/components/schemas/MultiLangText"},
                                            "category": {"$ref": "#/components/schemas/MultiLangText"},
                                            "date": {"type": "string", "format": "date"},
                                            "pdfUrl": {"type": "string"}
                                        },
                                        "required": ["title", "description", "category", "date"]
                                    }
                                }
                            }
                        },
                        "responses": {
                            "201": {
                                "description": "Law created",
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": "#/components/schemas/Law"}
                                    }
                                }
                            },
                            "400": {"description": "Validation error"},
                            "401": {"description": "Unauthorized"}
                        }
                    }
                },
                "/laws/{id}": {
                    "get": {
                        "tags": ["Laws"],
                        "summary": "Get law by ID",
                        "parameters": [{"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}}],
                        "responses": {
                            "200": {
                                "description": "Law details",
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": "#/components/schemas/Law"}
                                    }
                                }
                            },
                            "404": {"description": "Law not found"}
                        }
                    },
                    "put": {
                        "tags": ["Laws"],
                        "summary": "Update law",
                        "security": [{"Bearer": []}],
                        "parameters": [{"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}}],
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "title": {"$ref": "#/components/schemas/MultiLangText"},
                                            "description": {"$ref": "#/components/schemas/MultiLangText"},
                                            "category": {"$ref": "#/components/schemas/MultiLangText"},
                                            "date": {"type": "string", "format": "date"},
                                            "pdfUrl": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        },
                        "responses": {
                            "200": {"description": "Law updated"},
                            "404": {"description": "Law not found"},
                            "401": {"description": "Unauthorized"}
                        }
                    },
                    "delete": {
                        "tags": ["Laws"],
                        "summary": "Delete law",
                        "security": [{"Bearer": []}],
                        "parameters": [{"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}}],
                        "responses": {
                            "204": {"description": "Law deleted"},
                            "404": {"description": "Law not found"},
                            "401": {"description": "Unauthorized"}
                        }
                    }
                },
                "/news": {
                    "get": {
                        "tags": ["News"],
                        "summary": "Get all news",
                        "description": "Get all news with optional filtering and sorting",
                        "parameters": [
                            {"name": "search", "in": "query", "schema": {"type": "string"}},
                            {"name": "dateFrom", "in": "query", "schema": {"type": "string", "format": "date"}},
                            {"name": "dateTo", "in": "query", "schema": {"type": "string", "format": "date"}},
                            {"name": "limit", "in": "query", "schema": {"type": "integer", "default": 20}},
                            {"name": "offset", "in": "query", "schema": {"type": "integer", "default": 0}},
                            {"name": "sortBy", "in": "query", "schema": {"type": "string", "enum": ["date", "title"], "default": "date"}},
                            {"name": "sortOrder", "in": "query", "schema": {"type": "string", "enum": ["asc", "desc"], "default": "desc"}}
                        ],
                        "responses": {
                            "200": {
                                "description": "List of news",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "news": {"type": "array", "items": {"$ref": "#/components/schemas/News"}},
                                                "total": {"type": "integer"},
                                                "limit": {"type": "integer"},
                                                "offset": {"type": "integer"}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "post": {
                        "tags": ["News"],
                        "summary": "Create news",
                        "security": [{"Bearer": []}],
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "title": {"$ref": "#/components/schemas/MultiLangText"},
                                            "content": {"$ref": "#/components/schemas/MultiLangText"},
                                            "summary": {"$ref": "#/components/schemas/MultiLangText"},
                                            "date": {"type": "string", "format": "date"},
                                            "imageUrl": {"type": "string"}
                                        },
                                        "required": ["title", "content", "summary", "date"]
                                    }
                                }
                            }
                        },
                        "responses": {
                            "201": {"description": "News created"},
                            "401": {"description": "Unauthorized"}
                        }
                    }
                },
                "/news/{id}": {
                    "get": {
                        "tags": ["News"],
                        "summary": "Get news by ID",
                        "parameters": [{"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}}],
                        "responses": {
                            "200": {"description": "News details"},
                            "404": {"description": "News not found"}
                        }
                    },
                    "put": {
                        "tags": ["News"],
                        "summary": "Update news",
                        "security": [{"Bearer": []}],
                        "parameters": [{"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}}],
                        "responses": {
                            "200": {"description": "News updated"},
                            "401": {"description": "Unauthorized"}
                        }
                    },
                    "delete": {
                        "tags": ["News"],
                        "summary": "Delete news",
                        "security": [{"Bearer": []}],
                        "parameters": [{"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}}],
                        "responses": {
                            "204": {"description": "News deleted"},
                            "401": {"description": "Unauthorized"}
                        }
                    }
                },
                "/comrades": {
                    "get": {
                        "tags": ["Comrades"],
                        "summary": "Search comrades",
                        "parameters": [
                            {"name": "name", "in": "query", "schema": {"type": "string"}},
                            {"name": "unit", "in": "query", "schema": {"type": "string"}},
                            {"name": "region", "in": "query", "schema": {"type": "string"}},
                            {"name": "yearFrom", "in": "query", "schema": {"type": "integer"}},
                            {"name": "yearTo", "in": "query", "schema": {"type": "integer"}},
                            {"name": "rank", "in": "query", "schema": {"type": "string"}},
                            {"name": "limit", "in": "query", "schema": {"type": "integer", "default": 50}},
                            {"name": "offset", "in": "query", "schema": {"type": "integer", "default": 0}}
                        ],
                        "responses": {
                            "200": {"description": "Search results"}
                        }
                    },
                    "post": {
                        "tags": ["Comrades"],
                        "summary": "Add comrade",
                        "responses": {
                            "201": {"description": "Comrade added"}
                        }
                    }
                },
                "/comrades/{id}": {
                    "get": {
                        "tags": ["Comrades"],
                        "summary": "Get comrade by ID",
                        "parameters": [{"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}}],
                        "responses": {
                            "200": {"description": "Comrade details"},
                            "404": {"description": "Comrade not found"}
                        }
                    },
                    "put": {
                        "tags": ["Comrades"],
                        "summary": "Update comrade",
                        "security": [{"Bearer": []}],
                        "parameters": [{"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}}],
                        "responses": {
                            "200": {"description": "Comrade updated"},
                            "401": {"description": "Unauthorized"}
                        }
                    },
                    "delete": {
                        "tags": ["Comrades"],
                        "summary": "Delete comrade",
                        "security": [{"Bearer": []}],
                        "parameters": [{"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}}],
                        "responses": {
                            "204": {"description": "Comrade deleted"},
                            "401": {"description": "Unauthorized"}
                        }
                    }
                },
                "/files/upload": {
                    "post": {
                        "tags": ["Files"],
                        "summary": "Upload file",
                        "security": [{"Bearer": []}],
                        "requestBody": {
                            "content": {
                                "multipart/form-data": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "file": {"type": "string", "format": "binary"},
                                            "type": {"type": "string", "enum": ["pdf", "image"]},
                                            "category": {"type": "string", "enum": ["law", "news", "photo", "other"]}
                                        },
                                        "required": ["file", "type"]
                                    }
                                }
                            }
                        },
                        "responses": {
                            "201": {"description": "File uploaded"},
                            "400": {"description": "Invalid file"},
                            "401": {"description": "Unauthorized"}
                        }
                    }
                },
                "/files": {
                    "get": {
                        "tags": ["Files"],
                        "summary": "List files",
                        "security": [{"Bearer": []}],
                        "parameters": [
                            {"name": "type", "in": "query", "schema": {"type": "string", "enum": ["pdf", "image"]}},
                            {"name": "category", "in": "query", "schema": {"type": "string"}},
                            {"name": "limit", "in": "query", "schema": {"type": "integer", "default": 50}},
                            {"name": "offset", "in": "query", "schema": {"type": "integer", "default": 0}}
                        ],
                        "responses": {
                            "200": {"description": "File list"},
                            "401": {"description": "Unauthorized"}
                        }
                    }
                },
                "/files/{id}": {
                    "get": {
                        "tags": ["Files"],
                        "summary": "Get file metadata",
                        "parameters": [{"name": "id", "in": "path", "required": True, "schema": {"type": "string"}}],
                        "responses": {
                            "200": {"description": "File metadata"},
                            "404": {"description": "File not found"}
                        }
                    },
                    "delete": {
                        "tags": ["Files"],
                        "summary": "Delete file",
                        "security": [{"Bearer": []}],
                        "parameters": [{"name": "id", "in": "path", "required": True, "schema": {"type": "string"}}],
                        "responses": {
                            "204": {"description": "File deleted"},
                            "401": {"description": "Unauthorized"}
                        }
                    }
                }
            }
        }
        return jsonify(swagger_spec)
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat() + 'Z',
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