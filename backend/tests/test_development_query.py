import pytest
from app.services.router import TaskType

@pytest.fixture
def conversation_id(client, auth_headers):
    response = client.post("/api/conversations", headers=auth_headers)
    return response.json()["id"] if "id" in response.json() else response.json()["conversation_id"]

def test_location_development_query_success(client, conversation_id, auth_headers, monkeypatch):
    # Mock satellite data service
    class MockSatelliteDataService:
        def get_historical_timeline(self, lat, lon, radius_km, target_years):
            assert radius_km == 2.0
            assert target_years == 10
            return {
                "latitude": lat,
                "longitude": lon,
                "radius_km": radius_km,
                "target_years": target_years,
                "imagery": [
                    {
                        "period": "10_years",
                        "available": True,
                        "selected_date": "2014-06-15T00:00:00Z",
                        "cloud_cover": 5.0,
                        "asset": {"url": "http://example.com/2014.tif"}
                    },
                    {
                        "period": "current",
                        "available": True,
                        "selected_date": "2024-06-15T00:00:00Z",
                        "cloud_cover": 2.0,
                        "asset": {"url": "http://example.com/2024.tif"}
                    }
                ]
            }

    # IMPORTANT: Patch the class where it is imported in executor.py
    monkeypatch.setattr("app.services.satellite.SatelliteDataService", MockSatelliteDataService)
    
    class MockChangeDetectionService:
        def detect_change(self, img1, img2):
            return {
                "before_date": "2014-06-15T00:00:00Z",
                "after_date": "2024-06-15T00:00:00Z",
                "change_percentage": 15.5,
                "summary": "Mock change detected"
            }
            
    monkeypatch.setattr("app.services.change_detection.change_detection_service", MockChangeDetectionService())
    
    class MockLandCoverService:
        def calculate_indicators(self, img1, img2):
            return {
                "indicators": {
                    "vegetation": {"before": 40.0, "after": 30.0, "change": 10.0, "direction": "decreased"},
                    "water": {"before": 5.0, "after": 5.0, "change": 0.0, "direction": "stable"},
                    "built_up": {"before": 10.0, "after": 25.0, "change": 15.0, "direction": "increased"}
                }
            }
            
    monkeypatch.setattr("app.services.land_cover.land_cover_service", MockLandCoverService())

    response = client.post("/api/query", json={
        "query": "Is area mein pichle 10 saal mein kitna development hua?",
        "conversation_id": conversation_id,
        "context": {
            "latitude": 30.43,
            "longitude": 74.89,
            "locationName": "Jaitu",
            "radiusKm": 2.0
        }
    }, headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["task"] == TaskType.LOCATION_DEVELOPMENT_ANALYSIS
    
    assert "execution" in data and "answer" in data["execution"], f"Response: {data}"
    ans = data["execution"]["answer"]
    assert "Between 2014-06-15T00:00:00Z and 2024-06-15T00:00:00Z" in ans
    assert "Before imagery: 2014-06-15T00:00:00Z" in ans
    assert "After imagery: 2024-06-15T00:00:00Z" in ans
    assert "approximately 15.5% surface change" in ans
    assert "Built-up/development proxy" in ans
    assert "Vegetation indicator" in ans
    assert data["execution"]["evidence"]["analysis_context"]["baseline_confidence"] == "Moderate"
    assert data["execution"]["evidence"]["imagery_evidence"]["source"] == "Sentinel-2 / Earth Search"

def test_location_development_query_insufficient_imagery(client, conversation_id, auth_headers, monkeypatch):
    class MockSatelliteDataService:
        def get_historical_timeline(self, lat, lon, radius_km, target_years):
            return {
                "imagery": [
                    {
                        "period": "current",
                        "available": True,
                        "selected_date": "2024-06-15T00:00:00Z",
                        "cloud_cover": 2.0,
                        "asset": {"url": "http://example.com/2024.tif"}
                    }
                ]
            }

    monkeypatch.setattr("app.services.satellite.SatelliteDataService", MockSatelliteDataService)
    
    response = client.post("/api/query", json={
        "query": "development 5 years?",
        "conversation_id": conversation_id,
        "context": {
            "latitude": 30.43,
            "longitude": 74.89,
            "radiusKm": 2.0
        }
    }, headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "execution" in data and "answer" in data["execution"], f"Response: {data}"
    ans = data["execution"]["answer"]
    assert "A reliable quantitative change percentage could not be calculated from the available imagery." in ans
    assert data["execution"]["evidence"]["analysis_context"]["baseline_confidence"] == "Low"

def test_location_development_query_follow_up(client, conversation_id, auth_headers, monkeypatch):
    class MockSatelliteDataService:
        def get_historical_timeline(self, lat, lon, radius_km, target_years):
            return {
                "imagery": [
                    {
                        "period": "current",
                        "available": True,
                        "selected_date": "2024-06-15T00:00:00Z",
                        "cloud_cover": 2.0,
                        "asset": {"url": "http://example.com/2024.tif"}
                    }
                ]
            }

    monkeypatch.setattr("app.services.satellite.SatelliteDataService", MockSatelliteDataService)
    # Set context first via the conversation state logic
    client.post("/api/query", json={
        "query": "Analyze development",
        "conversation_id": conversation_id,
        "context": {
            "latitude": 30.43,
            "longitude": 74.89,
            "radiusKm": 2.0
        }
    }, headers=auth_headers)
    
    # Follow-up without explicit context (uses conversation context)
    response = client.post("/api/query", json={
        "query": "change kya hua?",
        "conversation_id": conversation_id
    }, headers=auth_headers)
    
    assert response.status_code == 200
    assert response.json()["task"] == TaskType.LOCATION_DEVELOPMENT_ANALYSIS
