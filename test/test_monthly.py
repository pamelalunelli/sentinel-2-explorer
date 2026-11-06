
from src.monthly_composite import create_monthly_composites
from src.spatial_analysis import load_area_geometry

geometry = load_area_geometry("data/area_teste.geojson")

acquisitions = [
    {
        "path": "output/test_ndvi.tif",
        "date": "2025-12-19T13:29:39Z"
    },
    {
        "path": "output/test_ndvi_2.tif",
        "date": "2025-12-11T13:29:45Z"
    }
]

results = create_monthly_composites(
    acquisitions=acquisitions,
    geometry=geometry,
    output_dir="output/monthly",
    min_valid_coverage=70
)

from src.temporal_analysis import plot_temporal_series

plot_temporal_series(
    results,
    "output/monthly/temporal_series.png"
)

for result in results:
    for key, value in result.items():
        print(f"{key}: {value}")
    print()

import rasterio
import numpy as np

with rasterio.open("output/monthly/ndvi_2025-12.tif") as dataset:
    ndvi = dataset.read(1)
    valid = dataset.read(2) == 1

    values = ndvi[valid]

    print("\nMonthly composite:")
    print("Dimensions:", dataset.width, dataset.height)
    print("Valid pixels:", np.count_nonzero(valid))
    print("NDVI mean:", values.mean())
    print("NDVI median:", np.median(values))
    print("NDVI min:", values.min())
    print("NDVI max:", values.max())

from src.reporting import export_monthly_report

report_path = export_monthly_report(
    results,
    "output/monthly/monthly_report.csv"
)

print(f"\nReport saved: {report_path}")