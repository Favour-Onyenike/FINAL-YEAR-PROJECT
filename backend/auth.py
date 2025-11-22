"""
AUTHENTICATION MODULE
=====================
This module handles all security and authentication logic:
- Password hashing (bcrypt)
- JWT token generation
- JWT token verification
- User authentication checks

WHAT HAPPENS HERE:
1. Passwords are hashed before saving to database (bcrypt)
2. Tokens are generated when user logs in (JWT)
3. Endpoints check tokens to verify user is logged in
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt  # JWT token library
import bcrypt  # Password hashing library
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import User
import os

# =============================================================================
# SECURITY CONFIGURATION
# =============================================================================

# Secret key used to sign JWT tokens
# In production, this should be a long random string from environment variables
# Currently defaults to a placeholder (CHANGE THIS IN PRODUCTION!)
# 
# How to set in production:
# export JWT_SECRET_KEY="your-super-secret-long-random-string-here"
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")

# Algorithm used to sign JWT tokens
# HS256 = HMAC with SHA-256 (industry standard)
ALGORITHM = "HS256"

# How long tokens last before expiring
# 60 * 24 * 7 = 60 minutes * 24 hours * 7 days = 1 week
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7

# Security scheme for FastAPI
# Tells FastAPI to expect "Bearer <token>" in Authorization header
security = HTTPBearer()

# =============================================================================
# PASSWORD HASHING FUNCTIONS
# =============================================================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a bcrypt hash.
    
    THIS IS USED FOR: Login (checking if password matches stored hash)
    
    PARAMETERS:
    - plain_password: Password user typed in login form
    - hashed_password: Password hash stored in database
    
    RETURNS: True if password matches, False otherwise
    
    HOW IT WORKS:
    1. Convert plain password to bytes (bcrypt needs bytes, not strings)
    2. Check if password is longer than 72 chars (bcrypt limit)
    3. Use bcrypt to verify: Does the hash match this password?
    4. Return True or False
    """
    # Convert password string to bytes (UTF-8 encoding)
    password_bytes = plain_password.encode('utf-8')
    
    # Bcrypt limitation: Can only hash passwords up to 72 bytes
    # Truncate if longer to prevent errors
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    
    # bcrypt.checkpw returns True if password matches hash, False otherwise
    # Convert hashed_password to bytes too (it's stored as string in DB)
    return bcrypt.checkpw(password_bytes, hashed_password.encode('utf-8'))

def get_password_hash(password: str) -> str:
    """
    Hash a plain text password using bcrypt.
    
    THIS IS USED FOR: Registration (storing password securely)
    
    PARAMETERS:
    - password: Plain text password from registration form
    
    RETURNS: Hashed password string (safe to store in database)
    
    HOW IT WORKS:
    1. Convert password to bytes
    2. Generate a salt (random string added to password before hashing)
    3. Hash password + salt using bcrypt
    4. Return the hash as a string
    
    WHY BCRYPT?
    - Bcrypt is SLOW on purpose (prevents brute force attacks)
    - If attacker steals hashes, it takes forever to crack them
    - Even with a supercomputer, each guess takes real time
    """
    # Convert password string to bytes
    password_bytes = password.encode('utf-8')
    
    # Truncate if longer than 72 bytes (bcrypt limit)
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    
    # bcrypt.hashpw does the actual hashing
    # bcrypt.gensalt() generates a random salt (default 12 rounds of hashing)
    # Returns bytes, so .decode('utf-8') converts back to string for storage
    return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode('utf-8')

# =============================================================================
# JWT TOKEN FUNCTIONS
# =============================================================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create a JWT token for a user.
    
    THIS IS USED FOR: Login (giving user a token to stay logged in)
    
    PARAMETERS:
    - data: Dictionary with info to encode in token (usually {"userId": 123})
    - expires_delta: How long until token expires (optional, uses default if None)
    
    RETURNS: JWT token string (send this to frontend)
    
    HOW IT WORKS:
    1. Copy the data dict (don't modify original)
    2. Calculate expiration time
    3. Add expiration time to the token data
    4. Sign the token using SECRET_KEY
    5. Return the signed token
    """
    # Make a copy of data so we don't modify the original dict
    to_encode = data.copy()
    
    # Calculate expiration time
    if expires_delta:
        # If custom expiration provided, use it
        expire = datetime.utcnow() + expires_delta
    else:
        # Otherwise use default (1 week)
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Add expiration time to token data
    # "exp" is the JWT standard field for expiration
    to_encode.update({"exp": expire})
    
    # Encode the data into a JWT token
    # jwt.encode(data, secret_key, algorithm)
    # Returns a token string that can be verified using SECRET_KEY
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt

# =============================================================================
# JWT VERIFICATION FUNCTION
# =============================================================================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Verify JWT token and get the current logged-in user.
    
    THIS IS USED FOR: Protected endpoints (to check if user is logged in)
    
    PARAMETERS:
    - credentials: Authorization header info (provided by FastAPI's HTTPBearer)
    - db: Database session (provided by FastAPI Depends)
    
    RETURNS: User object if token is valid, raises exception otherwise
    
    HOW IT WORKS:
    1. Extract token from "Authorization: Bearer <token>" header
    2. Decode and verify the JWT token using SECRET_KEY
    3. Extract userId from token
    4. Look up that user in database
    5. Return user object if found
    6. Raise 401 error if token invalid or user not found
    
    EXAMPLE USAGE:
    @app.get("/api/auth/me")
    def get_profile(current_user: User = Depends(get_current_user)):
        return current_user  # current_user is automatically verified!
    """
    
    # Error to raise if credentials are invalid
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,  # 401 = Not Authorized
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},  # Tell client to try Bearer token
    )
    
    try:
        # Extract the token from the credentials
        # credentials.credentials contains the token part of "Bearer <token>"
        token = credentials.credentials
        
        # Decode the JWT token using SECRET_KEY
        # jwt.decode verifies the signature and checks expiration
        # If token is invalid or expired, raises JWTError
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Extract userId from token payload
        # We stored userId in create_access_token
        user_id = payload.get("userId")
        
        # Check if userId was found in token
        if user_id is None:
            raise credentials_exception
            
    except JWTError:
        # If any JWT error occurs (invalid, expired, etc.)
        raise credentials_exception
    
    # Query database for the user with this ID
    user = db.query(User).filter(User.id == user_id).first()
    
    # Check if user exists
    if user is None:
        raise credentials_exception
    
    # Return the user object
    # If we got here, token is valid and user exists
    return user
