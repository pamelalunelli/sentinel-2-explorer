
from src.auth import get_access_token
from src.spatial_analysis import load_area_geometry
from src.processing import download_ndvi
from src.analysis import inspect_raster

geometry = load_area_geometry("data/area_teste.geojson")
token = get_access_token()

output = download_ndvi(
    token=token,
    geometry=geometry,
    date_from="2025-12-19T13:29:38Z",
    date_to="2025-12-19T13:29:41Z",
    output_path="output/test_ndvi.tif"
)

output_2 = download_ndvi(
    token=token,
    geometry=geometry,
    date_from="2025-12-11T13:29:44Z",
    date_to="2025-12-11T13:29:47Z",
    output_path="output/test_ndvi_2.tif"
)

print("Saved:", output)
inspect_raster(output, geometry)

import rasterio

for path in [output, output_2]:
    with rasterio.open(path) as dataset:
        print(f"\n{path}")
        print("CRS:", dataset.crs)
        print("Transform:", dataset.transform)
        print("Dimensions:", dataset.width, dataset.height)
        print("Bounds:", dataset.bounds)