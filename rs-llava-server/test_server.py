from fastapi.testclient import TestClient
from server import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    # We expect model_loaded to be False on this local setup
    assert "model_loaded" in data

def test_infer_missing_question():
    response = client.post("/infer", json={
        "model": "BigData-KSU/RS-llava-v1.5-7b-LoRA",
        "question": "",
        "image": "test.png"
    })
    assert response.status_code == 400
    assert "Missing question" in response.json()["detail"]

def test_infer_missing_image():
    response = client.post("/infer", json={
        "model": "BigData-KSU/RS-llava-v1.5-7b-LoRA",
        "question": "What is this?",
        "image": ""
    })
    assert response.status_code == 400
    assert "Missing image" in response.json()["detail"]

def test_infer_model_not_loaded():
    # Since the model won't load locally (no torch/llava), this should return 503
    response = client.post("/infer", json={
        "model": "BigData-KSU/RS-llava-v1.5-7b-LoRA",
        "question": "What is this?",
        "image": "test.png"
    })
    assert response.status_code == 503
    assert "Model not loaded" in response.json()["detail"]

if __name__ == "__main__":
    print("Running tests for RS-LLaVA wrapper server...")
    
    try:
        test_health()
        print("PASS: /health endpoint works.")
        
        test_infer_missing_question()
        print("PASS: Missing question validation works.")
        
        test_infer_missing_image()
        print("PASS: Missing image validation works.")
        
        test_infer_model_not_loaded()
        print("PASS: Model not loaded validation works.")
        
        print("All local wrapper tests passed!")
    except AssertionError as e:
        print("FAIL:", e)
