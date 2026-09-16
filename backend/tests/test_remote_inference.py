import pytest
import requests
from unittest.mock import patch, MagicMock
from app.models.remote_client import RemoteInferenceClient
from app.models.base import RemoteSensingVQAModel
from app.services.executor import execute_analysis
from app.services.router import TaskType

def test_remote_client_request_construction():
    client = RemoteInferenceClient()
    client.endpoint = "http://fake-endpoint:8001/infer"
    client.api_key = "fake_key"
    client.timeout = 10
    
    with patch("requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "success", "answer": "Test answer"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = client.infer("path/to/image.jpg", "What is this?")
        
        mock_post.assert_called_once_with(
            "http://fake-endpoint:8001/infer",
            json={
                "model": client.model,
                "question": "What is this?",
                "image": "path/to/image.jpg"
            },
            headers={"Authorization": "Bearer fake_key"},
            timeout=10
        )
        assert result["status"] == "success"
        assert result["answer"] == "Test answer"

def test_successful_remote_response():
    client = RemoteInferenceClient()
    client.endpoint = "http://fake"
    with patch("requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "success", "answer": "A building"}
        mock_post.return_value = mock_response
        
        result = client.infer("img.jpg", "q")
        assert result["status"] == "success"
        assert result["answer"] == "A building"

def test_connection_failure():
    client = RemoteInferenceClient()
    client.endpoint = "http://fake"
    with patch("requests.post", side_effect=requests.exceptions.ConnectionError):
        result = client.infer("img.jpg", "q")
        assert result["status"] == "error"
        assert "Failed to connect" in result["message"]

def test_http_failure():
    client = RemoteInferenceClient()
    client.endpoint = "http://fake"
    with patch("requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("500 Server Error")
        mock_post.return_value = mock_response
        
        result = client.infer("img.jpg", "q")
        assert result["status"] == "error"
        assert "HTTP error" in result["message"]

def test_invalid_response():
    client = RemoteInferenceClient()
    client.endpoint = "http://fake"
    with patch("requests.post") as mock_post:
        mock_response = MagicMock()
        # Invalid JSON
        mock_response.json.side_effect = Exception("JSON Decode Error")
        mock_post.return_value = mock_response
        
        result = client.infer("img.jpg", "q")
        assert result["status"] == "error"
        assert "unexpected error" in result["message"]

def test_empty_endpoint():
    client = RemoteInferenceClient()
    client.endpoint = ""
    result = client.infer("img.jpg", "q")
    assert result["status"] == "not_connected"
    assert "not configured" in result["message"]

def test_existing_mock_fallback():
    model = RemoteSensingVQAModel()
    # Force empty endpoint
    with patch("app.models.base.model_settings.RS_VQA_ENDPOINT", ""):
        result = model.analyze("What is this?", ["img.jpg"], {"task_type": "VQA"})
        assert result["status"] == "mock"
        assert "Fallback" in result["answer"]

def test_vqa_adapter():
    model = RemoteSensingVQAModel()
    with patch("app.models.base.model_settings.RS_VQA_ENDPOINT", "http://fake"):
        with patch("app.models.remote_client.RemoteInferenceClient.infer", return_value={"status": "success", "answer": "Real answer"}):
            result = model.analyze("What is this?", ["img.jpg"], {"task_type": "VQA"})
            assert result["status"] == "success"
            assert result["answer"] == "Real answer"

def test_captioning_adapter():
    model = RemoteSensingVQAModel()
    with patch("app.models.base.model_settings.RS_VQA_ENDPOINT", "http://fake"):
        with patch("app.models.remote_client.RemoteInferenceClient.infer", return_value={"status": "success", "answer": "Caption"}):
            result = model.analyze("Caption this", ["img.jpg"], {"task_type": "CAPTIONING"})
            assert result["status"] == "success"
            assert result["answer"] == "Caption"

def test_existing_executor_behavior():
    with patch("app.models.base.model_settings.RS_VQA_ENDPOINT", "http://fake"):
        with patch("app.models.remote_client.RemoteInferenceClient.infer", return_value={"status": "error", "message": "Connection Refused"}):
            result = execute_analysis(TaskType.VQA, ["img.jpg"], "Question", "session-1", {"task_type": "VQA"})
            assert result["status"] == "mock"
            assert "Fallback" in result["answer"]

def test_base64_image_request(tmp_path):
    client = RemoteInferenceClient()
    client.endpoint = "http://fake"
    
    # Create a dummy image file
    import base64
    img_path = tmp_path / "test.jpg"
    img_path.write_bytes(b"dummy image content")
    
    with patch("requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "success", "answer": "Test answer"}
        mock_post.return_value = mock_response
        
        client.infer(str(img_path), "What is this?")
        
        args, kwargs = mock_post.call_args
        encoded = base64.b64encode(b"dummy image content").decode('utf-8')
        assert kwargs["json"]["image"] == encoded

def test_timeout():
    client = RemoteInferenceClient()
    client.endpoint = "http://fake"
    with patch("requests.post", side_effect=requests.exceptions.Timeout):
        result = client.infer("img.jpg", "q")
        assert result["status"] == "error"
        assert "timed out" in result["message"]

def test_routing_correctness():
    from app.services.router import classify_query, TaskType
    assert classify_query("Describe this image") == TaskType.CAPTIONING
    assert classify_query("What changed here?", 2) == TaskType.CHANGE_ANALYSIS
    assert classify_query("What is this?", 1) == TaskType.VQA

