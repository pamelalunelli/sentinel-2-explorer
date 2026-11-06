from src.auth import get_access_token
from src.spatial_analysis import load_area_geometry
from src.catalog import search_sentinel_images

geometry = load_area_geometry("data/area_teste.geojson")
token = get_access_token()

images = search_sentinel_images(
    token=token,
    geometry=geometry,
    date_from="2025-01-01",
    date_to="2025-12-31",
    max_cloud=30
)

print(f"Images found: {len(images)}")

from collections import defaultdict

acquisitions = defaultdict(list)

for image in images:
    date = image["properties"]["datetime"]
    acquisitions[date].append(image)

print(f"\nDistinct acquisition dates: {len(acquisitions)}")

for date, scenes in sorted(acquisitions.items()):
    print(f"{date} - {len(scenes)} catalog items")