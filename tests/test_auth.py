"""
Comprehensive authentication tests for Task Manager API.

This module contains tests for user registration, login, and authentication flows,
including success cases, error cases, and security validation.
"""

import pytest
from backend.models import User


class TestUserRegistration:
    """Tests for user registration endpoint POST /api/auth/register"""

    def test_register_success(self, client, test_user_data):
        """Test successful user registration returns 201 with user data"""
        response = client.post("/api/auth/register", json=test_user_data)

        assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.json()}"
        data = response.json()

        # Verify response structure
        assert "id" in data, "Response should contain user id"
        assert isinstance(data["id"], int), "User id should be an integer"

        # Verify user data matches input (excluding password)
        assert data["email"] == test_user_data["email"], "Email should match input"
        assert data["username"] == test_user_data["username"], "Username should match input"

        # Verify password fields are NOT in response
        assert "password" not in data, "Plain password should never be in response"
        assert "hashed_password" not in data, "Hashed password should never be in response"

        # Verify additional fields
        assert "is_active" in data, "Response should contain is_active field"
        assert data["is_active"] is True, "New users should be active by default"
        assert "created_at" in data, "Response should contain created_at timestamp"

    def test_register_duplicate_email(self, client, test_user_data):
        """Test registration with existing email returns 409 Conflict"""
        # Create first user
        response1 = client.post("/api/auth/register", json=test_user_data)
        assert response1.status_code == 201, "First registration should succeed"

        # Try to create second user with same email
        duplicate_data = {
            "username": "differentuser",
            "email": test_user_data["email"],  # Same email
            "password": "anotherpass123"
        }
        response2 = client.post("/api/auth/register", json=duplicate_data)

        assert response2.status_code == 409, f"Expected 409 Conflict, got {response2.status_code}"
        assert "detail" in response2.json(), "Error response should contain detail message"
        assert "email" in response2.json()["detail"].lower(), "Error message should mention email"

    def test_register_duplicate_username(self, client, test_user_data):
        """Test registration with existing username returns 409 Conflict"""
        # Create first user
        response1 = client.post("/api/auth/register", json=test_user_data)
        assert response1.status_code == 201, "First registration should succeed"

        # Try to create second user with same username
        duplicate_data = {
            "username": test_user_data["username"],  # Same username
            "email": "different@example.com",
            "password": "anotherpass123"
        }
        response2 = client.post("/api/auth/register", json=duplicate_data)

        assert response2.status_code == 409, f"Expected 409 Conflict, got {response2.status_code}"
        assert "detail" in response2.json(), "Error response should contain detail message"
        assert "username" in response2.json()["detail"].lower(), "Error message should mention username"

    def test_register_invalid_email(self, client):
        """Test registration with invalid email format returns 422 Validation Error"""
        invalid_data = {
            "username": "testuser",
            "email": "not-a-valid-email",  # Invalid email format
            "password": "testpass123"
        }
        response = client.post("/api/auth/register", json=invalid_data)

        assert response.status_code == 422, f"Expected 422 Unprocessable Entity, got {response.status_code}"
        data = response.json()
        assert "detail" in data, "Validation error should contain detail"

    def test_register_short_password(self, client):
        """Test registration with password less than 8 characters returns 422"""
        short_password_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "short"  # Less than 8 characters
        }
        response = client.post("/api/auth/register", json=short_password_data)

        assert response.status_code == 422, f"Expected 422 Unprocessable Entity, got {response.status_code}"
        data = response.json()
        assert "detail" in data, "Validation error should contain detail"

    def test_register_missing_fields(self, client):
        """Test registration with missing required fields returns 422"""
        # Missing password field
        incomplete_data = {
            "username": "testuser",
            "email": "test@example.com"
            # password is missing
        }
        response = client.post("/api/auth/register", json=incomplete_data)

        assert response.status_code == 422, f"Expected 422 Unprocessable Entity, got {response.status_code}"
        data = response.json()
        assert "detail" in data, "Validation error should contain detail"


