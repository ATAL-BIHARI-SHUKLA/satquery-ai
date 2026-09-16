import json
import urllib.request
import urllib.error
from typing import Optional, Dict, Any
import logging
from datetime import datetime, timedelta, timezone
logger = logging.getLogger(__name__)
import math

class SatelliteDataService:
    def __init__(self, stac_url: str = "https://earth-search.aws.element84.com/v1/search"):
        self.stac_url = stac_url

    def _get_bbox(self, latitude: float, longitude: float, radius_km: float) -> list:
        # 1 degree of latitude is ~111.32 km
        d_lat = radius_km / 111.32
        # 1 degree of longitude is ~111.32 * cos(lat) km
        d_lon = radius_km / (111.32 * math.cos(math.radians(latitude)))
        return [longitude - d_lon, latitude - d_lat, longitude + d_lon, latitude + d_lat]

    def check_availability(
        self, 
        latitude: float, 
        longitude: float, 
        start_date: Optional[str] = None, 
        end_date: Optional[str] = None,
        radius_km: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Check for available satellite imagery given latitude and longitude.
        Uses Earth Search STAC API (Sentinel-2 L2A).
        """
        payload = {
            "collections": ["sentinel-2-l2a"],
            "limit": 5,
            "sortby": [{"field": "properties.datetime", "direction": "desc"}]
        }
        
        if radius_km:
            payload["bbox"] = self._get_bbox(latitude, longitude, radius_km)
        else:
            payload["intersects"] = {
                "type": "Point",
                "coordinates": [longitude, latitude]
            }

        if start_date and end_date:
            payload["datetime"] = f"{start_date}T00:00:00Z/{end_date}T23:59:59Z"
        elif start_date:
            payload["datetime"] = f"{start_date}T00:00:00Z/.."
        elif end_date:
            payload["datetime"] = f"../{end_date}T23:59:59Z"

        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            self.stac_url, 
            data=data, 
            headers={"Content-Type": "application/json"}
        )

        response_data = {
            "latitude": latitude,
            "longitude": longitude,
            "available": False,
            "provider": "Earth Search (Sentinel-2)",
            "imagery": []
        }

        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode('utf-8'))
                features = result.get("features", [])
                
                imagery = []
                for feat in features:
                    props = feat.get("properties", {})
                    imagery.append({
                        "date": props.get("datetime"),
                        "source": feat.get("collection"),
                        "cloud_cover": props.get("eo:cloud_cover")
                    })
                
                response_data["available"] = len(imagery) > 0
                response_data["imagery"] = imagery

        except urllib.error.URLError as e:
            logger.error(f"Satellite API request failed: {e}")
            response_data["error"] = "Provider unavailable"
        except Exception as e:
            logger.error(f"Unexpected error checking satellite availability: {e}")
            response_data["error"] = "Internal error checking availability"

        return response_data

    def get_imagery_asset(
        self,
        latitude: float,
        longitude: float,
        target_date: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        radius_km: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Retrieve a single usable satellite image asset URL near the requested date.
        Prefers lower cloud cover.
        """
        payload = {
            "collections": ["sentinel-2-l2a"],
            "limit": 10,
            "sortby": [{"field": "properties.eo:cloud_cover", "direction": "asc"}]
        }

        if radius_km:
            payload["bbox"] = self._get_bbox(latitude, longitude, radius_km)
        else:
            payload["intersects"] = {
                "type": "Point",
                "coordinates": [longitude, latitude]
            }

        if start_date and end_date:
            payload["datetime"] = f"{start_date}T00:00:00Z/{end_date}T23:59:59Z"
        elif start_date:
            payload["datetime"] = f"{start_date}T00:00:00Z/.."
        elif end_date:
            payload["datetime"] = f"../{end_date}T23:59:59Z"
        elif target_date:
            payload["datetime"] = f"{target_date}T00:00:00Z/{target_date}T23:59:59Z"

        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            self.stac_url, 
            data=data, 
            headers={"Content-Type": "application/json"}
        )

        response_data = {
            "latitude": latitude,
            "longitude": longitude,
            "provider": "Earth Search (Sentinel-2)",
        }

        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode('utf-8'))
                features = result.get("features", [])
                
                if not features:
                    response_data["available"] = False
                    response_data["reason"] = "No imagery found for the specified location and dates."
                    return response_data
                
                best_feature = features[0]
                props = best_feature.get("properties", {})
                assets = best_feature.get("assets", {})
                
                asset = assets.get("visual") or assets.get("thumbnail") or assets.get("rendered_preview")
                if not asset:
                    asset_key = next(iter(assets.keys()), None)
                    if asset_key:
                        asset = assets[asset_key]
                        
                if not asset:
                    response_data["available"] = False
                    response_data["reason"] = "Imagery found but no usable asset URLs."
                    return response_data

                response_data["available"] = True
                response_data["selected_date"] = props.get("datetime")
                response_data["cloud_cover"] = props.get("eo:cloud_cover")
                response_data["asset"] = {
                    "type": asset.get("title", "visual"),
                    "url": asset.get("href"),
                    "media_type": asset.get("type")
                }

        except urllib.error.URLError as e:
            logger.error(f"Satellite API request failed: {e}")
            response_data["available"] = False
            response_data["reason"] = "Provider unavailable"
        except Exception as e:
            logger.error(f"Unexpected error retrieving satellite asset: {e}")
            response_data["available"] = False
            response_data["reason"] = "Internal error retrieving asset"

        return response_data

    def get_historical_timeline(
        self,
        latitude: float,
        longitude: float,
        radius_km: Optional[float] = None,
        target_years: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Retrieve historical Sentinel-2 acquisitions for:
        - Current/latest
        - Approximately `target_years` before current date (if specified)
        - Otherwise defaults to 5 years and 10 years before current date
        """
        response_data = {
            "latitude": latitude,
            "longitude": longitude,
            "provider": "Earth Search (Sentinel-2)",
            "imagery": []
        }

        now = datetime.now(timezone.utc)
        
        # Define target periods
        if target_years is not None:
            periods = [
                {
                    "period": "current",
                    "target_date": now.strftime("%Y-%m-%d"),
                    "year_offset": 0
                },
                {
                    "period": f"{target_years}_years",
                    "target_date": (now.replace(year=now.year - target_years)).strftime("%Y-%m-%d"),
                    "year_offset": target_years
                }
            ]
        else:
            periods = [
                {
                    "period": "current",
                    "target_date": now.strftime("%Y-%m-%d"),
                    "year_offset": 0
                },
                {
                    "period": "5_years",
                    "target_date": (now.replace(year=now.year - 5)).strftime("%Y-%m-%d"),
                    "year_offset": 5
                },
                {
                    "period": "10_years",
                    "target_date": (now.replace(year=now.year - 10)).strftime("%Y-%m-%d"),
                    "year_offset": 10
                }
            ]

        for p in periods:
            # Create a 6-month window around the target date to ensure we find something
            # Sentinel-2 launched in 2015, so 10 years ago (2016) is available
            target_dt = now.replace(year=now.year - p["year_offset"])
            start_dt = target_dt - timedelta(days=90)
            end_dt = target_dt + timedelta(days=90)

            asset_result = self.get_imagery_asset(
                latitude=latitude,
                longitude=longitude,
                start_date=start_dt.strftime("%Y-%m-%d"),
                end_date=end_dt.strftime("%Y-%m-%d"),
                radius_km=radius_km
            )

            period_data = {
                "period": p["period"],
                "target_date": p["target_date"],
                "available": asset_result.get("available", False)
            }

            if period_data["available"]:
                period_data["selected_date"] = asset_result.get("selected_date")
                period_data["cloud_cover"] = asset_result.get("cloud_cover")
                period_data["asset"] = asset_result.get("asset")
            else:
                period_data["reason"] = asset_result.get("reason", "No imagery found in the window.")

            response_data["imagery"].append(period_data)

        return response_data
