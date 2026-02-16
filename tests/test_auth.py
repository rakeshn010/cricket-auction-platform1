"""
Authentication tests.
Run with: pytest tests/test_auth.py -v
"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from main_new import app
from database import db

client = TestClient(app)


@pytest.fixture(scope="module")
def test_user():
    """Create a test user."""
    # Clean up any existing test user
    db.users.delete_many({"email": "test@example.com"})
    
    yield {
        "email": "test@example.com",
        "password": "TestPassword123!@#",
        "name": "Test User"
    }
    
    # Cleanup after tests
    db.users.delete_many({"email": "test@example.com"})


class TestRegistration:
    """Test user registration."""
    
    def test_register_success(self, test_user):
        """Test successful registration."""
        response = client.post("/auth/register", data=test_user)
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert "Registration successful" in data["message"]
    
    def test_register_duplicate_email(self, test_user):
        """Test registration with duplicate email."""
        response = client.post("/auth/register", data=test_user)
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]
    
    def test_register_weak_password(self):
        """Test registration with weak password."""
        response = client.post("/auth/register", data={
            "email": "weak@example.com",
            "password": "123",
            "name": "Weak User"
        })
        assert response.status_code == 400
        assert "security requirements" in response.json()["detail"]["message"]
    
    def test_register_missing_email(self):
        """Test registration without email."""
        response = client.post("/auth/register", data={
            "password": "TestPassword123!@#",
            "name": "No Email"
        })
        assert response.status_code == 422


class TestLogin:
    """Test user login."""
    
    def test_login_success(self, test_user):
        """Test successful login."""
        response = client.post("/auth/login", data={
            "email": test_user["email"],
            "password": test_user["password"]
        })
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        
        # Check cookies are set
        assert "access_token" in response.cookies
        assert "refresh_token" in response.cookies
    
    def test_login_invalid_password(self, test_user):
        """Test login with wrong password."""
        response = client.post("/auth/login", data={
            "email": test_user["email"],
            "password": "WrongPassword123!"
        })
        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]
    
    def test_login_nonexistent_user(self):
        """Test login with non-existent email."""
        response = client.post("/auth/login", data={
            "email": "nonexistent@example.com",
            "password": "TestPassword123!@#"
        })
        assert response.status_code == 401
    
    def test_login_missing_credentials(self):
        """Test login without credentials."""
        response = client.post("/auth/login", data={})
        assert response.status_code == 422


class TestProtectedRoutes:
    """Test protected route access."""
    
    def test_access_without_token(self):
        """Test accessing protected route without token."""
        response = client.get("/admin")
        assert response.status_code == 303  # Redirect
    
    def test_access_with_valid_token(self, test_user):
        """Test accessing protected route with valid token."""
        # Login first
        login_response = client.post("/auth/login", data={
            "email": test_user["email"],
            "password": test_user["password"]
        })
        token = login_response.json()["access_token"]
        
        # Access protected route
        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert data["user"]["email"] == test_user["email"]


class TestLogout:
    """Test logout functionality."""
    
    def test_logout_success(self, test_user):
        """Test successful logout."""
        # Login first
        login_response = client.post("/auth/login", data={
            "email": test_user["email"],
            "password": test_user["password"]
        })
        token = login_response.json()["access_token"]
        
        # Logout
        response = client.post(
            "/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert "Logged out successfully" in response.json()["message"]
        
        # Try to use the same token (should fail)
        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code in [401, 303]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
