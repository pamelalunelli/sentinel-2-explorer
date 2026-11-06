import rasterio
import numpy as np
import matplotlib.pyplot as plt

def plot_ndvi(input_path, output_path):
    with rasterio.open(input_path) as dataset:
        ndvi = dataset.read(1)
        valid = dataset.read(2) == 1

    ndvi = np.where(valid, ndvi, np.nan)

    plt.figure(figsize=(9, 7))
    plt.imshow(ndvi, cmap="RdYlGn", vmin=-1, vmax=1)
    plt.colorbar(label="NDVI")
    plt.title("Sentinel-2 NDVI")
    plt.axis("off")
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()