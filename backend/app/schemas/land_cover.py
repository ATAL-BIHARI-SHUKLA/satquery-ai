from pydantic import BaseModel
from typing import Optional, Dict, Any, List

class LandCoverAnalysisRequest(BaseModel):
    before_asset_url: str
    after_asset_url: str

class IndicatorResult(BaseModel):
    before: Optional[float]
    after: Optional[float]
    change: Optional[float]
    direction: Optional[str]

class LandCoverIndicators(BaseModel):
    vegetation: Optional[IndicatorResult] = None
    water: Optional[IndicatorResult] = None
    built_up: Optional[IndicatorResult] = None

class LandCoverAnalysisResponse(BaseModel):
    status: str
    method: Optional[str] = "baseline_land_cover_indicators"
    before_date: Optional[str] = None
    after_date: Optional[str] = None
    summary: Optional[str] = None
    indicators: Optional[LandCoverIndicators] = None
    limitations: Optional[List[str]] = None
