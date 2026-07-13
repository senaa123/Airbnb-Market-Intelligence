"""
hypothesis_tests.py
Section 5.1: Formal hypothesis testing on the Airbnb dataset (H1-H5).
Usage: python src/analysis/hypothesis_tests.py
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[3]))

import duckdb
import pandas as pd
import numpy as np
from scipy import stats
from src.utils.config import load_config


def cohens_d(group1, group2):
    """Effect size for two independent groups."""
    n1, n2 = len(group1), len(group2)
    var1, var2 = group1.var(ddof=1), group2.var(ddof=1)
    pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
    return (group1.mean() - group2.mean()) / pooled_std


def eta_squared(groups):
    """Effect size for ANOVA (one-way)."""
    all_values = np.concatenate(groups)
    grand_mean = all_values.mean()
    ss_between = sum(len(g) * (g.mean() - grand_mean) ** 2 for g in groups)
    ss_total = sum((all_values - grand_mean) ** 2)
    return ss_between / ss_total


def main():
    config = load_config()
    city = config["city"]["name"]
    processed_dir = Path(config["paths"]["processed_dir"])
    raw_dir = Path(config["paths"]["raw_dir"]) / city

    db_path = processed_dir / f"{city}_warehouse.duckdb"
    con = duckdb.connect(str(db_path), read_only=True)

    results = []

    # ============================================================
    # H1: Entire-home listings have significantly higher prices than private rooms
    # ============================================================
    print("=== H1: Entire home vs Private room price ===")
    df = con.execute("""
        SELECT f.price, p.room_type
        FROM fact_listings f JOIN dim_property p ON f.listing_id = p.listing_id
        WHERE f.price IS NOT NULL AND NOT f.price_likely_artifact AND p.room_type IN ('Entire home/apt', 'Private room')
    """).df()

    entire = df[df["room_type"] == "Entire home/apt"]["price"]
    private = df[df["room_type"] == "Private room"]["price"]

    # Assumption check: normality via sample size (both n > 5000, CLT applies; skip Shapiro on huge n)
    # Use Mann-Whitney U as a robust alternative since price is right-skewed (non-normal)
    u_stat, p_val = stats.mannwhitneyu(entire, private, alternative="greater")
    d = cohens_d(entire, private)

    print(f"n_entire={len(entire)}, n_private={len(private)}")
    print(f"Mann-Whitney U={u_stat:.1f}, p={p_val:.6f}, Cohen's d={d:.3f}")
    print(f"Median entire={entire.median():.2f}, Median private={private.median():.2f}\n")

    results.append({
        "hypothesis": "H1", "test": "Mann-Whitney U", "statistic": u_stat,
        "p_value": p_val, "effect_size": d, "effect_size_type": "Cohen's d"
    })

    # ============================================================
    # H2: Superhost listings have higher review scores than non-superhost
    # ============================================================
    print("=== H2: Superhost vs non-superhost review scores ===")
    df2 = con.execute("""
        SELECT f.review_scores_rating, h.host_is_superhost
        FROM fact_listings f JOIN dim_host h ON f.host_id = h.host_id
        WHERE f.review_scores_rating IS NOT NULL
    """).df()

    superhost = df2[df2["host_is_superhost"] == True]["review_scores_rating"]
    non_superhost = df2[df2["host_is_superhost"] == False]["review_scores_rating"]

    u_stat2, p_val2 = stats.mannwhitneyu(superhost, non_superhost, alternative="greater")
    d2 = cohens_d(superhost, non_superhost)

    print(f"n_superhost={len(superhost)}, n_non={len(non_superhost)}")
    print(f"Mann-Whitney U={u_stat2:.1f}, p={p_val2:.6f}, Cohen's d={d2:.3f}")
    print(f"Mean superhost={superhost.mean():.3f}, Mean non-superhost={non_superhost.mean():.3f}\n")

    results.append({
        "hypothesis": "H2", "test": "Mann-Whitney U", "statistic": u_stat2,
        "p_value": p_val2, "effect_size": d2, "effect_size_type": "Cohen's d"
    })

    # ============================================================
    # H3: Listings with >10 reviews have significantly different prices than <=10
    # ============================================================
    print("=== H3: Price by review count (>10 vs <=10) ===")
    df3 = con.execute("""
        SELECT price, number_of_reviews
        FROM fact_listings
        WHERE price IS NOT NULL AND NOT price_likely_artifact
    """).df()

    more_reviews = df3[df3["number_of_reviews"] > 10]["price"]
    fewer_reviews = df3[df3["number_of_reviews"] <= 10]["price"]

    u_stat3, p_val3 = stats.mannwhitneyu(more_reviews, fewer_reviews, alternative="two-sided")
    d3 = cohens_d(more_reviews, fewer_reviews)

    print(f"n_more={len(more_reviews)}, n_fewer={len(fewer_reviews)}")
    print(f"Mann-Whitney U={u_stat3:.1f}, p={p_val3:.6f}, Cohen's d={d3:.3f}")
    print(f"Median more_reviews={more_reviews.median():.2f}, Median fewer_reviews={fewer_reviews.median():.2f}\n")

    results.append({
        "hypothesis": "H3", "test": "Mann-Whitney U", "statistic": u_stat3,
        "p_value": p_val3, "effect_size": d3, "effect_size_type": "Cohen's d"
    })

    # ============================================================
    # H4: Neighbourhood average prices differ significantly (ANOVA)
    # ============================================================
    print("=== H4: Price across neighbourhoods (ANOVA) ===")
    df4 = con.execute("""
        SELECT f.price, f.neighbourhood
        FROM fact_listings f
        WHERE f.price IS NOT NULL AND NOT f.price_likely_artifact
        AND f.neighbourhood IN (
            SELECT neighbourhood FROM dim_neighbourhood
            WHERE neighbourhood_listing_count >= 30
        )
    """).df()

    groups = [g["price"].values for _, g in df4.groupby("neighbourhood")]
    f_stat, p_val4 = stats.f_oneway(*groups)
    eta_sq = eta_squared(groups)

    print(f"n_neighbourhoods={len(groups)}, total_n={len(df4)}")
    print(f"F-statistic={f_stat:.3f}, p={p_val4:.6f}, eta-squared={eta_sq:.4f}\n")

    results.append({
        "hypothesis": "H4", "test": "One-way ANOVA", "statistic": f_stat,
        "p_value": p_val4, "effect_size": eta_sq, "effect_size_type": "eta-squared"
    })

    # ============================================================
    # H5: Weekend vs weekday pricing differences (from calendar — needs price per day,
    # which this scrape's calendar lacks; using listings.price as static proxy is invalid,
    # so we substitute: minimum_nights weekend vs weekday as the closest testable proxy,
    # and flag the original test as not feasible with this data)
    # ============================================================
    print("=== H5: Weekend vs weekday (adapted — see notes) ===")
    calendar_path = raw_dir / "calendar.csv.gz"
    df5 = con.execute(f"""
        SELECT date, minimum_nights,
               CASE WHEN strftime(CAST(date AS DATE), '%w') IN ('0','6') THEN 'weekend' ELSE 'weekday' END AS day_type
        FROM read_csv_auto('{calendar_path.as_posix()}')
    """).df()

    weekend = df5[df5["day_type"] == "weekend"]["minimum_nights"]
    weekday = df5[df5["day_type"] == "weekday"]["minimum_nights"]

    u_stat5, p_val5 = stats.mannwhitneyu(weekend, weekday, alternative="two-sided")
    d5 = cohens_d(weekend, weekday)

    print(f"n_weekend={len(weekend)}, n_weekday={len(weekday)}")
    print(f"Mann-Whitney U={u_stat5:.1f}, p={p_val5:.6f}, Cohen's d={d5:.3f}\n")

    results.append({
        "hypothesis": "H5 (adapted)", "test": "Mann-Whitney U", "statistic": u_stat5,
        "p_value": p_val5, "effect_size": d5, "effect_size_type": "Cohen's d"
    })

    # Save all results
    results_df = pd.DataFrame(results)
    results_df.to_csv("report/findings/section5_statistics/hypothesis_test_results.csv", index=False)
    print("Saved hypothesis_test_results.csv")

    con.close()


if __name__ == "__main__":
    main()