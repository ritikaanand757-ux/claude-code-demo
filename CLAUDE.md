# Claude Code Rules for Task Manager API

This document defines the coding standards, best practices, and rules that Claude Code must follow when working on this Task Manager API project.

---

## 1. Project Overview

### What This Project Is

**Task Manager API** is a RESTful API built with FastAPI for managing tasks with advanced features including priorities, tags, due dates, search, and statistics.

### Tech Stack

| Technology | Purpose | Version |
|------------|---------|---------|
| **FastAPI** | Web framework for building APIs | 0.104.1 |
| **PostgreSQL** | Relational database | 12+ |
| **SQLAlchemy** | ORM (Object-Relational Mapping) | 2.0.23 |
| **Alembic** | Database migration tool | 1.12.1 |
| **Pydantic** | Data validation and serialization | 2.5.0 |
| **pytest** | Testing framework | 7.4.3 |
| **Uvicorn** | ASGI server | 0.24.0 |

### Project Structure

```
claude-code-demo/
├── backend/                # Backend application code
│   ├── __init__.py        # Package initializer
│   ├── main.py            # FastAPI app entry point, CORS, middleware
│   ├── database.py        # Database connection, engine, session management
│   ├── models.py          # SQLAlchemy ORM models (database schema)
│   ├── schemas.py         # Pydantic schemas (API request/response)
│   ├── routes.py          # API route handlers (HTTP endpoints)
│   └── crud.py            # Database CRUD operations (business logic)
│
├── frontend/              # Frontend application (HTML/CSS/JS)
│   ├── index.html
│   ├── style.css
│   └── app.js
│
├── tests/                 # Test suite
│   ├── conftest.py       # pytest fixtures and configuration
│   ├── test_api.py       # Basic API tests
│   ├── test_enhanced_api.py    # Enhanced feature tests
│   └── test_refactored_api.py  # Refactored code tests
│
├── alembic/              # Database migrations
│   ├── versions/         # Migration files (never delete these!)
│   ├── env.py           # Alembic environment
│   └── script.py.mako   # Migration template
│
├── docs/                 # Documentation
│   └── API.md           # API documentation
│
├── alembic.ini           # Alembic configuration
├── requirements.txt      # Python dependencies
├── README.md            # Project documentation
├── CLAUDE.md            # This file (Claude Code rules)
└── .env                 # Environment variables (NEVER COMMIT!)
```

### Architecture Overview

**Layered Architecture:**
1. **API Layer** (`routes.py`) - HTTP request handling, validation
2. **Business Logic Layer** (`crud.py`) - Database operations, business rules
3. **Data Layer** (`models.py`) - Database schema, ORM models
4. **Schema Layer** (`schemas.py`) - Request/response validation, serialization

**Request Flow:**
```
HTTP Request → routes.py → schemas.py (validation) → crud.py → models.py → Database
                    ↓
            Response (JSON)
```

---

## 2. Coding Standards

### Naming Conventions

#### Variables and Functions: `snake_case`
```python
# ✅ CORRECT
def get_task_by_id(task_id: int):
    user_email = "user@example.com"
    total_count = 100

# ❌ WRONG
def GetTaskById(taskId: int):
    userEmail = "user@example.com"
    TotalCount = 100
```

#### Classes: `PascalCase`
```python
# ✅ CORRECT
class TaskCreate(BaseModel):
    pass

class UserResponse(BaseModel):
    pass

# ❌ WRONG
class task_create(BaseModel):
    pass
```

#### Constants: `UPPER_SNAKE_CASE`
```python
# ✅ CORRECT
DATABASE_URL = "postgresql://..."
MAX_PAGE_SIZE = 100

# ❌ WRONG
database_url = "postgresql://..."
maxPageSize = 100
```

### Always Use Pydantic Schemas for API Input/Output

```python
# ✅ CORRECT - Use Pydantic schemas
from backend.schemas import TaskCreate, TaskResponse

@router.post("/tasks/", response_model=TaskResponse)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    return crud.create_task(db=db, task=task)

# ❌ WRONG - Never expose raw SQLAlchemy models
@router.post("/tasks/")
def create_task(task: Task, db: Session = Depends(get_db)):
    db.add(task)
    db.commit()
    return task  # Returns SQLAlchemy model directly
```

