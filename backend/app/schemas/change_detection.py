from pydantic import BaseModel
from typing import Optional

class ChangeDetectionRequest(BaseModel):
    before_asset_url: str
    after_asset_url: str

class ChangeDetectionResponse(BaseModel):
    status: str
    method: str
    before_date: Optional[str] = None
    after_date: Optional[str] = None
    change_percentage: Optional[float] = None
    changed_area_available: bool
    summary: Optional[str] = None
