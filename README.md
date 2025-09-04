# Veterans Association Backend API

Flask-based REST API for managing laws, news, comrades search, and file uploads for the Veterans Association.

## Features

- **Authentication**: JWT-based authentication system
- **Laws Management**: CRUD operations for laws with multilingual support (Russian, Uzbek, English)
- **News Management**: CRUD operations for news with multilingual support
- **Comrades Search**: Search and manage veteran comrades information
- **File Management**: Upload and manage PDF documents and images
- **Swagger Documentation**: Interactive API documentation at `/docs/`
- **Multi-language Support**: All content supports Russian, Uzbek, and English languages

## Installation

1. Install Python 3.12+ and pip
2. Clone the repository
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

## API Documentation

Once the application is running, visit `http://localhost:5000/docs/` for interactive Swagger documentation.

## Default Admin Credentials

- Username: `admin`
- Password: `admin`

**Note**: Change these credentials in production!

## API Endpoints

### Authentication
- `POST /api/auth/login` - Login and get JWT token
- `POST /api/auth/logout` - Logout and invalidate token
- `GET /api/auth/verify` - Verify token validity

### Laws
- `GET /api/laws` - Get all laws (supports filtering and pagination)
- `GET /api/laws/{id}` - Get specific law
- `POST /api/laws` - Create new law (requires auth)
- `PUT /api/laws/{id}` - Update law (requires auth)
- `DELETE /api/laws/{id}` - Delete law (requires auth)

### News
- `GET /api/news` - Get all news (supports filtering, sorting, and pagination)
- `GET /api/news/{id}` - Get specific news
- `POST /api/news` - Create new news (requires auth)
- `PUT /api/news/{id}` - Update news (requires auth)
- `DELETE /api/news/{id}` - Delete news (requires auth)

### Comrades
- `GET /api/comrades` - Search comrades (supports multiple filters)
- `GET /api/comrades/{id}` - Get specific comrade
- `POST /api/comrades` - Add new comrade
- `PUT /api/comrades/{id}` - Update comrade (requires auth)
- `DELETE /api/comrades/{id}` - Delete comrade (requires auth)

### Files
- `POST /api/files/upload` - Upload file (requires auth)
- `GET /api/files` - List files (requires auth)
- `GET /api/files/{id}` - Get file metadata
- `DELETE /api/files/{id}` - Delete file (requires auth)

## Usage Examples

### Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'
```

### Get Laws
```bash
curl -X GET http://localhost:5000/api/laws?limit=10&category=федеральный
```

### Create News (with authentication)
```bash
curl -X POST http://localhost:5000/api/news \
  -H "Authorization: Bearer <your-jwt-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": {
      "ru": "Новая важная новость",
      "uz": "Yangi muhim yangilik", 
      "en": "New Important News"
    },
    "content": {
      "ru": "Содержание новости...",
      "uz": "Yangilik mazmuni...",
      "en": "News content..."
    },
    "summary": {
      "ru": "Краткое содержание",
      "uz": "Qisqacha mazmun",
      "en": "Brief summary"
    },
    "date": "2024-01-15"
  }'
```

### Upload File
```bash
curl -X POST http://localhost:5000/api/files/upload \
  -H "Authorization: Bearer <your-jwt-token>" \
  -F "file=@document.pdf" \
  -F "type=pdf" \
  -F "category=law"
```

## Configuration

Configuration is handled in `config.py`. Key settings:

- Database URL (defaults to SQLite)
- JWT secret keys
- File upload limits and allowed extensions
- CORS settings

## Database

The application uses SQLAlchemy ORM with SQLite by default. The database is automatically initialized with sample data on first run.

## Error Handling

All API endpoints return consistent error responses:

```json
{
  "error": "Error Type",
  "message": "Detailed error description",
  "timestamp": "2024-01-15T12:34:56Z",
  "details": {
    "field": "specific field error"
  }
}
```

## Security Features

- JWT token-based authentication
- Password hashing using Werkzeug
- File type and size validation
- Input validation and sanitization
- CORS configuration

## Development

For development, set the environment variable:
```bash
export FLASK_ENV=development
```

This enables debug mode with automatic reloading.

## Production Deployment

For production deployment:

1. Use a production WSGI server (e.g., Gunicorn)
2. Use a production database (PostgreSQL, MySQL)
3. Configure proper environment variables
4. Use HTTPS
5. Set up proper CORS policies
6. Configure rate limiting
7. Set up log monitoring

## File Structure

```
├── app.py              # Main application file
├── config.py           # Configuration settings
├── requirements.txt    # Python dependencies
├── models/             # Database models
├── routes/             # API route handlers
├── utils/              # Utility functions
├── uploads/            # File upload directory
└── API_DOCS.md        # Complete API documentation
```

See `API_DOCS.md` for complete API specification with detailed examples and response formats.