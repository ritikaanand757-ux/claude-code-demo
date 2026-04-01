"""
Authentication routes for Task Manager API.

This module defines authentication-related API endpoints including
user registration, login, and current user retrieval.
"""

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend import crud
from backend.auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    get_current_user,
    verify_password,
)
from backend.database import get_db
from backend.models import User
from backend.schemas import Token, UserCreate, UserLogin, UserResponse

router = APIRouter()


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.

    Args:
        user: User registration data (email, username, password)
        db: Database session

    Returns:
        Created user information (excluding password)

    Raises:
        HTTPException: 409 if email or username already exists
    """
    # Check if email already exists
    existing_user = crud.get_user_by_email(db=db, email=user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    # Check if username already exists
    existing_username = crud.get_user_by_username(db=db, username=user.username)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken",
        )

    # Create new user
    db_user = crud.create_user(db=db, user=user)
    return db_user


@router.post("/login", response_model=Token)
def login_user(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user and return JWT token.

    Args:
        user_credentials: User login credentials (email, password)
        db: Database session

    Returns:
        JWT access token and token type

    Raises:
        HTTPException: 401 if credentials are invalid
    """
    # Get user by email
    user = crud.get_user_by_email(db=db, email=user_credentials.email)

    # Verify user exists and password is correct
    if not user or not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user account",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user information.

    This endpoint requires authentication via JWT token.

    Args:
        current_user: Current authenticated user (injected by dependency)

    Returns:
        Current user information (excluding password)
    """
    return current_user
