import requests
from typing import Dict, Any
from app.core.model_config import model_settings

class RemoteInferenceClient:
    def __init__(self):
        self.endpoint = model_settings.RS_VQA_ENDPOINT
        self.api_key = model_settings.RS_VQA_API_KEY
        self.timeout = model_settings.RS_VQA_TIMEOUT
        self.model = model_settings.RS_VQA_MODEL_NAME

    def infer(self, image_path: str, question: str) -> Dict[str, Any]:
        import base64
        import os
        
        encoded_image = image_path
        if os.path.exists(image_path):
            try:
                with open(image_path, "rb") as f:
                    encoded_image = base64.b64encode(f.read()).decode('utf-8')
            except Exception as e:
                # If we fail to read, just pass the path and let the server try to resolve or fail
                pass

        payload = {
            "model": self.model,
            "question": question,
            "image": encoded_image
        }
        
        if not self.endpoint:
            return {
                "status": "not_connected",
                "message": "Remote RS-LLaVA inference server endpoint is not configured."
            }

        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
            
        try:
            response = requests.post(self.endpoint, json=payload, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            return data
            
        except requests.exceptions.Timeout:
            return {
                "status": "error",
                "message": f"Connection timed out after {self.timeout}s."
            }
        except requests.exceptions.ConnectionError:
            return {
                "status": "error",
                "message": "Failed to connect to the remote RS-LLaVA server."
            }
        except requests.exceptions.HTTPError as e:
            return {
                "status": "error",
                "message": f"HTTP error occurred: {str(e)}",
                "details": response.text if 'response' in locals() else None
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"An unexpected error occurred: {str(e)}"
            }
