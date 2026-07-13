"""
eda_geographic.py
Section 4.2: Geographic and spatial analysis — listing density, price gradients,
review score clustering by location.
Usage: python src/analysis/eda_geographic.py
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[3]))

import duckdb
import pandas as pd
import folium
from folium.plugins import HeatMap
from src.utils.config import load_config


def main():
    config = load_config()
    city = config["city"]["name"]
    processed_dir = Path(config["paths"]["processed_dir"])
    fig_dir = Path("report/figures")
    fig_dir.mkdir(parents=True, exist_ok=True)

    db_path = processed_dir / f"{city}_warehouse.duckdb"
    con = duckdb.connect(str(db_path), read_only=True)

    # We need lat/lon which live in the raw master parquet, not the star schema
    # (kept out of fact_listings deliberately — geo columns belong with property attributes)
    master = pd.read_parquet(processed_dir / f"listings_master_{city}.parquet")
    geo_df = master[["id", "latitude", "longitude", "price_clean", "review_scores_rating", "neighbourhood_cleansed", "price_likely_artifact"]].copy()
    geo_df = geo_df.dropna(subset=["latitude", "longitude"])
    geo_df = geo_df[~geo_df["price_likely_artifact"]]

    print(f"Listings with valid coordinates: {len(geo_df)}")

    # ---- 1. Listing density heatmap ----
    center_lat, center_lon = geo_df["latitude"].mean(), geo_df["longitude"].mean()
    density_map = folium.Map(location=[center_lat, center_lon], zoom_start=11, tiles="cartodbpositron")
    HeatMap(geo_df[["latitude", "longitude"]].values.tolist(), radius=8).add_to(density_map)
    density_map.save(str(fig_dir / "map01_listing_density.html"))
    print("Saved map01_listing_density.html")

    # ---- 2. Price gradient: is there a "distance from center" effect? ----
    import numpy as np
    geo_df["dist_from_center_km"] = np.sqrt(
        (geo_df["latitude"] - center_lat) ** 2 + (geo_df["longitude"] - center_lon) ** 2
    ) * 111  # rough degrees-to-km conversion

    corr = geo_df[["dist_from_center_km", "price_clean"]].dropna().corr().iloc[0, 1]
    print(f"\nCorrelation between distance-from-center and price: {corr:.3f}")

    # ---- 3. Review scores by neighbourhood — top/bottom 5 ----
    neigh_ratings = con.execute("""
        SELECT neighbourhood, neighbourhood_avg_rating, neighbourhood_listing_count
        FROM dim_neighbourhood
        WHERE neighbourhood_listing_count >= 30  -- avoid tiny-sample noise
        ORDER BY neighbourhood_avg_rating DESC
    """).df()

    print("\n=== Top 5 neighbourhoods by avg rating (min 30 listings) ===")
    print(neigh_ratings.head(5))
    print("\n=== Bottom 5 neighbourhoods by avg rating (min 30 listings) ===")
    print(neigh_ratings.tail(5))

    neigh_ratings.to_csv("report/findings/section4_eda/neighbourhood_ratings.csv", index=False)

    # ---- 4. Property/room type geographic clustering ----
    room_type_by_neigh = con.execute("""
        SELECT f.neighbourhood, p.room_type, COUNT(*) AS n
        FROM fact_listings f
        JOIN dim_property p ON f.listing_id = p.listing_id
        GROUP BY f.neighbourhood, p.room_type
    """).df()
    room_type_by_neigh.to_csv("report/findings/section4_eda/room_type_by_neighbourhood.csv", index=False)
    print("\nSaved room_type_by_neighbourhood.csv")

    con.close()
    print("\nEDA Part 2 (geographic) complete.")


if __name__ == "__main__":
    main()