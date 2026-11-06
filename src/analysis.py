
import rasterio
import numpy as np
from rasterio.features import geometry_mask
from pyproj import Transformer
from shapely.geometry import mapping
from shapely.ops import transform


def inspect_raster(path, geometry):
    with rasterio.open(path) as dataset:
        ndvi = dataset.read(1)
        mask_band = dataset.read(2)

        transformer = Transformer.from_crs(
            "EPSG:4326",
            dataset.crs,
            always_xy=True
        )

        projected_geometry = transform(
            transformer.transform,
            geometry
        )

        inside = geometry_mask(
            [mapping(projected_geometry)],
            out_shape=ndvi.shape,
            transform=dataset.transform,
            invert=True
        )

        valid = (mask_band == 1) & inside & np.isfinite(ndvi)
        values = ndvi[valid]

        total_pixels = np.count_nonzero(inside)
        valid_pixels = np.count_nonzero(valid)
        excluded_pixels = total_pixels - valid_pixels

        valid_percentage = (
            valid_pixels / total_pixels * 100
            if total_pixels > 0 else 0
        )

        print(f"CRS: {dataset.crs}")
        print(f"Dimensions: {dataset.width} x {dataset.height}")
        print(f"Resolution: {dataset.res}")
        print(f"Bounds: {dataset.bounds}")

        print(f"\nTotal pixels inside area: {total_pixels}")
        print(f"Valid pixels: {valid_pixels} ({valid_percentage:.2f}%)")
        print(f"Excluded pixels: {excluded_pixels}")

        result = {
            "total_pixels": int(total_pixels),
            "valid_pixels": int(valid_pixels),
            "valid_percentage": valid_percentage,
            "ndvi_mean": None,
            "ndvi_median": None,
            "ndvi_min": None,
            "ndvi_max": None,
            "low_vegetation": None,
            "moderate_vegetation": None,
            "dense_vegetation": None
        }

        if values.size == 0:
            print("\nNo valid pixels available.")
            return result

        print(f"\nNDVI min: {values.min():.3f}")
        print(f"NDVI max: {values.max():.3f}")
        print(f"NDVI mean: {values.mean():.3f}")
        print(f"NDVI median: {np.median(values):.3f}")

        ranges = {
            "low_vegetation": values < 0.2,
            "moderate_vegetation": (values >= 0.2) & (values < 0.5),
            "dense_vegetation": values >= 0.5
        }

        print("\nNDVI distribution:")

        for label, condition in ranges.items():
            count = np.count_nonzero(condition)
            percentage = count / valid_pixels * 100

            result[label] = percentage
            print(f"{label}: {count} pixels ({percentage:.2f}%)")

        result["ndvi_min"] = float(values.min())
        result["ndvi_max"] = float(values.max())
        result["ndvi_mean"] = float(values.mean())
        result["ndvi_median"] = float(np.median(values))

        return result
