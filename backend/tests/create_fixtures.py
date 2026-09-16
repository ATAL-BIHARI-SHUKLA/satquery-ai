import numpy as np
import rasterio
from rasterio.transform import from_origin
import os

def create_mock_tiffs():
    os.makedirs("tests/fixtures", exist_ok=True)
    
    transform = from_origin(0, 0, 10, 10)
    
    # Image 1 (Before)
    before_data = np.full((512, 512), 100, dtype=np.uint8)
    with rasterio.open(
        "tests/fixtures/before.tif",
        'w',
        driver='GTiff',
        height=512,
        width=512,
        count=1,
        dtype=before_data.dtype,
        crs='+proj=latlong',
        transform=transform,
    ) as dst:
        dst.write(before_data, 1)

    # Image 2 (After - No Change)
    with rasterio.open(
        "tests/fixtures/after_no_change.tif",
        'w',
        driver='GTiff',
        height=512,
        width=512,
        count=1,
        dtype=before_data.dtype,
        crs='+proj=latlong',
        transform=transform,
    ) as dst:
        dst.write(before_data, 1)

    # Image 3 (After - Changed)
    after_changed = np.full((512, 512), 100, dtype=np.uint8)
    after_changed[100:400, 100:400] = 200  # significant change block
    with rasterio.open(
        "tests/fixtures/after_changed.tif",
        'w',
        driver='GTiff',
        height=512,
        width=512,
        count=1,
        dtype=after_changed.dtype,
        crs='+proj=latlong',
        transform=transform,
    ) as dst:
        dst.write(after_changed, 1)

if __name__ == "__main__":
    create_mock_tiffs()
