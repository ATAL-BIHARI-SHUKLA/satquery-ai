import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class AnswerGeneratorService:
    def __init__(self):
        pass

    def generate_development_answer(self, query: str, evidence: Dict[str, Any]) -> str:
        """
        Convert structured evidence into a natural language answer about location development.
        Requires quoting data and adding limitations.
        """
        lines = []
        
        ctx = evidence.get("analysis_context", {})
        radius = ctx.get("radius_km", 2.0)
        
        img_ev = evidence.get("imagery_evidence", {})
        oldest_date = img_ev.get("oldest_date")
        newest_date = img_ev.get("newest_date")
        
        direction = ctx.get("development_direction", "unavailable")
        if direction not in {"increased", "decreased", "stable"}:
            direction = "direction unavailable"

        if oldest_date and newest_date and oldest_date != newest_date:
            lines.append(f"Between {oldest_date} and {newest_date}, the selected {radius} km area shows {direction} development-related surface change.")
            lines.append(f"Before imagery: {oldest_date}")
            lines.append(f"After imagery: {newest_date}")
        else:
            lines.append("Comparable before-and-after imagery dates are not available for this analysis.")

        change = evidence.get("change_evidence") or {}
        change_percentage = change.get("change_percentage")
        if change_percentage is not None:
            lines.append(f"The analysis indicates approximately {change_percentage}% surface change in the selected area.")
        else:
            lines.append("A reliable quantitative change percentage could not be calculated from the available imagery.")

        lines.append("")
        
        lc_ev = evidence.get("land_cover_evidence") or {}
        built_up = lc_ev.get("built_up") or {}
        veg = lc_ev.get("vegetation") or {}
        water = lc_ev.get("water") or {}
        
        if built_up:
            lines.append("Built-up/development proxy:")
            lines.append(f"Before: {built_up.get('before')}")
            lines.append(f"After: {built_up.get('after')}")
            lines.append(f"Change: {built_up.get('change')} ({built_up.get('direction')})\n")
            
        if veg:
            lines.append("Vegetation indicator:")
            lines.append(f"Before: {veg.get('before')}, After: {veg.get('after')}, Change: {veg.get('change')} ({veg.get('direction')})\n")
            
        if water:
            lines.append("Water indicator:")
            lines.append(f"Before: {water.get('before')}, After: {water.get('after')}, Change: {water.get('change')} ({water.get('direction')})\n")
            
        re_ev = evidence.get("real_estate_evidence") or {}
        overall = re_ev.get("overall_relevance")
        trend = re_ev.get("development_trend")
        
        lines.append("Overall interpretation:")
        if overall and trend:
            lines.append(f"The area has a {trend} development trend with an overall relevance of {overall}.")
        else:
            lines.append("Satellite-based surface changes have been quantified above.")
            
        lines.append("This is a satellite-derived land-use/development proxy and should not be interpreted as an exact measurement of constructed property area.")
        
        limitations = evidence.get("limitations", [])
        if limitations:
            lines.append("Additional Limitations:")
            for lim in limitations:
                lines.append(f"- {lim}")

        return "\n".join(lines)

answer_generator_service = AnswerGeneratorService()
