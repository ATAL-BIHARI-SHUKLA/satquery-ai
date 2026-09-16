from fastapi.testclient import TestClient
from app.main import app
import pytest

import json
import urllib.request
import urllib.error
from typing import Dict, Any

client = TestClient(app)

class MockResponse:
    def __init__(self, json_data: Dict[str, Any]):
        self.data = json.dumps(json_data).encode('utf-8')
    def read(self):
        return self.data
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

def test_satellite_valid_coordinates(monkeypatch):
    def mock_urlopen(req, timeout=None):
        return MockResponse({
            "features": [{
                "collection": "sentinel-2-l2a",
                "properties": {
                    "datetime": "2024-03-24T18:55:23Z",
                    "eo:cloud_cover": 4.12
                }
            }]
        })
    monkeypatch.setattr("urllib.request.urlopen", mock_urlopen)

    response = client.get("/api/satellite/availability?latitude=37.7749&longitude=-122.4194")
    assert response.status_code == 200
    data = response.json()
    assert data["latitude"] == 37.7749
    assert data["longitude"] == -122.4194
    assert "available" in data
    assert "provider" in data
    assert isinstance(data["imagery"], list)
    assert len(data["imagery"]) == 1
    assert data["imagery"][0]["cloud_cover"] == 4.12

def test_satellite_invalid_latitude():
    response = client.get("/api/satellite/availability?latitude=100.0&longitude=-122.4194")
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Invalid latitude"

def test_satellite_invalid_longitude():
    response = client.get("/api/satellite/availability?latitude=37.7749&longitude=-200.0")
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Invalid longitude"

def test_satellite_missing_coordinates():
    response = client.get("/api/satellite/availability?latitude=37.7749")
    assert response.status_code == 422 # Pydantic missing required query param

def test_satellite_provider_unavailable(monkeypatch):
    # Mock to force provider failure
    def mock_check_availability(*args, **kwargs):
        return {
            "latitude": 0.0,
            "longitude": 0.0,
            "available": False,
            "provider": "Mock",
            "imagery": [],
            "error": "Provider unavailable"
        }
    
    from app.api.routes import satellite
    monkeypatch.setattr(satellite.satellite_service, "check_availability", mock_check_availability)
    
    response = client.get("/api/satellite/availability?latitude=0.0&longitude=0.0")
    assert response.status_code == 200
    data = response.json()
    assert data["error"] == "Provider unavailable"
    assert data["available"] is False

def test_imagery_valid_location(monkeypatch):
    def mock_urlopen(req, timeout=None):
        return MockResponse({
            "features": [{
                "properties": {
                    "datetime": "2024-03-24T18:55:23Z",
                    "eo:cloud_cover": 4.12
                },
                "assets": {
                    "visual": {
                        "href": "https://example.com/image.tif",
                        "title": "visual",
                        "type": "image/tiff; application=geotiff; profile=cloud-optimized"
                    }
                }
            }]
        })
    monkeypatch.setattr("urllib.request.urlopen", mock_urlopen)
    
    response = client.get("/api/satellite/imagery?latitude=37.7749&longitude=-122.4194")
    assert response.status_code == 200
    data = response.json()
    assert data["latitude"] == 37.7749
    assert data["longitude"] == -122.4194
    assert data["available"] is True
    assert data["provider"] == "Earth Search (Sentinel-2)"
    assert data["selected_date"] == "2024-03-24T18:55:23Z"
    assert data["cloud_cover"] == 4.12
    assert "asset" in data
    assert data["asset"]["url"] == "https://example.com/image.tif"

