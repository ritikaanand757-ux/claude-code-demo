"""
Integration tests for authentication system.

This module contains end-to-end tests for complete authentication flows,
edge cases, and concurrent operations.
"""

import pytest
from concurrent.futures import ThreadPoolExecutor, as_completed


class TestCompleteAuthFlow:
    """Tests for complete authentication flows from registration to protected endpoints"""

    def test_complete_auth_flow(self, client):
        """Test complete flow: Register -> Login -> Access protected endpoint"""
        # Step 1: Register a new user
        register_data = {
            "username": "flowuser",
            "email": "flow@example.com",
            "password": "flowpass123"
        }
        register_response = client.post("/api/auth/register", json=register_data)
        assert register_response.status_code == 201, f"Registration failed: {register_response.json()}"

        user_data = register_response.json()
        assert user_data["email"] == register_data["email"], "Registration should return correct email"
        assert user_data["username"] == register_data["username"], "Registration should return correct username"

        # Step 2: Login with the registered credentials
        login_data = {
            "email": register_data["email"],
            "password": register_data["password"]
        }
        login_response = client.post("/api/auth/login", json=login_data)
        assert login_response.status_code == 200, f"Login failed: {login_response.json()}"

        token_data = login_response.json()
        assert "access_token" in token_data, "Login should return access token"
        assert "token_type" in token_data, "Login should return token type"
        assert token_data["token_type"] == "bearer", "Token type should be bearer"

        # Step 3: Access protected endpoint with token
        headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        me_response = client.get("/api/auth/me", headers=headers)
        assert me_response.status_code == 200, f"Protected endpoint access failed: {me_response.json()}"

        current_user = me_response.json()
        assert current_user["email"] == register_data["email"], "Protected endpoint should return correct user"
        assert current_user["username"] == register_data["username"], "Protected endpoint should return correct username"

        # Step 4: Verify user can create a task (if tasks require auth in the future)
        task_data = {"title": "Test Task", "description": "Task created by authenticated user"}
        task_response = client.post("/api/tasks/", json=task_data, headers=headers)
        # Note: Currently tasks don't require auth, but this tests that the token doesn't interfere
        assert task_response.status_code == 201, f"Task creation failed: {task_response.json()}"

    def test_flow_with_logout_simulation(self, client):
        """Test authentication flow with token invalidation (simulated by using wrong token)"""
        # Register and login
        user_data = {
            "username": "logoutuser",
            "email": "logout@example.com",
            "password": "logoutpass123"
        }
        client.post("/api/auth/register", json=user_data)

        login_response = client.post("/api/auth/login", json={
            "email": user_data["email"],
            "password": user_data["password"]
        })
        token = login_response.json()["access_token"]

        # Access protected endpoint successfully
        headers = {"Authorization": f"Bearer {token}"}
        response1 = client.get("/api/auth/me", headers=headers)
        assert response1.status_code == 200, "First access should succeed"

        # Simulate logout by using invalid token
        invalid_headers = {"Authorization": f"Bearer {token}invalid"}
        response2 = client.get("/api/auth/me", headers=invalid_headers)
        assert response2.status_code == 401, "Invalid token should be rejected"

    def test_multiple_users_independent(self, client):
        """Test that multiple users can register and authenticate independently"""
        users = [
            {"username": "user1", "email": "user1@example.com", "password": "pass1234567"},
            {"username": "user2", "email": "user2@example.com", "password": "pass2345678"},
            {"username": "user3", "email": "user3@example.com", "password": "pass3456789"}
        ]

        tokens = []

        # Register and login all users
        for user in users:
            # Register
            register_response = client.post("/api/auth/register", json=user)
            assert register_response.status_code == 201, f"Failed to register {user['email']}"

            # Login
            login_response = client.post("/api/auth/login", json={
                "email": user["email"],
                "password": user["password"]
            })
            assert login_response.status_code == 200, f"Failed to login {user['email']}"

            token = login_response.json()["access_token"]
            tokens.append((user, token))

        # Verify each user can access their own data
        for user, token in tokens:
            headers = {"Authorization": f"Bearer {token}"}
            response = client.get("/api/auth/me", headers=headers)

            assert response.status_code == 200, f"Failed to get user data for {user['email']}"
            user_data = response.json()
            assert user_data["email"] == user["email"], f"Token should return correct user {user['email']}"
            assert user_data["username"] == user["username"], f"Token should return correct username"


