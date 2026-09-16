from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from typing import List, Optional, Any, Dict

from app.services.conversation import conversation_store
from app.core.security import get_current_user
from app.schemas.auth import UserResponse
from app.schemas.conversation import (
    Conversation, 
    Message, 
    ImageReference, 
    AnalysisReference
)

router = APIRouter(tags=["conversations"])

class MessageCreate(BaseModel):
    role: str
    text: str

class ImageReferenceCreate(BaseModel):
    filename: str
    original_filename: str
    metadata: Optional[Dict[str, Any]] = None

class AnalysisReferenceCreate(BaseModel):
    task: str
    input_image_ids: List[str]
    result: Any
    confidence: Optional[float] = None
    evidence: Optional[Any] = None

class ConversationCreate(BaseModel):
    context: Optional[Dict[str, Any]] = None

@router.post("/conversations", response_model=Conversation, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    payload: Optional[ConversationCreate] = None,
    current_user: UserResponse = Depends(get_current_user)
):
    context = payload.context if payload else None
    conv = await conversation_store.create_conversation(user_id=current_user.id, context=context)
    return conv

from app.schemas.conversation import ConversationListItem

@router.get("/conversations", response_model=List[ConversationListItem])
async def list_conversations(
    current_user: UserResponse = Depends(get_current_user)
):
    return await conversation_store.list_conversations(user_id=current_user.id)

@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    try:
        return await conversation_store.get_full_conversation(user_id=current_user.id, conversation_id=conversation_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Conversation not found")

@router.post("/conversations/{conversation_id}/messages", response_model=Message)
async def add_message(
    conversation_id: str, 
    message_in: MessageCreate,
    current_user: UserResponse = Depends(get_current_user)
):
    try:
        msg = await conversation_store.add_message(
            user_id=current_user.id,
            conversation_id=conversation_id,
            role=message_in.role,
            text=message_in.text
        )
        return msg
    except ValueError:
        raise HTTPException(status_code=404, detail="Conversation not found")

@router.post("/conversations/{conversation_id}/images", response_model=ImageReference)
async def add_image(
    conversation_id: str, 
    image_in: ImageReferenceCreate,
    current_user: UserResponse = Depends(get_current_user)
):
    try:
        img = await conversation_store.add_image_reference(
            user_id=current_user.id,
            conversation_id=conversation_id,
            filename=image_in.filename,
            original_filename=image_in.original_filename,
            metadata=image_in.metadata
        )
        return img
    except ValueError:
        raise HTTPException(status_code=404, detail="Conversation not found")

@router.post("/conversations/{conversation_id}/analyses", response_model=AnalysisReference)
async def add_analysis(
    conversation_id: str, 
    analysis_in: AnalysisReferenceCreate,
    current_user: UserResponse = Depends(get_current_user)
):
    try:
        analysis = await conversation_store.add_analysis_result(
            user_id=current_user.id,
            conversation_id=conversation_id,
            task=analysis_in.task,
            input_image_ids=analysis_in.input_image_ids,
            result=analysis_in.result,
            confidence=analysis_in.confidence,
            evidence=analysis_in.evidence
        )
        return analysis
    except ValueError:
        raise HTTPException(status_code=404, detail="Conversation not found")
