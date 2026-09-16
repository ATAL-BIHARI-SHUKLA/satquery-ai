from pydantic import BaseModel
from typing import Optional, List

class QueryRequest(BaseModel):
    query: str
    filename: Optional[str] = None
    conversation_id: Optional[str] = None
    context: Optional[dict] = None


class QueryResponse(BaseModel):
    success: bool
    query: str
    filename: Optional[str] = None
    message: str
    task: Optional[str] = None
    context_status: Optional[str] = None
    resolved_images: Optional[List[str]] = None
    execution: Optional[dict] = None
