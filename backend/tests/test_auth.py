"""
Tests for authentication and authorization
"""
import pytest
from datetime import datetime, timedelta
from decimal import Decimal

from app.auth import (
    create_access_token,
    create_refresh_token,
    verify_token,
    get_password_hash,
    verify_password
)


class TestPasswordHashing:
    """Test password hashing functionality"""

    def test_hash_password(self):
        """Test password hashing"""
        password = "secure_password_123"
        hashed = get_password_hash(password)

        assert hashed != password
        assert len(hashed) > 20
        assert hashed.startswith("$2b$")  # bcrypt format

    def test_verify_correct_password(self):
        """Test verifying correct password"""
        password = "test_password"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_verify_incorrect_password(self):
        """Test verifying incorrect password"""
        password = "test_password"
        hashed = get_password_hash(password)

        assert verify_password("wrong_password", hashed) is False

    def test_different_hashes_same_password(self):
        """Test that same password generates different hashes (salt)"""
        password = "test_password"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        assert hash1 != hash2
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)


class TestJWTTokens:
    """Test JWT token creation and verification"""

    def test_create_access_token(self):
        """Test creating access token"""
        data = {"sub": "user@example.com", "user_id": 123}
        token = create_access_token(data)

        assert isinstance(token, str)
        assert len(token) > 50

    def test_create_refresh_token(self):
        """Test creating refresh token"""
        data = {"sub": "user@example.com", "user_id": 123}
        token = create_refresh_token(data)

        assert isinstance(token, str)
        assert len(token) > 50

    def test_verify_valid_token(self):
        """Test verifying valid token"""
        data = {"sub": "user@example.com", "user_id": 123}
        token = create_access_token(data)

        payload = verify_token(token)

        assert payload is not None
        assert payload["sub"] == "user@example.com"
        assert payload["user_id"] == 123

    def test_verify_expired_token(self):
        """Test that expired tokens are rejected"""
        data = {"sub": "user@example.com"}
        # Create token that expires immediately
        token = create_access_token(data, expires_delta=timedelta(seconds=-1))

        payload = verify_token(token)
        assert payload is None  # Expired token returns None

    def test_verify_invalid_token(self):
        """Test verifying invalid token"""
        invalid_token = "invalid.token.string"

        payload = verify_token(invalid_token)
        assert payload is None

    def test_token_contains_expiration(self):
        """Test that token contains expiration claim"""
        data = {"sub": "user@example.com"}
        token = create_access_token(data)

        payload = verify_token(token)

        assert "exp" in payload
        assert isinstance(payload["exp"], (int, float))

    def test_custom_expiration(self):
        """Test creating token with custom expiration"""
        data = {"sub": "user@example.com"}
        expires_delta = timedelta(hours=2)

        token = create_access_token(data, expires_delta=expires_delta)
        payload = verify_token(token)

        assert payload is not None
        # Token should be valid for at least 1.5 hours
        exp_time = datetime.fromtimestamp(payload["exp"])
        time_until_expiry = exp_time - datetime.utcnow()
        assert time_until_expiry.total_seconds() > 5400  # 1.5 hours


class TestAuthenticationMiddleware:
    """Test authentication middleware"""

    @pytest.mark.skip("Implement when middleware is active")
    def test_protected_endpoint_requires_auth(self, client):
        """Test that protected endpoints require authentication"""
        response = client.get("/api/protected-endpoint")

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    @pytest.mark.skip("Implement when middleware is active")
    def test_protected_endpoint_with_valid_token(self, client):
        """Test accessing protected endpoint with valid token"""
        # Create valid token
        token = create_access_token({"sub": "user@example.com", "user_id": 1})

        response = client.get(
            "/api/protected-endpoint",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200

    @pytest.mark.skip("Implement when middleware is active")
    def test_protected_endpoint_with_invalid_token(self, client):
        """Test accessing protected endpoint with invalid token"""
        response = client.get(
            "/api/protected-endpoint",
            headers={"Authorization": "Bearer invalid_token"}
        )

        assert response.status_code == 401

    @pytest.mark.skip("Implement when middleware is active")
    def test_protected_endpoint_with_expired_token(self, client):
        """Test accessing protected endpoint with expired token"""
        # Create expired token
        token = create_access_token(
            {"sub": "user@example.com"},
            expires_delta=timedelta(seconds=-1)
        )

        response = client.get(
            "/api/protected-endpoint",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 401


class TestUserAuthentication:
    """Test user authentication flow"""

    @pytest.mark.skip("Implement when user endpoints exist")
    def test_user_registration(self, client):
        """Test user registration"""
        user_data = {
            "email": "newuser@example.com",
            "password": "secure_password_123",
            "name": "New User"
        }

        response = client.post("/api/auth/register", json=user_data)

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]
        assert "password" not in data  # Password should not be returned

    @pytest.mark.skip("Implement when user endpoints exist")
    def test_user_login(self, client):
        """Test user login"""
        # First register user
        user_data = {
            "email": "testuser@example.com",
            "password": "password123"
        }
        client.post("/api/auth/register", json=user_data)

        # Now login
        login_data = {
            "email": "testuser@example.com",
            "password": "password123"
        }
        response = client.post("/api/auth/login", json=login_data)

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.skip("Implement when user endpoints exist")
    def test_login_with_wrong_password(self, client):
        """Test login with incorrect password"""
        # Register user
        client.post("/api/auth/register", json={
            "email": "user@example.com",
            "password": "correct_password"
        })

        # Try login with wrong password
        response = client.post("/api/auth/login", json={
            "email": "user@example.com",
            "password": "wrong_password"
        })

        assert response.status_code == 401

    @pytest.mark.skip("Implement when user endpoints exist")
    def test_refresh_token_flow(self, client):
        """Test refreshing access token"""
        # Login to get tokens
        login_response = client.post("/api/auth/login", json={
            "email": "user@example.com",
            "password": "password123"
        })
        refresh_token = login_response.json()["refresh_token"]

        # Use refresh token to get new access token
        response = client.post(
            "/api/auth/refresh",
            json={"refresh_token": refresh_token}
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

    @pytest.mark.skip("Implement when user endpoints exist")
    def test_logout(self, client):
        """Test user logout"""
        # Login first
        login_response = client.post("/api/auth/login", json={
            "email": "user@example.com",
            "password": "password123"
        })
        token = login_response.json()["access_token"]

        # Logout
        response = client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200

        # Try using the token after logout (should fail)
        protected_response = client.get(
            "/api/protected-endpoint",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert protected_response.status_code == 401


class TestRBAC:
    """Test Role-Based Access Control"""

    @pytest.mark.skip("Implement when RBAC is active")
    def test_admin_only_endpoint(self, client):
        """Test endpoint that requires admin role"""
        # Regular user token
        user_token = create_access_token({
            "sub": "user@example.com",
            "role": "user"
        })

        response = client.get(
            "/api/admin/users",
            headers={"Authorization": f"Bearer {user_token}"}
        )

        assert response.status_code == 403  # Forbidden

    @pytest.mark.skip("Implement when RBAC is active")
    def test_admin_access_to_admin_endpoint(self, client):
        """Test admin can access admin endpoint"""
        # Admin token
        admin_token = create_access_token({
            "sub": "admin@example.com",
            "role": "admin"
        })

        response = client.get(
            "/api/admin/users",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
