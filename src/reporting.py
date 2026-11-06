
import csv
from pathlib import Path


def export_monthly_report(results, output_path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "month",
        "acquisitions",
        "valid_coverage",
        "ndvi_mean",
        "ndvi_median",
        "ndvi_min",
        "ndvi_max",
        "low_vegetation",
        "moderate_vegetation",
        "dense_vegetation",
        "status",
        "output"
    ]

    with output_path.open("w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for result in results:
            writer.writerow({
                key: result.get(key)
                for key in fieldnames
            })

    return output_path
