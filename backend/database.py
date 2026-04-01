"""
Database configuration and session management.

This module handles database connection setup, engine creation, and session management
for the Task Manager application using SQLAlchemy.
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Load environment variables
load_dotenv()

# Database connection settings
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/taskmanager_db"
)
"""
str: PostgreSQL database connection URL.

Format: postgresql://username:password@host:port/database_name

Example:
    postgresql://postgres:password@localhost:5432/taskmanager_db
"""

# Create database engine
engine = create_engine(DATABASE_URL)
"""
Engine: SQLAlchemy database engine instance.

This engine manages connections to the PostgreSQL database and handles
connection pooling automatically.
"""

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
"""
sessionmaker: Factory for creating database sessions.

Configuration:
    - autocommit=False: Transactions must be explicitly committed
    - autoflush=False: Changes are not automatically flushed to the database
    - bind=engine: Sessions are bound to the database engine
"""

# Create base class for models
Base = declarative_base()
"""
DeclarativeMeta: Base class for SQLAlchemy ORM models.

All database models should inherit from this base class to get ORM functionality.
"""


def get_db():
    """
    Dependency function that provides a database session.

    This function is used as a FastAPI dependency to inject database sessions
    into route handlers. It ensures that sessions are properly closed after use,
    even if an exception occurs.

    Yields:
        Session: SQLAlchemy database session

    Example:
        @app.get("/tasks")
        def get_tasks(db: Session = Depends(get_db)):
            return db.query(Task).all()

    Note:
        The session is automatically closed after the request is complete,
        ensuring proper resource management.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
