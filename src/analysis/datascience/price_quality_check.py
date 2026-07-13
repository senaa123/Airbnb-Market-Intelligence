"""
price_quality_check.py
Data quality investigation: checks whether extreme high prices are genuine
outliers or scraping/data-entry artifacts, using the cleaned master dataset
(before any modeling-specific filtering).
Usage: python src/analysis/datascience/price_quality_check.py
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[3]))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from src.utils.config import load_config


def main():
    config = load_config()
    city = config["city"]["name"]
    processed_dir = Path(config["paths"]["processed_dir"])
    out_dir = Path("report/findings/section6_datascience")
    fig_dir = Path("report/figures")
    out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_parquet(processed_dir / f"listings_master_{city}.parquet")
    df = df[df["price_clean"].notna()].copy()

    print(f"Total listings with valid price: {len(df)}")
    print(f"\nPrice percentiles:")
    for p in [50, 90, 95, 99, 99.5, 99.9, 100]:
        print(f"  {p}th percentile: {df['price_clean'].quantile(p/100):,.2f}")

    # ---- 1. Scatter: price vs accommodates (log scale) — genuine prices should
    #    roughly trend upward with capacity; scattered "vertical strips" of
    #    identical extreme prices across different capacities suggest artifacts ----
    plt.figure(figsize=(9, 6))
    plt.scatter(df["accommodates"], df["price_clean"], alpha=0.15, s=10)
    plt.yscale("log")
    plt.xlabel("Accommodates (guest capacity)")
    plt.ylabel("Price (THB, log scale)")
    plt.title("Price vs Accommodates (log scale) — checking for outlier patterns")
    plt.tight_layout()
    plt.savefig(fig_dir / "fig09_price_quality_check.png")
    plt.close()
    print("\nSaved fig09_price_quality_check.png")

    # ---- 2. Check top 20 highest prices for suspicious patterns:
    #    round numbers, repeated exact values, or price_per_bedroom absurdity ----
    top20 = df.nlargest(20, "price_clean")[
        ["id", "price_clean", "accommodates", "bedrooms", "price_per_bedroom", "room_type", "name"]
    ].copy()
    top20["is_round_number"] = (top20["price_clean"] % 1000 == 0) | (top20["price_clean"] % 10000 == 0)
    print("\n=== Top 20 highest-priced listings ===")
    print(top20.to_string(index=False))
    top20.to_csv(out_dir / "price_quality_top20.csv", index=False)

    # ---- 3. Check for duplicate/repeated exact extreme prices (a real signal
    #    of scraping artifacts — genuine market prices rarely repeat exactly) ----
    high_price_threshold = df["price_clean"].quantile(0.99)
    high_prices = df[df["price_clean"] >= high_price_threshold]["price_clean"]
    duplicated_count = high_prices.duplicated().sum()
    print(f"\nOf {len(high_prices)} listings above the 99th percentile "
          f"({high_price_threshold:,.2f} THB), {duplicated_count} share an exact "
          f"duplicate price with another listing in this group.")

    # ---- 4. price_per_bedroom sanity check — extreme per-bedroom prices are a
    #    stronger signal of error than raw price alone, since it normalizes for size ----
    print("\n=== Top 10 by price_per_bedroom (normalizes for listing size) ===")
    top_ppb = df.nlargest(10, "price_per_bedroom")[
        ["id", "price_clean", "bedrooms", "price_per_bedroom", "room_type"]
    ]
    print(top_ppb.to_string(index=False))
    top_ppb.to_csv(out_dir / "price_per_bedroom_check.csv", index=False)

    print("\nQuality check complete. Review fig09 and the two CSVs before deciding on outlier handling.")


if __name__ == "__main__":
    main()