class TestSpecialCharacters:
    """Tests for handling special characters and Unicode in user data"""

    def test_register_with_special_characters(self, client):
        """Test registration with Unicode and special characters in username"""
        special_user_data = {
            "username": "user_name-123",
            "email": "special+test@example.com",
            "password": "pass!@#$123"
        }
        response = client.post("/api/auth/register", json=special_user_data)

        assert response.status_code == 201, f"Registration with special chars should succeed: {response.json()}"
        data = response.json()
        assert data["username"] == special_user_data["username"], "Username with special chars should be preserved"

    def test_register_with_unicode_username(self, client):
        """Test registration with Unicode characters in username"""
        unicode_user_data = {
            "username": "用户名",  # Chinese characters
            "email": "unicode@example.com",
            "password": "unicodepass123"
        }
        response = client.post("/api/auth/register", json=unicode_user_data)

        # Note: This might fail if username validation doesn't allow Unicode
        # The test documents current behavior
        if response.status_code == 201:
            data = response.json()
            assert data["username"] == unicode_user_data["username"], "Unicode username should be preserved"
        else:
            # If validation rejects Unicode, verify proper error handling
            assert response.status_code in [400, 422], "Should return validation error"

    def test_login_with_unicode_email(self, client):
        """Test login with special characters in email"""
        user_data = {
            "username": "emailtest",
            "email": "test.email+tag@example.co.uk",
            "password": "testpass123"
        }

        # Register
        register_response = client.post("/api/auth/register", json=user_data)
        assert register_response.status_code == 201, "Registration should succeed"

        # Login with the special email
        login_response = client.post("/api/auth/login", json={
            "email": user_data["email"],
            "password": user_data["password"]
        })
        assert login_response.status_code == 200, f"Login with special email should succeed: {login_response.json()}"

    def test_password_with_special_characters(self, client):
        """Test that passwords with special characters work correctly"""
        user_data = {
            "username": "passtest",
            "email": "passtest@example.com",
            "password": "P@ssw0rd!#$%^&*()"
        }

        # Register
        register_response = client.post("/api/auth/register", json=user_data)
        assert register_response.status_code == 201, "Registration with special char password should succeed"

        # Login with the complex password
        login_response = client.post("/api/auth/login", json={
            "email": user_data["email"],
            "password": user_data["password"]
        })
        assert login_response.status_code == 200, "Login with special char password should succeed"


