#!/usr/bin/env python
"""
Comprehensive test to verify authentication implementation
This script checks all components of the authentication system
"""

import os
import sys

# Set environment variables before importing
os.environ['SECRET_KEY'] = 'test-secret-key-for-verification-only-do-not-use-in-production-32chars'
os.environ['DATABASE_URL'] = 'postgresql://postgres:postgres@localhost:5432/taskmanager_db'

print("=" * 60)
print("AUTHENTICATION SYSTEM IMPLEMENTATION TEST")
print("=" * 60)
print()

# Test 1: File existence
print("TEST 1: Checking file existence")
print("-" * 60)

files_to_check = {
    'backend/auth.py': 'Authentication utilities',
    'backend/auth_routes.py': 'Authentication routes',
    'backend/models.py': 'Database models (with User)',
    'backend/schemas.py': 'Pydantic schemas (with User schemas)',
    'backend/crud.py': 'CRUD operations (with User operations)',
    'backend/main.py': 'Main application',
    'backend/database.py': 'Database configuration',
    '.env.example': 'Environment variable example',
    'requirements.txt': 'Python dependencies'
}

all_files_exist = True
for file_path, description in files_to_check.items():
    if os.path.exists(file_path):
        print(f"✓ {file_path:<30} - {description}")
    else:
        print(f"✗ {file_path:<30} - MISSING!")
        all_files_exist = False

if not all_files_exist:
    print("\n✗ Some files are missing!")
    sys.exit(1)

print("\n✓ All files exist")
print()

# Test 2: Import tests
print("TEST 2: Testing module imports")
print("-" * 60)

try:
    from backend.auth import (
        get_password_hash,
        verify_password,
        create_access_token,
        verify_token,
        get_current_user,
        SECRET_KEY,
        ALGORITHM,
        ACCESS_TOKEN_EXPIRE_MINUTES
    )
    print("✓ backend.auth - All functions and constants imported")
except Exception as e:
    print(f"✗ backend.auth - Import failed: {e}")
    sys.exit(1)

try:
    from backend.models import User, Task
    print("✓ backend.models - User and Task models imported")
except Exception as e:
    print(f"✗ backend.models - Import failed: {e}")
    sys.exit(1)

try:
    from backend.schemas import (
        UserBase,
        UserCreate,
        UserResponse,
        UserLogin,
        Token,
        TokenData
    )
    print("✓ backend.schemas - All user schemas imported")
except Exception as e:
    print(f"✗ backend.schemas - Import failed: {e}")
    sys.exit(1)

try:
    from backend.crud import (
        create_user,
        get_user_by_email,
        get_user_by_username,
        get_user_by_id
    )
    print("✓ backend.crud - All user CRUD functions imported")
except Exception as e:
    print(f"✗ backend.crud - Import failed: {e}")
    sys.exit(1)

try:
    from backend.auth_routes import router
    print("✓ backend.auth_routes - Router imported")
except Exception as e:
    print(f"✗ backend.auth_routes - Import failed: {e}")
    sys.exit(1)

try:
    from backend.main import app
    print("✓ backend.main - FastAPI app imported")
except Exception as e:
    print(f"✗ backend.main - Import failed: {e}")
    sys.exit(1)

print()

# Test 3: Check User model attributes
print("TEST 3: Verifying User model structure")
print("-" * 60)

required_attributes = ['id', 'username', 'email', 'hashed_password', 'is_active', 'created_at', 'updated_at']
missing_attrs = []

for attr in required_attributes:
    if hasattr(User, attr):
        print(f"✓ User.{attr}")
    else:
        print(f"✗ User.{attr} - MISSING!")
        missing_attrs.append(attr)

if missing_attrs:
    print(f"\n✗ User model missing attributes: {', '.join(missing_attrs)}")
    sys.exit(1)

print("\n✓ User model has all required attributes")
print()

# Test 4: Test password hashing
print("TEST 4: Testing password hashing")
print("-" * 60)

test_password = "TestPassword123"
hashed = get_password_hash(test_password)

if verify_password(test_password, hashed):
    print(f"✓ Password hashing works correctly")
else:
    print("✗ Password verification failed")
    sys.exit(1)

if not verify_password("WrongPassword", hashed):
    print(f"✓ Password verification rejects wrong password")
else:
    print("✗ Password verification should reject wrong password")
    sys.exit(1)

print()

# Test 5: Test JWT token creation
print("TEST 5: Testing JWT token creation and verification")
print("-" * 60)

