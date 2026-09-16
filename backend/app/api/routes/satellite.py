from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from app.services.satellite import SatelliteDataService
from app.schemas.satellite import SatelliteAvailabilityResponse, SatelliteImageryResponse, SatelliteHistoryResponse, SatelliteSummaryRequest, SatelliteSummaryResponse, RealEstateRelevanceRequest, RealEstateRelevanceResponse, RealEstateIndicators, EvidenceRequest, EvidenceResponse, ImageryEvidence, ChangeEvidence, LandCoverEvidence, LandCoverEvidenceIndicator, RealEstateEvidence
from app.services.change_detection import change_detection_service
from app.schemas.change_detection import ChangeDetectionRequest, ChangeDetectionResponse
from app.schemas.land_cover import LandCoverAnalysisRequest, LandCoverAnalysisResponse
from app.services.land_cover import land_cover_service
from app.services.real_estate import real_estate_service
from app.services.evidence import evidence_service
import asyncio

router = APIRouter()
satellite_service = SatelliteDataService()

@router.get("/satellite/availability", response_model=SatelliteAvailabilityResponse)
async def check_satellite_availability(
    latitude: float = Query(..., description="Latitude"),
    longitude: float = Query(..., description="Longitude"),
    start_date: Optional[str] = Query(None, description="Optional start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Optional end date (YYYY-MM-DD)")
):
    """
    Check for available satellite imagery at the given coordinates.
    """
    if not (-90 <= latitude <= 90):
        raise HTTPException(status_code=400, detail="Invalid latitude")
    
    if not (-180 <= longitude <= 180):
        raise HTTPException(status_code=400, detail="Invalid longitude")

    try:
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            None, 
            satellite_service.check_availability, 
            latitude, 
            longitude, 
            start_date, 
            end_date
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/satellite/imagery", response_model=SatelliteImageryResponse)
async def get_satellite_imagery(
    latitude: float = Query(..., description="Latitude"),
    longitude: float = Query(..., description="Longitude"),
    target_date: Optional[str] = Query(None, description="Optional target date (YYYY-MM-DD)"),
    start_date: Optional[str] = Query(None, description="Optional start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Optional end date (YYYY-MM-DD)")
):
    """
    Get the best satellite imagery asset for the given coordinates and date parameters.
    """
    if not (-90 <= latitude <= 90):
        raise HTTPException(status_code=400, detail="Invalid latitude")
    
    if not (-180 <= longitude <= 180):
        raise HTTPException(status_code=400, detail="Invalid longitude")

    try:
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            None, 
            satellite_service.get_imagery_asset, 
            latitude, 
            longitude, 
            target_date,
            start_date, 
            end_date
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/satellite/history", response_model=SatelliteHistoryResponse)
async def get_satellite_history(
    latitude: float = Query(..., description="Latitude"),
    longitude: float = Query(..., description="Longitude")
):
    """
    Get the historical satellite imagery timeline for the given coordinates.
    Returns imagery for current, ~5 years ago, and ~10 years ago.
    """
    if not (-90 <= latitude <= 90):
        raise HTTPException(status_code=400, detail="Invalid latitude")
    
    if not (-180 <= longitude <= 180):
        raise HTTPException(status_code=400, detail="Invalid longitude")

    try:
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            None, 
            satellite_service.get_historical_timeline, 
            latitude, 
            longitude
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/satellite/change-detection", response_model=ChangeDetectionResponse)
async def post_change_detection(request: ChangeDetectionRequest):
    """
    Perform a baseline change detection between two satellite images.
    """
    if not request.before_asset_url or not request.after_asset_url:
        raise HTTPException(status_code=400, detail="Both before and after asset URLs are required.")
        
    try:
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            None,
            change_detection_service.detect_change,
            request.before_asset_url,
            request.after_asset_url
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/satellite/land-cover-analysis", response_model=LandCoverAnalysisResponse)
async def post_land_cover_analysis(request: LandCoverAnalysisRequest):
    """
    Perform a baseline land-cover indicator analysis between two satellite images.
    """
    if not request.before_asset_url or not request.after_asset_url:
        raise HTTPException(status_code=400, detail="Both before and after asset URLs are required.")
        
    try:
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            None,
            land_cover_service.calculate_indicators,
            request.before_asset_url,
            request.after_asset_url
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/satellite/summary", response_model=SatelliteSummaryResponse)
async def post_satellite_summary(request: SatelliteSummaryRequest):
    """
    Get a combined structured summary of historical imagery, change detection,
    and land cover analysis for a given location.
    """
    if not (-90 <= request.latitude <= 90):
        raise HTTPException(status_code=400, detail="Invalid latitude")
    
    if not (-180 <= request.longitude <= 180):
        raise HTTPException(status_code=400, detail="Invalid longitude")
        
    try:
        loop = asyncio.get_running_loop()
        
        # 1. Get historical imagery
        history = await loop.run_in_executor(
            None,
            satellite_service.get_historical_timeline,
            request.latitude,
            request.longitude
        )
        
        available = [p for p in history.imagery if p.available and p.asset and p.asset.url]
        # Sort chronologically
        available.sort(key=lambda x: x.selected_date or "")
        
        limitations = []
        oldest = None
        newest = None
        change_analysis = None
        land_cover_analysis = None
        
        if len(available) >= 2:
            oldest = available[0]
            newest = available[-1]
            
            # 2. Run change detection
            try:
                change_analysis = await loop.run_in_executor(
                    None,
                    change_detection_service.detect_change,
                    oldest.asset.url,
                    newest.asset.url
                )
            except Exception as e:
                limitations.append(f"Change detection failed: {str(e)}")
                
            # 3. Run land cover analysis
            try:
                land_cover_analysis = await loop.run_in_executor(
                    None,
                    land_cover_service.calculate_indicators,
                    oldest.asset.url,
                    newest.asset.url
                )
            except Exception as e:
                limitations.append(f"Land cover analysis failed: {str(e)}")
        elif len(available) == 1:
            oldest = available[0]
            newest = available[0]
            limitations.append("Only one usable imagery asset found. Comparison analysis requires at least two.")
        else:
            limitations.append("No usable satellite imagery found for this location.")
            
        return SatelliteSummaryResponse(
            latitude=request.latitude,
            longitude=request.longitude,
            imagery_count=len(available),
            oldest_imagery=oldest,
            newest_imagery=newest,
            historical_imagery=history.imagery,
            change_analysis=change_analysis,
            land_cover_analysis=land_cover_analysis,
            limitations=limitations
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/satellite/real-estate", response_model=RealEstateRelevanceResponse)
async def post_real_estate_relevance(request: RealEstateRelevanceRequest):
    """
    Get real-estate relevance indicators based on satellite analysis.
    """
    if not (-90 <= request.latitude <= 90):
        raise HTTPException(status_code=400, detail="Invalid latitude")
    
    if not (-180 <= request.longitude <= 180):
        raise HTTPException(status_code=400, detail="Invalid longitude")
        
    try:
        loop = asyncio.get_running_loop()
        
        history = await loop.run_in_executor(
            None,
            satellite_service.get_historical_timeline,
            request.latitude,
            request.longitude
        )
        
        available = [p for p in history.get("imagery", []) if p.get("available") and p.get("asset") and p.get("asset").get("url")]
        available.sort(key=lambda x: x.get("selected_date") or "")
        
        change_analysis = None
        land_cover_analysis = None
        
        if len(available) >= 2:
            oldest = available[0]
            newest = available[-1]
            try:
                change_analysis = await loop.run_in_executor(
                    None,
                    change_detection_service.detect_change,
                    oldest.get("asset").get("url"),
                    newest.get("asset").get("url")
                )
            except Exception:
                pass
                
            try:
                land_cover_analysis = await loop.run_in_executor(
                    None,
                    land_cover_service.calculate_indicators,
                    oldest.get("asset").get("url"),
                    newest.get("asset").get("url")
                )
            except Exception:
                pass
                
        summary_data = {
            "change_analysis": change_analysis.dict() if change_analysis and hasattr(change_analysis, "dict") else change_analysis,
            "land_cover_analysis": land_cover_analysis.dict() if land_cover_analysis and hasattr(land_cover_analysis, "dict") else land_cover_analysis,
            "limitations": []
        }
        
        result = real_estate_service.evaluate(summary_data)
        
        return RealEstateRelevanceResponse(
            latitude=request.latitude,
            longitude=request.longitude,
            status=result["status"],
            indicators=RealEstateIndicators(**result["indicators"]),
            reasons=result["reasons"],
            limitations=result["limitations"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/satellite/evidence", response_model=EvidenceResponse)
async def post_satellite_evidence(request: EvidenceRequest):
    """
    Get the structured evidence layer for location analysis.
    """
    if not (-90 <= request.latitude <= 90):
        raise HTTPException(status_code=400, detail="Invalid latitude")
    
    if not (-180 <= request.longitude <= 180):
        raise HTTPException(status_code=400, detail="Invalid longitude")
        
    try:
        loop = asyncio.get_running_loop()
        
        history = await loop.run_in_executor(
            None,
            satellite_service.get_historical_timeline,
            request.latitude,
            request.longitude
        )
        
        available = [p for p in history.get("imagery", []) if p.get("available") and p.get("asset") and p.get("asset").get("url")]
        available.sort(key=lambda x: x.get("selected_date") or "")
        
        change_analysis = None
        land_cover_analysis = None
        
        if len(available) >= 2:
            oldest = available[0]
            newest = available[-1]
            try:
                change_analysis = await loop.run_in_executor(
                    None,
                    change_detection_service.detect_change,
                    oldest.get("asset").get("url"),
                    newest.get("asset").get("url")
                )
            except Exception:
                pass
                
            try:
                land_cover_analysis = await loop.run_in_executor(
                    None,
                    land_cover_service.calculate_indicators,
                    oldest.get("asset").get("url"),
                    newest.get("asset").get("url")
                )
            except Exception:
                pass
                
        oldest_imagery = available[0] if len(available) >= 1 else None
        newest_imagery = available[-1] if len(available) >= 1 else None
        
        summary_data = {
            "imagery_count": len(available),
            "oldest_imagery": oldest_imagery,
            "newest_imagery": newest_imagery,
            "change_analysis": change_analysis.dict() if change_analysis and hasattr(change_analysis, "dict") else change_analysis,
            "land_cover_analysis": land_cover_analysis.dict() if land_cover_analysis and hasattr(land_cover_analysis, "dict") else land_cover_analysis,
            "limitations": []
        }
        
        if len(available) < 2:
            summary_data["limitations"].append("Only one usable imagery asset found. Comparison analysis requires at least two.")
        if len(available) == 0:
            summary_data["limitations"].append("No usable satellite imagery found for this location.")
            
        real_estate_data = real_estate_service.evaluate(summary_data)
        evidence_result = evidence_service.build_evidence(summary_data, real_estate_data)
        
        ie_data = evidence_result.get("imagery_evidence", {})
        imagery_evidence = ImageryEvidence(**ie_data)
        
        change_evidence = None
        if evidence_result.get("change_evidence"):
            change_evidence = ChangeEvidence(**evidence_result["change_evidence"])
            
        land_cover_evidence = None
        if evidence_result.get("land_cover_evidence"):
            lc_data = evidence_result["land_cover_evidence"]
            
            veg = None
            if lc_data.get("vegetation"):
                veg = LandCoverEvidenceIndicator(**lc_data["vegetation"])
                
            water = None
            if lc_data.get("water"):
                water = LandCoverEvidenceIndicator(**lc_data["water"])
                
            built_up = None
            if lc_data.get("built_up"):
                built_up = LandCoverEvidenceIndicator(**lc_data["built_up"])
                
            land_cover_evidence = LandCoverEvidence(
                vegetation=veg,
                water=water,
                built_up=built_up,
                method=lc_data.get("method")
            )
            
        real_estate_evidence = None
        if evidence_result.get("real_estate_evidence"):
            real_estate_evidence = RealEstateEvidence(**evidence_result["real_estate_evidence"])
            
        return EvidenceResponse(
            latitude=request.latitude,
            longitude=request.longitude,
            imagery_evidence=imagery_evidence,
            change_evidence=change_evidence,
            land_cover_evidence=land_cover_evidence,
            real_estate_evidence=real_estate_evidence,
            limitations=evidence_result.get("limitations", []),
            evidence_summary=evidence_result.get("evidence_summary", [])
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
