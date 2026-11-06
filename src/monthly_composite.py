
from collections import defaultdict
from datetime import datetime
from pathlib import Path
import numpy as np
import rasterio
from rasterio.features import geometry_mask
from pyproj import Transformer
from shapely.geometry import mapping
from shapely.ops import transform


def create_monthly_composites(acquisitions, geometry, output_dir, min_valid_coverage=70):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    monthly_groups = defaultdict(list)

    for acquisition in acquisitions:
        date = datetime.fromisoformat(
            acquisition["date"].replace("Z", "+00:00")
        )
        month = date.strftime("%Y-%m")
        monthly_groups[month].append(acquisition["path"])

    results = []

    for month, paths in sorted(monthly_groups.items()):
        datasets = [rasterio.open(path) for path in paths]

        try:
            reference = datasets[0]

            for dataset in datasets[1:]:
                if (
                    dataset.crs != reference.crs
                    or dataset.transform != reference.transform
                    or dataset.width != reference.width
                    or dataset.height != reference.height
                ):
                    raise ValueError(
                        f"Raster grid mismatch in month {month}: "
                        f"{dataset.name}"
                    )

            ndvi_stack = []

            for dataset in datasets:
                ndvi = dataset.read(1)
                valid = dataset.read(2) == 1
                ndvi_stack.append(np.where(valid, ndvi, np.nan))

            stack = np.stack(ndvi_stack)
            composite = np.ma.median(
                np.ma.masked_invalid(stack),
                axis=0
            ).filled(-9999).astype(np.float32)

            valid = np.any(np.isfinite(stack), axis=0)

            transformer = Transformer.from_crs(
                "EPSG:4326",
                reference.crs,
                always_xy=True
            )
            projected_geometry = transform(
                transformer.transform,
                geometry
            )

            inside = geometry_mask(
                [mapping(projected_geometry)],
                out_shape=composite.shape,
                transform=reference.transform,
                invert=True
            )

            valid_area = valid & inside
            total_pixels = np.count_nonzero(inside)
            valid_pixels = np.count_nonzero(valid_area)

            coverage = (
                valid_pixels / total_pixels * 100
                if total_pixels else 0
            )

            result = {
                "month": month,
                "acquisitions": len(paths),
                "valid_coverage": float(coverage),
                "ndvi_mean": None,
                "ndvi_median": None,
                "ndvi_min": None,
                "ndvi_max": None,
                "low_vegetation": None,
                "moderate_vegetation": None,
                "dense_vegetation": None,
                "output": None,
                "status": "APPROVED" if coverage >= min_valid_coverage else "DISCARDED"
            }

            if result["status"] == "APPROVED":
                values = composite[valid_area]

                result.update({
                    "ndvi_mean": float(np.mean(values)),
                    "ndvi_median": float(np.median(values)),
                    "ndvi_min": float(np.min(values)),
                    "ndvi_max": float(np.max(values)),
                    "low_vegetation": float(np.count_nonzero(values < 0.2) / valid_pixels * 100),
                    "moderate_vegetation": float(np.count_nonzero((values >= 0.2) & (values < 0.5)) / valid_pixels * 100),
                    "dense_vegetation": float(np.count_nonzero(values >= 0.5) / valid_pixels * 100)
                })

                composite[~valid_area] = -9999

                output_path = output_dir / f"ndvi_{month}.tif"

                profile = reference.profile.copy()
                profile.update(
                    count=2,
                    dtype="float32",
                    nodata=-9999
                )

                with rasterio.open(output_path, "w", **profile) as output:
                    output.write(composite, 1)
                    output.write(
                        valid_area.astype(np.float32),
                        2
                    )

                result["output"] = str(output_path)

            results.append(result)

        finally:
            for dataset in datasets:
                dataset.close()

    return results
