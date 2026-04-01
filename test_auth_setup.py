"""
Quick test to verify authentication setup is correct
"""
import os
import sys

# Set a dummy SECRET_KEY for testing imports
os.environ['SECRET_KEY'] = 'test-secret-key-for-verification-only-32-chars-long'
os.environ['DATABASE_URL'] = 'postgresql://postgres:postgres@localhost:5432/taskmanager_db'

sys.path.insert(0, '.')

print("Testing authentication system setup...\n")

# Test 1: Import auth utilities
try:
    from backend.auth import get_password_hash, verify_password, create_access_token, verify_token
    print("✓ backend.auth imports successful")
except Exception as e:
    print(f"✗ backend.auth import error: {e}")
    sys.exit(1)

# Test 2: Import models
try:
    from backend.models import User, Task
    print("✓ backend.models imports successful (User and Task)")
except Exception as e:
    print(f"✗ backend.models import error: {e}")
    sys.exit(1)

# Test 3: Import schemas
try:
    from backend.schemas import UserCreate, UserResponse, Token, UserLogin, TokenData
    print("✓ backend.schemas imports successful (User and Auth schemas)")
except Exception as e:
    print(f"✗ backend.schemas import error: {e}")
    sys.exit(1)

# Test 4: Import CRUD operations
try:
    from backend.crud import create_user, get_user_by_email, get_user_by_username, get_user_by_id
    print("✓ backend.crud imports successful (User operations)")
except Exception as e:
    print(f"✗ backend.crud import error: {e}")
    sys.exit(1)

# Test 5: Import auth routes
try:
    from backend.auth_routes import router
    print("✓ backend.auth_routes imports successful")
except Exception as e:
    print(f"✗ backend.auth_routes import error: {e}")
    sys.exit(1)

# Test 6: Import main app
try:
    from backend.main import app
    print("✓ backend.main imports successful")
except Exception as e:
    print(f"✗ backend.main import error: {e}")
    sys.exit(1)

# Test 7: Password hashing
try:
    password = "testpassword123"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed), "Password verification failed"
    assert not verify_password("wrongpassword", hashed), "Password should not verify with wrong password"
    print("✓ Password hashing and verification working")
except Exception as e:
    print(f"✗ Password hashing error: {e}")
    sys.exit(1)

# Test 8: JWT token creation
try:
    token = create_access_token(data={"sub": "test@example.com"})
    assert token, "Token creation failed"
    assert isinstance(token, str), "Token should be a string"
    print("✓ JWT token creation working")
except Exception as e:
    print(f"✗ JWT token creation error: {e}")
    sys.exit(1)

# Test 9: Check User model attributes
try:
    user_attrs = ['id', 'username', 'email', 'hashed_password', 'is_active', 'created_at', 'updated_at']
    for attr in user_attrs:
        assert hasattr(User, attr), f"User model missing attribute: {attr}"
    print("✓ User model has all required attributes")
except Exception as e:
    print(f"✗ User model error: {e}")
    sys.exit(1)

# Test 10: Check UserCreate schema validation
try:
    from pydantic import ValidationError
    
    # Valid user
    valid_user = UserCreate(
        email="test@example.com",
        username="testuser",
        password="password123"
    )
    assert valid_user.email == "test@example.com"
    
    # Test email validation
    try:
        invalid_user = UserCreate(
            email="not-an-email",
            username="testuser",
            password="password123"
        )
        print("✗ Email validation not working")
        sys.exit(1)
    except ValidationError:
        pass  # Expected to fail
    
    # Test username length validation
    try:
        invalid_user = UserCreate(
            email="test@example.com",
            username="ab",  # Too short
            password="password123"
        )
        print("✗ Username length validation not working")
        sys.exit(1)
    except ValidationError:
        pass  # Expected to fail
    
    # Test password length validation
    try:
        invalid_user = UserCreate(
            email="test@example.com",
            username="testuser",
            password="short"  # Too short
        )
        print("✗ Password length validation not working")
        sys.exit(1)
    except ValidationError:
        pass  # Expected to fail
    
    print("✓ Pydantic schema validation working correctly")
except Exception as e:
    print(f"✗ Schema validation error: {e}")
    sys.exit(1)

print("\n" + "="*50)
print("All authentication setup tests passed!")
print("="*50)
print("\nAuthentication system is ready to use.")
print("\nNext steps:")
print("1. Create a .env file with SECRET_KEY (use: openssl rand -hex 32)")
print("2. Run database migration: alembic revision --autogenerate -m 'add users table'")
print("3. Apply migration: alembic upgrade head")
print("4. Start the server: uvicorn backend.main:app --reload")
