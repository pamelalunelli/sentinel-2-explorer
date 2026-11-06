# Sentinel-2 Explorer

A Python-based geospatial tool for analyzing vegetation changes over time using Sentinel-2 satellite imagery.

The project automates the workflow of searching satellite imagery, filtering scenes by cloud coverage, calculating NDVI, and generating monthly composites for temporal and spatial analysis.

## Features

- Search Sentinel-2 imagery by area of interest (AOI) and date range.
- Filter satellite scenes by maximum cloud coverage.
- Calculate NDVI from Sentinel-2 imagery.
- Generate monthly NDVI composites using pixel-wise median values.
- Assess valid spatial coverage for each monthly composite.
- Export monthly statistics to CSV.
- Generate temporal NDVI charts.
- Generate spatial comparison maps for monthly composites.
- Support AOI files in Shapefile, GeoJSON, JSON, and KML formats.

## Tech Stack

- Python
- Rasterio
- NumPy
- GeoPandas
- Shapely
- Pandas
- Matplotlib
- PyProj
- Copernicus Data Space Ecosystem

## Requirements

- Python 3.12+
- Copernicus Data Space account and API credentials

## Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/sentinel-2-explorer.git
cd sentinel-2-explorer
```

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure your Copernicus Data Space credentials in a `.env` file in the project root. Use the environment variable names expected by `src/auth.py`.

## Usage

Run the application by providing an area of interest, a date range, and optional processing parameters:

```bash
python main.py --area data/area_teste.geojson --start 2024-06-01 --end 2025-06-30
```

Available arguments:

| Argument | Description | Default |
|---|---|---|
| `--area` | Path to the AOI file | Required |
| `--start` | Start date (`YYYY-MM-DD`) | Required |
| `--end` | End date (`YYYY-MM-DD`) | Required |
| `--max-cloud` | Maximum scene cloud coverage (%) | 30 |
| `--min-coverage` | Minimum valid AOI coverage required for a monthly composite (%) | 70 |

Example with custom thresholds:

```bash
python main.py --area data/area_teste.geojson --start 2024-06-01 --end 2025-06-30 --max-cloud 20 --min-coverage 80
```

## Outputs

Generated files are saved under `output/`:

```text
output/
├── acquisitions/
│   └── Individual acquisition data
└── monthly/
    ├── Monthly NDVI GeoTIFF composites
    ├── monthly_report.csv
    ├── temporal_series_summary.csv
    ├── temporal_series.png
    └── ndvi_comparison_*.png
```

Monthly composites are generated only when the minimum valid spatial coverage threshold is met. Months without sufficient valid data are reported but are not interpolated or artificially filled.

<img width="2713" height="2860" alt="ndvi_monthly_comparison_2025" src="https://github.com/user-attachments/assets/6ca1a758-9e7d-40da-a148-0a8596ad4eb6" />


## Methodology

The processing workflow consists of:

1. Searching Sentinel-2 scenes intersecting the supplied AOI and date range.
2. Filtering scenes according to their reported cloud coverage.
3. Calculating NDVI for each acquisition.
4. Grouping valid acquisitions by calendar month.
5. Generating monthly composites using the pixel-wise median of valid NDVI observations.
6. Evaluating valid pixel coverage within the AOI.
7. Exporting temporal statistics and spatial visualizations.

The monthly composites use a consistent spatial grid to support pixel-level comparison across time.

## Limitations

- Cloud coverage metadata is scene-level and does not represent cloud coverage exclusively within the AOI.
- Monthly composites below the configured valid coverage threshold are excluded.
- Missing months are not interpolated.
- UTM-based processing is intended for areas that can be represented appropriately in a single UTM zone.

## License

To be defined.
