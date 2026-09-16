import logging
import rasterio
from rasterio.windows import Window
import numpy as np
from typing import Dict, Any

logger = logging.getLogger(__name__)

class LandCoverService:
    def __init__(self):
        pass

    def calculate_indicators(self, before_url: str, after_url: str) -> Dict[str, Any]:
        response = {
            "status": "success",
            "method": "baseline_land_cover_indicators",
            "before_date": None,
            "after_date": None,
            "indicators": {},
            "limitations": []
        }

        try:
            with rasterio.Env(CPL_VSIL_CURL_ALLOWED_EXTENSIONS="tif,tiff,jp2,png,jpg,jpeg"):
                with rasterio.open(before_url) as src_before:
                    with rasterio.open(after_url) as src_after:
                        # Check band count for spectral indices
                        if src_before.count < 4 or src_after.count < 4:
                            response["status"] = "error"
                            response["summary"] = "insufficient spectral data"
                            response["limitations"].append(f"Assets have {src_before.count} and {src_after.count} bands. At least 4 bands (including NIR) are required for NDVI/NDWI.")
                            return response

                        # Read a central 512x512 window
                        w = min(src_before.width, src_after.width)
                        h = min(src_before.height, src_after.height)
                        
                        window_size = 512
                        read_w = min(w, window_size)
                        read_h = min(h, window_size)
                        
                        col_off = max(0, (w - read_w) // 2)
                        row_off = max(0, (h - read_h) // 2)
                        window = Window(col_off, row_off, read_w, read_h)

                        if src_before.count == 4:
                            # Assume Blue, Green, Red, NIR (common for 4-band stacks)
                            green_idx, red_idx, nir_idx = 2, 3, 4
                        else:
                            # Assume Sentinel-2 stacked order (B2, B3, B4, ..., B8, etc)
                            # B3=Green (idx 2 or 3 depending on stack, but usually 3), B4=Red, B8=NIR
                            green_idx, red_idx, nir_idx = 3, 4, 8

                        green_before = src_before.read(green_idx, window=window).astype(np.float32)
                        red_before = src_before.read(red_idx, window=window).astype(np.float32)
                        nir_before = src_before.read(nir_idx, window=window).astype(np.float32)

                        green_after = src_after.read(green_idx, window=window).astype(np.float32)
                        red_after = src_after.read(red_idx, window=window).astype(np.float32)
                        nir_after = src_after.read(nir_idx, window=window).astype(np.float32)

                        def safe_index(b1, b2):
                            denom = (b1 + b2)
                            return (b1 - b2) / (denom + 1e-8)

                        # NDVI = (NIR - Red) / (NIR + Red)
                        ndvi_before = safe_index(nir_before, red_before)
                        ndvi_after = safe_index(nir_after, red_after)

                        # NDWI = (Green - NIR) / (Green + NIR)
                        ndwi_before = safe_index(green_before, nir_before)
                        ndwi_after = safe_index(green_after, nir_after)
                        
                        # Built-up index (NDBI) needs SWIR, but as a basic indicator using available bands:
                        # Modified NDBI / bare soil proxy = (Red - Green) / (Red + Green) - extremely simplified if SWIR is missing
                        bare_before = safe_index(red_before, green_before)
                        bare_after = safe_index(red_after, green_after)

                        def get_change_direction(before_val, after_val, threshold=0.05):
                            change = after_val - before_val
                            if change > threshold:
                                return "increased"
                            elif change < -threshold:
                                return "decreased"
                            return "stable"

                        mean_ndvi_before = float(np.nanmean(ndvi_before))
                        mean_ndvi_after = float(np.nanmean(ndvi_after))
                        
                        mean_ndwi_before = float(np.nanmean(ndwi_before))
                        mean_ndwi_after = float(np.nanmean(ndwi_after))
                        
                        mean_bare_before = float(np.nanmean(bare_before))
                        mean_bare_after = float(np.nanmean(bare_after))

                        response["indicators"]["vegetation"] = {
                            "before": round(mean_ndvi_before, 3),
                            "after": round(mean_ndvi_after, 3),
                            "change": round(mean_ndvi_after - mean_ndvi_before, 3),
                            "direction": get_change_direction(mean_ndvi_before, mean_ndvi_after)
                        }

                        response["indicators"]["water"] = {
                            "before": round(mean_ndwi_before, 3),
                            "after": round(mean_ndwi_after, 3),
                            "change": round(mean_ndwi_after - mean_ndwi_before, 3),
                            "direction": get_change_direction(mean_ndwi_before, mean_ndwi_after)
                        }
                        
                        response["indicators"]["built_up"] = {
                            "before": round(mean_bare_before, 3),
                            "after": round(mean_bare_after, 3),
                            "change": round(mean_bare_after - mean_bare_before, 3),
                            "direction": get_change_direction(mean_bare_before, mean_bare_after)
                        }
                        
                        response["limitations"].extend([
                            "Baseline non-ML spectral indices only.",
                            "Assumes band 4/8 is NIR depending on channel count.",
                            "Not calibrated for true land-cover classification.",
                            "Does not predict precise soil fertility or real-estate values."
                        ])
                        
        except rasterio.errors.RasterioIOError as e:
            logger.error(f"Inaccessible asset or incompatible raster: {e}")
            response["status"] = "error"
            response["summary"] = "inaccessible asset or incompatible raster"
            response["limitations"].append(str(e))
        except Exception as e:
            logger.error(f"Unexpected error in land cover analysis: {e}")
            response["status"] = "error"
            response["summary"] = "provider or network failure"
            response["limitations"].append(str(e))

        return response

land_cover_service = LandCoverService()