class TestUserLogin:
    """Tests for user login endpoint POST /api/auth/login"""

    def test_login_success(self, client, create_test_user, test_user_data):
        """Test successful login returns access token with correct structure"""
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
        response = client.post("/api/auth/login", json=login_data)

        assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}: {response.json()}"
        data = response.json()

        # Verify token structure
        assert "access_token" in data, "Response should contain access_token"
        assert "token_type" in data, "Response should contain token_type"

        # Verify token type
        assert data["token_type"] == "bearer", f"Token type should be 'bearer', got '{data['token_type']}'"

        # Verify token is a non-empty string
        assert isinstance(data["access_token"], str), "Access token should be a string"
        assert len(data["access_token"]) > 0, "Access token should not be empty"

    def test_login_wrong_password(self, client, create_test_user, test_user_data):
        """Test login with incorrect password returns 401 Unauthorized"""
        login_data = {
            "email": test_user_data["email"],
            "password": "wrongpassword123"  # Wrong password
        }
        response = client.post("/api/auth/login", json=login_data)

        assert response.status_code == 401, f"Expected 401 Unauthorized, got {response.status_code}"
        data = response.json()
        assert "detail" in data, "Error response should contain detail message"

    def test_login_wrong_email(self, client, create_test_user, test_user_data):
        """Test login with incorrect email returns 401 Unauthorized"""
        login_data = {
            "email": "wrong@example.com",  # Wrong email
            "password": test_user_data["password"]
        }
        response = client.post("/api/auth/login", json=login_data)

        assert response.status_code == 401, f"Expected 401 Unauthorized, got {response.status_code}"
        data = response.json()
        assert "detail" in data, "Error response should contain detail message"

    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user returns 401 Unauthorized"""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "somepassword123"
        }
        response = client.post("/api/auth/login", json=login_data)

        assert response.status_code == 401, f"Expected 401 Unauthorized, got {response.status_code}"
        data = response.json()
        assert "detail" in data, "Error response should contain detail message"

    def test_login_token_is_valid(self, client, create_test_user, test_user_data):
        """Test that token returned from login works for protected endpoints"""
        # Login to get token
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
        login_response = client.post("/api/auth/login", json=login_data)
        assert login_response.status_code == 200, "Login should succeed"

        token = login_response.json()["access_token"]

        # Use token to access protected endpoint
        headers = {"Authorization": f"Bearer {token}"}
        me_response = client.get("/api/auth/me", headers=headers)

        assert me_response.status_code == 200, f"Token should be valid for protected endpoint, got {me_response.status_code}"
        user_data = me_response.json()
        assert user_data["email"] == test_user_data["email"], "Should return correct user data"


class TestGetCurrentUser:
    """Tests for get current user endpoint GET /api/auth/me"""

    def test_get_current_user_success(self, authenticated_client, test_user_data):
        """Test getting current user info with valid token returns user data"""
        response = authenticated_client.get("/api/auth/me")

        assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}: {response.json()}"
        data = response.json()

        # Verify user data structure
        assert "id" in data, "Response should contain user id"
        assert "email" in data, "Response should contain email"
        assert "username" in data, "Response should contain username"
        assert "is_active" in data, "Response should contain is_active"

        # Verify data matches test user
        assert data["email"] == test_user_data["email"], "Email should match authenticated user"
        assert data["username"] == test_user_data["username"], "Username should match authenticated user"

        # Verify password is NOT in response
        assert "password" not in data, "Password should never be in response"
        assert "hashed_password" not in data, "Hashed password should never be in response"

    def test_get_current_user_no_token(self, client):
        """Test accessing protected endpoint without Authorization header returns 401"""
        response = client.get("/api/auth/me")

        assert response.status_code == 401, f"Expected 401 Unauthorized, got {response.status_code}"
        data = response.json()
        assert "detail" in data, "Error response should contain detail message"

    def test_get_current_user_invalid_token(self, client):
        """Test accessing protected endpoint with invalid token returns 401"""
        headers = {"Authorization": "Bearer invalid.token.here"}
        response = client.get("/api/auth/me", headers=headers)

        assert response.status_code == 401, f"Expected 401 Unauthorized, got {response.status_code}"
        data = response.json()
        assert "detail" in data, "Error response should contain detail message"

    def test_get_current_user_malformed_header(self, client):
        """Test accessing protected endpoint with malformed Authorization header returns 401"""
        # Test without "Bearer" prefix
        headers = {"Authorization": "some-random-token"}
        response = client.get("/api/auth/me", headers=headers)

        assert response.status_code == 401, f"Expected 401 Unauthorized, got {response.status_code}"


class TestSecurity:
    """Security-focused tests for authentication system"""

    def test_password_is_hashed(self, client, db_session, test_user_data):
        """Test that passwords are stored as bcrypt hashes in the database"""
        # Register user
        response = client.post("/api/auth/register", json=test_user_data)
        assert response.status_code == 201, "Registration should succeed"

        user_id = response.json()["id"]

        # Query database directly
        user = db_session.query(User).filter(User.id == user_id).first()
        assert user is not None, "User should exist in database"

        # Verify password is hashed
        assert user.hashed_password != test_user_data["password"], "Password should be hashed, not stored in plain text"
        assert user.hashed_password.startswith("$2b$"), "Password should be bcrypt hash (starts with $2b$)"
        assert len(user.hashed_password) == 60, "Bcrypt hash should be 60 characters"

    def test_password_not_in_response(self, client, test_user_data):
        """Test that hashed_password is never exposed in any API response"""
        # Test registration response
        register_response = client.post("/api/auth/register", json=test_user_data)
        assert register_response.status_code == 201, "Registration should succeed"
        register_data = register_response.json()

        assert "password" not in register_data, "Password should not be in registration response"
        assert "hashed_password" not in register_data, "Hashed password should not be in registration response"

        # Test login response
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
        login_response = client.post("/api/auth/login", json=login_data)
        assert login_response.status_code == 200, "Login should succeed"
        login_response_data = login_response.json()

        assert "password" not in login_response_data, "Password should not be in login response"
        assert "hashed_password" not in login_response_data, "Hashed password should not be in login response"

        # Test get current user response
        token = login_response_data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        me_response = client.get("/api/auth/me", headers=headers)
        assert me_response.status_code == 200, "Get current user should succeed"
        me_data = me_response.json()

        assert "password" not in me_data, "Password should not be in current user response"
        assert "hashed_password" not in me_data, "Hashed password should not be in current user response"
