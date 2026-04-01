.PHONY: help install run dev test test-cov migrate migrate-create migrate-down migrate-history db-reset format lint clean

# Default target - show help
help:
	@echo "=========================================="
	@echo "Task Manager API - Available Commands"
	@echo "=========================================="
	@echo ""
	@echo "Development:"
	@echo "  make install          - Install all Python dependencies"
	@echo "  make run              - Run the FastAPI server (production mode)"
	@echo "  make dev              - Run the FastAPI server (development mode with auto-reload)"
	@echo ""
	@echo "Database:"
	@echo "  make migrate          - Run pending database migrations"
	@echo "  make migrate-create   - Create a new migration (use MSG='description')"
	@echo "  make migrate-down     - Rollback last migration"
	@echo "  make migrate-history  - Show migration history"
	@echo "  make db-reset         - Reset database (WARNING: destroys all data)"
	@echo ""
	@echo "Testing:"
	@echo "  make test             - Run all tests"
	@echo "  make test-cov         - Run tests with coverage report"
	@echo "  make test-verbose     - Run tests with verbose output"
	@echo ""
	@echo "Code Quality:"
	@echo "  make format           - Format code with Black"
	@echo "  make format-check     - Check code formatting without changes"
	@echo "  make lint             - Run linting checks"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean            - Clean up temporary files and caches"
	@echo "  make shell            - Open Python shell with app context"
	@echo ""
	@echo "=========================================="

# Install dependencies
install:
	@echo "📦 Installing dependencies..."
	python -m pip install --upgrade pip
	pip install -r requirements.txt
	@echo "✅ Dependencies installed!"

# Run server (production mode)
run:
	@echo "🚀 Starting FastAPI server (production mode)..."
	uvicorn backend.main:app --host 0.0.0.0 --port 8000

# Run server (development mode with auto-reload)
dev:
	@echo "🔧 Starting FastAPI server (development mode with auto-reload)..."
	uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# Run tests
test:
	@echo "🧪 Running tests..."
	python -m pytest tests/ -v

# Run tests with coverage
test-cov:
	@echo "🧪 Running tests with coverage..."
	python -m pytest tests/ -v --cov=backend --cov-report=html --cov-report=term

# Run tests with verbose output
test-verbose:
	@echo "🧪 Running tests (verbose mode)..."
	python -m pytest tests/ -vv -s

# Run database migrations
migrate:
	@echo "🔄 Running database migrations..."
	alembic upgrade head
	@echo "✅ Migrations completed!"

# Create new migration
# Usage: make migrate-create MSG="add new field"
migrate-create:
	@echo "📝 Creating new migration..."
	@if [ -z "$(MSG)" ]; then \
		echo "❌ Error: Please provide a message using MSG='description'"; \
		echo "   Example: make migrate-create MSG='add status field'"; \
		exit 1; \
	fi
	alembic revision --autogenerate -m "$(MSG)"
	@echo "✅ Migration created! Please review it in alembic/versions/"

# Rollback last migration
migrate-down:
	@echo "⏪ Rolling back last migration..."
	alembic downgrade -1
	@echo "✅ Rollback completed!"

# Show migration history
migrate-history:
	@echo "📜 Migration history:"
	alembic history --verbose

# Reset database (WARNING: destroys all data)
db-reset:
	@echo "⚠️  WARNING: This will destroy all data!"
	@echo "Press Ctrl+C to cancel, or Enter to continue..."
	@read dummy
	@echo "🗑️  Resetting database..."
	alembic downgrade base
	alembic upgrade head
	@echo "✅ Database reset completed!"

# Format code with Black
format:
	@echo "✨ Formatting code with Black..."
	python -m black backend/ tests/
	@echo "✅ Code formatted!"

# Check code formatting
format-check:
	@echo "🔍 Checking code formatting..."
	python -m black backend/ tests/ --check

# Run linting
lint:
	@echo "🔍 Running linting checks..."
	@echo "Note: Install flake8 if not available: pip install flake8"
	-python -m flake8 backend/ tests/ --max-line-length=100 --extend-ignore=E203,W503
	@echo "✅ Linting completed!"

# Clean temporary files
clean:
	@echo "🧹 Cleaning up temporary files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".coverage" -delete 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	rm -f .coverage 2>/dev/null || true
	@echo "✅ Cleanup completed!"

# Open Python shell with app context
shell:
	@echo "🐍 Opening Python shell..."
	python -i -c "from backend.database import SessionLocal, engine; from backend import models, crud; db = SessionLocal(); print('Database session available as: db'); print('Models available: models.*'); print('CRUD operations: crud.*')"
