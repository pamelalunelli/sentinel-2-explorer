
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


def plot_temporal_series(results, output_path, start, end):
    data = pd.DataFrame(results)

    start_month = pd.to_datetime(start).to_period("M").to_timestamp()
    end_month = pd.to_datetime(end).to_period("M").to_timestamp()

    months = pd.date_range(
        start=start_month,
        end=end_month,
        freq="MS"
    )

    if not data.empty:
        data["month"] = pd.to_datetime(data["month"]).dt.to_period("M").dt.to_timestamp()
        data = data.set_index("month").reindex(months)
    else:
        data = pd.DataFrame(index=months)

    data.index.name = "month"

    data["acquisitions"] = data["acquisitions"].fillna(0).astype(int)
    data["status"] = data["status"].fillna("NO_DATA")

    approved = data["status"] == "APPROVED"

    for column in [
        "valid_coverage",
        "ndvi_mean",
        "ndvi_median",
        "ndvi_min",
        "ndvi_max",
        "low_vegetation",
        "moderate_vegetation",
        "dense_vegetation"
    ]:
        data.loc[~approved, column] = float("nan")

    output_dir = Path(output_path)
    output_dir.parent.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(12, 6))

    plt.plot(
        data.index,
        data["ndvi_median"],
        marker="o",
        linewidth=2,
        label="Monthly median NDVI"
    )

    plt.fill_between(
        data.index,
        data["ndvi_min"],
        data["ndvi_max"],
        alpha=0.2,
        label="NDVI range"
    )

    plt.title("Monthly NDVI Time Series")
    plt.xlabel("Month")
    plt.ylabel("NDVI")
    plt.ylim(-1, 1)
    plt.xticks(months, [month.strftime("%b %Y") for month in months], rotation=45)
    plt.grid(True, alpha=0.3)
    plt.legend()

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()

    summary_path = output_dir.with_name(
        f"{output_dir.stem}_summary.csv"
    )

    data.reset_index().to_csv(
        summary_path,
        index=False,
        na_rep="",
        encoding="utf-8-sig"
    )

    print(f"Temporal chart saved: {output_path}")
    print(f"Monthly summary saved: {summary_path}")
