import re
from typing import List, Dict, Any

class TaskType:
    VQA = "VQA"
    CAPTIONING = "CAPTIONING"
    GROUNDING = "GROUNDING"
    CHANGE_ANALYSIS = "CHANGE_ANALYSIS"
    OPTICAL_SAR_ANALYSIS = "OPTICAL_SAR_ANALYSIS"
    GEO_ANALYSIS = "GEO_ANALYSIS"
    LOCATION_DEVELOPMENT_ANALYSIS = "LOCATION_DEVELOPMENT_ANALYSIS"

def classify_query(query: str, num_resolved_images: int = 1, has_location_context: bool = False) -> str:
    q = query.lower()

    # A location conversation without uploaded imagery should use the
    # location-analysis workflow rather than falling back to image VQA.
    if has_location_context and num_resolved_images == 0:
        return TaskType.LOCATION_DEVELOPMENT_ANALYSIS
    
    # 0. LOCATION_DEVELOPMENT_ANALYSIS
    if has_location_context:
        dev_keywords = ["development", "develop", "construction", "growth", "build", "change"]
        if any(kw in q for kw in dev_keywords):
            return TaskType.LOCATION_DEVELOPMENT_ANALYSIS
    
    # 1. OPTICAL_SAR_ANALYSIS
    if "sar" in q or "radar" in q:
        return TaskType.OPTICAL_SAR_ANALYSIS
        
    # 2. CHANGE_ANALYSIS
    change_keywords = ["change", "difference", "compare", "new"]
    if any(kw in q for kw in change_keywords):
        if num_resolved_images >= 2:
            return TaskType.CHANGE_ANALYSIS
        
    # 3. GEO_ANALYSIS
    if "area" in q or "near" in q or "region" in q or "map" in q:
        return TaskType.GEO_ANALYSIS
        
    # 4. GROUNDING
    if "where is" in q or "locate" in q or "find" in q:
        return TaskType.GROUNDING
        
    # 5. CAPTIONING
    if "describe" in q or "caption" in q or "summarize" in q:
        return TaskType.CAPTIONING
        
    # 6. Default to VQA
    return TaskType.VQA


def route_query(query: str, available_inputs: Dict[str, Any]) -> Dict[str, Any]:
    num_resolved_images = len(available_inputs.get("images", [])) if "images" in available_inputs else 1
    
    has_location_context = False
    if "latitude" in available_inputs and "longitude" in available_inputs:
        has_location_context = True
    elif "context" in available_inputs:
        ctx = available_inputs["context"]
        if isinstance(ctx, dict) and "latitude" in ctx and "longitude" in ctx:
            has_location_context = True
            
    task = classify_query(query, num_resolved_images, has_location_context)
    
    required_inputs = []
    if task == TaskType.VQA:
        required_inputs = ["image", "query"]
    elif task == TaskType.CAPTIONING:
        required_inputs = ["image"]
    elif task == TaskType.GROUNDING:
        required_inputs = ["image", "query"]
    elif task == TaskType.CHANGE_ANALYSIS:
        required_inputs = ["image_1", "image_2"]
    elif task == TaskType.OPTICAL_SAR_ANALYSIS:
        required_inputs = ["optical_image", "sar_image"]
    elif task == TaskType.GEO_ANALYSIS:
        required_inputs = ["location_data"]
    elif task == TaskType.LOCATION_DEVELOPMENT_ANALYSIS:
        required_inputs = ["context"]
        
    missing_inputs = [req for req in required_inputs if not available_inputs.get(req)]
    
    if missing_inputs:
        return {
            "task": task,
            "required_inputs": required_inputs,
            "status": f"missing inputs: {', '.join(missing_inputs)}"
        }
        
    return {
        "task": task,
        "required_inputs": required_inputs,
        "status": "ready"
    }
