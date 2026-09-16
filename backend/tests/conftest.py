import pytest
from fastapi.testclient import TestClient
from app.main import app
import time

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="module")
def auth_headers(client):
    timestamp = int(time.time() * 1000)
    user = {
        "full_name": "Test Auth User",
        "email": f"auth_{timestamp}@example.com",
        "password": "SecurePassword123!",
        "confirm_password": "SecurePassword123!"
    }
    client.post("/api/auth/signup", json=user)
    response = client.post("/api/auth/login", json={"email": user["email"], "password": user["password"]})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
