from typing import List, Dict, Any, Optional
from app.core.model_config import model_settings
from app.models.remote_client import RemoteInferenceClient
class SpecialistModel:
    model_name: str = "BaseModel"
    supported_tasks: List[str] = []

    def is_available(self) -> bool:
        return False

    def analyze(self, query: str, image_paths: List[str], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {
            "status": "unavailable",
            "reason": "Real model is not connected yet."
        }

class RemoteSensingVQAModel(SpecialistModel):
    @property
    def model_name(self) -> str:
        return model_settings.RS_VQA_MODEL_NAME

    supported_tasks = ["VQA", "CAPTIONING"]

    def is_available(self) -> bool:
        return bool(model_settings.RS_VQA_ENDPOINT)

    def _infer_remote(self, query: str, image_paths: List[str], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not self.is_available():
            return {
                "status": "unavailable",
                "reason": "Remote RS-LLaVA inference endpoint is not connected yet."
            }
        
        client = RemoteInferenceClient()
        # VQA typically uses one image. We'll pass the first image.
        image_path = image_paths[0] if image_paths else ""
        return client.infer(image_path, query)

    def analyze(self, query: str, image_paths: List[str], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        task = context.get("task_type", "VQA") if context else "VQA"
        if task == "CAPTIONING" and not query:
            query = "Describe this satellite image in detail."
            
        result = self._infer_remote(query, image_paths, context)
        
        # If the remote call failed due to connection error or not connected,
        # we can indicate a fallback is needed. We'll handle this directly here
        # or return a specific status so the executor knows.
        # But wait, the executor expects analyze to return the final result.
        # So if we fallback here, we need to return the mock.
        if result.get("status") in ["error", "not_connected", "unavailable"]:
            # Perform fallback manually here to avoid crashing
            task = context.get("task_type", "VQA") if context else "VQA"
            return {
                "task": task,
                "status": "mock",
                "answer": f"Mock {task} result. (Fallback due to: {result.get('message', result.get('reason', 'Unknown error'))})"
            }
            
        # Standardize the output for the executor/router
        task = context.get("task_type", "VQA") if context else "VQA"
        return {
            "task": task,
            "status": "success",
            "answer": result.get("answer", ""),
            "metadata": result
        }

class ChangeDetectionModel(SpecialistModel):
    model_name = "ChangeDetectionModel"
    supported_tasks = ["CHANGE_ANALYSIS"]

class OpticalSARModel(SpecialistModel):
    model_name = "OpticalSARModel"
    supported_tasks = ["OPTICAL_SAR_ANALYSIS"]

class GroundingModel(SpecialistModel):
    model_name = "GroundingModel"
    supported_tasks = ["GROUNDING"]

class GeoAnalysisModel(SpecialistModel):
    model_name = "GeoAnalysisModel"
    supported_tasks = ["GEO_ANALYSIS"]
