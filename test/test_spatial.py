from src.auth import get_access_token
from src.spatial_analysis import get_park_geometry, inspect_tile_coverage

token = get_access_token()
geometry = get_park_geometry("Tingui")

print(f"Park area: {geometry.area:.8f}")
print(f"BBOX: {geometry.bounds}")

inspect_tile_coverage(
    token=token,
    geometry=geometry,
    date_from="2025-01-01",
    date_to="2025-12-31"
)
