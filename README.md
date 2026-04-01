# Task Manager API

A modern, full-stack task management application built with FastAPI, PostgreSQL, and vanilla JavaScript. Features a RESTful API with comprehensive task management capabilities including priorities, tags, search, and statistics.

## Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Authentication](#authentication)
- [API Documentation](#api-documentation)
- [Environment Variables](#environment-variables)
- [Database Migrations](#database-migrations)
- [Running Tests](#running-tests)
- [Development](#development)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)

## Features

### Core Features
- **CRUD Operations**: Create, read, update, and delete tasks
- **Task Completion**: Mark tasks as completed or pending
- **Priority Management**: Assign priority levels (low, medium, high) to tasks
- **Tagging System**: Add comma-separated tags for better organization
- **Due Dates**: Set and track task due dates

### Advanced Features
- **Search**: Full-text search across task titles, descriptions, and tags
- **Statistics**: Get comprehensive task statistics including completion rates and priority distribution
- **Filtering**: Filter tasks by priority, completion status, or pagination
- **Bulk Operations**: Delete multiple tasks at once
- **Pagination**: Efficient data loading with customizable page sizes

### Technical Features
- RESTful API with automatic OpenAPI documentation
- PostgreSQL database with SQLAlchemy ORM
- Database migrations with Alembic
- Comprehensive test suite with pytest
- CORS-enabled for frontend integration
- Responsive web interface

## Technology Stack

### Backend
- **FastAPI** (0.104.1) - Modern, fast web framework for building APIs
- **SQLAlchemy** (2.0.23) - SQL toolkit and ORM
- **PostgreSQL** (via psycopg2-binary) - Robust relational database
- **Alembic** (1.12.1) - Database migration tool
- **Pydantic** (2.5.0) - Data validation using Python type hints
- **Uvicorn** (0.24.0) - Lightning-fast ASGI server

### Frontend
- **HTML5** - Semantic markup
- **CSS3** - Modern styling with flexbox/grid
- **Vanilla JavaScript** - No framework dependencies

### Testing
- **pytest** (7.4.3) - Testing framework
- **pytest-cov** (4.1.0) - Coverage reporting
- **httpx** (0.25.2) - Async HTTP client for testing

## Project Structure

```
claude-code-demo/
├── backend/                    # Backend application
│   ├── __init__.py            # Package initializer
│   ├── main.py                # FastAPI application entry point
│   ├── database.py            # Database configuration and session management
│   ├── models.py              # SQLAlchemy ORM models
│   ├── schemas.py             # Pydantic request/response schemas
│   ├── routes.py              # API route handlers
│   └── crud.py                # Database CRUD operations
│
├── frontend/                   # Frontend application
│   ├── index.html             # Main HTML page
│   ├── style.css              # Styling and layout
│   └── app.js                 # JavaScript functionality
│
├── tests/                      # Test suite
│   ├── __init__.py            # Test package initializer
│   ├── conftest.py            # Pytest configuration and fixtures
│   ├── test_api.py            # Basic API tests
│   ├── test_enhanced_api.py   # Enhanced feature tests
│   └── test_refactored_api.py # Refactored code tests
│
├── alembic/                    # Database migrations
│   ├── versions/              # Migration version files
│   │   ├── 001_initial_migration.py
│   │   └── 002_add_priority_tags_duedate.py
│   ├── env.py                 # Alembic environment configuration
│   ├── script.py.mako         # Migration script template
│   └── README                 # Alembic documentation
│
├── alembic.ini                 # Alembic configuration file
├── requirements.txt            # Python dependencies
├── run_backend.bat            # Windows script to start backend
├── run_backend.sh             # Unix script to start backend
├── run_frontend.bat           # Windows script to start frontend
├── run_frontend.sh            # Unix script to start frontend
├── run_tests.py               # Test runner script
└── README.md                  # This file
```

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8+** - [Download Python](https://www.python.org/downloads/)
- **PostgreSQL 12+** - [Download PostgreSQL](https://www.postgresql.org/download/)
- **pip** - Python package manager (usually comes with Python)
- **Git** - Version control system

### Optional
- **virtualenv** or **venv** - For creating isolated Python environments
- **PostgreSQL GUI tool** - pgAdmin, DBeaver, or similar for database management

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd claude-code-demo
```

### 2. Create a Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- FastAPI and Uvicorn for the web server
- SQLAlchemy and psycopg2 for database operations
- Alembic for migrations
- Pydantic for data validation
- pytest and testing utilities

### 4. Set Up PostgreSQL Database

Start PostgreSQL and create the database:

```sql
-- Connect to PostgreSQL (as postgres user or admin)
psql -U postgres

-- Create the database
CREATE DATABASE taskmanager_db;

-- Create a user (optional but recommended)
CREATE USER taskmanager_user WITH PASSWORD 'your_secure_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE taskmanager_db TO taskmanager_user;

-- Exit psql
\q
```

### 5. Configure Database Connection

Edit `backend/database.py` and update the `DATABASE_URL`:

```python
DATABASE_URL = "postgresql://postgres:your_password@localhost:5432/taskmanager_db"
```

Also update `alembic.ini` (line with `sqlalchemy.url`):

```ini
sqlalchemy.url = postgresql://postgres:your_password@localhost:5432/taskmanager_db
```

### 6. Run Database Migrations

```bash
# Apply all migrations to create tables
alembic upgrade head
```

This will create the `tasks` table with all necessary columns.

## Configuration

### Database Configuration

The database connection is configured in `backend/database.py`:

```python
DATABASE_URL = "postgresql://username:password@host:port/database_name"
```

**Format breakdown:**
- `username` - PostgreSQL username (default: postgres)
- `password` - Your PostgreSQL password
- `host` - Database host (default: localhost)
- `port` - PostgreSQL port (default: 5432)
- `database_name` - Database name (taskmanager_db)

### CORS Configuration

CORS is configured in `backend/main.py`. For development, all origins are allowed:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change in production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Production:** Replace `["*"]` with specific origins like `["https://yourdomain.com"]`

## Running the Application

### Option 1: Using Shell Scripts (Recommended)

**Windows:**
```bash
# Terminal 1 - Start backend
run_backend.bat

# Terminal 2 - Start frontend
run_frontend.bat
```

**macOS/Linux:**
```bash
# Terminal 1 - Start backend
chmod +x run_backend.sh
./run_backend.sh

# Terminal 2 - Start frontend
chmod +x run_frontend.sh
./run_frontend.sh
```

### Option 2: Manual Commands

**Start Backend:**
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

**Start Frontend:**
```bash
cd frontend
python -m http.server 3000
```

### Accessing the Application

Once both servers are running:

- **Frontend Application**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation (Swagger UI)**: http://localhost:8000/docs
- **API Documentation (ReDoc)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## API Documentation

### Base URL

```
http://localhost:8000/api
```

### Endpoints Overview

#### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/register` | Register new user | No |
| POST | `/api/auth/login` | Login and get JWT token | No |
| GET | `/api/auth/me` | Get current user info | Yes |

#### Task Endpoints (Authentication Required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tasks/` | Get all tasks (with filters) |
| GET | `/api/tasks/{task_id}` | Get a specific task |
| POST | `/api/tasks/` | Create a new task |
| PUT | `/api/tasks/{task_id}` | Update a task |
| DELETE | `/api/tasks/{task_id}` | Delete a task |
| GET | `/api/tasks/search` | Search tasks |
| GET | `/api/tasks/stats` | Get task statistics |
| POST | `/api/tasks/bulk/delete` | Bulk delete tasks |

### Detailed Endpoint Documentation

#### 1. Get All Tasks

```http
GET /api/tasks/
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| skip | integer | 0 | Number of records to skip (offset) |
| limit | integer | 20 | Maximum number of records (max: 100) |
| page | integer | null | Page number (overrides skip) |
| priority | string | null | Filter by priority (low/medium/high) |
| completed | boolean | null | Filter by completion status |

**Example Requests:**

```bash
# Get first 20 tasks
curl "http://localhost:8000/api/tasks/"

# Get next 20 tasks (pagination)
curl "http://localhost:8000/api/tasks/?skip=20&limit=20"

# Get page 2 (page-based pagination)
curl "http://localhost:8000/api/tasks/?page=2&limit=20"

# Filter by priority
curl "http://localhost:8000/api/tasks/?priority=high"

# Filter by completion status
curl "http://localhost:8000/api/tasks/?completed=false"

# Combine filters
curl "http://localhost:8000/api/tasks/?priority=high&completed=false&limit=10"
```

**Response Example:**

```json
[
  {
    "id": 1,
    "title": "Complete project documentation",
    "description": "Write comprehensive API documentation",
    "completed": false,
    "priority": "high",
    "tags": "documentation,urgent",
    "due_date": "2024-12-31T23:59:59Z",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
]
```

#### 2. Get Single Task

```http
GET /api/tasks/{task_id}
```

**Example:**

```bash
curl "http://localhost:8000/api/tasks/1"
```

**Response:** Same as single task object above

**Error Response (404):**

```json
{
  "detail": "Task with id 1 not found"
}
```

#### 3. Create Task

```http
POST /api/tasks/
```

**Request Body:**

```json
{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread, and vegetables",
  "priority": "medium",
  "tags": "shopping,personal",
  "due_date": "2024-01-20T18:00:00Z",
  "completed": false
}
```

**Field Descriptions:**

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| title | string | Yes | - | Task title |
| description | string | No | null | Detailed description |
| priority | string | No | "medium" | Priority level: low, medium, or high |
| tags | string | No | null | Comma-separated tags |
| due_date | datetime | No | null | Due date in ISO 8601 format |
| completed | boolean | No | false | Completion status |

**Example:**

```bash
curl -X POST "http://localhost:8000/api/tasks/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "priority": "medium",
    "tags": "shopping",
    "completed": false
  }'
```

**Response (201 Created):**

```json
{
  "id": 1,
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "priority": "medium",
  "tags": "shopping",
  "due_date": null,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

#### 4. Update Task

```http
PUT /api/tasks/{task_id}
```

**Request Body:** (All fields optional)

```json
{
  "title": "Buy groceries - Updated",
  "description": "Milk, eggs, bread, and cheese",
  "completed": true,
  "priority": "high",
  "tags": "shopping,urgent"
}
```

**Example:**

```bash
curl -X PUT "http://localhost:8000/api/tasks/1" \
  -H "Content-Type: application/json" \
  -d '{
    "completed": true
  }'
```

**Response:** Updated task object

#### 5. Delete Task

```http
DELETE /api/tasks/{task_id}
```

**Example:**

```bash
curl -X DELETE "http://localhost:8000/api/tasks/1"
```

**Response (204 No Content):** Empty response

**Error Response (404):**

```json
{
  "detail": "Task with id 1 not found"
}
```

#### 6. Search Tasks

```http
GET /api/tasks/search
```

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| q | string | Yes | Search query (min 1 character) |
| limit | integer | No | Max results (default: 50, max: 100) |

**Example:**

```bash
# Search for "grocery" in titles, descriptions, and tags
curl "http://localhost:8000/api/tasks/search?q=grocery"

# Limit results
curl "http://localhost:8000/api/tasks/search?q=urgent&limit=10"
```

**Response:** Array of matching tasks

#### 7. Get Statistics

```http
GET /api/tasks/stats
```

**Example:**

```bash
curl "http://localhost:8000/api/tasks/stats"
```

**Response:**

```json
{
  "total": 25,
  "completed": 10,
  "pending": 15,
  "by_priority": {
    "high": 5,
    "medium": 12,
    "low": 8
  }
}
```

#### 8. Bulk Delete Tasks

```http
POST /api/tasks/bulk/delete
```

**Request Body:**

```json
{
  "task_ids": [1, 2, 3, 5, 8]
}
```

**Example:**

```bash
curl -X POST "http://localhost:8000/api/tasks/bulk/delete" \
  -H "Content-Type: application/json" \
  -d '{
    "task_ids": [1, 2, 3]
  }'
```

**Response:**

```json
{
  "deleted_count": 3,
  "requested_count": 3
}
```

## Authentication

The Task Manager API includes JWT-based authentication to secure user data and ensure that users can only access their own tasks.

### Authentication Overview

- **Token Type**: JSON Web Tokens (JWT)
- **Token Expiration**: 30 minutes
- **Password Security**: bcrypt hashing with salt rounds
- **Token Format**: Bearer token in Authorization header

### Quick Start

**1. Register a new user:**
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "email": "john@example.com",
    "password": "securepass123"
  }'
```

**Response:**
```json
{
  "id": 1,
  "username": "john",
  "email": "john@example.com",
  "is_active": true,
  "created_at": "2026-04-01T10:00:00Z"
}
```

**2. Login to get access token:**
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "password": "securepass123"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**3. Use the token in API requests:**
```bash
curl -X GET "http://localhost:8000/api/tasks/" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**4. Get current user information:**
```bash
curl -X GET "http://localhost:8000/api/auth/me" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Security Features

- **Password Hashing**: All passwords are hashed using bcrypt before storage
- **Unique Constraints**: Email and username must be unique
- **Token Expiration**: Tokens automatically expire after 30 minutes
- **Validation**: Email format and password strength validation
- **Protected Routes**: All task endpoints require authentication

### Environment Variables

The authentication system requires a `SECRET_KEY` environment variable for JWT token signing. See the [Environment Variables](#environment-variables) section below for setup instructions.

For detailed authentication documentation, see [docs/AUTHENTICATION.md](docs/AUTHENTICATION.md) and the [API Authentication](#authentication) section in [docs/API.md](docs/API.md).

## Environment Variables

The application uses the following environment variables:

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| DATABASE_URL | PostgreSQL connection string | See config | Yes |
| SECRET_KEY | JWT secret key for token signing | None | **Yes** |
| API_HOST | API server host | 0.0.0.0 | No |
| API_PORT | API server port | 8000 | No |
| ACCESS_TOKEN_EXPIRE_MINUTES | Token expiration time in minutes | 30 | No |

### Creating .env File

Create a `.env` file in the project root:

```bash
# Database Configuration
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/taskmanager_db

# Authentication (REQUIRED)
SECRET_KEY=your-super-secret-key-min-32-characters-long-random-string
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Server Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Environment
ENV=development
```

**Note:** The `.env` file should be added to `.gitignore` to avoid committing sensitive credentials.

### Generating a Secure Secret Key

Generate a secure random secret key for JWT token signing:

```bash
# Using Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Using OpenSSL
openssl rand -hex 32
```

### Loading Environment Variables

To use the `.env` file, update `backend/database.py`:

```python
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/taskmanager_db")
SECRET_KEY = os.getenv("SECRET_KEY")

# Validate required environment variables
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable must be set")
```

## Database Migrations

This project uses Alembic for database schema management.

### Common Migration Commands

**View current migration status:**
```bash
alembic current
```

**View migration history:**
```bash
alembic history --verbose
```

**Apply all pending migrations:**
```bash
alembic upgrade head
```

**Rollback one migration:**
```bash
alembic downgrade -1
```

**Rollback to specific version:**
```bash
alembic downgrade <revision_id>
```

### Creating New Migrations

After modifying models in `backend/models.py`:

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Add new field to tasks"

# Review the generated migration file in alembic/versions/

# Apply the migration
alembic upgrade head
```

### Migration Files

Existing migrations:
- `001_initial_migration.py` - Creates tasks table
- `002_add_priority_tags_duedate.py` - Adds priority, tags, and due_date fields

## Running Tests

The project includes a comprehensive test suite using pytest.

### Running All Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=backend tests/

# Run with coverage and HTML report
pytest --cov=backend --cov-report=html tests/
```

### Running Specific Tests

```bash
# Run specific test file
pytest tests/test_api.py

# Run specific test class
pytest tests/test_api.py::TestTaskAPI

# Run specific test function
pytest tests/test_api.py::test_create_task

# Run tests matching pattern
pytest -k "search"
```

### Using the Test Runner Script

```bash
python run_tests.py
```

### Test Coverage

To generate and view coverage report:

```bash
# Generate coverage report
pytest --cov=backend --cov-report=html tests/

# Open coverage report in browser
# Windows
start htmlcov/index.html

# macOS
open htmlcov/index.html

# Linux
xdg-open htmlcov/index.html
```

### Test Structure

- `tests/conftest.py` - Pytest fixtures and configuration
- `tests/test_api.py` - Basic API endpoint tests
- `tests/test_enhanced_api.py` - Tests for search, stats, filtering
- `tests/test_refactored_api.py` - Tests after code refactoring

## Development

### Code Style

The project follows PEP 8 style guidelines for Python code.

**Install development tools:**

```bash
pip install black flake8 isort mypy
```

**Format code:**

```bash
# Format with black
black backend/ tests/

# Sort imports
isort backend/ tests/

# Check style
flake8 backend/ tests/

# Type checking
mypy backend/
```

### Database Schema

**Tasks Table:**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Auto-incrementing ID |
| title | VARCHAR | NOT NULL | Task title |
| description | VARCHAR | NULL | Task description |
| completed | BOOLEAN | DEFAULT FALSE | Completion status |
| priority | VARCHAR | DEFAULT 'medium' | Priority level |
| tags | VARCHAR | NULL | Comma-separated tags |
| due_date | TIMESTAMP | NULL | Due date with timezone |
| created_at | TIMESTAMP | DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP | ON UPDATE NOW() | Last update timestamp |

### API Response Codes

| Code | Status | Description |
|------|--------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 204 | No Content | Resource deleted successfully |
| 400 | Bad Request | Invalid request data |
| 404 | Not Found | Resource not found |
| 422 | Unprocessable Entity | Validation error |
| 500 | Internal Server Error | Server error |

### Adding New Features

1. **Update models** in `backend/models.py`
2. **Create migration**: `alembic revision --autogenerate -m "Description"`
3. **Update schemas** in `backend/schemas.py`
4. **Add CRUD operations** in `backend/crud.py`
5. **Add routes** in `backend/routes.py`
6. **Write tests** in `tests/`
7. **Run tests**: `pytest`
8. **Apply migration**: `alembic upgrade head`

## Deployment

### Production Checklist

- [ ] Update CORS origins to specific domains
- [ ] Use environment variables for all sensitive data
- [ ] Enable database connection pooling
- [ ] Set up database backups
- [ ] Use HTTPS/TLS for database connections
- [ ] Configure reverse proxy (Nginx/Apache)
- [ ] Set up monitoring and logging
- [ ] Use production ASGI server
- [ ] Optimize database indexes
- [ ] Implement rate limiting

### Backend Deployment

**Using Gunicorn with Uvicorn workers:**

```bash
pip install gunicorn

gunicorn backend.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

**Using Docker:**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend Deployment

Serve static files with Nginx:

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    root /path/to/frontend;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Database Deployment

**Recommended settings for production:**

```python
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False
)
```

## Troubleshooting

### Database Connection Issues

**Problem:** `could not connect to server: Connection refused`

**Solutions:**
- Ensure PostgreSQL is running: `sudo service postgresql status`
- Check PostgreSQL port: Default is 5432
- Verify credentials in DATABASE_URL
- Check PostgreSQL logs for errors

### Migration Errors

**Problem:** `Target database is not up to date`

**Solution:**
```bash
alembic upgrade head
```

**Problem:** `Can't locate revision identified by 'xxxxx'`

**Solution:**
```bash
# Reset to base and reapply
alembic downgrade base
alembic upgrade head
```

### CORS Errors

**Problem:** `CORS policy: No 'Access-Control-Allow-Origin' header`

**Solution:** Update `backend/main.py`:
```python
allow_origins=["http://localhost:3000", "https://yourdomain.com"]
```

### Port Already in Use

**Problem:** `Address already in use`

**Solutions:**

**Windows:**
```bash
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**macOS/Linux:**
```bash
lsof -i :8000
kill -9 <PID>
```

Or change port:
```bash
uvicorn backend.main:app --port 8001
```

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'backend'`

**Solution:** Run from project root:
```bash
# Ensure you're in the project directory
cd claude-code-demo

# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Run with proper Python path
PYTHONPATH=. uvicorn backend.main:app --reload
```

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Write tests for new functionality
4. Ensure all tests pass: `pytest`
5. Follow code style guidelines: `black` and `flake8`
6. Commit your changes: `git commit -m "Add your feature"`
7. Push to the branch: `git push origin feature/your-feature`
8. Create a Pull Request

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Support

For questions, issues, or suggestions:

- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Documentation**: http://localhost:8000/docs
- **Email**: support@example.com

## Acknowledgments

- FastAPI for the excellent web framework
- SQLAlchemy for robust ORM capabilities
- The Python community for amazing tools and libraries

---

**Version:** 1.0.0
**Last Updated:** 2024-01-15
**Author:** Your Name
**Repository:** https://github.com/your-username/claude-code-demo