def test_imagery_historical_date(monkeypatch):
    def mock_urlopen(req, timeout=None):
        assert "2020-01-01" in req.data.decode('utf-8')
        return MockResponse({
            "features": [{
                "properties": {
                    "datetime": "2020-01-01T12:00:00Z",
                    "eo:cloud_cover": 1.0
                },
                "assets": {
                    "rendered_preview": {
                        "href": "https://example.com/preview.png",
                        "title": "rendered_preview",
                        "type": "image/png"
                    }
                }
            }]
        })
    monkeypatch.setattr("urllib.request.urlopen", mock_urlopen)
    
    response = client.get("/api/satellite/imagery?latitude=37.7&longitude=-122.4&target_date=2020-01-01")
    assert response.status_code == 200
    data = response.json()
    assert data["available"] is True
    assert data["selected_date"] == "2020-01-01T12:00:00Z"
    assert data["asset"]["type"] == "rendered_preview"
    assert data["asset"]["url"] == "https://example.com/preview.png"

def test_imagery_no_imagery_found(monkeypatch):
    def mock_urlopen(req, timeout=None):
        return MockResponse({"features": []})
    monkeypatch.setattr("urllib.request.urlopen", mock_urlopen)
    
    response = client.get("/api/satellite/imagery?latitude=37.7&longitude=-122.4")
    assert response.status_code == 200
    data = response.json()
    assert data["available"] is False
    assert "reason" in data

def test_imagery_invalid_coordinates():
    response = client.get("/api/satellite/imagery?latitude=200&longitude=0")
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid latitude"

def test_imagery_provider_unavailable(monkeypatch):
    def mock_urlopen(req, timeout=None):
        raise urllib.error.URLError("Connection refused")
    monkeypatch.setattr("urllib.request.urlopen", mock_urlopen)
    
    response = client.get("/api/satellite/imagery?latitude=37.7&longitude=-122.4")
    assert response.status_code == 200
    data = response.json()
    assert data["available"] is False
    assert data["reason"] == "Provider unavailable"

def test_history_valid_location(monkeypatch):
    def mock_urlopen(req, timeout=None):
        return MockResponse({
            "features": [{
                "properties": {
                    "datetime": "2024-03-24T18:55:23Z",
                    "eo:cloud_cover": 4.12
                },
                "assets": {
                    "visual": {
                        "href": "https://example.com/image.tif",
                        "title": "visual",
                        "type": "image/tiff; application=geotiff; profile=cloud-optimized"
                    }
                }
            }]
        })
    monkeypatch.setattr("urllib.request.urlopen", mock_urlopen)
    
    response = client.get("/api/satellite/history?latitude=37.7749&longitude=-122.4194")
    assert response.status_code == 200
    data = response.json()
    assert data["latitude"] == 37.7749
    assert data["longitude"] == -122.4194
    assert data["provider"] == "Earth Search (Sentinel-2)"
    assert len(data["imagery"]) == 3
    
    for item in data["imagery"]:
        assert item["available"] is True
        assert item["cloud_cover"] == 4.12
        assert item["asset"]["url"] == "https://example.com/image.tif"
        
    periods = [item["period"] for item in data["imagery"]]
    assert "current" in periods
    assert "5_years" in periods
    assert "10_years" in periods

def test_history_partial_unavailable(monkeypatch):
    call_count = 0
    def mock_urlopen(req, timeout=None):
        nonlocal call_count
        call_count += 1
        if call_count == 3:
            return MockResponse({"features": []})
            
        return MockResponse({
            "features": [{
                "properties": {
                    "datetime": "2024-03-24T18:55:23Z",
                    "eo:cloud_cover": 4.12
                },
                "assets": {
                    "visual": {
                        "href": "https://example.com/image.tif",
                        "title": "visual",
                        "type": "image/tiff"
                    }
                }
            }]
        })
    monkeypatch.setattr("urllib.request.urlopen", mock_urlopen)
    
    response = client.get("/api/satellite/history?latitude=37.7749&longitude=-122.4194")
    assert response.status_code == 200
    data = response.json()
    
    assert data["imagery"][0]["available"] is True
    assert data["imagery"][1]["available"] is True
    assert data["imagery"][2]["available"] is False
    assert data["imagery"][2]["period"] == "10_years"
    assert "reason" in data["imagery"][2]

def test_history_invalid_coordinates():
    response = client.get("/api/satellite/history?latitude=200&longitude=0")
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid latitude"
