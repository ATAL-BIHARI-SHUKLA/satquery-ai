from pydantic import BaseModel
from typing import List, Optional, Any
from app.schemas.change_detection import ChangeDetectionResponse
from app.schemas.land_cover import LandCoverAnalysisResponse

class ImageryInfo(BaseModel):
    date: Optional[str]
    source: Optional[str]
    cloud_cover: Optional[float]

class SatelliteAvailabilityResponse(BaseModel):
    latitude: float
    longitude: float
    available: bool
    provider: str
    imagery: List[ImageryInfo]
    error: Optional[str] = None

class AssetInfo(BaseModel):
    type: str
    url: str
    media_type: Optional[str] = None

class SatelliteImageryResponse(BaseModel):
    latitude: float
    longitude: float
    provider: str
    available: Optional[bool] = None
    reason: Optional[str] = None
    selected_date: Optional[str] = None
    cloud_cover: Optional[float] = None
    asset: Optional[AssetInfo] = None

class HistoricalPeriod(BaseModel):
    period: str
    target_date: str
    available: bool
    reason: Optional[str] = None
    selected_date: Optional[str] = None
    cloud_cover: Optional[float] = None
    asset: Optional[AssetInfo] = None

class SatelliteHistoryResponse(BaseModel):
    latitude: float
    longitude: float
    provider: str
    imagery: List[HistoricalPeriod]
    error: Optional[str] = None

class SatelliteSummaryRequest(BaseModel):
    latitude: float
    longitude: float

class SatelliteSummaryResponse(BaseModel):
    latitude: float
    longitude: float
    imagery_count: int
    oldest_imagery: Optional[HistoricalPeriod] = None
    newest_imagery: Optional[HistoricalPeriod] = None
    historical_imagery: List[HistoricalPeriod]
    change_analysis: Optional[ChangeDetectionResponse] = None
    land_cover_analysis: Optional[LandCoverAnalysisResponse] = None
    limitations: List[str] = []

class RealEstateRelevanceRequest(BaseModel):
    latitude: float
    longitude: float

class RealEstateIndicators(BaseModel):
    development_activity: str
    built_up_presence: str
    vegetation_presence: str
    water_presence: str
    development_trend: str
    overall_relevance: str

class RealEstateRelevanceResponse(BaseModel):
    latitude: float
    longitude: float
    status: str
    indicators: RealEstateIndicators
    reasons: List[str]
    limitations: List[str]

class ImageryEvidence(BaseModel):
    oldest_date: Optional[str] = None
    newest_date: Optional[str] = None
    provider: Optional[str] = None
    oldest_cloud_cover: Optional[float] = None
    newest_cloud_cover: Optional[float] = None
    oldest_asset_url: Optional[str] = None
    newest_asset_url: Optional[str] = None

class ChangeEvidence(BaseModel):
    before_asset_url: Optional[str] = None
    after_asset_url: Optional[str] = None
    change_percentage: Optional[float] = None
    change_summary: Optional[str] = None
    method: Optional[str] = None

class LandCoverEvidenceIndicator(BaseModel):
    before: Optional[float] = None
    after: Optional[float] = None
    change: Optional[float] = None
    direction: Optional[str] = None

class LandCoverEvidence(BaseModel):
    vegetation: Optional[LandCoverEvidenceIndicator] = None
    water: Optional[LandCoverEvidenceIndicator] = None
    built_up: Optional[LandCoverEvidenceIndicator] = None
    method: Optional[str] = None

class RealEstateEvidence(BaseModel):
    development_activity: str
    built_up_presence: str
    vegetation_presence: str
    water_presence: str
    development_trend: str
    overall_relevance: str
    reasons: List[str]

class EvidenceRequest(BaseModel):
    latitude: float
    longitude: float

class EvidenceResponse(BaseModel):
    latitude: float
    longitude: float
    imagery_evidence: ImageryEvidence
    change_evidence: Optional[ChangeEvidence] = None
    land_cover_evidence: Optional[LandCoverEvidence] = None
    real_estate_evidence: Optional[RealEstateEvidence] = None
    limitations: List[str] = []
    evidence_summary: List[str] = []
