"""
enrich_listings.py
Joins cleaned listings with calendar occupancy data and adds neighbourhood-level
aggregates and derived fields.

"""

import pandas as pd
import yaml
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))  # adds project root to path

from src.utils.config import load_config


def main():
    config = load_config()
    city = config["city"]["name"]
    processed_dir = Path(config["paths"]["processed_dir"])

    listings = pd.read_parquet(processed_dir / f"listings_clean_{city}.parquet")
    occupancy = pd.read_parquet(processed_dir / f"calendar_occupancy_{city}.parquet")

    print(f"Listings: {len(listings)} rows | Occupancy: {len(occupancy)} rows")

    # 1. Join listings with calendar occupancy (left join — some listings may lack calendar data)
    master = listings.merge(
        occupancy[["listing_id", "booked_days", "occupancy_rate_pct", "avg_minimum_nights"]],
        left_on="id", right_on="listing_id", how="left"
    )
    unmatched = master["occupancy_rate_pct"].isnull().sum()
    print(f"Listings without matching calendar data: {unmatched}")

    # 2. Revenue estimate — since calendar has no price column for this city (documented limitation),
    #    we estimate using cleaned listing price x already-provided estimated_occupancy_l365d
    master["estimated_revenue_365d"] = master["price_clean"] * master["estimated_occupancy_l365d"]

    # 3. Neighbourhood-level aggregates, joined back onto each listing
    neigh_agg = master.groupby("neighbourhood_cleansed").agg(
        neighbourhood_listing_count=("id", "count"),
        neighbourhood_median_price=("price_clean", "median"),
        neighbourhood_avg_rating=("review_scores_rating", "mean")
    ).reset_index()

    master = master.merge(neigh_agg, on="neighbourhood_cleansed", how="left")

    # 4. Review frequency (reviews per month already exists, but let's confirm/derive cleanly)
    master["review_frequency"] = master["reviews_per_month"].fillna(0)

    out_path = processed_dir / f"listings_master_{city}.parquet"
    master.to_parquet(out_path, index=False)
    print(f"Saved enriched master table: {out_path}")
    print(f"Final shape: {master.shape}")


if __name__ == "__main__":
    main()