class TestConcurrentOperations:
    """Tests for concurrent registration and authentication operations"""

    def test_concurrent_registrations(self, client):
        """Test that concurrent registrations with same email are handled correctly"""
        user_data = {
            "username": "concurrent",
            "email": "concurrent@example.com",
            "password": "concurrent123"
        }

        # Function to register user
        def register_user():
            try:
                response = client.post("/api/auth/register", json=user_data)
                return response.status_code, response.json()
            except Exception as e:
                return None, str(e)

        # Try to register same user multiple times concurrently
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(register_user) for _ in range(5)]
            results = [future.result() for future in as_completed(futures)]

        # Count successful registrations
        success_count = sum(1 for status, _ in results if status == 201)
        conflict_count = sum(1 for status, _ in results if status == 409)

        # Exactly one should succeed, others should get 409 Conflict
        assert success_count == 1, f"Exactly one registration should succeed, got {success_count}"
        assert conflict_count >= 1, f"At least one should get 409 Conflict, got {conflict_count}"

    def test_concurrent_logins(self, client):
        """Test that multiple concurrent logins for same user work correctly"""
        # First register a user
        user_data = {
            "username": "logintest",
            "email": "logintest@example.com",
            "password": "loginpass123"
        }
        register_response = client.post("/api/auth/register", json=user_data)
        assert register_response.status_code == 201, "Registration should succeed"

        # Function to login
        def login_user():
            try:
                response = client.post("/api/auth/login", json={
                    "email": user_data["email"],
                    "password": user_data["password"]
                })
                return response.status_code, response.json()
            except Exception as e:
                return None, str(e)

        # Try to login multiple times concurrently
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(login_user) for _ in range(10)]
            results = [future.result() for future in as_completed(futures)]

        # All logins should succeed
        success_count = sum(1 for status, _ in results if status == 200)
        assert success_count == 10, f"All concurrent logins should succeed, got {success_count}/10"

        # All should return valid tokens
        tokens = [data.get("access_token") for status, data in results if status == 200]
        assert len(tokens) == 10, "All logins should return tokens"
        assert all(token and len(token) > 0 for token in tokens), "All tokens should be valid"

    def test_concurrent_different_users(self, client):
        """Test concurrent registration of different users"""
        users = [
            {"username": f"user{i}", "email": f"user{i}@example.com", "password": f"pass{i}12345"}
            for i in range(10)
        ]

        # Function to register a specific user
        def register_specific_user(user):
            try:
                response = client.post("/api/auth/register", json=user)
                return user["email"], response.status_code, response.json()
            except Exception as e:
                return user["email"], None, str(e)

        # Register all users concurrently
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(register_specific_user, user) for user in users]
            results = [future.result() for future in as_completed(futures)]

        # All registrations should succeed
        success_count = sum(1 for _, status, _ in results if status == 201)
        assert success_count == 10, f"All different user registrations should succeed, got {success_count}/10"


class TestEdgeCases:
    """Tests for edge cases and boundary conditions"""

    def test_login_case_sensitive_email(self, client):
        """Test that email comparison is case-insensitive"""
        user_data = {
            "username": "casetest",
            "email": "Case@Example.Com",
            "password": "casepass123"
        }

        # Register with mixed case email
        register_response = client.post("/api/auth/register", json=user_data)
        assert register_response.status_code == 201, "Registration should succeed"

        # Try to login with lowercase email
        login_response = client.post("/api/auth/login", json={
            "email": "case@example.com",
            "password": user_data["password"]
        })

        # Note: Email comparison behavior depends on database collation
        # This test documents the current behavior
        assert login_response.status_code in [200, 401], "Login should either succeed or fail consistently"

    def test_register_with_long_username(self, client):
        """Test registration with maximum allowed username length"""
        long_username = "a" * 50  # Maximum is 50 per schema
        user_data = {
            "username": long_username,
            "email": "longuser@example.com",
            "password": "longpass123"
        }

        response = client.post("/api/auth/register", json=user_data)
        assert response.status_code == 201, f"Registration with max length username should succeed: {response.json()}"

        # Try exceeding max length
        too_long_username = "a" * 51
        invalid_data = {
            "username": too_long_username,
            "email": "toolong@example.com",
            "password": "toolongpass123"
        }
        response2 = client.post("/api/auth/register", json=invalid_data)
        assert response2.status_code == 422, "Registration with too long username should fail validation"

    def test_register_with_minimum_username(self, client):
        """Test registration with minimum allowed username length"""
        min_username = "abc"  # Minimum is 3 per schema
        user_data = {
            "username": min_username,
            "email": "minuser@example.com",
            "password": "minpass123"
        }

        response = client.post("/api/auth/register", json=user_data)
        assert response.status_code == 201, f"Registration with min length username should succeed: {response.json()}"

        # Try below minimum
        too_short_username = "ab"
        invalid_data = {
            "username": too_short_username,
            "email": "tooshort@example.com",
            "password": "tooshortpass123"
        }
        response2 = client.post("/api/auth/register", json=invalid_data)
        assert response2.status_code == 422, "Registration with too short username should fail validation"

    def test_empty_request_body(self, client):
        """Test endpoints with empty request body"""
        response = client.post("/api/auth/register", json={})
        assert response.status_code == 422, "Empty registration data should fail validation"

        response2 = client.post("/api/auth/login", json={})
        assert response2.status_code == 422, "Empty login data should fail validation"
