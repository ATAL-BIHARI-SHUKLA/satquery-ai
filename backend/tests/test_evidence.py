import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.evidence import evidence_service

client = TestClient(app)

def test_evidence_valid_location():
    response = client.post("/api/satellite/evidence", json={
        "latitude": 37.7749,
        "longitude": -122.4194
    })
    
    assert response.status_code == 200
    data = response.json()
    
    assert "imagery_evidence" in data
    assert "limitations" in data
    assert "evidence_summary" in data

def test_evidence_invalid_latitude():
    response = client.post("/api/satellite/evidence", json={
        "latitude": 100.0,
        "longitude": 0.0
    })
    assert response.status_code == 400

def test_evidence_invalid_longitude():
    response = client.post("/api/satellite/evidence", json={
        "latitude": 0.0,
        "longitude": 200.0
    })
    assert response.status_code == 400

def test_evidence_service_logic_insufficient_imagery():
    summary_data = {
        "imagery_count": 0,
        "oldest_imagery": None,
        "newest_imagery": None,
        "change_analysis": None,
        "land_cover_analysis": None,
        "limitations": ["No usable satellite imagery found for this location."]
    }
    
    real_estate_data = {
        "status": "error",
        "indicators": {},
        "reasons": ["Insufficient spectral data to compute relevance indicators."],
        "limitations": []
    }
    
    result = evidence_service.build_evidence(summary_data, real_estate_data)
    assert result["change_evidence"] is None
    assert result["land_cover_evidence"] is None
    assert any("No historical satellite imagery available" in s for s in result["evidence_summary"])
    assert any("No usable satellite imagery found" in l for l in result["limitations"])

def test_evidence_service_logic_missing_spectral_data():
    summary_data = {
        "imagery_count": 2,
        "oldest_imagery": {"selected_date": "2020-01-01", "provider": "test"},
        "newest_imagery": {"selected_date": "2021-01-01", "provider": "test"},
        "change_analysis": {"change_percentage": 5.0, "summary": "Some change", "method": "test_method"},
        "land_cover_analysis": None,
        "limitations": ["Land cover analysis failed"]
    }
    
    real_estate_data = {
        "status": "error",
        "indicators": {},
        "reasons": ["Insufficient spectral data to compute relevance indicators."],
        "limitations": []
    }
    
    result = evidence_service.build_evidence(summary_data, real_estate_data)
    assert result["change_evidence"] is not None
    assert result["land_cover_evidence"] is None
    assert result["real_estate_evidence"] is None
    assert any("Land cover analysis failed" in l for l in result["limitations"])

def test_evidence_service_logic_partial_analysis():
    summary_data = {
        "imagery_count": 2,
        "oldest_imagery": {"selected_date": "2020-01-01"},
        "newest_imagery": {"selected_date": "2021-01-01"},
        "change_analysis": None,
        "land_cover_analysis": {
            "indicators": {
                "built_up": {"after": 0.5, "direction": "increased"}
            }
        },
        "limitations": ["Change detection failed"]
    }
    real_estate_data = {
        "status": "partial",
        "indicators": {
            "overall_relevance": "high"
        },
        "reasons": [],
        "limitations": []
    }
    
    result = evidence_service.build_evidence(summary_data, real_estate_data)
    assert result["change_evidence"] is None
    assert result["land_cover_evidence"] is not None
    assert result["real_estate_evidence"] is not None
    assert any("Change detection failed" in l for l in result["limitations"])
    
def test_evidence_summary_contains_facts():
    summary_data = {
        "imagery_count": 2,
        "oldest_imagery": {"selected_date": "2020-01-01"},
        "newest_imagery": {"selected_date": "2021-01-01"},
        "change_analysis": {"change_percentage": 10.0},
        "land_cover_analysis": {
            "indicators": {
                "built_up": {"direction": "increased"}
            }
        }
    }
    real_estate_data = {
        "indicators": {
            "overall_relevance": "high"
        }
    }
    
    result = evidence_service.build_evidence(summary_data, real_estate_data)
    summary = result["evidence_summary"]
    
    # Check that summary points match the inputs exactly
    assert any("10.0%" in s for s in summary)
    assert any("increased over time" in s for s in summary)
    assert any("relevance is high" in s for s in summary)
    assert any("2020-01-01 to 2021-01-01" in s for s in summary)
