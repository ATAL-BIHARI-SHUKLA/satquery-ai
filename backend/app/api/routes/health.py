from fastapi import APIRouter
from app.schemas.health import HealthResponse
from app.core.database import db

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
def health_check():
    mongodb_status = "connected" if db.client is not None else "disconnected"
    status = "ok" if mongodb_status == "connected" else "degraded"
    return HealthResponse(status=status, service="satquery-ai", mongodb=mongodb_status)
