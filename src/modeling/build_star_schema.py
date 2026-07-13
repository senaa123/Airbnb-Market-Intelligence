"""
build_star_schema.py
Builds a star schema (fact + dimension tables) in a persistent DuckDB database
from the enriched master listings table.
Usage: python src/build_star_schema.py
"""

import duckdb
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

    master = pd.read_parquet(processed_dir / f"listings_master_{city}.parquet")

    db_path = processed_dir / f"{city}_warehouse.duckdb"
    con = duckdb.connect(str(db_path))

    con.register("master_df", master)

    # ---- dim_host ----
    con.execute("""
        CREATE OR REPLACE TABLE dim_host AS
        SELECT DISTINCT
            host_id,
            host_name,
            host_is_superhost,
            host_listings_count,
            host_identity_verified,
            host_has_profile_pic
        FROM master_df
    """)

    # ---- dim_neighbourhood ----
    con.execute("""
        CREATE OR REPLACE TABLE dim_neighbourhood AS
        SELECT DISTINCT
            neighbourhood_cleansed AS neighbourhood,
            neighbourhood_listing_count,
            neighbourhood_median_price,
            neighbourhood_avg_rating
        FROM master_df
    """)

    # ---- dim_property ----
    con.execute("""
        CREATE OR REPLACE TABLE dim_property AS
        SELECT DISTINCT
            id AS listing_id,
            property_type,
            room_type,
            accommodates,
            bedrooms,
            bathrooms,
            beds
        FROM master_df
    """)

    # ---- fact_listings (grain: one row per listing) ----
    con.execute("""
        CREATE OR REPLACE TABLE fact_listings AS
        SELECT
            id AS listing_id,
            host_id,
            neighbourhood_cleansed AS neighbourhood,
            price_clean AS price,
            price_missing,
            price_likely_artifact,
            occupancy_rate_pct,
            booked_days,
            estimated_revenue_365d,
            number_of_reviews,
            has_reviews,
            is_new_listing,
            review_scores_rating,
            review_frequency,
            price_per_bedroom
        FROM master_df
    """)

    print("Star schema built. Tables created:")
    print(con.execute("SHOW TABLES").df())

    print("\nfact_listings row count:", con.execute("SELECT COUNT(*) FROM fact_listings").fetchone()[0])

    # ---- Sample analytical queries demonstrating the model ----
    print("\n--- Query 1: Top 5 neighbourhoods by median price ---")
    print(con.execute("""
        SELECT neighbourhood, neighbourhood_median_price, neighbourhood_listing_count
        FROM dim_neighbourhood
        ORDER BY neighbourhood_median_price DESC
        LIMIT 5
    """).df())

    print("\n--- Query 2: Avg price and occupancy by room type ---")
    print(con.execute("""
        SELECT p.room_type,
               ROUND(AVG(f.price), 2) AS avg_price,
               ROUND(AVG(f.occupancy_rate_pct), 2) AS avg_occupancy_pct,
               COUNT(*) AS n_listings
        FROM fact_listings f
        JOIN dim_property p ON f.listing_id = p.listing_id
        GROUP BY p.room_type
        ORDER BY avg_price DESC
    """).df())

    print("\n--- Query 3: Superhost vs non-superhost avg rating ---")
    print(con.execute("""
        SELECT h.host_is_superhost,
               ROUND(AVG(f.review_scores_rating), 3) AS avg_rating,
               COUNT(*) AS n_listings
        FROM fact_listings f
        JOIN dim_host h ON f.host_id = h.host_id
        WHERE f.review_scores_rating IS NOT NULL
        GROUP BY h.host_is_superhost
    """).df())

    con.close()
    print(f"\nDatabase saved at: {db_path}")


if __name__ == "__main__":
    main()