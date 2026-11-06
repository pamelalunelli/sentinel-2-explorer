
import geopandas as gpd
from pathlib import Path
from shapely.geometry import Polygon, MultiPolygon, mapping
from shapely.ops import unary_union


def load_area_geometry(file_path):
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"Area file not found: {file_path}")

    supported_formats = [".shp", ".geojson", ".json", ".kml"]

    if file_path.suffix.lower() not in supported_formats:
        raise ValueError(
            f"Unsupported format: {file_path.suffix}. "
            f"Supported formats: {', '.join(supported_formats)}"
        )

    try:
        gdf = gpd.read_file(file_path)
    except Exception as error:
        raise ValueError(f"Could not read area file: {error}") from error

    if gdf.empty:
        raise ValueError("Area file contains no features.")

    if gdf.crs is None:
        raise ValueError("Area file has no defined CRS.")

    gdf = gdf.to_crs("EPSG:4326")
    geometries = gdf.geometry.dropna()

    if geometries.empty:
        raise ValueError("Area file contains no valid geometries.")

    geometry = unary_union(geometries)

    if not geometry.is_valid:
        geometry = geometry.buffer(0)

    if geometry.is_empty or not geometry.is_valid:
        raise ValueError("Could not create a valid area geometry.")

    if not isinstance(geometry, (Polygon, MultiPolygon)):
        raise ValueError(
            "Area geometry must be a Polygon or MultiPolygon."
        )

    return geometry


def geometry_to_geojson(geometry):
    return mapping(geometry)


def get_geometry_bbox(geometry):
    return list(geometry.bounds)
