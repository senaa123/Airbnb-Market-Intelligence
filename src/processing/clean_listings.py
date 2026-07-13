"""
clean_listings.py
Cleans the listings dataset: drops dead columns, fixes types, validates ranges.
Usage: python src/clean_listings.py
"""

import pandas as pd
import numpy as np
import yaml
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))  # adds project root to path

from src.utils.config import load_config

COLUMNS_TO_DROP = [
    "neighborhood_overview", "host_since", "host_response_time",
    "host_response_rate", "host_acceptance_rate", "host_thumbnail_url",
    "host_neighbourhood", "host_total_listings_count", "host_verifications",
    "neighbourhood", "neighbourhood_group_cleansed", "calendar_updated",
    "license", "instant_bookable"
]

BOOL_COLUMNS = ["host_is_superhost", "host_has_profile_pic", "host_identity_verified", "has_availability"]

DATE_COLUMNS = ["last_scraped", "first_review", "last_review", "calendar_last_scraped"]


def clean_price(series: pd.Series) -> pd.Series:
    """Converts '$1,234.00' style strings to float. Leaves NaN as NaN."""
    return (
        series.astype(str)
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
        .replace("nan", np.nan)
        .astype(float)
    )


def clean_bool(series: pd.Series) -> pd.Series:
    """Converts 't'/'f' strings to True/False, keeps NaN as NaN."""
    return series.map({"t": True, "f": False})


def main():
    config = load_config()
    city = config["city"]["name"]
    raw_dir = Path(config["paths"]["raw_dir"]) / city
    processed_dir = Path(config["paths"]["processed_dir"])
    processed_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(raw_dir / "listings.csv.gz", compression="gzip", low_memory=False)
    print(f"Loaded {len(df)} rows, {len(df.columns)} columns")

    # 1. Drop dead columns
    df = df.drop(columns=[c for c in COLUMNS_TO_DROP if c in df.columns])
    print(f"After dropping dead columns: {len(df.columns)} columns")

    # 2. Clean price — flag missing, don't drop (keeps rows usable for non-price analyses)
    df["price_clean"] = clean_price(df["price"])
    df["price_missing"] = df["price_clean"].isnull()
    print(f"Price missing: {df['price_missing'].sum()} rows ({df['price_missing'].mean()*100:.1f}%) — kept, flagged, not dropped")

    # Data quality: flag likely non-genuine listings with placeholder/artifact prices.
    # Verified against raw source: several extreme-price listings are Chinese-language
    # internal placeholder entries (e.g. "room swap standby," "not for sale"), and a
    # separate cluster of 5 unrelated "My Hostel" listings share an identical $300,000
    # price to the cent — both patterns inconsistent with genuine host-set pricing.
    price_99th = df["price_clean"].quantile(0.99)
    df["price_likely_artifact"] = df["price_clean"] > price_99th
    n_flagged = df["price_likely_artifact"].sum()
    print(f"Flagged {n_flagged} listings above 99th percentile price ({price_99th:.2f} THB) as likely data artifacts")
    
    # 3. Convert boolean columns
    for col in BOOL_COLUMNS:
        if col in df.columns:
            df[col] = clean_bool(df[col])

    # 4. Parse dates
    for col in DATE_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # 5. Impute bathrooms/bedrooms/beds using median by room_type, with global fallback
    for col in ["bathrooms", "bedrooms", "beds"]:
        group_median = df.groupby("room_type")[col].transform("median")
        df[col] = df[col].fillna(group_median)
        df[col] = df[col].fillna(df[col].median())  # fallback if a room_type group was all-NaN

    # 5b. Review-based flags
    df["has_reviews"] = df["number_of_reviews"] > 0
    df["is_new_listing"] = df["number_of_reviews"] == 0
       
    # 6. Validation checks — flag, don't silently drop
    invalid_price = (df["price_clean"] < 0).sum()
    invalid_lat = ((df["latitude"] < -90) | (df["latitude"] > 90)).sum()
    invalid_lon = ((df["longitude"] < -180) | (df["longitude"] > 180)).sum()
    print(f"Validation -> negative prices: {invalid_price}, invalid lat: {invalid_lat}, invalid lon: {invalid_lon}")

    # 7. Derived fields the assignment explicitly asks for
    df["price_per_bedroom"] = df["price_clean"] / df["bedrooms"].replace(0, np.nan)

    # 8. Save cleaned data (parquet = industry standard: smaller, faster, keeps dtypes)
    out_path = processed_dir / f"listings_clean_{city}.parquet"
    df.to_parquet(out_path, index=False)
    print(f"Saved cleaned listings to {out_path}")


if __name__ == "__main__":
    main()