import pytest
from fastapi.testclient import TestClient
from app.main import app
import os

client = TestClient(app)

def test_change_detection_no_change():
    before = os.path.abspath("tests/fixtures/before.tif").replace("\\", "/")
    after = os.path.abspath("tests/fixtures/after_no_change.tif").replace("\\", "/")
    
    response = client.post("/api/satellite/change-detection", json={
        "before_asset_url": before,
        "after_asset_url": after
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["method"] == "baseline_change_detection"
    assert data["change_percentage"] == 0.0
    assert "Minimal or no change detected" in data["summary"]
    
def test_change_detection_changed():
    before = os.path.abspath("tests/fixtures/before.tif").replace("\\", "/")
    after = os.path.abspath("tests/fixtures/after_changed.tif").replace("\\", "/")
    
    response = client.post("/api/satellite/change-detection", json={
        "before_asset_url": before,
        "after_asset_url": after
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["change_percentage"] > 0
    assert "Significant change detected" in data["summary"]

def test_change_detection_invalid_input():
    response = client.post("/api/satellite/change-detection", json={
        "before_asset_url": "",
        "after_asset_url": "valid.tif"
    })
    assert response.status_code == 400
    
def test_change_detection_inaccessible_asset():
    response = client.post("/api/satellite/change-detection", json={
        "before_asset_url": "nonexistent_before.tif",
        "after_asset_url": "nonexistent_after.tif"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "error"
    assert "Inaccessible asset or incompatible raster" in data["summary"]
