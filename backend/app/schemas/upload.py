from pydantic import BaseModel
from typing import Optional

class UploadResponse(BaseModel):
    success: bool
    filename: str
    original_filename: str
    message: str
    conversation_id: Optional[str] = None
    image_id: Optional[str] = None
