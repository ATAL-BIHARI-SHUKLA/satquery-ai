from fastapi import APIRouter, HTTPException, status, Depends
from app.schemas.query import QueryRequest, QueryResponse
from app.services.conversation import conversation_store
from app.services.router import route_query
from app.services.context import ConversationContextResolver
from app.core.security import get_current_user
from app.schemas.auth import UserResponse
import json

router = APIRouter()

@router.post("/query", response_model=QueryResponse, status_code=status.HTTP_200_OK)
async def process_query(
    request: QueryRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    if not request.filename and not request.context and not request.conversation_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either filename, context, or conversation_id must be provided"
        )
    if not request.query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query cannot be empty"
        )

    if request.conversation_id:
        try:
            await conversation_store.get_full_conversation(current_user.id, request.conversation_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
            
        # Store user message
        await conversation_store.add_message(
            user_id=current_user.id,
            conversation_id=request.conversation_id,
            role="user",
            text=request.query
        )
        
        # 1. Run context resolver
        context_result = await ConversationContextResolver.resolve_context(
            conversation_id=request.conversation_id, 
            query=request.query, 
            request_context=request.context,
            user_id=current_user.id
        )
        context_status = context_result["status"]
        
        if context_status == "missing-context":
            # Missing context -> abort routing
            assistant_reply = "Missing required context/images to answer this query."
            await conversation_store.add_message(
                user_id=current_user.id,
                conversation_id=request.conversation_id,
                role="assistant",
                text=assistant_reply
            )
            return QueryResponse(
                success=False,
                filename=request.filename,
                query=request.query,
                message=assistant_reply,
                context_status="missing-context",
                resolved_images=[]
            )
            
        else:
            # Context is ready
            resolved_images_list = context_result.get("resolved_images", [])
            resolved_images = [img["filename"] for img in resolved_images_list]
            
            router_inputs = {"query": request.query}
            
            if resolved_images:
                router_inputs["image"] = resolved_images[0]
                router_inputs["images"] = resolved_images
                if len(resolved_images) >= 2:
                    router_inputs["image_1"] = resolved_images[0]
                    router_inputs["image_2"] = resolved_images[1]
            else:
                router_inputs["image"] = request.filename
                router_inputs["images"] = [request.filename] if request.filename else []

            
            # Combine request.context and context_result for location
            enriched_context = {}
            if request.context:
                # Handle Pydantic model vs dict
                req_ctx_dict = request.context.model_dump() if hasattr(request.context, "model_dump") else (request.context.dict() if hasattr(request.context, "dict") else request.context)
                enriched_context.update(req_ctx_dict)
                
            if "latitude" in context_result and "longitude" in context_result:
                enriched_context["latitude"] = context_result["latitude"]
                enriched_context["longitude"] = context_result["longitude"]
                if "radiusKm" in context_result:
                    enriched_context["radiusKm"] = context_result["radiusKm"]
            
            router_inputs["context"] = enriched_context
            
            # 2. Run the query router
            router_result = route_query(request.query, router_inputs)
            task = router_result["task"]
            
            # 3. Call execute_analysis
            from app.services.executor import execute_analysis
            execution_result = execute_analysis(
                task=task,
                resolved_images=resolved_images,
                query=request.query,
                conversation_id=request.conversation_id,
                context=enriched_context
            )
            
            # 4. Store the executor result in the conversation
            conv_images = await conversation_store.get_conversation_images(current_user.id, request.conversation_id)
            input_image_ids = []
            for img in conv_images:
                if img.filename in resolved_images:
                    input_image_ids.append(img.image_id)
            
            await conversation_store.add_analysis_result(
                user_id=current_user.id,
                conversation_id=request.conversation_id,
                task=task,
                input_image_ids=input_image_ids,
                result=execution_result,
            )
            
            assistant_reply = json.dumps(execution_result)
            await conversation_store.add_message(
                user_id=current_user.id,
                conversation_id=request.conversation_id,
                role="assistant",
                text=assistant_reply
            )
            
            return QueryResponse(
                success=True,
                filename=request.filename,
                query=request.query,
                message="Query received successfully",
                task=task,
                context_status=context_status,
                resolved_images=resolved_images,
                execution=execution_result
            )
            
    else:
        # NO conversation_id provided -> Preserve existing behavior
        router_result = route_query(request.query, {
            "image": request.filename,
            "images": [request.filename],
            "query": request.query,
            "context": request.context or {}
        })
        
        return QueryResponse(
            success=True,
            filename=request.filename,
            query=request.query,
            message="Query received successfully"
        )
