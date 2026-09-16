from fastapi.testclient import TestClient
from app.main import app
import pytest
import time
from app.core.database import get_db, db

client = TestClient(app)

@pytest.fixture
def test_user():
    timestamp = int(time.time() * 1000)
    return {
        "full_name": "Test User",
        "email": f"TestUser_{timestamp}@Example.com ", # Unique email, mixed case, trailing space
        "password": "SecurePassword123!",
        "confirm_password": "SecurePassword123!"
    }

def test_signup_success(test_user):
    # Since client = TestClient(app), startup events (lifespan) are triggered during requests automatically if we use it correctly or manually.
    with TestClient(app) as client:
        response = client.post("/api/auth/signup", json=test_user)
        assert response.status_code == 201
        data = response.json()
        assert data["full_name"] == test_user["full_name"]
        
        # Verify email was normalized
        expected_email = test_user["email"].strip().lower()
        assert data["email"] == expected_email
        assert "id" in data
        assert "password_hash" not in data

def test_signup_duplicate_email(test_user):
    with TestClient(app) as client:
        # First signup should succeed
        response1 = client.post("/api/auth/signup", json=test_user)
        assert response1.status_code == 201
        
        # Second signup should fail
        response2 = client.post("/api/auth/signup", json=test_user)
        assert response2.status_code == 400
        assert response2.json()["detail"] == "Email already registered"

def test_signup_password_mismatch(test_user):
    test_user["confirm_password"] = "DifferentPassword!"
    
    with TestClient(app) as client:
        response = client.post("/api/auth/signup", json=test_user)
        assert response.status_code == 422
        assert "Passwords do not match" in str(response.json())

def test_signup_invalid_email(test_user):
    test_user["email"] = "not-an-email"
    
    with TestClient(app) as client:
        response = client.post("/api/auth/signup", json=test_user)
        assert response.status_code == 422

def test_login_success(test_user):
    with TestClient(app) as client:
        # First sign up the user
        client.post("/api/auth/signup", json=test_user)
        
        # Then try logging in
        login_data = {
            "email": test_user["email"], # Un-normalized, backend should handle it
            "password": test_user["password"]
        }
        response = client.post("/api/auth/login", json=login_data)
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        
        user_data = data["user"]
        assert user_data["email"] == test_user["email"].strip().lower()
        assert "password_hash" not in user_data
        assert "password" not in user_data

def test_login_wrong_password(test_user):
    with TestClient(app) as client:
        client.post("/api/auth/signup", json=test_user)
        
        login_data = {
            "email": test_user["email"],
            "password": "WrongPassword123!"
        }
        response = client.post("/api/auth/login", json=login_data)
        assert response.status_code == 401
        assert response.json()["detail"] == "Incorrect email or password"

def test_login_non_existing_email():
    with TestClient(app) as client:
        login_data = {
            "email": "doesnotexist@example.com",
            "password": "Password123!"
        }
        response = client.post("/api/auth/login", json=login_data)
        assert response.status_code == 401
        assert response.json()["detail"] == "Incorrect email or password"

def test_login_invalid_email():
    with TestClient(app) as client:
        login_data = {
            "email": "not-an-email",
            "password": "Password123!"
        }
        response = client.post("/api/auth/login", json=login_data)
        assert response.status_code == 422

def test_login_missing_fields(test_user):
    with TestClient(app) as client:
        # Missing password
        login_data = {
            "email": test_user["email"]
        }
        response = client.post("/api/auth/login", json=login_data)
        assert response.status_code == 422

def test_get_me_success(test_user):
    with TestClient(app) as client:
        client.post("/api/auth/signup", json=test_user)
        login_response = client.post("/api/auth/login", json={"email": test_user["email"], "password": test_user["password"]})
        token = login_response.json()["access_token"]
        
        response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        
        data = response.json()
        assert data["email"] == test_user["email"].strip().lower()
        assert "password_hash" not in data

def test_get_me_missing_token():
    with TestClient(app) as client:
        response = client.get("/api/auth/me")
        assert response.status_code == 401

def test_get_me_invalid_token():
    with TestClient(app) as client:
        response = client.get("/api/auth/me", headers={"Authorization": "Bearer invalid_token_here"})
        assert response.status_code == 401

def test_get_me_expired_token(test_user):
    from app.core.security import create_access_token
    from datetime import timedelta
    with TestClient(app) as client:
        client.post("/api/auth/signup", json=test_user)
        # Create an explicitly expired token
        expired_token = create_access_token(data={"sub": "some_id"}, expires_delta=timedelta(minutes=-10))
        
        response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {expired_token}"})
        assert response.status_code == 401

def test_get_me_nonexistent_user():
    from app.core.security import create_access_token
    with TestClient(app) as client:
        # Generate a valid token for an ID that doesn't exist in the database
        fake_id = "507f1f77bcf86cd799439011"
        token = create_access_token(data={"sub": fake_id})
        
        response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 401
