import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class RealEstateRelevanceService:
    def __init__(self):
        pass

    def evaluate(self, summary_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate real estate relevance using existing satellite summary data.
        summary_data is expected to be a dict representation of SatelliteSummaryResponse.
        """
        response = {
            "status": "success",
            "indicators": {
                "development_activity": "unavailable",
                "built_up_presence": "unavailable",
                "vegetation_presence": "unavailable",
                "water_presence": "unavailable",
                "development_trend": "unavailable",
                "overall_relevance": "unavailable",
            },
            "reasons": [],
            "limitations": [
                "This is a satellite-derived land-use proxy, NOT a financial or market analysis.",
                "Does not predict exact property prices, market value, ROI, or investment returns."
            ]
        }

        limitations = summary_data.get("limitations", [])
        if limitations:
            response["limitations"].extend(limitations)
        
        change_analysis = summary_data.get("change_analysis")
        land_cover = summary_data.get("land_cover_analysis")

        if not land_cover or not land_cover.get("indicators"):
            response["reasons"].append("Insufficient spectral data to compute relevance indicators.")
            response["status"] = "error" if not change_analysis else "partial"
            return response

        indicators = land_cover.get("indicators", {})
        vegetation = indicators.get("vegetation", {})
        water = indicators.get("water", {})
        built_up = indicators.get("built_up", {})
        
        # 1. Built-up Presence (based on after value)
        built_after = built_up.get("after", 0.0)
        if built_after > 0.1:
            built_presence = "high"
        elif built_after > 0.0:
            built_presence = "medium"
        else:
            built_presence = "low"
        response["indicators"]["built_up_presence"] = built_presence
        response["reasons"].append(f"Built-up proxy indicator is {built_presence} ({built_after}).")

        # 2. Vegetation Presence
        veg_after = vegetation.get("after", 0.0)
        if veg_after > 0.3:
            veg_presence = "high"
        elif veg_after > 0.1:
            veg_presence = "medium"
        else:
            veg_presence = "low"
        response["indicators"]["vegetation_presence"] = veg_presence
        response["reasons"].append(f"Vegetation indicator is {veg_presence} ({veg_after}).")
        
        # 3. Water Proximity/Presence
        water_after = water.get("after", 0.0)
        if water_after > 0.1:
            water_presence = "high"
        elif water_after > 0.0:
            water_presence = "medium"
        else:
            water_presence = "low"
        response["indicators"]["water_presence"] = water_presence
        response["reasons"].append(f"Water indicator is {water_presence} ({water_after}).")

        # 4. Development Trend
        trend = built_up.get("direction", "unavailable")
        response["indicators"]["development_trend"] = trend
        
        # 5. Development Activity
        change_pct = 0.0
        if change_analysis and change_analysis.get("change_percentage") is not None:
            change_pct = change_analysis.get("change_percentage")
            
        if change_pct > 10.0 and trend == "increased":
            dev_activity = "high"
        elif change_pct > 5.0:
            dev_activity = "medium"
        else:
            dev_activity = "low"
        response["indicators"]["development_activity"] = dev_activity
        response["reasons"].append(f"Overall change is {change_pct}% with a {trend} built-up trend.")

        # 6. Overall Development Relevance
        if dev_activity == "high" or built_presence == "high":
            overall = "high"
        elif dev_activity == "medium" or built_presence == "medium":
            overall = "medium"
        else:
            overall = "low"
            
        response["indicators"]["overall_relevance"] = overall
        response["reasons"].append(f"Overall development relevance assessed as {overall}.")

        return response

real_estate_service = RealEstateRelevanceService()
