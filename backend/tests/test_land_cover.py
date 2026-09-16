import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from app.services.land_cover import land_cover_service
import rasterio

class MockRaster:
    def __init__(self, count=4, data_override=None):
        self.count = count
        self.width = 100
        self.height = 100
        self.data_override = data_override
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
        
    def read(self, band, window=None):
        if self.data_override and band in self.data_override:
            return self.data_override[band]
        # Return random data if no override
        return np.random.rand(50, 50).astype(np.float32)

def test_insufficient_spectral_bands():
    with patch('rasterio.open') as mock_open, patch('rasterio.Env'):
        mock_open.side_effect = [MockRaster(count=3), MockRaster(count=3)]
        
        result = land_cover_service.calculate_indicators("url1", "url2")
        
        assert result["status"] == "error"
        assert result["summary"] == "insufficient spectral data"
        assert "At least 4 bands" in result["limitations"][0]

def test_vegetation_increase():
    with patch('rasterio.open') as mock_open, patch('rasterio.Env'):
        # Before: Low NIR (4), High Red (3) -> Low NDVI
        # After: High NIR (4), Low Red (3) -> High NDVI
        # If count=4: Green=2, Red=3, NIR=4
        before_data = {
            2: np.ones((50,50), dtype=np.float32) * 0.1, # Green
            3: np.ones((50,50), dtype=np.float32) * 0.8, # Red
            4: np.ones((50,50), dtype=np.float32) * 0.2  # NIR
        }
        after_data = {
            2: np.ones((50,50), dtype=np.float32) * 0.1, # Green
            3: np.ones((50,50), dtype=np.float32) * 0.2, # Red
            4: np.ones((50,50), dtype=np.float32) * 0.8  # NIR
        }
        
        mock_open.side_effect = [
            MockRaster(count=4, data_override=before_data),
            MockRaster(count=4, data_override=after_data)
        ]
        
        result = land_cover_service.calculate_indicators("url1", "url2")
        
        assert result["status"] == "success"
        assert result["indicators"]["vegetation"]["direction"] == "increased"
        assert result["indicators"]["vegetation"]["change"] > 0

def test_water_change():
    with patch('rasterio.open') as mock_open, patch('rasterio.Env'):
        # NDWI = (Green - NIR) / (Green + NIR)
        # Before: Low Green (2), High NIR (4) -> Low NDWI
        # After: High Green (2), Low NIR (4) -> High NDWI
        before_data = {
            2: np.ones((50,50), dtype=np.float32) * 0.2,
            3: np.ones((50,50), dtype=np.float32) * 0.2,
            4: np.ones((50,50), dtype=np.float32) * 0.8 
        }
        after_data = {
            2: np.ones((50,50), dtype=np.float32) * 0.8, 
            3: np.ones((50,50), dtype=np.float32) * 0.2,
            4: np.ones((50,50), dtype=np.float32) * 0.2  
        }
        
        mock_open.side_effect = [
            MockRaster(count=4, data_override=before_data),
            MockRaster(count=4, data_override=after_data)
        ]
        
        result = land_cover_service.calculate_indicators("url1", "url2")
        
        assert result["status"] == "success"
        assert result["indicators"]["water"]["direction"] == "increased"
        assert result["indicators"]["water"]["change"] > 0

def test_invalid_inputs_handling():
    with patch('rasterio.open') as mock_open, patch('rasterio.Env'):
        mock_open.side_effect = rasterio.errors.RasterioIOError("Cannot open file")
        
        result = land_cover_service.calculate_indicators("invalid", "invalid")
        
        assert result["status"] == "error"
        assert result["summary"] == "inaccessible asset or incompatible raster"

