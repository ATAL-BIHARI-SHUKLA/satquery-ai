import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class EvidenceService:
    def __init__(self):
        pass

    def build_evidence(self, summary_data: Dict[str, Any], real_estate_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build an evidence response from the output of the satellite summary and real estate services.
        summary_data and real_estate_data should be dictionary representations of their respective responses.
        """
        response = {
            "imagery_evidence": {},
            "change_evidence": None,
            "land_cover_evidence": None,
            "real_estate_evidence": None,
            "limitations": [],
            "evidence_summary": []
        }

        # Handle limitations
        limitations = []
        if summary_data and summary_data.get("limitations"):
            limitations.extend(summary_data["limitations"])
        if real_estate_data and real_estate_data.get("limitations"):
            limitations.extend(real_estate_data["limitations"])
            
        # Remove duplicates while preserving order
        unique_limitations = []
        for lim in limitations:
            if lim not in unique_limitations:
                unique_limitations.append(lim)
        response["limitations"] = unique_limitations

        evidence_summary_points = []

        if not summary_data:
            response["limitations"].append("No satellite summary data available.")
            return response
            
        # Context Evidence
        analysis_center = summary_data.get("analysis_center")
        radius_km = summary_data.get("radius_km")
        area = summary_data.get("approximate_area_sqkm")
        confidence = summary_data.get("confidence")
        imagery_count = summary_data.get("imagery_count", 0)
        has_analysis_result = bool(
            summary_data.get("change_analysis")
            or (summary_data.get("land_cover_analysis") or {}).get("indicators")
        )
        baseline_confidence = "Moderate" if imagery_count >= 2 and has_analysis_result else "Low"
        
        response["analysis_context"] = {
            "center": analysis_center,
            "radius_km": radius_km,
            "approximate_area_sqkm": area,
            "confidence": confidence,
            "baseline_confidence": baseline_confidence,
        }
        if radius_km and area:
            evidence_summary_points.append(f"Analyzed an approximate area of {area} km² within a {radius_km} km radius.")
        if confidence:
            evidence_summary_points.append(f"Analysis confidence is {confidence} based on image quality/cloud cover.")

        # 1. Imagery Evidence
        oldest = summary_data.get("oldest_imagery") or {}
        newest = summary_data.get("newest_imagery") or {}
        
        provider = summary_data.get("imagery_provider")
        if oldest and oldest.get("provider"):
            provider = oldest.get("provider")
        elif newest and newest.get("provider"):
            provider = newest.get("provider")

        oldest_date = oldest.get("selected_date")
        newest_date = newest.get("selected_date")

        response["imagery_evidence"] = {
            "oldest_date": oldest_date,
            "newest_date": newest_date,
            "provider": provider,
            "oldest_cloud_cover": oldest.get("cloud_cover"),
            "newest_cloud_cover": newest.get("cloud_cover"),
            "oldest_asset_url": oldest.get("asset", {}).get("url") if oldest and oldest.get("asset") else None,
            "newest_asset_url": newest.get("asset", {}).get("url") if newest and newest.get("asset") else None,
            "source": provider or "Sentinel-2 / Earth Search",
        }
        
        if imagery_count > 0:
            evidence_summary_points.append(f"Found {imagery_count} historical imagery records for this location.")
            if oldest_date and newest_date and oldest_date != newest_date:
                evidence_summary_points.append(f"Imagery spans from {oldest_date} to {newest_date}.")
        else:
            evidence_summary_points.append("No historical satellite imagery available to analyze.")

        # 2. Change Evidence
        change = summary_data.get("change_analysis")
        if change:
            change_percentage = change.get("change_percentage")
            response["change_evidence"] = {
                "before_asset_url": response["imagery_evidence"]["oldest_asset_url"],
                "after_asset_url": response["imagery_evidence"]["newest_asset_url"],
                "change_percentage": change_percentage,
                "change_summary": change.get("summary"),
                "method": change.get("method")
            }
            if change_percentage is not None:
                evidence_summary_points.append(f"A baseline change detection measured {change_percentage}% pixel difference between the oldest and newest imagery.")

        # 3. Land Cover Evidence
        land_cover = summary_data.get("land_cover_analysis")
        if land_cover and land_cover.get("indicators"):
            indicators = land_cover.get("indicators", {})
            response["land_cover_evidence"] = {
                "vegetation": indicators.get("vegetation"),
                "water": indicators.get("water"),
                "built_up": indicators.get("built_up"),
                "method": land_cover.get("method")
            }
            
            built_up = indicators.get("built_up", {})
            if built_up and built_up.get("direction"):
                evidence_summary_points.append(f"Built-up proxy spectral indicator has {built_up.get('direction')} over time.")
                response["analysis_context"]["development_direction"] = built_up.get("direction")
                
            vegetation = indicators.get("vegetation", {})
            if vegetation and vegetation.get("direction"):
                evidence_summary_points.append(f"Vegetation proxy spectral indicator has {vegetation.get('direction')} over time.")

        # 4. Real Estate Evidence
        if real_estate_data and real_estate_data.get("indicators"):
            re_indicators = real_estate_data.get("indicators", {})
            response["real_estate_evidence"] = {
                "development_activity": re_indicators.get("development_activity", "unavailable"),
                "built_up_presence": re_indicators.get("built_up_presence", "unavailable"),
                "vegetation_presence": re_indicators.get("vegetation_presence", "unavailable"),
                "water_presence": re_indicators.get("water_presence", "unavailable"),
                "development_trend": re_indicators.get("development_trend", "unavailable"),
                "overall_relevance": re_indicators.get("overall_relevance", "unavailable"),
                "reasons": real_estate_data.get("reasons", [])
            }
            
            overall = re_indicators.get("overall_relevance")
            if overall and overall != "unavailable":
                evidence_summary_points.append(f"Assessed overall development relevance is {overall}.")

        response["evidence_summary"] = evidence_summary_points
        response["analysis_context"].setdefault("development_direction", "unavailable")
        return response

evidence_service = EvidenceService()