### Never Expose Raw SQLAlchemy Models in API Responses

```python
# ✅ CORRECT - Return Pydantic schema
@router.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = crud.get_task_by_id(db=db, task_id=task_id)
    return task  # SQLAlchemy model auto-converted to TaskResponse

# ❌ WRONG - Exposing internal model structure
@router.get("/tasks/{task_id}")
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    return task  # Returns raw SQLAlchemy model
```

### All Routes Must Return Consistent JSON Structure

```python
# ✅ CORRECT - Consistent structure
{
    "id": 1,
    "title": "Task",
    "completed": false,
    "created_at": "2024-01-15T10:00:00Z"
}

# ❌ WRONG - Inconsistent structure
{
    "taskId": 1,
    "taskTitle": "Task",
    "isCompleted": false,
    "createdAt": "2024-01-15T10:00:00Z"
}
```

### Use Async Functions for All Database Operations

**IMPORTANT:** Currently this project uses synchronous database operations. When adding new features:

```python
# ✅ CURRENT PATTERN - Synchronous (keep for consistency)
def get_tasks(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Task).offset(skip).limit(limit).all()

# 🔄 FUTURE PATTERN - Async (when migrating)
async def get_tasks(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(Task).offset(skip).limit(limit))
    return result.scalars().all()
```

**Rule:** Match the existing pattern in the codebase. Don't mix async and sync without a complete migration.

---

## 3. Database Rules

### Always Create an Alembic Migration for Every Schema Change

```bash
# ✅ CORRECT - Create migration for model changes
# 1. Modify backend/models.py
# 2. Create migration
alembic revision --autogenerate -m "add status field to tasks"
# 3. Review generated migration in alembic/versions/
# 4. Apply migration
alembic upgrade head

# ❌ WRONG - Modifying database schema directly
psql -U postgres -d taskmanager_db -c "ALTER TABLE tasks ADD COLUMN status VARCHAR(50);"
```

### Never Use Raw SQL — Always Use SQLAlchemy ORM

```python
# ✅ CORRECT - Use SQLAlchemy ORM
def get_completed_tasks(db: Session):
    return db.query(Task).filter(Task.completed == True).all()

def update_task_priority(db: Session, task_id: int, priority: str):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        task.priority = priority
        db.commit()
        db.refresh(task)
    return task

# ❌ WRONG - Using raw SQL
def get_completed_tasks(db: Session):
    return db.execute("SELECT * FROM tasks WHERE completed = true").fetchall()

def update_task_priority(db: Session, task_id: int, priority: str):
    db.execute(f"UPDATE tasks SET priority = '{priority}' WHERE id = {task_id}")
    db.commit()
```

**Exception:** Raw SQL is acceptable only for:
- Complex aggregations that SQLAlchemy can't express efficiently
- Database-specific features (e.g., PostgreSQL full-text search)
- Must be documented with a comment explaining why

### Always Add `created_at` and `updated_at` to New Models

```python
# ✅ CORRECT - Include timestamp fields
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# ❌ WRONG - Missing timestamp fields
class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
```

### Never Delete Migrations — Only Add New Ones

```bash
# ✅ CORRECT - Create new migration to reverse changes
alembic revision --autogenerate -m "remove status field from tasks"

# ❌ WRONG - Deleting migration files
rm alembic/versions/abc123_add_status_field.py

# ❌ WRONG - Modifying existing migration files
# Never edit files in alembic/versions/ after they've been applied
```

**Migration Best Practices:**
- Keep migrations small and focused
- Test migrations on development database first
- Always review auto-generated migrations before applying
- Add data migrations separately if needed
- Document complex migrations with comments

---

## 4. API Rules

### Follow REST Conventions Strictly

| HTTP Method | Endpoint | Purpose | Success Status |
|-------------|----------|---------|----------------|
| GET | `/api/tasks/` | List all tasks | 200 OK |
| GET | `/api/tasks/{id}` | Get single task | 200 OK |
| POST | `/api/tasks/` | Create new task | 201 Created |
| PUT | `/api/tasks/{id}` | Update entire task | 200 OK |
| PATCH | `/api/tasks/{id}` | Update partial task | 200 OK |
| DELETE | `/api/tasks/{id}` | Delete task | 204 No Content |

