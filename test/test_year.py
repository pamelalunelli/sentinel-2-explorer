
from datetime import datetime, timedelta
from pathlib import Path

from src.auth import get_access_token
from src.spatial_analysis import load_area_geometry
from src.catalog import search_sentinel_images
from src.processing import download_ndvi

geometry = load_area_geometry("data/area_teste.geojson")
token = get_access_token()

images = search_sentinel_images(
    token=token,
    geometry=geometry,
    date_from="2025-01-01",
    date_to="2025-12-31",
    max_cloud=30
)

output_dir = Path("output/acquisitions")
output_dir.mkdir(parents=True, exist_ok=True)

acquisitions = []

for image in images:
    properties = image["properties"]

    print(f"Catalog item ID: {image['id']}")

    acquisition = datetime.fromisoformat(
        properties["datetime"].replace("Z", "+00:00")
    )

    date_from = (acquisition - timedelta(seconds=1)).isoformat()
    date_to = (acquisition + timedelta(seconds=1)).isoformat()

    date_from = date_from.replace("+00:00", "Z")
    date_to = date_to.replace("+00:00", "Z")

    timestamp = acquisition.strftime("%Y%m%dT%H%M%S")
    output_path = output_dir / f"ndvi_{timestamp}.tif"

    print(f"\nProcessing: {properties['datetime']}")

    download_ndvi(
        token=token,
        geometry=geometry,
        date_from=date_from,
        date_to=date_to,
        output_path=output_path,
        expected_product_id=image["id"],
    )

    acquisitions.append({
        "date": properties["datetime"],
        "path": str(output_path)
    })

print(f"\nProcessed acquisitions: {len(acquisitions)}")


from src.monthly_composite import create_monthly_composites
from src.reporting import export_monthly_report
from src.temporal_analysis import plot_temporal_series

results = create_monthly_composites(
    acquisitions=acquisitions,
    geometry=geometry,
    output_dir="output/monthly",
    min_valid_coverage=70
)

for result in results:
    print(
        f"{result['month']}: "
        f"{result['status']} | "
        f"Coverage: {result['valid_coverage']:.2f}% | "
        f"Acquisitions: {result['acquisitions']}"
    )

report_path = export_monthly_report(
    results,
    "output/monthly/monthly_report.csv"
)

plot_temporal_series(
    results,
    "output/monthly/temporal_series.png",
    start="2025-01-01",
    end="2025-12-31"
)

print(f"\nReport saved: {report_path}")