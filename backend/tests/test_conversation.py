import pytest

def test_list_conversations_unauthorized(client):
    response = client.get("/api/conversations")
    assert response.status_code == 401

def test_list_conversations_empty(client, auth_headers):
    response = client.get("/api/conversations", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []

def test_create_and_list_conversations(client, auth_headers):
    # Create two conversations
    resp1 = client.post("/api/conversations", headers=auth_headers, json={})
    assert resp1.status_code == 201
    
    resp2 = client.post("/api/conversations", headers=auth_headers, json={})
    assert resp2.status_code == 201
    
    # List conversations
    response = client.get("/api/conversations", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 2
    
    # Check structure
    conv = data[0]
    assert "id" in conv
    assert "title" in conv
    assert "created_at" in conv
    assert "updated_at" in conv
    
    # Check ordering (descending by updated_at)
    # The second one created should have a later or equal updated_at
    assert data[0]["id"] == resp2.json()["conversation_id"]
    assert data[1]["id"] == resp1.json()["conversation_id"]
