"""
Authentication and authorization service

Implements JWT-based authentication with refresh tokens
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os

from .logging_config import get_logger
from .exceptions import AuthenticationError, AuthorizationError


logger = get_logger(__name__)

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer scheme
security = HTTPBearer()


class AuthService:
    """
    Authentication service for user management and JWT tokens
    """

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password

        Args:
            password: Plain text password

        Returns:
            Hashed password
        """
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash

        Args:
            plain_password: Plain text password
            hashed_password: Hashed password

        Returns:
            True if password matches, False otherwise
        """
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_access_token(
        data: dict,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a JWT access token

        Args:
            data: Data to encode in token
            expires_delta: Token expiration time

        Returns:
            JWT token string
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        })

        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

        logger.info(
            "Access token created",
            extra={'extra_data': {'user_id': data.get('sub'), 'expires_at': expire.isoformat()}}
        )

        return encoded_jwt

    @staticmethod
    def create_refresh_token(data: dict) -> str:
        """
        Create a JWT refresh token

        Args:
            data: Data to encode in token

        Returns:
            JWT refresh token string
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        })

        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

        return encoded_jwt

    @staticmethod
    def decode_token(token: str) -> dict:
        """
        Decode and validate a JWT token

        Args:
            token: JWT token string

        Returns:
            Decoded token payload

        Raises:
            AuthenticationError: If token is invalid
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError as e:
            logger.warning(f"Token decode failed: {e}")
            raise AuthenticationError("Invalid or expired token")

    @staticmethod
    def get_current_user_id(
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> str:
        """
        Get current user ID from JWT token

        Args:
            credentials: HTTP authorization credentials

        Returns:
            User ID string

        Raises:
            AuthenticationError: If token is invalid
        """
        token = credentials.credentials

        try:
            payload = AuthService.decode_token(token)

            # Check token type
            if payload.get("type") != "access":
                raise AuthenticationError("Invalid token type")

            user_id: str = payload.get("sub")
            if user_id is None:
                raise AuthenticationError("Token missing user identifier")

            return user_id

        except JWTError:
            raise AuthenticationError("Could not validate credentials")


class RoleChecker:
    """
    Dependency to check user roles
    """

    def __init__(self, required_roles: list):
        self.required_roles = required_roles

    def __call__(self, user_id: str = Depends(AuthService.get_current_user_id)):
        # In a real app, you'd fetch user roles from database
        # For now, this is a placeholder
        user_roles = ["user"]  # Fetch from DB based on user_id

        for role in self.required_roles:
            if role not in user_roles:
                logger.warning(
                    f"Authorization failed for user {user_id}",
                    extra={'extra_data': {'required_roles': self.required_roles}}
                )
                raise AuthorizationError(
                    f"Required role '{role}' not found"
                )

        return user_id


# Example usage:
# @app.get("/admin/users", dependencies=[Depends(RoleChecker(["admin"]))])
# async def get_users():
#     return {"users": []}


# Backward compatibility aliases for tests
create_access_token = AuthService.create_access_token
create_refresh_token = AuthService.create_refresh_token
verify_token = AuthService.decode_token
get_password_hash = AuthService.hash_password
verify_password = AuthService.verify_password
