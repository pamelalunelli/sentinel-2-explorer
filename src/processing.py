import io
import json
import tarfile
import requests
import rasterio
from pathlib import Path
from rasterio.mask import mask
from rasterio.io import MemoryFile
from pyproj import CRS, Transformer
from shapely.geometry import mapping
from shapely.ops import transform

PROCESS_URL = "https://sh.dataspace.copernicus.eu/process/v1"

NDVI_EVALSCRIPT = """
//VERSION=3

function setup() {
    return {
        input: ["B04", "B08", "SCL", "dataMask"],
        mosaicking: Mosaicking.TILE,
        output: {
            id: "default",
            bands: 2,
            sampleType: "FLOAT32"
        }
    };
}

function evaluatePixel(samples) {
    let invalidClasses = [0, 1, 2, 3, 7, 8, 9, 10, 11];

    for (let i = 0; i < samples.length; i++) {
        let sample = samples[i];

        let valid = sample.dataMask === 1 &&
            !invalidClasses.includes(sample.SCL);

        if (valid) {
            let denominator = sample.B08 + sample.B04;

            let ndvi = denominator === 0
                ? 0
                : (sample.B08 - sample.B04) / denominator;

            return [ndvi, 1];
        }
    }

    return [0, 0];
}

function updateOutputMetadata(scenes, inputMetadata, outputMetadata) {
    outputMetadata.userData = {
        "tiles": scenes.tiles
    };
}
"""

def get_utm_crs(geometry):
    lon, lat = geometry.centroid.x, geometry.centroid.y

    if not -80 <= lat <= 84:
        raise ValueError("UTM is not suitable for this latitude.")

    zone = int((lon + 180) / 6) + 1
    zone = min(max(zone, 1), 60)

    epsg = (32600 if lat >= 0 else 32700) + zone

    return CRS.from_epsg(epsg)


def download_ndvi(token, geometry, date_from, date_to, output_path, resolution=10, expected_product_id=None):
    crs = get_utm_crs(geometry)

    transformer = Transformer.from_crs(
        "EPSG:4326",
        crs,
        always_xy=True
    )

    projected_geometry = transform(transformer.transform, geometry)
    bbox = list(projected_geometry.bounds)

    crs_url = f"http://www.opengis.net/def/crs/EPSG/0/{crs.to_epsg()}"

    response = requests.post(
        PROCESS_URL,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/x-tar"
        },
        json={
            "input": {
                "bounds": {
                    "bbox": bbox,
                    "geometry": mapping(projected_geometry),
                    "properties": {"crs": crs_url}
                },
                "data": [
                    {
                        "type": "sentinel-2-l2a",
                        "dataFilter": {
                            "timeRange": {
                                "from": date_from,
                                "to": date_to
                            },
                            "maxCloudCoverage": 100,
                            "mosaickingOrder": "leastCC"
                        }
                    }
                ]
            },
            "output": {
                "resx": resolution,
                "resy": resolution,
                "responses": [
                    {
                        "identifier": "default",
                        "format": {"type": "image/tiff"}
                    },
                    {
                        "identifier": "userdata",
                        "format": {"type": "application/json"}
                    }
                ]
            },
            "evalscript": NDVI_EVALSCRIPT
        },
        timeout=120
    )

    response.raise_for_status()

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with tarfile.open(fileobj=io.BytesIO(response.content), mode="r:*") as archive:
        tif_member = next(
            member for member in archive.getmembers()
            if member.name.endswith(".tif")
        )

        userdata_member = archive.getmember("userdata.json")

        tif_content = archive.extractfile(tif_member).read()
        userdata = json.load(archive.extractfile(userdata_member))
    
    tiles = userdata.get("tiles", [])
    product_ids = {
        tile.get("productId") or tile.get("sentinel2ProductId")
        for tile in tiles
    }

    if expected_product_id and expected_product_id not in product_ids:
        raise ValueError(
            f"Product mismatch. Expected {expected_product_id}, "
            f"received: {product_ids}"
        )
    
    metadata_path = output_path.with_suffix(".json")

    with metadata_path.open("w", encoding="utf-8") as file:
        json.dump(userdata, file, indent=4, ensure_ascii=False)

    #print(f"Tiles metadata saved: {metadata_path}")
    #print(json.dumps(userdata.get("tiles", []), indent=2))

    with MemoryFile(tif_content) as memory_file:
        with memory_file.open() as dataset:
            clipped, clipped_transform = mask(
                dataset,
                [mapping(projected_geometry)],
                crop=True,
                nodata=-9999
            )

            profile = dataset.profile.copy()
            profile.update(
                height=clipped.shape[1],
                width=clipped.shape[2],
                transform=clipped_transform,
                crs=crs,
                nodata=-9999
            )

    with rasterio.open(output_path, "w", **profile) as output:
        output.write(clipped)

    return output_path