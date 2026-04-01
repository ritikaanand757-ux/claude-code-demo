# Authentication System Documentation

**Version:** 1.0.0  
**Last Updated:** 2026-04-01

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [JWT Token Structure](#jwt-token-structure)
- [Password Security](#password-security)
- [Token Lifecycle](#token-lifecycle)
- [Implementation Guide](#implementation-guide)
- [Protecting Routes](#protecting-routes)
- [Security Best Practices](#security-best-practices)
- [Testing Authentication](#testing-authentication)
- [Troubleshooting](#troubleshooting)
- [API Reference](#api-reference)

---

## Overview

The Task Manager API uses a modern JWT-based authentication system to secure user data and ensure proper access control. This document provides comprehensive technical details about the authentication architecture, implementation, and best practices.

### Key Features

- **JWT Token Authentication** - Stateless, scalable authentication
- **bcrypt Password Hashing** - Industry-standard password security
- **Token Expiration** - Automatic token invalidation after 30 minutes
- **User Isolation** - Users can only access their own tasks
- **Email & Username Validation** - Input validation at API level
- **Secure Password Storage** - Never store plain-text passwords

### Authentication Flow

```
┌─────────┐                  ┌─────────┐                  ┌──────────┐
│  Client │                  │   API   │                  │ Database │
└────┬────┘                  └────┬────┘                  └────┬─────┘
     │                            │                            │
     │  1. POST /auth/register    │                            │
     ├───────────────────────────>│                            │
     │  {username, email, pass}   │                            │
     │                            │  2. Hash password (bcrypt) │
     │                            │                            │
     │                            │  3. Save user              │
     │                            ├───────────────────────────>│
     │                            │                            │
     │  4. User created (201)     │                            │
     │<───────────────────────────┤                            │
     │                            │                            │
     │  5. POST /auth/login       │                            │
     ├───────────────────────────>│                            │
     │  {username, password}      │                            │
     │                            │  6. Get user by username   │
     │                            ├───────────────────────────>│
     │                            │                            │
     │                            │  7. Verify password hash   │
     │                            │                            │
     │                            │  8. Generate JWT token     │
     │                            │                            │
     │  9. Token + expiry (200)   │                            │
     │<───────────────────────────┤                            │
     │                            │                            │
     │  10. GET /tasks/           │                            │
     │  Authorization: Bearer JWT │                            │
     ├───────────────────────────>│                            │
     │                            │  11. Verify token          │
     │                            │                            │
     │                            │  12. Extract user_id       │
     │                            │                            │
     │                            │  13. Get user's tasks      │
     │                            ├───────────────────────────>│
     │                            │                            │
     │  14. Tasks array (200)     │                            │
     │<───────────────────────────┤                            │
     │                            │                            │
```

---

## Architecture

### Components

The authentication system consists of several key components:

#### 1. User Model (`backend/models.py`)

```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func

class User(Base):
    """
    User model for authentication and authorization.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

**Key Fields:**
- `username` - Unique username (3-50 characters)
- `email` - Unique email address
- `hashed_password` - bcrypt hashed password (never plain text)
- `is_active` - User account status
- `created_at` - Account creation timestamp
- `updated_at` - Last modification timestamp

#### 2. Authentication Schemas (`backend/schemas.py`)

```python
from pydantic import BaseModel, EmailStr, Field, validator
import re

class UserRegister(BaseModel):
    """Schema for user registration"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    
    @validator('username')
    def username_alphanumeric(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username must contain only letters, numbers, and underscores')
        return v

class UserLogin(BaseModel):
    """Schema for user login"""
    username: str
    password: str

class UserResponse(BaseModel):
    """Schema for user response (no password)"""
    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    """Schema for token response"""
    access_token: str
    token_type: str
    expires_in: int
```

#### 3. Password Hashing (`backend/auth.py`)

```python
from passlib.context import CryptContext

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Hash a plain text password using bcrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password string
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a hashed password.
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password from database
        
    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)
```

**Security Features:**
- Uses bcrypt algorithm (industry standard)
- Automatic salt generation per password
- Configurable work factor (default: 12 rounds)
- Protection against timing attacks

#### 4. JWT Token Generation (`backend/auth.py`)

```python
from datetime import datetime, timedelta
from jose import JWTError, jwt
from typing import Optional
import os

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Dictionary containing claims to encode (e.g., {"sub": username})
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt

def decode_token(token: str) -> dict:
    """
    Decode and verify a JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token payload
        
    Raises:
        JWTError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise
```

#### 5. Authentication Dependency (`backend/auth.py`)

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

# Security scheme for Swagger UI
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get the current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Bearer token credentials
        db: Database session
        
    Returns:
        User object for the authenticated user
        
    Raises:
        HTTPException: 401 if token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = decode_token(token)
        username: str = payload.get("sub")
        
        if username is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    # Get user from database
    user = db.query(User).filter(User.username == username).first()
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    return user
```

---

## JWT Token Structure

### Token Format

A JWT token consists of three parts separated by dots:

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huIiwiZXhwIjoxNzA5MzE2MDAwfQ.signature
└─────────── header ────────────┘ └──────────── payload ──────────┘ └── signature ──┘
```

### Token Components

#### 1. Header

```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

- `alg` - Algorithm used for signing (HMAC SHA-256)
- `typ` - Token type (JWT)

#### 2. Payload (Claims)

```json
{
  "sub": "john",
  "exp": 1709316000
}
```

**Standard Claims:**
- `sub` (Subject) - Username of the authenticated user
- `exp` (Expiration) - Unix timestamp when token expires
- `iat` (Issued At) - Unix timestamp when token was issued (optional)

**Custom Claims (Optional):**
```json
{
  "sub": "john",
  "exp": 1709316000,
  "user_id": 1,
  "email": "john@example.com",
  "roles": ["user"]
}
```

#### 3. Signature

The signature is created by:
```
HMACSHA256(
  base64UrlEncode(header) + "." + base64UrlEncode(payload),
  SECRET_KEY
)
```

This ensures:
- **Integrity** - Token hasn't been tampered with
- **Authenticity** - Token was issued by your server

### Token Verification Process

```python
def verify_token(token: str) -> bool:
    """
    Verify token validity
    """
    try:
        # 1. Decode and verify signature
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        
        # 2. Check expiration
        exp = payload.get("exp")
        if exp is None or datetime.utcnow().timestamp() > exp:
            return False
        
        # 3. Validate subject (username)
        sub = payload.get("sub")
        if sub is None:
            return False
        
        return True
        
    except JWTError:
        return False
```

---

## Password Security

### Hashing Strategy

The application uses **bcrypt** for password hashing, which is specifically designed for password storage.

#### Why bcrypt?

1. **Adaptive** - Configurable work factor (cost)
2. **Salted** - Automatic unique salt per password
3. **Slow** - Intentionally slow to prevent brute-force attacks
4. **Battle-tested** - Industry standard since 1999

#### Hash Example

```python
# Plain password (never stored)
password = "securepass123"

# Hashed password (stored in database)
hashed = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyWpQkn2nS3e"
#        │  │  │                                                      │
#        │  │  │                                                      └─ Hash (31 chars)
#        │  │  └─────────────────────────── Salt (22 chars)
#        │  └─ Cost factor (12 = 2^12 = 4096 rounds)
#        └─ Version (2b = current bcrypt)
```

#### Work Factor

The work factor determines computational cost:

| Cost | Iterations | Time (approx) |
|------|-----------|---------------|
| 10   | 1,024     | ~0.1s         |
| 11   | 2,048     | ~0.2s         |
| 12   | 4,096     | ~0.4s         |
| 13   | 8,192     | ~0.8s         |
| 14   | 16,384    | ~1.6s         |

**Recommendation:** Cost 12 provides good security with acceptable performance.

### Password Requirements

**Minimum Requirements:**
- Length: 8 characters minimum
- No maximum length (bcrypt handles up to 72 bytes)

**Recommended Requirements:**
- Length: 12+ characters
- Mix of uppercase and lowercase letters
- Include numbers
- Include special characters
- Not in common password dictionary

**Example Validation:**
```python
from pydantic import BaseModel, Field, validator
import re

class UserRegister(BaseModel):
    password: str = Field(..., min_length=8)
    
    @validator('password')
    def password_strength(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        
        # Check for uppercase
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        
        # Check for lowercase
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        
        # Check for digit
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        
        # Check for special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        
        return v
```

### Security Considerations

1. **Never Log Passwords**
   ```python
   # ❌ WRONG
   logger.info(f"User login attempt: {username} with password {password}")
   
   # ✅ CORRECT
   logger.info(f"User login attempt: {username}")
   ```

2. **Never Return Passwords**
   ```python
   # ❌ WRONG
   return {
       "id": user.id,
       "username": user.username,
       "password": user.hashed_password  # Never expose!
   }
   
   # ✅ CORRECT
   return {
       "id": user.id,
       "username": user.username,
       "email": user.email
   }
   ```

3. **Use Constant-Time Comparison**
   ```python
   # bcrypt's verify() already uses constant-time comparison
   # This prevents timing attacks
   is_valid = verify_password(plain_password, hashed_password)
   ```

---

## Token Lifecycle

### Creation

```python
# 1. User logs in
# 2. Credentials verified
# 3. Token created

from datetime import timedelta

token = create_access_token(
    data={"sub": user.username},
    expires_delta=timedelta(minutes=30)
)

# Token contains:
# - username (sub claim)
# - expiration time (exp claim)
# - signature
```

### Usage

```python
# 1. Client includes token in Authorization header
# Authorization: Bearer <token>

# 2. API extracts and verifies token
token = request.headers.get("Authorization").replace("Bearer ", "")
payload = decode_token(token)

# 3. Extract user information
username = payload.get("sub")
user = get_user_by_username(username)

# 4. User authenticated - proceed with request
```

### Expiration

```python
# Tokens automatically expire after configured time
# Default: 30 minutes

# Check expiration
exp_timestamp = payload.get("exp")
current_timestamp = datetime.utcnow().timestamp()

if current_timestamp > exp_timestamp:
    # Token expired
    raise HTTPException(
        status_code=401,
        detail="Token has expired"
    )
```

### Refresh Strategy

**Current Implementation:** No refresh tokens

**Option 1 - Re-login:**
```
User's token expires → User logs in again → New token issued
```

**Option 2 - Refresh Tokens (Future Enhancement):**
```
User's token expires → Use refresh token → New access token issued
```

**Refresh Token Flow (Future):**
```python
# Login response includes both tokens
{
    "access_token": "short-lived-token",  # 30 minutes
    "refresh_token": "long-lived-token",  # 7 days
    "token_type": "bearer",
    "expires_in": 1800
}

# When access token expires, use refresh token
POST /api/auth/refresh
{
    "refresh_token": "long-lived-token"
}

# Response: New access token
{
    "access_token": "new-short-lived-token",
    "token_type": "bearer",
    "expires_in": 1800
}
```

---

## Implementation Guide

### Step 1: Install Dependencies

Add to `requirements.txt`:
```
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
```

Install:
```bash
pip install python-jose[cryptography] passlib[bcrypt] python-multipart
```

### Step 2: Set Up Environment Variables

Create or update `.env`:
```bash
# Authentication Configuration
SECRET_KEY=your-super-secret-key-at-least-32-characters-long
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Generate secure secret key:
```bash
# Option 1: Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Option 2: OpenSSL
openssl rand -hex 32

# Option 3: Password manager generated key
# Use a password manager to generate a 32+ character random string
```

### Step 3: Create User Model

`backend/models.py`:
```python
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

### Step 4: Create Database Migration

```bash
# Create migration
alembic revision --autogenerate -m "add users table"

# Review migration file in alembic/versions/

# Apply migration
alembic upgrade head
```

### Step 5: Create Authentication Schemas

`backend/schemas.py`:
```python
from pydantic import BaseModel, EmailStr, Field

class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
```

### Step 6: Create Authentication Utilities

`backend/auth.py`:
```python
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt

def decode_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
```

### Step 7: Create Authentication Routes

`backend/routes.py` (add auth router):
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend import schemas, models, auth
from backend.database import get_db

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

@auth_router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: schemas.UserRegister, db: Session = Depends(get_db)):
    """Register a new user"""
    
    # Check if username exists
    existing_user = db.query(models.User).filter(models.User.username == user.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already registered"
        )
    
    # Check if email exists
    existing_email = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = auth.hash_password(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@auth_router.post("/login", response_model=schemas.TokenResponse)
def login(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    """Login and receive JWT token"""
    
    # Get user
    user = db.query(models.User).filter(models.User.username == credentials.username).first()
    
    # Verify credentials
    if not user or not auth.verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Create access token
    access_token = auth.create_access_token(data={"sub": user.username})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": auth.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@auth_router.get("/me", response_model=schemas.UserResponse)
def get_current_user_info(current_user: models.User = Depends(auth.get_current_user)):
    """Get current authenticated user"""
    return current_user
```

### Step 8: Update Main Application

`backend/main.py`:
```python
from backend.routes import router, auth_router

app = FastAPI(title="Task Manager API")

# Include routers
app.include_router(auth_router, prefix="/api")
app.include_router(router, prefix="/api")
```

---

## Protecting Routes

### Method 1: Dependency Injection

Protect individual routes using the `get_current_user` dependency:

```python
from fastapi import Depends
from backend.auth import get_current_user
from backend.models import User

@router.get("/tasks/")
def get_tasks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get tasks for authenticated user"""
    # current_user is automatically injected
    tasks = db.query(Task).filter(Task.user_id == current_user.id).all()
    return tasks

@router.post("/tasks/")
def create_task(
    task: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create task for authenticated user"""
    db_task = Task(**task.dict(), user_id=current_user.id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task
```

### Method 2: Router-Level Protection

Protect all routes in a router:

```python
from fastapi import APIRouter, Depends

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"],
    dependencies=[Depends(get_current_user)]  # Apply to all routes
)

@router.get("/")
def get_tasks(db: Session = Depends(get_db)):
    """This route is automatically protected"""
    # Access current user from context if needed
    pass
```

### Method 3: Middleware (Global Protection)

Protect all routes except explicitly excluded ones:

```python
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Paths that don't require authentication
        public_paths = [
            "/api/auth/register",
            "/api/auth/login",
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json"
        ]
        
        if request.url.path in public_paths:
            return await call_next(request)
        
        # Verify token for protected paths
        auth_header = request.headers.get("Authorization")
        
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid token")
        
        token = auth_header.replace("Bearer ", "")
        
        try:
            payload = decode_token(token)
            request.state.user = payload.get("sub")
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        return await call_next(request)

# Add middleware to app
app.add_middleware(AuthMiddleware)
```

---

## Security Best Practices

### 1. Environment Variables

**Never hardcode secrets:**
```python
# ❌ WRONG
SECRET_KEY = "my-secret-key-12345"

# ✅ CORRECT
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable must be set")
```

### 2. HTTPS in Production

**Always use HTTPS:**
- JWT tokens in HTTP headers can be intercepted
- Use TLS/SSL certificates (Let's Encrypt)
- Redirect HTTP to HTTPS

```python
# Enforce HTTPS in production
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

if os.getenv("ENV") == "production":
    app.add_middleware(HTTPSRedirectMiddleware)
```

### 3. CORS Configuration

**Restrict allowed origins:**
```python
from fastapi.middleware.cors import CORSMiddleware

# ❌ WRONG (Development only)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins!
    allow_credentials=True
)

# ✅ CORRECT (Production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://yourdomain.com",
        "https://app.yourdomain.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"]
)
```

### 4. Rate Limiting

**Prevent brute-force attacks:**
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@auth_router.post("/login")
@limiter.limit("5/minute")  # Max 5 login attempts per minute
def login(request: Request, credentials: UserLogin, db: Session = Depends(get_db)):
    # Login logic
    pass
```

### 5. Token Storage (Client-Side)

**Best Practices:**

| Storage Method | Security | Pros | Cons |
|----------------|----------|------|------|
| **localStorage** | Low | Persists across tabs, Simple | Vulnerable to XSS |
| **sessionStorage** | Low | Cleared on tab close | Vulnerable to XSS |
| **Memory** | Medium | Not persisted | Lost on refresh |
| **httpOnly Cookie** | **High** | Immune to XSS | More complex, CSRF protection needed |

**Recommended for SPAs:**
```javascript
// Store token in memory (most secure for SPAs)
let accessToken = null;

async function login(username, password) {
  const response = await fetch('/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
  
  const data = await response.json();
  accessToken = data.access_token;  // Store in memory
  
  // Set token expiration warning
  setTimeout(() => {
    alert('Session expiring soon. Please refresh.');
  }, (data.expires_in - 60) * 1000);  // 1 minute before expiry
}

async function apiCall(endpoint) {
  const response = await fetch(endpoint, {
    headers: {
      'Authorization': `Bearer ${accessToken}`
    }
  });
  
  if (response.status === 401) {
    // Token expired - redirect to login
    window.location.href = '/login';
  }
  
  return response.json();
}
```

### 6. Input Validation

**Validate all inputs:**
```python
from pydantic import BaseModel, EmailStr, Field, validator
import re

class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    
    @validator('username')
    def username_alphanumeric(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username must contain only letters, numbers, and underscores')
        return v.lower()
    
    @validator('email')
    def email_lowercase(cls, v):
        return v.lower()
```

### 7. Error Messages

**Don't leak information:**
```python
# ❌ WRONG
if not user:
    raise HTTPException(status_code=404, detail="User not found")
if not verify_password(password, user.hashed_password):
    raise HTTPException(status_code=401, detail="Incorrect password")

# ✅ CORRECT
if not user or not verify_password(password, user.hashed_password):
    raise HTTPException(
        status_code=401,
        detail="Incorrect username or password"  # Generic message
    )
```

### 8. Logging

**Log authentication events:**
```python
import logging

logger = logging.getLogger(__name__)

@auth_router.post("/login")
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    logger.info(f"Login attempt for user: {credentials.username}")
    
    user = db.query(User).filter(User.username == credentials.username).first()
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        logger.warning(f"Failed login attempt for user: {credentials.username}")
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    logger.info(f"Successful login for user: {credentials.username}")
    
    # Create token
    access_token = create_access_token(data={"sub": user.username})
    
    return {"access_token": access_token, "token_type": "bearer"}
```

---

## Testing Authentication

### Unit Tests

`tests/test_auth.py`:
```python
import pytest
from backend.auth import hash_password, verify_password, create_access_token, decode_token
from jose import JWTError

class TestPasswordHashing:
    def test_hash_password(self):
        """Test password hashing"""
        password = "testpassword123"
        hashed = hash_password(password)
        
        assert hashed != password
        assert hashed.startswith("$2b$")  # bcrypt format
    
    def test_verify_password_correct(self):
        """Test password verification with correct password"""
        password = "testpassword123"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password"""
        password = "testpassword123"
        hashed = hash_password(password)
        
        assert verify_password("wrongpassword", hashed) is False

class TestJWT:
    def test_create_token(self):
        """Test JWT token creation"""
        token = create_access_token(data={"sub": "testuser"})
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_decode_token(self):
        """Test JWT token decoding"""
        username = "testuser"
        token = create_access_token(data={"sub": username})
        
        payload = decode_token(token)
        
        assert payload["sub"] == username
        assert "exp" in payload
    
    def test_decode_invalid_token(self):
        """Test decoding invalid token"""
        with pytest.raises(JWTError):
            decode_token("invalid.token.here")
```

### Integration Tests

`tests/test_auth_api.py`:
```python
import pytest
from fastapi.testclient import TestClient

class TestAuthEndpoints:
    def test_register_user(self, client: TestClient):
        """Test user registration"""
        response = client.post("/api/auth/register", json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123"
        })
        
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert "hashed_password" not in data  # Password not exposed
    
    def test_register_duplicate_username(self, client: TestClient):
        """Test registration with duplicate username"""
        # Register first user
        client.post("/api/auth/register", json={
            "username": "testuser",
            "email": "test1@example.com",
            "password": "testpass123"
        })
        
        # Try to register with same username
        response = client.post("/api/auth/register", json={
            "username": "testuser",
            "email": "test2@example.com",
            "password": "testpass123"
        })
        
        assert response.status_code == 409
        assert "already registered" in response.json()["detail"].lower()
    
    def test_login_success(self, client: TestClient):
        """Test successful login"""
        # Register user
        client.post("/api/auth/register", json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123"
        })
        
        # Login
        response = client.post("/api/auth/login", json={
            "username": "testuser",
            "password": "testpass123"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] == 1800  # 30 minutes
    
    def test_login_wrong_password(self, client: TestClient):
        """Test login with wrong password"""
        # Register user
        client.post("/api/auth/register", json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123"
        })
        
        # Login with wrong password
        response = client.post("/api/auth/login", json={
            "username": "testuser",
            "password": "wrongpassword"
        })
        
        assert response.status_code == 401
    
    def test_get_current_user(self, client: TestClient):
        """Test getting current user with valid token"""
        # Register and login
        client.post("/api/auth/register", json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123"
        })
        
        login_response = client.post("/api/auth/login", json={
            "username": "testuser",
            "password": "testpass123"
        })
        
        token = login_response.json()["access_token"]
        
        # Get current user
        response = client.get("/api/auth/me", headers={
            "Authorization": f"Bearer {token}"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
    
    def test_protected_route_without_token(self, client: TestClient):
        """Test accessing protected route without token"""
        response = client.get("/api/tasks/")
        
        assert response.status_code == 401
    
    def test_protected_route_with_invalid_token(self, client: TestClient):
        """Test accessing protected route with invalid token"""
        response = client.get("/api/tasks/", headers={
            "Authorization": "Bearer invalid.token.here"
        })
        
        assert response.status_code == 401
```

### Running Tests

```bash
# Run all authentication tests
pytest tests/test_auth.py tests/test_auth_api.py -v

# Run with coverage
pytest tests/test_auth.py tests/test_auth_api.py --cov=backend.auth --cov-report=html

# Run specific test
pytest tests/test_auth_api.py::TestAuthEndpoints::test_login_success -v
```

---

## Troubleshooting

### Common Issues

#### 1. "SECRET_KEY environment variable must be set"

**Problem:** Missing SECRET_KEY in environment variables

**Solution:**
```bash
# Add to .env file
SECRET_KEY=your-super-secret-key-at-least-32-characters-long

# Or export directly
export SECRET_KEY="your-super-secret-key-at-least-32-characters-long"
```

#### 2. "Could not validate credentials"

**Problem:** Invalid or expired JWT token

**Possible Causes:**
- Token has expired (default: 30 minutes)
- Token format is incorrect
- SECRET_KEY changed after token was issued
- Token malformed (missing "Bearer " prefix)

**Solutions:**
```bash
# 1. Check token format
Authorization: Bearer <token>  # Must have "Bearer " prefix

# 2. Login again to get new token
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "password": "securepass123"}'

# 3. Verify SECRET_KEY is consistent
echo $SECRET_KEY
```

#### 3. "Username already registered"

**Problem:** Attempting to register with existing username

**Solution:**
```bash
# Choose a different username
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john2",  # Different username
    "email": "john2@example.com",
    "password": "securepass123"
  }'
```

#### 4. "Incorrect username or password"

**Problem:** Login credentials don't match

**Solutions:**
1. Verify username spelling (case-sensitive)
2. Verify password spelling
3. Reset password if forgotten (implement password reset endpoint)

#### 5. bcrypt ImportError

**Problem:** `ImportError: cannot import name 'bcrypt' from 'passlib'`

**Solution:**
```bash
# Install bcrypt dependency
pip install passlib[bcrypt]

# Or install bcrypt separately
pip install bcrypt
```

#### 6. jose ImportError

**Problem:** `ImportError: No module named 'jose'`

**Solution:**
```bash
# Install python-jose with cryptography
pip install python-jose[cryptography]
```

### Debugging Tips

#### 1. Enable Debug Logging

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
```

#### 2. Decode JWT Token (Debugging)

```bash
# Decode JWT payload (without verification)
echo "eyJhbGc..." | cut -d. -f2 | base64 -d | jq

# Or use jwt.io website
# Copy token to https://jwt.io for inspection
```

#### 3. Test Token Manually

```python
from backend.auth import create_access_token, decode_token

# Create test token
token = create_access_token(data={"sub": "testuser"})
print(f"Token: {token}")

# Decode token
payload = decode_token(token)
print(f"Payload: {payload}")
```

#### 4. Verify Password Hash

```python
from backend.auth import hash_password, verify_password

password = "testpass123"
hashed = hash_password(password)

print(f"Password: {password}")
print(f"Hashed: {hashed}")
print(f"Verify: {verify_password(password, hashed)}")
```

---

## API Reference

### Endpoints Summary

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/register` | Register new user | No |
| POST | `/api/auth/login` | Login and get token | No |
| GET | `/api/auth/me` | Get current user | Yes |

### Error Codes

| Status | Description | Example |
|--------|-------------|---------|
| 200 | Success | Login successful |
| 201 | Created | User registered |
| 401 | Unauthorized | Invalid credentials or token |
| 403 | Forbidden | User account inactive |
| 409 | Conflict | Username/email already exists |
| 422 | Validation Error | Invalid email format |
| 500 | Server Error | Database connection failed |

### Rate Limits (Recommended)

| Endpoint | Limit | Window |
|----------|-------|--------|
| `/auth/register` | 3 requests | 1 hour per IP |
| `/auth/login` | 5 requests | 1 minute per IP |
| `/auth/me` | 100 requests | 1 minute per user |

---

## Additional Resources

### Documentation

- **FastAPI Security**: https://fastapi.tiangolo.com/tutorial/security/
- **JWT.io**: https://jwt.io/ (JWT debugging tool)
- **python-jose**: https://python-jose.readthedocs.io/
- **passlib**: https://passlib.readthedocs.io/

### Security Resources

- **OWASP Authentication Cheatsheet**: https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
- **JWT Best Practices**: https://datatracker.ietf.org/doc/html/rfc8725
- **bcrypt**: https://en.wikipedia.org/wiki/Bcrypt

### Tools

- **jwt.io** - Decode and verify JWT tokens
- **Postman** - API testing with authentication
- **curl** - Command-line API testing

---

**Last Updated:** 2026-04-01  
**Version:** 1.0.0  
**Author:** Task Manager API Team
