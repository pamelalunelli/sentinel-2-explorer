import rasterio
from pyproj import Transformer
from shapely.ops import transform
from rasterio.mask import mask

from src.auth import get_access_token
from src.spatial_analysis import get_park_geometry
from src.processing import download_ndvi

token = get_access_token()
geometry = get_park_geometry("Tingui")

# Data de teste: 31/12/2025
date_from = "2025-12-31T13:29:52Z"
date_to = "2025-12-31T13:29:54Z"

output_path = "output/test_tingui_20251231.tif"

download_ndvi(
    token=token,
    bbox=list(geometry.bounds),
    date_from=date_from,
    date_to=date_to,
    output_path=output_path
)

with rasterio.open(output_path) as src:
    print(f"\nCRS: {src.crs}")
    print(f"Resolução: {src.res}")
    print(f"Dimensões: {src.width} x {src.height}")

    transformer = Transformer.from_crs(
        "EPSG:4326",
        src.crs,
        always_xy=True
    )

    projected_geometry = transform(
        transformer.transform,
        geometry
    )

    masked, _ = mask(
        src,
        [projected_geometry],
        crop=False,
        filled=False
    )

    inside = ~masked.mask[0]
    valid = masked[1].data == 1

    total_pixels = inside.sum()
    valid_pixels = (inside & valid).sum()

    print(f"Pixels dentro do parque: {total_pixels}")
    print(f"Pixels válidos: {valid_pixels}")
    print(
        f"Cobertura válida: "
        f"{valid_pixels / total_pixels * 100:.2f}%"
    )