```python
# ✅ CORRECT - RESTful endpoint
@router.post("/tasks/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    return crud.create_task(db=db, task=task)

# ❌ WRONG - Non-RESTful endpoint
@router.get("/create_task/")
def create_task_get(title: str, db: Session = Depends(get_db)):
    # Don't use GET for creating resources
    pass
```

### Always Validate Input with Pydantic

```python
# ✅ CORRECT - Pydantic validation
from pydantic import BaseModel, Field, validator

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    priority: str = Field(default="medium", pattern="^(low|medium|high)$")

    @validator('title')
    def title_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Title cannot be empty or whitespace')
        return v.strip()

# ❌ WRONG - Manual validation in route handler
@router.post("/tasks/")
def create_task(title: str, priority: str):
    if not title or len(title) > 500:
        raise HTTPException(status_code=400, detail="Invalid title")
    if priority not in ["low", "medium", "high"]:
        raise HTTPException(status_code=400, detail="Invalid priority")
```

### Return Proper HTTP Status Codes

```python
# ✅ CORRECT - Proper status codes
@router.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = crud.get_task_by_id(db=db, task_id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,  # 404 for not found
            detail=f"Task with id {task_id} not found"
        )
    return task  # 200 OK

@router.post("/tasks/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    return crud.create_task(db=db, task=task)  # 201 Created

@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    success = crud.delete_task(db=db, task_id=task_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return None  # 204 No Content

# ❌ WRONG - Always returning 200
@router.post("/tasks/")
def create_task(task: TaskCreate):
    # Should return 201, not 200
    return {"status": "ok"}
```

**Status Code Reference:**
- `200 OK` - GET success, PUT success
- `201 Created` - POST success (resource created)
- `204 No Content` - DELETE success
- `400 Bad Request` - Invalid request format
- `404 Not Found` - Resource doesn't exist
- `422 Unprocessable Entity` - Validation error (Pydantic)
- `500 Internal Server Error` - Server error

### Always Include Error Messages in Responses

```python
# ✅ CORRECT - Descriptive error messages
@router.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = crud.get_task_by_id(db=db, task_id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )
    return task

# ❌ WRONG - Generic or missing error messages
@router.get("/tasks/{task_id}")
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = crud.get_task_by_id(db=db, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404)  # No detail message
    return task
```

---

## 5. Testing Rules

### Every New Endpoint Must Have a Test

```python
# ✅ CORRECT - Test for new endpoint
class TestTaskAPI:
    def test_create_task(self, client):
        """Test creating a new task"""
        task_data = {"title": "Test Task", "priority": "high"}
        response = client.post("/api/tasks/", json=task_data)
        assert response.status_code == 201
        assert response.json()["title"] == "Test Task"

    def test_get_task(self, client):
        """Test getting a task by ID"""
        # First create a task
        create_response = client.post("/api/tasks/", json={"title": "Test"})
        task_id = create_response.json()["id"]

        # Then get it
        response = client.get(f"/api/tasks/{task_id}")
        assert response.status_code == 200
        assert response.json()["id"] == task_id

# ❌ WRONG - Endpoint without test
# If you add a new endpoint, you MUST add a test
```

### Tests Must Cover Success Case AND Error Case

```python
# ✅ CORRECT - Both success and error cases
class TestTaskAPI:
    def test_get_task_success(self, client):
        """Test getting a task that exists"""
        # Create task
        create_response = client.post("/api/tasks/", json={"title": "Test"})
        task_id = create_response.json()["id"]

        # Get task (success case)
        response = client.get(f"/api/tasks/{task_id}")
        assert response.status_code == 200
        assert response.json()["id"] == task_id

    def test_get_task_not_found(self, client):
        """Test getting a task that doesn't exist"""
        # Try to get non-existent task (error case)
        response = client.get("/api/tasks/9999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

# ❌ WRONG - Only testing success case
class TestTaskAPI:
    def test_get_task(self, client):
        """Test getting a task"""
        create_response = client.post("/api/tasks/", json={"title": "Test"})
        task_id = create_response.json()["id"]
        response = client.get(f"/api/tasks/{task_id}")
        assert response.status_code == 200
        # Missing: What happens if task doesn't exist?
```

