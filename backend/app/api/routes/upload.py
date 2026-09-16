import os
import uuid
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status, Depends
from app.core.config import settings
from app.schemas.upload import UploadResponse
from app.services.conversation import conversation_store
from app.core.security import get_current_user
from app.schemas.auth import UserResponse

router = APIRouter()

@router.post("/upload", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_image(
    file: UploadFile = File(...), 
    conversation_id: Optional[str] = Form(None),
    current_user: UserResponse = Depends(get_current_user)
):
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided in upload."
        )

    # 0. Validate conversation_id if provided
    if conversation_id:
        try:
            await conversation_store.get_full_conversation(current_user.id, conversation_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )


    # 1. Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type '{file_ext}'. Allowed formats: {', '.join(sorted(settings.ALLOWED_IMAGE_EXTENSIONS))}."
        )

    # 2. Validate MIME content-type (if provided)
    if file.content_type and file.content_type not in settings.ALLOWED_IMAGE_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid content type '{file.content_type}'. Must be an image (JPEG, PNG, WEBP)."
        )

    # 3. Read and validate file size
    contents = await file.read()
    if len(contents) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty."
        )

    if len(contents) > settings.MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds the maximum limit of {settings.MAX_FILE_SIZE_MB}MB."
        )

    # 4. Generate a unique, safe filename
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    generated_filename = f"{uuid.uuid4().hex}{file_ext}"
    target_path = settings.UPLOAD_DIR / generated_filename

    # In the extremely rare case of collision, regenerate
    while target_path.exists():
        generated_filename = f"{uuid.uuid4().hex}{file_ext}"
        target_path = settings.UPLOAD_DIR / generated_filename

    # 5. Save file locally
    with open(target_path, "wb") as f:
        f.write(contents)

    # 6. Add to conversation if provided
    image_id = None
    if conversation_id:
        img_ref = await conversation_store.add_image_reference(
            user_id=current_user.id,
            conversation_id=conversation_id,
            filename=generated_filename,
            original_filename=file.filename
        )
        image_id = img_ref.image_id

    return UploadResponse(
        success=True,
        filename=generated_filename,
        original_filename=file.filename,
        message="Image uploaded successfully",
        conversation_id=conversation_id,
        image_id=image_id
    )
