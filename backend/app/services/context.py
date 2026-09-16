from typing import Dict, Any
from app.services.conversation import conversation_store

class ConversationContextResolver:
    @staticmethod
    async def resolve_context(conversation_id: str, query: str, request_context: dict = None, user_id: str = None) -> Dict[str, Any]:
        """
        Inspects an existing conversation and determines the relevant context for a query.
        """
        if request_context is None:
            request_context = {}
            
        try:
            conv_data = await conversation_store.get_full_conversation(user_id, conversation_id)
        except ValueError:
            return {"status": "error", "message": "Conversation not found"}

        messages = conv_data.get("messages", [])
        images = conv_data.get("images", [])
        analyses = conv_data.get("analyses", [])
        
        num_images = len(images)
        latest_image = images[-1] if num_images > 0 else None
        previous_image = images[-2] if num_images > 1 else None
        
        context = {
            "conversation_id": conversation_id,
            "recent_messages": messages[-10:],
            "available_images": images,
            "available_image_ids": [img["image_id"] for img in images],
            "available_analyses": analyses,
            "number_of_images": num_images,
            "latest_image": latest_image,
            "previous_image": previous_image,
            "resolved_images": [],
            "status": "ready"
        }
        
        query_lower = query.lower()
        has_location = "latitude" in request_context and "longitude" in request_context
        
        # Fallback to conversation-level context for location
        conv_context = conv_data.get("conversation", {}).get("context")
        if not has_location and conv_context:
            if "latitude" in conv_context and "longitude" in conv_context:
                request_context["latitude"] = conv_context["latitude"]
                request_context["longitude"] = conv_context["longitude"]
                if "radiusKm" in conv_context:
                    request_context["radiusKm"] = conv_context["radiusKm"]
                if "locationName" in conv_context:
                    request_context["locationName"] = conv_context["locationName"]
                has_location = True

        # Fallback to latest analysis context for location
        if not has_location and analyses:
            latest_analysis = analyses[-1]
            # Try to get evidence either directly or from result dict
            evidence = latest_analysis.get("evidence")
            if not evidence and isinstance(latest_analysis.get("result"), dict):
                evidence = latest_analysis["result"].get("evidence")
                
            if evidence:
                ev_ctx = evidence.get("analysis_context", {})
                center = ev_ctx.get("center", {})
                if "latitude" in center and "longitude" in center:
                    request_context["latitude"] = center["latitude"]
                    request_context["longitude"] = center["longitude"]
                    if "radius_km" in ev_ctx:
                        request_context["radiusKm"] = ev_ctx["radius_km"]
                    has_location = True
                    
        # Update context payload to carry forward the request_context
        for k, v in request_context.items():
            context[k] = v
        
        # Rule 3 & Combo for case 3
        if "these two images" in query_lower or "both images" in query_lower or "these images" in query_lower:
            if num_images >= 2:
                context["resolved_images"] = [latest_image, previous_image]
            elif not has_location:
                context["status"] = "missing-context"
                
        elif "previous image" in query_lower or "earlier image" in query_lower:
            if "this" in query_lower: # "compare this with previous image"
                if num_images >= 2:
                    context["resolved_images"] = [latest_image, previous_image]
                elif not has_location:
                    context["status"] = "missing-context"
            else:
                if num_images >= 2:
                    context["resolved_images"] = [previous_image]
                elif not has_location:
                    context["status"] = "missing-context"
                    
        # Rule 1
        elif "this image" in query_lower or "this" in query_lower:
            if num_images >= 1:
                context["resolved_images"] = [latest_image]
            elif not has_location:
                context["status"] = "missing-context"
                
        # Rule 5: Normal query with no explicit reference (default fallback to latest if available)
        else:
            if num_images >= 1:
                context["resolved_images"] = [latest_image]
                
        return context
