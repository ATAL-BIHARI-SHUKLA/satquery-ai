from typing import Dict, Any, List, Optional
from app.services.router import TaskType

def execute_vqa(resolved_images: List[str], query: str, conversation_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
    if not resolved_images or len(resolved_images) < 1:
        return {"task": TaskType.VQA, "status": "missing-input", "reason": "Requires at least 1 image."}
    return {
        "task": TaskType.VQA,
        "status": "mock",
        "answer": "Mock VQA result. Real remote-sensing model not connected yet."
    }

def execute_captioning(resolved_images: List[str], query: str, conversation_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
    if not resolved_images or len(resolved_images) < 1:
        return {"task": TaskType.CAPTIONING, "status": "missing-input", "reason": "Requires at least 1 image."}
    return {
        "task": TaskType.CAPTIONING,
        "status": "mock",
        "answer": "Mock CAPTIONING result. Real remote-sensing model not connected yet."
    }

def execute_grounding(resolved_images: List[str], query: str, conversation_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
    if not resolved_images or len(resolved_images) < 1:
        return {"task": TaskType.GROUNDING, "status": "missing-input", "reason": "Requires at least 1 image."}
    if not query or not query.strip():
        return {"task": TaskType.GROUNDING, "status": "missing-input", "reason": "Requires a query."}
    return {
        "task": TaskType.GROUNDING,
        "status": "mock",
        "answer": "Mock GROUNDING result. Real remote-sensing model not connected yet."
    }

def execute_change_analysis(resolved_images: List[str], query: str, conversation_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
    if not resolved_images or len(resolved_images) < 2:
        return {"task": TaskType.CHANGE_ANALYSIS, "status": "missing-input", "reason": "Requires at least 2 images."}
    return {
        "task": TaskType.CHANGE_ANALYSIS,
        "status": "mock",
        "answer": "Mock CHANGE_ANALYSIS result. Real change detection model not connected yet."
    }

def execute_optical_sar_analysis(resolved_images: List[str], query: str, conversation_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
    if not resolved_images or len(resolved_images) < 2:
        return {"task": TaskType.OPTICAL_SAR_ANALYSIS, "status": "missing-input", "reason": "Requires at least 2 images."}
    
    # Preserve separate images
    image_1 = resolved_images[0]
    image_2 = resolved_images[1]
    
    return {
        "task": TaskType.OPTICAL_SAR_ANALYSIS,
        "status": "mock",
        "answer": "Mock OPTICAL_SAR_ANALYSIS result. Real remote-sensing model not connected yet.",
        "image_1": image_1,
        "image_2": image_2
    }

def execute_geo_analysis(resolved_images: List[str], query: str, conversation_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
    if "location" not in context and "geospatial" not in context:
        return {"task": TaskType.GEO_ANALYSIS, "status": "missing-input", "reason": "Requires appropriate location/geospatial context."}
    return {
        "task": TaskType.GEO_ANALYSIS,
        "status": "mock",
        "answer": "Mock GEO_ANALYSIS result. Real remote-sensing model not connected yet."
    }

def execute_location_development(query: str, conversation_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
    if "latitude" not in context or "longitude" not in context:
        return {"task": TaskType.LOCATION_DEVELOPMENT_ANALYSIS, "status": "missing-input", "reason": "Requires latitude and longitude in context."}
    
    latitude = context["latitude"]
    longitude = context["longitude"]
    radius_km = context.get("radiusKm", 2.0)
    
    import re
    import math
    
    target_years = None
    match = re.search(r'(\d+)\s*(years|saal)', query, re.IGNORECASE)
    if match:
        target_years = int(match.group(1))
    
    from app.services.satellite import SatelliteDataService
    from app.services.change_detection import change_detection_service
    from app.services.land_cover import land_cover_service
    from app.services.real_estate import real_estate_service
    from app.services.evidence import evidence_service
    from app.services.answer_generator import answer_generator_service
    
    satellite_service = SatelliteDataService()
    
    try:
        # Get historical imagery
        history = satellite_service.get_historical_timeline(latitude, longitude, radius_km, target_years)
        available = [p for p in history.get("imagery", []) if p.get("available") and p.get("asset") and p.get("asset").get("url")]
        available.sort(key=lambda x: x.get("selected_date") or "")
        
        change_analysis = None
        land_cover_analysis = None
        
        if len(available) >= 2:
            oldest = available[0]
            newest = available[-1]
            try:
                change_analysis = change_detection_service.detect_change(
                    oldest.get("asset").get("url"),
                    newest.get("asset").get("url")
                )
                if change_analysis and hasattr(change_analysis, "dict"):
                    change_analysis = change_analysis.dict()
            except Exception:
                pass
                
            try:
                land_cover_analysis = land_cover_service.calculate_indicators(
                    oldest.get("asset").get("url"),
                    newest.get("asset").get("url")
                )
                if land_cover_analysis and hasattr(land_cover_analysis, "dict"):
                    land_cover_analysis = land_cover_analysis.dict()
            except Exception:
                pass
                
        oldest_imagery = available[0] if len(available) >= 1 else None
        newest_imagery = available[-1] if len(available) >= 1 else None
        
        # Calculate confidence
        confidence = "low"
        if oldest_imagery and newest_imagery:
            c1 = oldest_imagery.get("cloud_cover", 100.0)
            c2 = newest_imagery.get("cloud_cover", 100.0)
            if c1 < 20 and c2 < 20:
                confidence = "high"
            elif c1 < 50 and c2 < 50:
                confidence = "medium"
        
        summary_data = {
            "analysis_center": {"latitude": latitude, "longitude": longitude},
            "radius_km": radius_km,
            "approximate_area_sqkm": round(math.pi * (radius_km ** 2), 2),
            "confidence": confidence,
            "imagery_provider": history.get("provider", "Sentinel-2 / Earth Search"),
            "imagery_count": len(available),
            "oldest_imagery": oldest_imagery,
            "newest_imagery": newest_imagery,
            "change_analysis": change_analysis,
            "land_cover_analysis": land_cover_analysis,
            "limitations": []
        }
        
        if len(available) < 2:
            summary_data["limitations"].append("Only one usable imagery asset found. Comparison analysis requires at least two.")
        if len(available) == 0:
            summary_data["limitations"].append("No usable satellite imagery found for this location.")
            
        real_estate_data = real_estate_service.evaluate(summary_data)
        evidence_result = evidence_service.build_evidence(summary_data, real_estate_data)
        
        answer = answer_generator_service.generate_development_answer(query, evidence_result)
        
        return {
            "task": TaskType.LOCATION_DEVELOPMENT_ANALYSIS,
            "status": "success",
            "answer": answer,
            "evidence": evidence_result
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "task": TaskType.LOCATION_DEVELOPMENT_ANALYSIS,
            "status": "error",
            "reason": str(e)
        }


def execute_analysis(task: str, resolved_images: List[str], query: str, conversation_id: Optional[str] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Dispatcher that selects the appropriate specialist executor based on the task.
    """
    from app.models.registry import registry

    if context is None:
        context = {}
        
    # 1. Lookup model adapter from registry
    model = registry.find_model_for_task(task)
    if model and model.is_available():
        return model.analyze(query=query, image_paths=resolved_images, context=context)
        
    # 2. Fallback to existing mock execution logic if model unavailable
    if task == TaskType.VQA:
        return execute_vqa(resolved_images, query, conversation_id or "", context)
    elif task == TaskType.CAPTIONING:
        return execute_captioning(resolved_images, query, conversation_id or "", context)
    elif task == TaskType.GROUNDING:
        return execute_grounding(resolved_images, query, conversation_id or "", context)
    elif task == TaskType.CHANGE_ANALYSIS:
        return execute_change_analysis(resolved_images, query, conversation_id or "", context)
    elif task == TaskType.OPTICAL_SAR_ANALYSIS:
        return execute_optical_sar_analysis(resolved_images, query, conversation_id or "", context)
    elif task == TaskType.GEO_ANALYSIS:
        return execute_geo_analysis(resolved_images, query, conversation_id or "", context)
    elif task == TaskType.LOCATION_DEVELOPMENT_ANALYSIS:
        return execute_location_development(query, conversation_id or "", context)
        
    return {"task": task, "status": "missing-input", "reason": f"Unsupported task type: {task}"}
