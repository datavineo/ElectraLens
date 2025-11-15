"""
Authentication configuration and JWT utilities for production-ready security.
"""
import os
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

logger = logging.getLogger(__name__)

# Security configuration
class AuthConfig:
    # Generate a secure secret key for production
    SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    REFRESH_TOKEN_EXPIRE_DAYS = 7
    
    # Password hashing
    PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    # Security bearer for JWT tokens
    SECURITY = HTTPBearer()

# Authentication utilities
class AuthUtils:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a plain password against its hash."""
        return AuthConfig.PWD_CONTEXT.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password for storage."""
        return AuthConfig.PWD_CONTEXT.hash(password)
    
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=AuthConfig.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        })
        
        encoded_jwt = jwt.encode(to_encode, AuthConfig.SECRET_KEY, algorithm=AuthConfig.ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: Dict[str, Any]) -> str:
        """Create a JWT refresh token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=AuthConfig.REFRESH_TOKEN_EXPIRE_DAYS)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        })
        
        encoded_jwt = jwt.encode(to_encode, AuthConfig.SECRET_KEY, algorithm=AuthConfig.ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(token, AuthConfig.SECRET_KEY, algorithms=[AuthConfig.ALGORITHM])
            
            # Verify token type
            if payload.get("type") != token_type:
                return None
                
            # Check expiration
            exp = payload.get("exp")
            if exp is None or datetime.fromtimestamp(exp) < datetime.utcnow():
                return None
                
            return payload
            
        except JWTError as e:
            logger.warning(f"JWT verification failed: {e}")
            return None
    
    @staticmethod
    def get_current_user_from_token(credentials: HTTPAuthorizationCredentials = Depends(AuthConfig.SECURITY)) -> Dict[str, Any]:
        """Extract current user from JWT token."""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            payload = AuthUtils.verify_token(credentials.credentials)
            if payload is None:
                raise credentials_exception
                
            username = payload.get("sub")
            if username is None:
                raise credentials_exception
                
            return {
                "username": username,
                "user_id": payload.get("user_id"),
                "role": payload.get("role"),
                "full_name": payload.get("full_name")
            }
            
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            raise credentials_exception

# Role-based access control
class RoleChecker:
    def __init__(self, allowed_roles: Optional[list[str]] = None):
        self.allowed_roles = allowed_roles or ["viewer", "admin"]
    
    def __call__(self, current_user: Dict[str, Any] = Depends(AuthUtils.get_current_user_from_token)) -> Dict[str, Any]:
        user_role = current_user.get("role", "viewer")
        
        if user_role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted"
            )
        
        return current_user

# Pre-defined role checkers
require_admin = RoleChecker(["admin"])
require_viewer_or_admin = RoleChecker(["viewer", "admin"])

# Password validation
class PasswordValidator:
    @staticmethod
    def validate_password(password: str) -> tuple[bool, str]:
        """Validate password strength."""
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if len(password) > 128:
            return False, "Password must be less than 128 characters"
        
        # Check for at least one digit, one letter
        has_digit = any(c.isdigit() for c in password)
        has_letter = any(c.isalpha() for c in password)
        
        if not (has_digit and has_letter):
            return False, "Password must contain at least one letter and one number"
        
        return True, "Password is valid"

# Environment variable setup helper
def setup_environment_variables():
    """Setup required environment variables if not present."""
    if not os.getenv("JWT_SECRET_KEY"):
        secret_key = secrets.token_urlsafe(32)
        print(f"[AUTH] Generated JWT secret key. Add this to your environment:")
        print(f"JWT_SECRET_KEY={secret_key}")
        print("[AUTH] For production, store this in your environment variables!")
    else:
        print("[AUTH] Using existing JWT_SECRET_KEY from environment")