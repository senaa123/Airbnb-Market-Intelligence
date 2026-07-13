"""
eda_temporal.py
Section 4.3: Temporal and seasonal trends — pricing evolution, review volume,
minimum night policy shifts. Uses DuckDB directly on the calendar file since
we need daily granularity here (the star schema is listing-grain, aggregated).
Usage: python src/analysis/eda/eda_temporal.py
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[3]))

import duckdb
import pandas as pd
import matplotlib.pyplot as plt
from src.utils.config import load_config

plt.rcParams["figure.dpi"] = 120


def main():
    config = load_config()
    city = config["city"]["name"]
    raw_dir = Path(config["paths"]["raw_dir"]) / city
    processed_dir = Path(config["paths"]["processed_dir"])
    fig_dir = Path("report/figures")
    fig_dir.mkdir(parents=True, exist_ok=True)

    con = duckdb.connect()
    calendar_path = raw_dir / "calendar.csv.gz"

    # ---- 1. Booking rate by month (available='f' means booked) ----
    print("=== Booking rate by month ===")
    monthly = con.execute(f"""
        SELECT
            strftime(CAST(date AS DATE), '%Y-%m') AS year_month,
            COUNT(*) AS total_days,
            SUM(CASE WHEN available = 'f' THEN 1 ELSE 0 END) AS booked_days,
            ROUND(SUM(CASE WHEN available = 'f' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS booked_pct
        FROM read_csv_auto('{calendar_path.as_posix()}')
        GROUP BY year_month
        ORDER BY year_month
    """).df()
    print(monthly)
    monthly.to_csv("report/findings/section4_eda/monthly_booking_rate.csv", index=False)

    plt.figure(figsize=(10, 5))
    plt.plot(monthly["year_month"], monthly["booked_pct"], marker="o")
    plt.title("Figure 5: Booking Rate (%) by Month")
    plt.xlabel("Month")
    plt.ylabel("Booked Days (%)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(fig_dir / "fig05_monthly_booking_rate.png")
    plt.close()
    print("Saved fig05_monthly_booking_rate.png")

    # ---- 2. Minimum nights policy — does it shift seasonally? ----
    print("\n=== Avg minimum nights by month ===")
    min_nights_monthly = con.execute(f"""
        SELECT
            strftime(CAST(date AS DATE), '%Y-%m') AS year_month,
            ROUND(AVG(minimum_nights), 2) AS avg_min_nights
        FROM read_csv_auto('{calendar_path.as_posix()}')
        GROUP BY year_month
        ORDER BY year_month
    """).df()
    print(min_nights_monthly)
    min_nights_monthly.to_csv("report/findings/section4_eda/monthly_min_nights.csv", index=False)

    # ---- 3. Review volume trend — are bookings growing or declining? ----
    reviews_path = raw_dir / "reviews.csv.gz"
    print("\n=== Review volume by year ===")
    review_trend = con.execute(f"""
        SELECT
            strftime(CAST(date AS DATE), '%Y') AS year,
            COUNT(*) AS n_reviews
        FROM read_csv_auto('{reviews_path.as_posix()}')
        GROUP BY year
        ORDER BY year
    """).df()
    print(review_trend)
    review_trend.to_csv("report/findings/section4_eda/review_volume_by_year.csv", index=False)

    plt.figure(figsize=(9, 5))
    plt.bar(review_trend["year"], review_trend["n_reviews"])
    plt.title("Figure 6: Review Volume by Year (Booking Demand Proxy)")
    plt.xlabel("Year")
    plt.ylabel("Number of Reviews")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(fig_dir / "fig06_review_volume_by_year.png")
    plt.close()
    print("Saved fig06_review_volume_by_year.png")

    con.close()
    print("\nEDA Part 3 (temporal) complete.")


if __name__ == "__main__":
    main()