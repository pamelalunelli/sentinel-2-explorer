import argparse
import os
from datetime import datetime, timedelta
from pathlib import Path

from src.auth import get_access_token
from src.catalog import search_sentinel_images
from src.processing import download_ndvi
from src.spatial_analysis import load_area_geometry
from src.monthly_composite import create_monthly_composites
from src.reporting import export_monthly_report
from src.temporal_analysis import plot_temporal_series
from src.spatial_comparison import plot_monthly_comparison

def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate monthly Sentinel-2 NDVI composites."
    )

    parser.add_argument("--area", required=True, help="Path to AOI file (SHP, GeoJSON, JSON or KML).")
    parser.add_argument("--start", required=True, help="Start date (YYYY-MM-DD).")
    parser.add_argument("--end", required=True, help="End date (YYYY-MM-DD).")
    parser.add_argument("--max-cloud", type=float, default=30)
    parser.add_argument("--min-coverage", type=float, default=70)

    args = parser.parse_args()

    try:
        start = datetime.strptime(args.start, "%Y-%m-%d")
        end = datetime.strptime(args.end, "%Y-%m-%d")
    except ValueError:
        parser.error("Invalid date. Use a valid date in YYYY-MM-DD format.")

    if start > end:
        parser.error("Start date must be earlier than or equal to end date.")

    if not 0 <= args.max_cloud <= 100:
        parser.error("Maximum cloud cover must be between 0 and 100.")

    if not 0 <= args.min_coverage <= 100:
        parser.error("Minimum coverage must be between 0 and 100.")

    return args


def main():
    args = parse_args()

    geometry = load_area_geometry(args.area)
    token = get_access_token()

    images = search_sentinel_images(
        token=token,
        geometry=geometry,
        date_from=args.start,
        date_to=args.end,
        max_cloud=args.max_cloud
    )

    images.sort(key=lambda image: image["properties"]["datetime"])

    # print(f"\nArea: {args.area}")
    # print(f"Images found: {len(images)}")

    output_dir = Path("output")
    acquisition_dir = output_dir / "acquisitions"
    monthly_dir = output_dir / "monthly"

    acquisition_dir.mkdir(parents=True, exist_ok=True)

    acquisitions = []

    for image in images:
        properties = image["properties"]
        acquisition_date = datetime.fromisoformat(
            properties["datetime"].replace("Z", "+00:00")
        )

        date_from = (acquisition_date - timedelta(seconds=1)).isoformat()
        date_to = (acquisition_date + timedelta(seconds=1)).isoformat()

        date_from = date_from.replace("+00:00", "Z")
        date_to = date_to.replace("+00:00", "Z")

        timestamp = acquisition_date.strftime("%Y%m%dT%H%M%S")
        output_path = acquisition_dir / f"ndvi_{timestamp}.tif"

        print(f"\nProcessing: {properties['datetime']}")

        download_ndvi(
            token=token,
            geometry=geometry,
            date_from=date_from,
            date_to=date_to,
            output_path=output_path
        )

        acquisitions.append({
            "date": properties["datetime"],
            "path": str(output_path)
        })

    #print(f"\nProcessed acquisitions: {len(acquisitions)}")

    results = create_monthly_composites(
        acquisitions=acquisitions,
        geometry=geometry,
        output_dir=monthly_dir,
        min_valid_coverage=args.min_coverage
    )

    # for result in results:
    #     print(
    #         f"{result['month']}: {result['status']} | "
    #         f"Coverage: {result['valid_coverage']:.2f}% | "
    #         f"Acquisitions: {result['acquisitions']}"
    #     )

    report_path = export_monthly_report(
        results,
        monthly_dir / "monthly_report.csv"
    )

    plot_temporal_series(
        results,
        monthly_dir / "temporal_series.png",
        start=args.start,
        end=args.end
    )

    spatial_comparison_path = monthly_dir / f"ndvi_comparison_{args.start}_{args.end}.png"
    plot_monthly_comparison(spatial_comparison_path, args.start, args.end)

    print("\n" + "=" * 55)
    print("PROCESSING COMPLETED")
    print("=" * 55)
    print(f"Images processed: {len(acquisitions)}")
    print(f"Monthly composites: {len(results)}")
    print(f"Monthly report: {report_path}")
    print(f"Temporal chart: {monthly_dir / 'temporal_series.png'}")
    print(f"Spatial comparison: {spatial_comparison_path}")
    print("=" * 55)
    print("\nOpening final result...")

    os.startfile(str(spatial_comparison_path.resolve()))


if __name__ == "__main__":
    main()