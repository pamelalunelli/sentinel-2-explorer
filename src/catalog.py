
import requests
from shapely.geometry import shape

CATALOG_URL = "https://sh.dataspace.copernicus.eu/catalog/v1/search"


def search_sentinel_images(token, geometry, date_from, date_to, max_cloud=30):
    results = []
    next_page = None
    bbox = list(geometry.bounds)

    while True:
        payload = {
            "bbox": bbox,
            "datetime": f"{date_from}T00:00:00Z/{date_to}T23:59:59Z",
            "collections": ["sentinel-2-l2a"],
            "limit": 100
        }

        if next_page is not None:
            payload["next"] = next_page

        response = requests.post(
            CATALOG_URL,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=60
        )

        response.raise_for_status()
        data = response.json()

        results.extend(data.get("features", []))

        next_page = data.get("context", {}).get("next")

        if next_page is None:
            break

    filtered = []

    for image in results:
        image_geometry = image.get("geometry")
        properties = image.get("properties", {})
        cloud_cover = properties.get("eo:cloud_cover")

        if not image_geometry or cloud_cover is None:
            continue

        if cloud_cover > max_cloud:
            continue

        if shape(image_geometry).intersects(geometry):
            filtered.append(image)

    return filtered
