import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.real_estate import real_estate_service

client = TestClient(app)

def test_real_estate_valid_location():
    # A location likely to have valid satellite data
    response = client.post("/api/satellite/real-estate", json={
        "latitude": 37.7749,
        "longitude": -122.4194
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "indicators" in data
    
    indicators = data["indicators"]
    assert "development_activity" in indicators
    assert "built_up_presence" in indicators
    assert "overall_relevance" in indicators
    
def test_real_estate_invalid_coordinates():
    response = client.post("/api/satellite/real-estate", json={
        "latitude": 100.0,
        "longitude": 0.0
    })
    assert response.status_code == 400
    
def test_real_estate_service_logic_unavailable():
    # Test internal logic for unavailable spectral data
    summary_data = {
        "change_analysis": None,
        "land_cover_analysis": None
    }
    result = real_estate_service.evaluate(summary_data)
    assert result["status"] == "error"
    assert result["indicators"]["overall_relevance"] == "unavailable"
    assert any("Insufficient spectral data" in r for r in result["reasons"])

def test_real_estate_service_logic_stable():
    summary_data = {
        "change_analysis": {"change_percentage": 2.0},
        "land_cover_analysis": {
            "indicators": {
                "built_up": {"after": 0.5, "direction": "stable"},
                "vegetation": {"after": 0.1},
                "water": {"after": 0.0}
            }
        }
    }
    result = real_estate_service.evaluate(summary_data)
    assert result["status"] == "success"
    assert result["indicators"]["built_up_presence"] == "high"
    assert result["indicators"]["development_trend"] == "stable"
    assert result["indicators"]["development_activity"] == "low"
    assert result["indicators"]["overall_relevance"] == "high" # built_presence is high

def test_real_estate_service_logic_increasing():
    summary_data = {
        "change_analysis": {"change_percentage": 15.0},
        "land_cover_analysis": {
            "indicators": {
                "built_up": {"after": 0.2, "direction": "increased"},
                "vegetation": {"after": 0.4},
                "water": {"after": 0.2}
            }
        }
    }
    result = real_estate_service.evaluate(summary_data)
    assert result["status"] == "success"
    assert result["indicators"]["development_trend"] == "increased"
    assert result["indicators"]["development_activity"] == "high"
    assert result["indicators"]["overall_relevance"] == "high"

def test_real_estate_service_logic_decreasing():
    summary_data = {
        "change_analysis": {"change_percentage": 8.0},
        "land_cover_analysis": {
            "indicators": {
                "built_up": {"after": 0.05, "direction": "decreased"},
                "vegetation": {"after": 0.8},
                "water": {"after": 0.0}
            }
        }
    }
    result = real_estate_service.evaluate(summary_data)
    assert result["status"] == "success"
    assert result["indicators"]["development_trend"] == "decreased"
    assert result["indicators"]["development_activity"] == "medium"
    assert result["indicators"]["built_up_presence"] == "medium"
    assert result["indicators"]["overall_relevance"] == "medium"
