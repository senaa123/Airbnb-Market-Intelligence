"""
process_calendar.py
Uses DuckDB to compute per-listing occupancy stats directly from the compressed
calendar file, without loading all 11M+ rows into pandas memory.

"""

import duckdb
import yaml
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))  # adds project root to path

from src.utils.config import load_config


def main():
    config = load_config()
    city = config["city"]["name"]
    raw_dir = Path(config["paths"]["raw_dir"]) / city
    processed_dir = Path(config["paths"]["processed_dir"])
    processed_dir.mkdir(parents=True, exist_ok=True)

    calendar_path = raw_dir / "calendar.csv.gz"

    con = duckdb.connect()

    # Query directly on the compressed CSV — DuckDB reads gzip natively
    query = f"""
        SELECT
            listing_id,
            COUNT(*) AS total_days,
            SUM(CASE WHEN available = 'f' THEN 1 ELSE 0 END) AS booked_days,
            ROUND(SUM(CASE WHEN available = 'f' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS occupancy_rate_pct,
            AVG(minimum_nights) AS avg_minimum_nights,
            MIN(date) AS calendar_start,
            MAX(date) AS calendar_end
        FROM read_csv_auto('{calendar_path.as_posix()}')
        GROUP BY listing_id
    """

    print("Running DuckDB aggregation over calendar file...")
    result_df = con.execute(query).df()
    print(f"Computed occupancy stats for {len(result_df)} listings")
    print(result_df.head())

    out_path = processed_dir / f"calendar_occupancy_{city}.parquet"
    result_df.to_parquet(out_path, index=False)
    print(f"Saved to {out_path}")

    con.close()


if __name__ == "__main__":
    main()