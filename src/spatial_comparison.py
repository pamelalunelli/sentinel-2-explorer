from datetime import datetime
import numpy as np
import rasterio
import matplotlib.pyplot as plt
from pathlib import Path


OUTPUT_DIR = Path("output/monthly")
OUTPUT_PATH = OUTPUT_DIR / "ndvi_monthly_comparison_2025.png"


def read_raster(path):
    with rasterio.open(path) as dataset:
        ndvi = dataset.read(1)
        valid = dataset.read(2) == 1

        return {
            "ndvi": np.ma.masked_where(~valid, ndvi),
            "bounds": dataset.bounds,
            "transform": dataset.transform,
            "crs": dataset.crs,
            "shape": dataset.shape
        }

def plot_monthly_comparison(output_path, start, end):
    start = datetime.strptime(start, "%Y-%m-%d")
    end = datetime.strptime(end, "%Y-%m-%d")

    months = []
    current = start.replace(day=1)

    while current <= end:
        months.append(current)
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1)
        else:
            current = current.replace(month=current.month + 1)

    columns = min(3, len(months))
    rows = (len(months) + columns - 1) // columns

    fig, axes = plt.subplots(
        rows, columns,
        figsize=(5 * columns, 4 * rows),
        constrained_layout=True,
        squeeze=False
    )

    image = None
    reference = None

    for ax, month in zip(axes.flat, months):
        path = OUTPUT_DIR / f"ndvi_{month.year}-{month.month:02d}.tif"
        ax.set_title(month.strftime("%B %Y"))

        if not path.exists():
            ax.text(0.5, 0.5, "No data", ha="center", va="center",
                    transform=ax.transAxes)
            ax.set_axis_off()
            continue

        raster = read_raster(path)

        if reference is None:
            reference = raster
        elif (
            raster["shape"] != reference["shape"]
            or raster["transform"] != reference["transform"]
            or raster["crs"] != reference["crs"]
        ):
            raise ValueError("Monthly rasters do not share the same spatial grid.")

        bounds = raster["bounds"]
        image = ax.imshow(
            raster["ndvi"],
            cmap="RdYlGn",
            vmin=-1,
            vmax=1,
            extent=[bounds.left, bounds.right, bounds.bottom, bounds.top]
        )
        ax.set_xticks([])
        ax.set_yticks([])

    for ax in axes.flat[len(months):]:
        ax.set_axis_off()

    if image is not None:
        fig.colorbar(image, ax=axes, label="NDVI", shrink=0.75)

    fig.suptitle(
        f"Monthly NDVI Comparison ({start:%Y-%m} to {end:%Y-%m})",
        fontsize=16
    )
    plt.savefig(output_path, dpi=180, bbox_inches="tight")
    plt.close()

if __name__ == "__main__":
    plot_monthly_comparison(OUTPUT_PATH)
    print(f"Monthly comparison saved: {OUTPUT_PATH}")
