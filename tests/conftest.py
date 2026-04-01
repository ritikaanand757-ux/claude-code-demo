"""
Pytest configuration and fixtures for Task Manager API tests.

This module provides test fixtures that are shared across all test files:
- Database setup with SQLite for testing
- Test client configuration
- Session management

The fixtures ensure test isolation by creating a fresh database for each test
and properly cleaning up resources after test completion.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.main import app
from backend.database import Base, get_db

# Use an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
"""str: SQLite database URL for testing purposes."""

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
"""Engine: SQLAlchemy engine for test database."""

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
"""sessionmaker: Session factory for creating test database sessions."""


@pytest.fixture(scope="function")
def db_session():
    """
    Pytest fixture that provides a fresh database session for each test.

    This fixture creates all database tables before the test runs and drops
    them after the test completes, ensuring test isolation.

    Yields:
        Session: SQLAlchemy database session for testing

    Scope:
        function - A new database is created for each test function

    Example:
        def test_create_task(db_session):
            task = Task(title="Test")
            db_session.add(task)
            db_session.commit()
    """
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """
    Pytest fixture that provides a test client with overridden database dependency.

    This fixture creates a FastAPI TestClient that uses the test database
    instead of the production database. It overrides the get_db dependency
    to inject the test session.

    Args:
        db_session: Database session fixture (injected by pytest)

    Yields:
        TestClient: FastAPI test client configured with test database

    Scope:
        function - A new client is created for each test function

    Example:
        def test_create_task(client):
            response = client.post("/api/tasks/", json={"title": "Test"})
            assert response.status_code == 201

    Note:
        The dependency overrides are automatically cleared after each test.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    """
    Pytest fixture that provides test user data for registration/authentication.

    Returns:
        dict: Dictionary containing test user credentials with username, email, and password

    Example:
        def test_register(client, test_user_data):
            response = client.post("/api/auth/register", json=test_user_data)
            assert response.status_code == 201
    """
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    }


@pytest.fixture
def create_test_user(client, test_user_data):
    """
    Pytest fixture that creates a test user via the registration API.

    This fixture registers a new user and returns the response data,
    which can be used for subsequent authentication tests.

    Args:
        client: FastAPI test client fixture
        test_user_data: Test user data fixture

    Returns:
        dict: Created user data (excluding password)

    Example:
        def test_login(client, create_test_user, test_user_data):
            login_data = {
                "email": test_user_data["email"],
                "password": test_user_data["password"]
            }
            response = client.post("/api/auth/login", json=login_data)
            assert response.status_code == 200
    """
    response = client.post("/api/auth/register", json=test_user_data)
    assert response.status_code == 201, f"Failed to create test user: {response.json()}"
    return response.json()


@pytest.fixture
def auth_token(client, test_user_data):
    """
    Pytest fixture that creates a test user and returns a valid JWT token.

    This fixture registers a user, logs them in, and returns the JWT access token
    that can be used for authenticated requests.

    Args:
        client: FastAPI test client fixture
        test_user_data: Test user data fixture

    Returns:
        str: JWT access token

    Example:
        def test_protected_endpoint(client, auth_token):
            headers = {"Authorization": f"Bearer {auth_token}"}
            response = client.get("/api/auth/me", headers=headers)
            assert response.status_code == 200
    """
    # Register user
    client.post("/api/auth/register", json=test_user_data)

    # Login to get token
    login_data = {
        "email": test_user_data["email"],
        "password": test_user_data["password"]
    }
    response = client.post("/api/auth/login", json=login_data)
    assert response.status_code == 200, f"Failed to login: {response.json()}"

    return response.json()["access_token"]


@pytest.fixture
def authenticated_client(client, auth_token):
    """
    Pytest fixture that returns a test client with Authorization header pre-configured.

    This fixture provides a client that automatically includes the JWT token
    in the Authorization header for all requests.

    Args:
        client: FastAPI test client fixture
        auth_token: JWT access token fixture

    Returns:
        TestClient: Test client with Authorization header set

    Example:
        def test_get_current_user(authenticated_client):
            response = authenticated_client.get("/api/auth/me")
            assert response.status_code == 200
    """
    client.headers.update({"Authorization": f"Bearer {auth_token}"})
    return client
