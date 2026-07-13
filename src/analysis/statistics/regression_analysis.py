"""
regression_analysis.py
Section 5.2: Confidence intervals for mean prices.
Section 5.3: Correlation matrix, OLS regression, multicollinearity check (VIF).
Usage: python src/analysis/statistics/regression_analysis.py
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[3]))

import duckdb
import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
from src.utils.config import load_config


def confidence_interval(data, confidence=0.95):
    n = len(data)
    mean = data.mean()
    sem = stats.sem(data)
    margin = sem * stats.t.ppf((1 + confidence) / 2, n - 1)
    return mean, mean - margin, mean + margin


def main():
    config = load_config()
    city = config["city"]["name"]
    processed_dir = Path(config["paths"]["processed_dir"])
    out_dir = Path("report/findings/section5_statistics")
    out_dir.mkdir(parents=True, exist_ok=True)

    db_path = processed_dir / f"{city}_warehouse.duckdb"
    con = duckdb.connect(str(db_path), read_only=True)

    # ============================================================
    # Section 5.2: Confidence intervals by room type
    # ============================================================
    print("=== 5.2: Confidence intervals for mean price by room type ===")
    df = con.execute("""
        SELECT f.price, p.room_type
        FROM fact_listings f JOIN dim_property p ON f.listing_id = p.listing_id
        WHERE f.price IS NOT NULL AND NOT f.price_likely_artifact
    """).df()

    ci_results = []
    for room_type, group in df.groupby("room_type"):
        mean, lower, upper = confidence_interval(group["price"])
        ci_results.append({
            "room_type": room_type, "n": len(group),
            "mean_price": round(mean, 2),
            "ci_lower_95": round(lower, 2), "ci_upper_95": round(upper, 2)
        })
        print(f"{room_type}: mean={mean:.2f}, 95% CI=[{lower:.2f}, {upper:.2f}], n={len(group)}")

    ci_df = pd.DataFrame(ci_results)
    ci_df.to_csv(out_dir / "confidence_intervals_by_room_type.csv", index=False)

    # ============================================================
    # Section 5.3: Correlation matrix
    # ============================================================
    print("\n=== 5.3: Correlation matrix ===")
    df_corr = con.execute("""
        SELECT f.price, f.number_of_reviews, f.review_scores_rating,
               f.occupancy_rate_pct, p.accommodates, p.bedrooms, p.bathrooms, p.beds
        FROM fact_listings f JOIN dim_property p ON f.listing_id = p.listing_id
        WHERE f.price IS NOT NULL AND NOT f.price_likely_artifact
    """).df().dropna()

    corr_matrix = df_corr.corr()
    print(corr_matrix["price"].sort_values(ascending=False))
    corr_matrix.to_csv(out_dir / "correlation_matrix.csv")

    # ============================================================
    # Section 5.3: OLS Regression — what drives price?
    # ============================================================
    print("\n=== 5.3: OLS Regression on price ===")
    X = df_corr[["number_of_reviews", "review_scores_rating", "occupancy_rate_pct",
                 "accommodates", "bedrooms", "bathrooms", "beds"]]
    y = df_corr["price"]
    X = sm.add_constant(X)

    model = sm.OLS(y, X).fit()
    print(model.summary())

    with open(out_dir / "regression_summary.txt", "w") as f:
        f.write(str(model.summary()))

    # ============================================================
    # Section 5.3: VIF (multicollinearity check)
    # ============================================================
    print("\n=== 5.3: Variance Inflation Factor (multicollinearity check) ===")
    vif_data = pd.DataFrame()
    vif_data["feature"] = X.columns
    vif_data["VIF"] = [variance_inflation_factor(X.values, i) for i in range(X.shape[1])]
    print(vif_data)
    vif_data.to_csv(out_dir / "vif_results.csv", index=False)

    # ============================================================
    # Section 5.3 (revised): OLS Regression on log(price) -  fixes non-normal residuals
    # ============================================================
    print("\n=== 5.3 (revised): OLS Regression on log(price) ===")
    df_corr["log_price"] = np.log(df_corr["price"])

    X_log = df_corr[["number_of_reviews", "review_scores_rating", "occupancy_rate_pct",
                      "accommodates", "bedrooms", "bathrooms", "beds"]]
    y_log = df_corr["log_price"]
    X_log = sm.add_constant(X_log)

    model_log = sm.OLS(y_log, X_log).fit()
    print(model_log.summary())

    with open(out_dir / "regression_summary_log_price.txt", "w") as f:
        f.write(str(model_log.summary()))

    print(f"\nOriginal model R-squared (raw price): {model.rsquared:.4f}")
    print(f"Revised model R-squared (log price): {model_log.rsquared:.4f}")

    con.close()
    print("\nSection 5.2/5.3 complete. Results saved to report/findings/section5_statistics/")


if __name__ == "__main__":
    main()