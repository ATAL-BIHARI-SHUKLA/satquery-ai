import logging
import rasterio
from rasterio.windows import Window
import numpy as np
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ChangeDetectionService:
    def __init__(self):
        pass

    def detect_change(self, before_url: str, after_url: str) -> Dict[str, Any]:
        """
        Baseline change detection comparing two remote COG assets.
        To avoid downloading the full scene, it reads a central window.
        """
        response = {
            "status": "success",
            "method": "baseline_change_detection",
            "before_date": None,
            "after_date": None,
            "change_percentage": None,
            "changed_area_available": False,
            "summary": None
        }

        try:
            with rasterio.Env(CPL_VSIL_CURL_ALLOWED_EXTENSIONS="tif,tiff"):
                with rasterio.open(before_url) as src_before:
                    with rasterio.open(after_url) as src_after:
                        # Read a central 512x512 window to save bandwidth
                        w = min(src_before.width, src_after.width)
                        h = min(src_before.height, src_after.height)
                        
                        window_size = 512
                        read_w = min(w, window_size)
                        read_h = min(h, window_size)
                        
                        col_off = max(0, (w - read_w) // 2)
                        row_off = max(0, (h - read_h) // 2)
                        
                        window = Window(col_off, row_off, read_w, read_h)
                        
                        # Read the first band
                        band_before = src_before.read(1, window=window).astype(np.float32)
                        band_after = src_after.read(1, window=window).astype(np.float32)
                        
                        # Normalize 
                        def normalize(arr):
                            min_val = np.min(arr)
                            max_val = np.max(arr)
                            if max_val - min_val == 0:
                                return arr
                            return (arr - min_val) / (max_val - min_val)
                            
                        norm_before = normalize(band_before)
                        norm_after = normalize(band_after)
                        
                        # Simple absolute difference
                        diff = np.abs(norm_after - norm_before)
                        
                        # Threshold for "significant" change
                        threshold = 0.2
                        changed_pixels = np.sum(diff > threshold)
                        total_pixels = diff.size
                        
                        change_percentage = float(changed_pixels / total_pixels) * 100.0
                        
                        response["change_percentage"] = round(change_percentage, 2)
                        response["changed_area_available"] = True
                        
                        if change_percentage > 5.0:
                            response["summary"] = f"Significant change detected ({round(change_percentage, 1)}% of sampled region)."
                        else:
                            response["summary"] = f"Minimal or no change detected ({round(change_percentage, 1)}% of sampled region)."
                            
        except rasterio.errors.RasterioIOError as e:
            logger.error(f"Inaccessible asset or incompatible raster: {e}")
            response["status"] = "error"
            response["summary"] = "Inaccessible asset or incompatible raster format."
        except Exception as e:
            logger.error(f"Unexpected error in change detection: {e}")
            response["status"] = "error"
            response["summary"] = f"Provider or network failure: {str(e)}"

        return response

change_detection_service = ChangeDetectionService()