**Test Coverage Requirements:**
- Success case (happy path)
- Not found case (404)
- Validation error case (422)
- Edge cases (empty input, large input, etc.)

### Use pytest Fixtures for Database Setup

```python
# ✅ CORRECT - Use fixtures from conftest.py
def test_create_task(client):
    """Test uses client fixture which has clean database"""
    response = client.post("/api/tasks/", json={"title": "Test"})
    assert response.status_code == 201

def test_get_tasks(client):
    """Each test gets a fresh database via fixtures"""
    # Create tasks
    client.post("/api/tasks/", json={"title": "Task 1"})
    client.post("/api/tasks/", json={"title": "Task 2"})

    # Get tasks
    response = client.get("/api/tasks/")
    assert len(response.json()) == 2

# ❌ WRONG - Manual database setup
def test_create_task():
    engine = create_engine("sqlite:///test.db")
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    # Don't manually create database connections in tests
```

### Never Test Against Production Database

```python
# ✅ CORRECT - Use test database (SQLite in-memory or separate test DB)
# In conftest.py:
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"  # Test database

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# ❌ WRONG - Using production database URL
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:password@localhost:5432/taskmanager_db"
```

**Test Database Best Practices:**
- Use SQLite for tests (faster, isolated)
- Each test gets a fresh database (via fixtures)
- Clean up after tests (fixtures handle this)
- Never modify production data in tests

---

## 6. Security Rules

### Never Log Passwords or Tokens

```python
# ✅ CORRECT - Don't log sensitive data
import logging

logger = logging.getLogger(__name__)

def create_user(username: str, password: str):
    logger.info(f"Creating user: {username}")  # OK to log username
    # Process password...

def authenticate(token: str):
    logger.info("User authentication attempt")  # Don't log token
    # Verify token...

# ❌ WRONG - Logging sensitive data
def create_user(username: str, password: str):
    logger.info(f"Creating user: {username} with password: {password}")  # NEVER!

def authenticate(token: str):
    logger.debug(f"Authenticating with token: {token}")  # NEVER!
```

**Never Log:**
- Passwords (plain text or hashed)
- API tokens
- JWT tokens
- Session IDs
- Credit card numbers
- Personal identification numbers

### Always Validate and Sanitize User Input

```python
# ✅ CORRECT - Pydantic validation and sanitization
from pydantic import BaseModel, Field, validator

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=2000)

    @validator('title', 'description')
    def sanitize_text(cls, v):
        if v:
            # Remove potentially dangerous characters
            v = v.strip()
            # Additional sanitization if needed
        return v

# ❌ WRONG - No validation or sanitization
@router.post("/tasks/")
def create_task(title: str, description: str):
    # Directly using user input without validation
    task = Task(title=title, description=description)
    db.add(task)
    db.commit()
```

### Never Expose Internal Error Details to API Responses

```python
# ✅ CORRECT - Generic error message for client
@router.get("/tasks/{task_id}")
def get_task(task_id: int, db: Session = Depends(get_db)):
    try:
        task = crud.get_task_by_id(db=db, task_id=task_id)
        if not task:
            raise HTTPException(
                status_code=404,
                detail="Task not found"  # Generic message
            )
        return task
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")  # Log full error
        raise HTTPException(
            status_code=500,
            detail="Internal server error"  # Don't expose database details
        )

# ❌ WRONG - Exposing internal errors
@router.get("/tasks/{task_id}")
def get_task(task_id: int, db: Session = Depends(get_db)):
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        return task
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)  # NEVER expose internal error messages
        )
```

### Always Use Environment Variables for Credentials

```python
# ✅ CORRECT - Use environment variables
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/taskmanager_db"
)

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable must be set")

# ❌ WRONG - Hardcoded credentials
DATABASE_URL = "postgresql://postgres:my_password_123@localhost:5432/taskmanager_db"
SECRET_KEY = "super-secret-key-12345"
API_TOKEN = "sk-1234567890abcdef"
```

