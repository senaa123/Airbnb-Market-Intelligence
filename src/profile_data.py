"""
profile_data.py
Loads raw Airbnb data, profiles it, and saves a data quality report to disk.

"""

import pandas as pd
import yaml
from pathlib import Path

pd.set_option("display.max_rows", None)      # don't truncate rows
pd.set_option("display.max_columns", None)   # don't truncate columns
pd.set_option("display.width", 150)


def load_config(config_path: str = "config.yaml") -> dict:
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def profile_dataframe(df: pd.DataFrame, name: str) -> pd.DataFrame:
    profile = pd.DataFrame({
        "dtype": df.dtypes.astype(str),
        "null_count": df.isnull().sum(),
        "null_pct": (df.isnull().sum() / len(df) * 100).round(2),
        "n_unique": df.nunique(),
    })
    profile.insert(0, "column", profile.index)
    profile.reset_index(drop=True, inplace=True)
    return profile


def check_duplicates(df: pd.DataFrame, key_col: str) -> dict:
    total = len(df)
    unique_keys = df[key_col].nunique()
    return {
        "total_rows": total,
        "unique_keys": unique_keys,
        "exact_duplicate_rows": df.duplicated().sum(),
        "duplicate_key_rows": total - unique_keys
    }


def save_report(profile: pd.DataFrame, extra_notes: str, filename: str, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / filename
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(extra_notes)
        f.write("\n\n")
        f.write(profile.to_markdown(index=False))
    print(f"Saved report: {out_path}")


def main():
    config = load_config()
    city = config["city"]["name"]
    raw_dir = Path(config["paths"]["raw_dir"]) / city
    report_dir = Path("report") / "data_quality"

    # ---- listings ----
    listings = pd.read_csv(raw_dir / "listings.csv.gz", compression="gzip", low_memory=False)
    dq = check_duplicates(listings, "id")
    notes = f"# listings.csv.gz\nShape: {listings.shape}\nDuplicate check: {dq}\n"
    profile = profile_dataframe(listings, "listings")
    save_report(profile, notes, "listings_profile.md", report_dir)

    # ---- calendar ----
    calendar = pd.read_csv(raw_dir / "calendar.csv.gz", compression="gzip", low_memory=False)
    dq = check_duplicates(calendar, "listing_id")  # note: NOT unique per row, many rows per listing
    notes = f"# calendar.csv.gz\nShape: {calendar.shape}\nRows per listing (approx): {len(calendar)/calendar['listing_id'].nunique():.1f}\n"
    profile = profile_dataframe(calendar, "calendar")
    save_report(profile, notes, "calendar_profile.md", report_dir)

    # ---- reviews ----
    reviews = pd.read_csv(raw_dir / "reviews.csv.gz", compression="gzip", low_memory=False)
    dq = check_duplicates(reviews, "id")
    notes = f"# reviews.csv.gz\nShape: {reviews.shape}\nDuplicate check: {dq}\n"
    profile = profile_dataframe(reviews, "reviews")
    save_report(profile, notes, "reviews_profile.md", report_dir)

    # ---- neighbourhoods ----
    neighbourhoods = pd.read_csv(raw_dir / "neighbourhoods.csv")
    notes = f"# neighbourhoods.csv\nShape: {neighbourhoods.shape}\n"
    profile = profile_dataframe(neighbourhoods, "neighbourhoods")
    save_report(profile, notes, "neighbourhoods_profile.md", report_dir)

    print("\nAll profiling reports saved to report/data_quality/")


if __name__ == "__main__":
    main()