
from src.spatial_analysis import (
    load_area_geometry,
    geometry_to_geojson,
    get_geometry_bbox
)

geometry = load_area_geometry("data/area_teste.geojson")

print("Geometry type:", geometry.geom_type)
print("Area bounds:", get_geometry_bbox(geometry))
print("GeoJSON type:", geometry_to_geojson(geometry)["type"])
print("Area valid:", geometry.is_valid)
