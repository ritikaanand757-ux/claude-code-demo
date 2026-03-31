# Task Manager

A full-stack task manager application built with FastAPI, PostgreSQL, and vanilla JavaScript.

## Features

- Create, read, update, and delete tasks
- Mark tasks as completed
- Filter tasks (All, Active, Completed)
- Clean and responsive UI
- RESTful API with FastAPI
- PostgreSQL database with SQLAlchemy ORM
- Database migrations with Alembic
- Comprehensive test suite

## Project Structure

```
task-manager/
├── backend/               # FastAPI backend
│   ├── __init__.py
│   ├── main.py           # FastAPI application entry point
│   ├── database.py       # Database configuration
│   ├── models.py         # SQLAlchemy models
│   ├── routes.py         # API routes
│   └── schemas.py        # Pydantic schemas
├── frontend/             # Frontend files
│   ├── index.html        # Main HTML file
│   ├── style.css         # Styling
│   └── app.js           # JavaScript functionality
├── tests/                # Test files
│   ├── __init__.py
│   ├── conftest.py      # Pytest configuration
│   └── test_api.py      # API tests
├── alembic/              # Database migrations
│   ├── versions/        # Migration files
│   ├── env.py
│   └── script.py.mako
├── alembic.ini           # Alembic configuration
├── requirements.txt      # Python dependencies
├── .env.example         # Example environment variables
├── .gitignore
└── README.md
```

## Prerequisites

- Python 3.8+
- PostgreSQL 12+
- pip (Python package manager)

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd task-manager
```

### 2. Create a virtual environment

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up PostgreSQL database

```sql
CREATE DATABASE taskmanager_db;
```

### 5. Configure environment variables

Copy `.env.example` to `.env` and update the values:

```bash
cp .env.example .env
```

Edit `.env` with your database credentials:

```
DB_PASSWORD=your_password_here
```

### 6. Update database connection

Edit `backend/database.py` and update the DATABASE_URL with your password:

```python
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/taskmanager_db"
```

Also update `alembic.ini` with the same connection string:

```ini
sqlalchemy.url = postgresql://postgres:postgres@localhost:5432/taskmanager_db
```

### 7. Run database migrations

```bash
# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

## Running the Application

### Start the backend server

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

### Serve the frontend

You can use any static file server. Here are a few options:

**Option 1: Python's built-in server**
```bash
cd frontend
python -m http.server 3000
```

**Option 2: Using Node.js http-server**
```bash
npx http-server frontend -p 3000
```

**Option 3: Using VS Code Live Server extension**
- Right-click on `frontend/index.html`
- Select "Open with Live Server"

The frontend will be available at http://localhost:3000 (or the port specified)

## Running Tests

Run the test suite with pytest:

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=backend tests/

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_api.py
```

## API Endpoints

### Tasks

- `GET /api/tasks/` - Get all tasks
  - Query params: `skip` (default: 0), `limit` (default: 100)
- `GET /api/tasks/{task_id}` - Get a specific task
- `POST /api/tasks/` - Create a new task
- `PUT /api/tasks/{task_id}` - Update a task
- `DELETE /api/tasks/{task_id}` - Delete a task

### Health Check

- `GET /` - Root endpoint
- `GET /health` - Health check endpoint

## API Request Examples

### Create a task

```bash
curl -X POST "http://localhost:8000/api/tasks/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": false
  }'
```

### Get all tasks

```bash
curl "http://localhost:8000/api/tasks/"
```

### Update a task

```bash
curl -X PUT "http://localhost:8000/api/tasks/1" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries",
    "completed": true
  }'
```

### Delete a task

```bash
curl -X DELETE "http://localhost:8000/api/tasks/1"
```

## Database Migrations

Create a new migration after model changes:

```bash
alembic revision --autogenerate -m "Description of changes"
```

Apply migrations:

```bash
alembic upgrade head
```

Rollback last migration:

```bash
alembic downgrade -1
```

View migration history:

```bash
alembic history
```

## Development

### Code Style

The project follows PEP 8 style guidelines. You can use tools like `black` and `flake8`:

```bash
pip install black flake8
black backend/ tests/
flake8 backend/ tests/
```

### Database Schema

The application uses a single `tasks` table with the following structure:

- `id` (Integer, Primary Key)
- `title` (String, Required)
- `description` (String, Optional)
- `completed` (Boolean, Default: False)
- `created_at` (DateTime, Auto-generated)
- `updated_at` (DateTime, Auto-updated)

## Troubleshooting

### Database connection issues

- Ensure PostgreSQL is running
- Verify database credentials in `backend/database.py` and `alembic.ini`
- Check if the database `taskmanager_db` exists

### CORS errors

- The backend is configured to allow all origins for development
- For production, update CORS settings in `backend/main.py`

### Port already in use

- Change the port in the uvicorn command: `--port 8001`
- Update the API_BASE_URL in `frontend/app.js` accordingly

## Production Deployment

### Backend

1. Set environment variables securely (don't use .env in production)
2. Update CORS settings to allow only specific origins
3. Use a production ASGI server like Gunicorn with Uvicorn workers:

```bash
gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Frontend

1. Serve static files using Nginx or Apache
2. Update API_BASE_URL in `app.js` to point to your production API

### Database

1. Use connection pooling
2. Set up regular backups
3. Use environment variables for credentials
4. Enable SSL for database connections

## License

MIT License

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Support

For issues and questions, please open an issue on the GitHub repository.
