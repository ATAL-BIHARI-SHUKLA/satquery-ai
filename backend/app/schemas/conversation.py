from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import datetime, timezone
import uuid

def generate_uuid():
    return str(uuid.uuid4())

def get_now():
    return datetime.now(timezone.utc)

class Message(BaseModel):
    message_id: str = Field(default_factory=generate_uuid)
    conversation_id: str
    role: str  # "user" or "assistant"
    text: str
    timestamp: datetime = Field(default_factory=get_now)

class ImageReference(BaseModel):
    image_id: str = Field(default_factory=generate_uuid)
    conversation_id: str
    filename: str
    original_filename: str
    timestamp: datetime = Field(default_factory=get_now)
    metadata: Optional[Dict[str, Any]] = None

class AnalysisReference(BaseModel):
    analysis_id: str = Field(default_factory=generate_uuid)
    conversation_id: str
    task: str
    input_image_ids: List[str]
    result: Any
    confidence: Optional[float] = None
    evidence: Optional[Any] = None
    timestamp: datetime = Field(default_factory=get_now)

class Conversation(BaseModel):
    conversation_id: str = Field(default_factory=generate_uuid)
    user_id: str  # Owner of the conversation
    created_at: datetime = Field(default_factory=get_now)
    updated_at: datetime = Field(default_factory=get_now)
    context: Optional[Dict[str, Any]] = None

class ConversationListItem(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