try:
    token = create_access_token(data={"sub": "test@example.com"})
    print(f"✓ Token created successfully")

    token_data = verify_token(token)
    if token_data.email == "test@example.com":
        print(f"✓ Token verification works correctly")
    else:
        print(f"✗ Token data mismatch")
        sys.exit(1)
except Exception as e:
    print(f"✗ Token creation/verification failed: {e}")
    sys.exit(1)

print()

# Test 6: Test Pydantic schema validation
print("TEST 6: Testing Pydantic schema validation")
print("-" * 60)

from pydantic import ValidationError

# Test valid user creation
try:
    valid_user = UserCreate(
        email="test@example.com",
        username="testuser",
        password="password123"
    )
    print("✓ Valid UserCreate schema accepted")
except Exception as e:
    print(f"✗ Valid UserCreate schema rejected: {e}")
    sys.exit(1)

# Test invalid email
try:
    invalid_user = UserCreate(
        email="not-an-email",
        username="testuser",
        password="password123"
    )
    print("✗ Invalid email accepted (should reject)")
    sys.exit(1)
except ValidationError:
    print("✓ Invalid email rejected")

# Test short username
try:
    invalid_user = UserCreate(
        email="test@example.com",
        username="ab",
        password="password123"
    )
    print("✗ Short username accepted (should reject)")
    sys.exit(1)
except ValidationError:
    print("✓ Short username rejected")

# Test short password
try:
    invalid_user = UserCreate(
        email="test@example.com",
        username="testuser",
        password="short"
    )
    print("✗ Short password accepted (should reject)")
    sys.exit(1)
except ValidationError:
    print("✓ Short password rejected")

print()

# Test 7: Check routes in main app
print("TEST 7: Verifying routes in FastAPI app")
print("-" * 60)

routes = [route.path for route in app.routes]

required_routes = [
    '/api/auth/register',
    '/api/auth/login',
    '/api/auth/me'
]

missing_routes = []
for route in required_routes:
    if route in routes:
        print(f"✓ {route}")
    else:
        print(f"✗ {route} - MISSING!")
        missing_routes.append(route)

if missing_routes:
    print(f"\n✗ Missing routes: {', '.join(missing_routes)}")
    print("Available routes:", routes)
    sys.exit(1)

print("\n✓ All authentication routes registered")
print()

# Test 8: Check dependencies in requirements.txt
print("TEST 8: Verifying requirements.txt")
print("-" * 60)

with open('requirements.txt', 'r') as f:
    requirements = f.read()

required_packages = [
    'python-jose',
    'passlib',
    'python-dotenv',
    'fastapi',
    'sqlalchemy',
    'pydantic'
]

missing_packages = []
for package in required_packages:
    if package in requirements:
        print(f"✓ {package}")
    else:
        print(f"✗ {package} - MISSING!")
        missing_packages.append(package)

if missing_packages:
    print(f"\n✗ Missing packages: {', '.join(missing_packages)}")
    sys.exit(1)

print("\n✓ All required packages in requirements.txt")
print()

# Test 9: Check .env.example
print("TEST 9: Verifying .env.example")
print("-" * 60)

with open('.env.example', 'r') as f:
    env_example = f.read()

required_vars = ['DATABASE_URL', 'SECRET_KEY', 'ACCESS_TOKEN_EXPIRE_MINUTES']
missing_vars = []

for var in required_vars:
    if var in env_example:
        print(f"✓ {var}")
    else:
        print(f"✗ {var} - MISSING!")
        missing_vars.append(var)

if missing_vars:
    print(f"\n✗ Missing environment variables: {', '.join(missing_vars)}")
    sys.exit(1)

print("\n✓ All required environment variables in .env.example")
print()

# Final summary
print("=" * 60)
print("FINAL SUMMARY")
print("=" * 60)
print()
print("✓ All files created successfully")
print("✓ All modules import correctly")
print("✓ User model structure is correct")
print("✓ Password hashing works")
print("✓ JWT token creation/verification works")
print("✓ Pydantic validation works")
print("✓ All authentication routes registered")
print("✓ All dependencies listed")
print("✓ Environment variables documented")
print()
print("=" * 60)
print("AUTHENTICATION IMPLEMENTATION SUCCESSFUL!")
print("=" * 60)
print()
print("Next steps:")
print("1. Install dependencies: pip install -r requirements.txt")
print("2. Create .env file: cp .env.example .env")
print("3. Generate secret key: openssl rand -hex 32")
print("4. Add secret key to .env file")
print("5. Create migration: alembic revision --autogenerate -m 'add users table'")
print("6. Apply migration: alembic upgrade head")
print("7. Start server: uvicorn backend.main:app --reload")
print("8. Test endpoints at: http://localhost:8000/docs")
print()
