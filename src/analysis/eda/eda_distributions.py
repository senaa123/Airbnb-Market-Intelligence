"""
eda_distributions.py
Section 4.1: Summary statistics and distribution analysis, queried directly
from the star schema (fact_listings + dim_property + dim_host).
Usage: python src/analysis/eda_distributions.py
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[3]))

import duckdb
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from src.utils.config import load_config

sns.set_style("whitegrid")
plt.rcParams["figure.dpi"] = 120


def main():
    config = load_config()
    city = config["city"]["name"]
    processed_dir = Path(config["paths"]["processed_dir"])
    fig_dir = Path("report/figures")
    fig_dir.mkdir(parents=True, exist_ok=True)

    db_path = processed_dir / f"{city}_warehouse.duckdb"
    con = duckdb.connect(str(db_path), read_only=True)

    # ---- 1. Descriptive stats on key numerical variables ----
    print("=== Descriptive Statistics: price ===")
    stats = con.execute("""
        SELECT
            COUNT(*) AS n,
            ROUND(AVG(price), 2) AS mean_price,
            ROUND(MEDIAN(price), 2) AS median_price,
            ROUND(STDDEV(price), 2) AS std_price,
            ROUND(MIN(price), 2) AS min_price,
            ROUND(MAX(price), 2) AS max_price,
            ROUND(QUANTILE_CONT(price, 0.25), 2) AS q1,
            ROUND(QUANTILE_CONT(price, 0.75), 2) AS q3
        FROM fact_listings
        WHERE price IS NOT NULL AND NOT price_likely_artifact
    """).df()
    print(stats)
    stats.to_csv("report/findings/section4_eda/price_summary_stats.csv", index=False)

    # ---- 2. Price distribution by room type ----
    df_price_room = con.execute("""
        SELECT f.price, p.room_type
        FROM fact_listings f
        JOIN dim_property p ON f.listing_id = p.listing_id
        WHERE f.price IS NOT NULL AND NOT f.price_likely_artifact
    """).df()

    plt.figure(figsize=(9, 5))
    sns.boxplot(data=df_price_room, x="room_type", y="price")
    plt.title("Figure 1: Price Distribution by Room Type (Bangkok)")
    plt.ylabel("Price (THB)")
    plt.xlabel("Room Type")
    plt.tight_layout()
    plt.savefig(fig_dir / "fig01_price_by_room_type.png")
    plt.close()
    print("Saved fig01_price_by_room_type.png")

    # ---- 3. Price distribution by neighbourhood (top 10 by listing count) ----
    df_price_neigh = con.execute("""
        SELECT f.price, f.neighbourhood
        FROM fact_listings f
        WHERE f.price IS NOT NULL AND NOT f.price_likely_artifact
        AND f.neighbourhood IN (
            SELECT neighbourhood FROM dim_neighbourhood
            ORDER BY neighbourhood_listing_count DESC LIMIT 10
        )
    """).df()

    plt.figure(figsize=(10, 6))
    order = df_price_neigh.groupby("neighbourhood")["price"].median().sort_values(ascending=False).index
    sns.boxplot(data=df_price_neigh, x="price", y="neighbourhood", order=order)
    plt.title("Figure 2: Price Distribution — Top 10 Neighbourhoods by Listing Count")
    plt.xlabel("Price (THB)")
    plt.ylabel("Neighbourhood")
    plt.tight_layout()
    plt.savefig(fig_dir / "fig02_price_by_neighbourhood.png")
    plt.close()
    print("Saved fig02_price_by_neighbourhood.png")

    # ---- 4. Listings per host (power law check) ----
    df_host_counts = con.execute("""
        SELECT host_id, COUNT(*) AS n_listings
        FROM fact_listings
        GROUP BY host_id
        ORDER BY n_listings DESC
    """).df()

    print("\n=== Host concentration ===")
    top_1pct_cutoff = int(len(df_host_counts) * 0.01)
    top_1pct_listings = df_host_counts.head(top_1pct_cutoff)["n_listings"].sum()
    total_listings = df_host_counts["n_listings"].sum()
    print(f"Top 1% of hosts ({top_1pct_cutoff} hosts) control "
          f"{top_1pct_listings} listings = {top_1pct_listings/total_listings*100:.1f}% of all listings")

    plt.figure(figsize=(9, 5))
    plt.hist(df_host_counts["n_listings"], bins=50, log=True)
    plt.title("Figure 3: Distribution of Listings per Host (log scale)")
    plt.xlabel("Number of Listings per Host")
    plt.ylabel("Number of Hosts (log scale)")
    plt.tight_layout()
    plt.savefig(fig_dir / "fig03_listings_per_host.png")
    plt.close()
    print("Saved fig03_listings_per_host.png")

    # ---- 5. Review score distribution + rating inflation check ----
    df_ratings = con.execute("""
        SELECT review_scores_rating
        FROM fact_listings
        WHERE review_scores_rating IS NOT NULL
    """).df()

    print("\n=== Review score distribution ===")
    print(df_ratings["review_scores_rating"].describe())
    pct_above_4_8 = (df_ratings["review_scores_rating"] >= 4.8).mean() * 100
    print(f"% of listings with rating >= 4.8: {pct_above_4_8:.1f}%")

    plt.figure(figsize=(9, 5))
    plt.hist(df_ratings["review_scores_rating"], bins=30)
    plt.title("Figure 4: Review Score Distribution")
    plt.xlabel("Review Score Rating")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig(fig_dir / "fig04_review_score_distribution.png")
    plt.close()
    print("Saved fig04_review_score_distribution.png")

    con.close()
    print("\nEDA Part 1 (distributions) complete. Figures in report/figures/, stats in report/findings/section4_eda/")


if __name__ == "__main__":
    main()