**Environment Variables Best Practices:**
- Store in `.env` file (never commit!)
- Add `.env` to `.gitignore`
- Provide `.env.example` with dummy values
- Validate required variables at startup
- Use different values for dev/test/prod

---

## 7. Git Rules

### Meaningful Commit Messages: `type(scope): description`

**Format:**
```
type(scope): short description (50 chars max)

Longer explanation if needed (wrap at 72 chars)
- Bullet points for multiple changes
- Each point starts with a dash
- Keep it clear and concise

Closes #123
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring (no functional change)
- `test`: Adding or updating tests
- `chore`: Maintenance tasks, dependency updates

**Examples:**

```bash
# ✅ CORRECT - Clear, descriptive commit messages
git commit -m "feat(api): add task filtering by due date

- Add due_date_from and due_date_to query parameters
- Update TaskResponse schema to include due_date
- Add tests for date range filtering
- Update API documentation

Closes #42"

git commit -m "fix(database): prevent duplicate task creation

- Add unique constraint on task title per user
- Update migration to add constraint
- Add test for duplicate prevention"

git commit -m "docs: update API documentation with new endpoints"

git commit -m "test(api): add tests for bulk delete endpoint"

# ❌ WRONG - Vague or unclear commit messages
git commit -m "fix bug"
git commit -m "updates"
git commit -m "changes to code"
git commit -m "WIP"  # Never commit work in progress
```

### Never Commit .env Files

```bash
# ✅ CORRECT - .env is in .gitignore
# .gitignore file:
.env
.env.local
.env.*.local
*.env

# Commit .env.example instead:
# .env.example:
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
SECRET_KEY=your-secret-key-here

# ❌ WRONG - Committing environment files
git add .env
git commit -m "add environment variables"  # NEVER DO THIS!
```

**If you accidentally commit `.env`:**
1. Remove it from git: `git rm --cached .env`
2. Add to `.gitignore`
3. Rotate all credentials immediately
4. Consider using `git filter-branch` to remove from history

### Always Run Tests Before Committing

```bash
# ✅ CORRECT - Test before commit
pytest                           # Run all tests
pytest --cov=backend tests/      # Check coverage

# Only commit if tests pass
git add .
git commit -m "feat(api): add new endpoint"

# ❌ WRONG - Committing without testing
git add .
git commit -m "feat(api): add new endpoint"  # Did tests pass? Unknown!
```

**Pre-commit Checklist:**
- [ ] All tests pass (`pytest`)
- [ ] No linting errors (`flake8 backend/ tests/`)
- [ ] Code is formatted (`black backend/ tests/`)
- [ ] No sensitive data in commits
- [ ] Commit message follows conventions

### Branch Naming: `feature/`, `bugfix/`, `hotfix/`

```bash
# ✅ CORRECT - Descriptive branch names
git checkout -b feature/add-task-categories
git checkout -b feature/user-authentication
git checkout -b bugfix/fix-date-parsing-error
git checkout -b bugfix/resolve-n-plus-one-query
git checkout -b hotfix/critical-security-fix
git checkout -b refactor/separate-crud-operations

# ❌ WRONG - Vague or unclear branch names
git checkout -b new-feature
git checkout -b fix
git checkout -b test
git checkout -b branch123
git checkout -b johns-branch
```

**Branch Naming Conventions:**
- `feature/` - New features
- `bugfix/` - Bug fixes
- `hotfix/` - Critical production fixes
- `refactor/` - Code refactoring
- `docs/` - Documentation updates
- `test/` - Test additions or updates

---

## 8. What Claude Code Must NEVER Do

### ❌ Never Drop or Truncate Database Tables

```python
# ❌ ABSOLUTELY FORBIDDEN
Base.metadata.drop_all(bind=engine)
db.execute("DROP TABLE tasks;")
db.execute("TRUNCATE TABLE tasks;")
db.execute("DELETE FROM tasks;")  # Without WHERE clause

