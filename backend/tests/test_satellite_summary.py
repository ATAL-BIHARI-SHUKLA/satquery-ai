from fastapi.testclient import TestClient
from app.main import app
from app.schemas.satellite import SatelliteHistoryResponse, HistoricalPeriod, AssetInfo
from app.schemas.change_detection import ChangeDetectionResponse
from app.schemas.land_cover import LandCoverAnalysisResponse, LandCoverIndicators, IndicatorResult
import pytest

client = TestClient(app)

def test_summary_invalid_latitude():
    response = client.post("/api/satellite/summary", json={"latitude": 100.0, "longitude": -122.4194})
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid latitude"

def test_summary_invalid_longitude():
    response = client.post("/api/satellite/summary", json={"latitude": 37.7749, "longitude": 200.0})
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid longitude"

def test_summary_valid_full_analysis(monkeypatch):
    def mock_get_historical_timeline(lat, lon, radius_km=None, target_years=None):
        return SatelliteHistoryResponse(
            latitude=lat,
            longitude=lon,
            provider="mock",
            imagery=[
                HistoricalPeriod(period="10 years ago", target_date="2014-01-01", available=True, selected_date="2014-01-05", asset=AssetInfo(type="image", url="url1")),
                HistoricalPeriod(period="Current", target_date="2024-01-01", available=True, selected_date="2024-01-02", asset=AssetInfo(type="image", url="url2"))
            ]
        )
        
    def mock_detect_change(before, after):
        return ChangeDetectionResponse(
            status="success",
            method="baseline",
            changed_area_available=True,
            change_percentage=5.5
        )
        
    def mock_calculate_indicators(before, after):
        return LandCoverAnalysisResponse(
            status="success",
            indicators=LandCoverIndicators(
                vegetation=IndicatorResult(before=0.5, after=0.6, change=0.1, direction="increase")
            )
        )
        
    monkeypatch.setattr("app.api.routes.satellite.satellite_service.get_historical_timeline", mock_get_historical_timeline)
    monkeypatch.setattr("app.api.routes.satellite.change_detection_service.detect_change", mock_detect_change)
    monkeypatch.setattr("app.api.routes.satellite.land_cover_service.calculate_indicators", mock_calculate_indicators)
    
    response = client.post("/api/satellite/summary", json={"latitude": 37.7749, "longitude": -122.4194})
    assert response.status_code == 200
    data = response.json()
    assert data["imagery_count"] == 2
    assert data["oldest_imagery"]["selected_date"] == "2014-01-05"
    assert data["newest_imagery"]["selected_date"] == "2024-01-02"
    assert data["change_analysis"]["change_percentage"] == 5.5
    assert data["land_cover_analysis"]["indicators"]["vegetation"]["direction"] == "increase"
    assert len(data["limitations"]) == 0

def test_summary_insufficient_imagery(monkeypatch):
    def mock_get_historical_timeline(lat, lon, radius_km=None, target_years=None):
        return SatelliteHistoryResponse(
            latitude=lat,
            longitude=lon,
            provider="mock",
            imagery=[
                HistoricalPeriod(period="Current", target_date="2024-01-01", available=False)
            ]
        )
        
    monkeypatch.setattr("app.api.routes.satellite.satellite_service.get_historical_timeline", mock_get_historical_timeline)
    
    response = client.post("/api/satellite/summary", json={"latitude": 37.7749, "longitude": -122.4194})
    assert response.status_code == 200
    data = response.json()
    assert data["imagery_count"] == 0
    assert data["oldest_imagery"] is None
    assert data["change_analysis"] is None
    assert data["land_cover_analysis"] is None
    assert "No usable satellite imagery found" in data["limitations"][0]

def test_summary_partial_analysis(monkeypatch):
    def mock_get_historical_timeline(lat, lon, radius_km=None, target_years=None):
        return SatelliteHistoryResponse(
            latitude=lat,
            longitude=lon,
            provider="mock",
            imagery=[
                HistoricalPeriod(period="10 years ago", target_date="2014-01-01", available=True, selected_date="2014-01-05", asset=AssetInfo(type="image", url="url1")),
                HistoricalPeriod(period="Current", target_date="2024-01-01", available=True, selected_date="2024-01-02", asset=AssetInfo(type="image", url="url2"))
            ]
        )
        
    def mock_detect_change(before, after):
        return ChangeDetectionResponse(
            status="success",
            method="baseline",
            changed_area_available=True,
            change_percentage=5.5
        )
        
    def mock_calculate_indicators(before, after):
        raise Exception("insufficient spectral data")
        
    monkeypatch.setattr("app.api.routes.satellite.satellite_service.get_historical_timeline", mock_get_historical_timeline)
    monkeypatch.setattr("app.api.routes.satellite.change_detection_service.detect_change", mock_detect_change)
    monkeypatch.setattr("app.api.routes.satellite.land_cover_service.calculate_indicators", mock_calculate_indicators)
    
    response = client.post("/api/satellite/summary", json={"latitude": 37.7749, "longitude": -122.4194})
    assert response.status_code == 200
    data = response.json()
    assert data["imagery_count"] == 2
    assert data["change_analysis"]["change_percentage"] == 5.5
    assert data["land_cover_analysis"] is None
    assert any("insufficient spectral data" in limit for limit in data["limitations"])