# ✅ CORRECT - Use migrations for schema changes
alembic revision --autogenerate -m "remove old table"
# Then manually edit migration to drop specific table if needed
```

### ❌ Never Delete Migration Files

```bash
# ❌ ABSOLUTELY FORBIDDEN
rm alembic/versions/001_initial_migration.py
rm alembic/versions/*.py

# ✅ CORRECT - Create new migration to reverse changes
alembic revision --autogenerate -m "reverse previous change"
```

**Why?** Deleting migrations breaks migration history and can cause database inconsistencies across environments.

### ❌ Never Hardcode Credentials in Source Files

```python
# ❌ ABSOLUTELY FORBIDDEN
DATABASE_URL = "postgresql://admin:SuperSecret123@prod.example.com:5432/db"
API_KEY = "sk-1234567890abcdefghijklmnop"
JWT_SECRET = "my-secret-jwt-key-12345"

# ✅ CORRECT - Use environment variables
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
API_KEY = os.getenv("API_KEY")
JWT_SECRET = os.getenv("JWT_SECRET")
```

### ❌ Never Push Directly to Main Without Tests Passing

```bash
# ❌ WRONG - Pushing without running tests
git add .
git commit -m "new feature"
git push origin main  # Don't push if tests haven't passed!

# ✅ CORRECT - Always test first
pytest                    # All tests must pass
pytest --cov=backend      # Check coverage
git add .
git commit -m "feat: add new feature"
git push origin main
```

**Ideal Workflow:**
1. Create feature branch
2. Make changes
3. Run tests locally
4. Commit changes
5. Push to feature branch
6. Create pull request
7. CI/CD runs tests
8. Merge to main after approval

### ❌ Never Expose the .env File

```python
# ❌ ABSOLUTELY FORBIDDEN
@router.get("/config")
def get_config():
    with open(".env") as f:
        return {"config": f.read()}  # NEVER expose .env contents

@router.get("/debug")
def debug():
    return {"env": dict(os.environ)}  # NEVER expose all environment variables

# ✅ CORRECT - Only expose necessary, non-sensitive info
@router.get("/health")
def health():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": os.getenv("ENV", "development")  # OK: non-sensitive
    }
```

---

## Additional Guidelines

### Code Review Checklist

Before considering code complete, verify:

- [ ] Follows all coding standards (naming, structure)
- [ ] Uses Pydantic schemas, not raw models
- [ ] Has proper error handling with appropriate status codes
- [ ] Includes docstrings for all functions and classes
- [ ] Has tests for success and error cases
- [ ] No hardcoded credentials or sensitive data
- [ ] Migration created for any database changes
- [ ] No raw SQL (or justified with comments)
- [ ] Meaningful commit message
- [ ] All tests pass
- [ ] `.env` not committed

### When in Doubt

1. **Check existing code** - Follow patterns already in the codebase
2. **Consult documentation** - README.md, API.md, this file
3. **Run tests** - If tests pass, you're probably on the right track
4. **Ask for clarification** - Better to ask than to break things

### File-Specific Rules

**`backend/models.py`:**
- Only SQLAlchemy models
- Always include `created_at` and `updated_at`
- Add docstrings for each model

**`backend/schemas.py`:**
- Only Pydantic models
- Use for API request/response validation
- Add field descriptions and examples

**`backend/routes.py`:**
- Only HTTP route handlers
- Delegate business logic to `crud.py`
- Always specify response_model

**`backend/crud.py`:**
- Only database operations
- No HTTP-specific code (no HTTPException here)
- Return None or objects, let routes handle HTTP errors

**`backend/database.py`:**
- Only database configuration
- Connection strings from environment variables
- Session management

**`tests/`:**
- Use fixtures from conftest.py
- Test both success and error cases
- Clear, descriptive test names

---

## Summary

This document defines the rules and standards for the Task Manager API project. When working with Claude Code:

1. **Always follow these rules** - They exist to maintain code quality and consistency
2. **Never do the forbidden actions** - They can cause data loss or security issues
3. **When adding features** - Follow the patterns established in the codebase
4. **When fixing bugs** - Add tests to prevent regression
5. **When in doubt** - Ask for clarification rather than guessing

**Remember:** Good code is consistent, well-tested, secure, and maintainable.

---

**Last Updated:** 2024-01-15
**Version:** 1.0.0
**Maintained by:** Claude Code
