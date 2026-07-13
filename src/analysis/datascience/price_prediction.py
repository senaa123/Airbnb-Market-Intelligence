"""
price_prediction.py
Section 6.1: Trains and compares 3 model families for price prediction,
with cross-validation, residual analysis, and SHAP explainability.

"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[3]))

import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, mean_absolute_percentage_error
import xgboost as xgb
import shap
import matplotlib.pyplot as plt
from src.utils.config import load_config


def main():
    config = load_config()
    city = config["city"]["name"]
    processed_dir = Path(config["paths"]["processed_dir"])
    out_dir = Path("report/findings/section6_datascience")
    fig_dir = Path("report/figures")
    out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_parquet(processed_dir / f"ml_features_{city}.parquet")

    # Drop non-feature columns (identifiers, raw text, and target)
    drop_cols = ["listing_id", "host_id", "neighbourhood", "amenities", "price_missing", "price"]
    X = df.drop(columns=drop_cols)
    y = np.log1p(df["price"])  # log1p handles any zero-price edge cases safely

    # Ensure boolean columns are proper 0/1 ints for all model libraries
    bool_cols = X.select_dtypes(include="bool").columns
    X[bool_cols] = X[bool_cols].astype(int)

    print(f"Feature matrix shape: {X.shape}")
    print(f"Target: price | mean={y.mean():.2f}, median={y.median():.2f}")

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    models = {
        "LinearRegression": LinearRegression(),
        "RandomForest": RandomForestRegressor(n_estimators=200, max_depth=12, random_state=42, n_jobs=-1),
        "XGBoost": xgb.XGBRegressor(n_estimators=200, max_depth=6, learning_rate=0.1, random_state=42)
    }

    results = []
    predictions = {}

    for name, model in models.items():
        print(f"\n=== Training {name} ===")
        model.fit(X_train, y_train)
        y_pred_log = model.predict(X_test)

        # Convert back to real price (THB) scale for interpretable metrics
        y_test_actual = np.expm1(y_test)
        y_pred_actual = np.expm1(y_pred_log)
        predictions[name] = y_pred_actual

        mae = mean_absolute_error(y_test_actual, y_pred_actual)
        rmse = np.sqrt(mean_squared_error(y_test_actual, y_pred_actual))
        mape = mean_absolute_percentage_error(y_test_actual, y_pred_actual) * 100

        # 5-fold CV on training data (stays in log space, standard practice)
        cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring="neg_mean_absolute_error")
        cv_mae = -cv_scores.mean()  # this MAE is in log-price units, note that in output

        print(f"Test MAE: {mae:.2f} | RMSE: {rmse:.2f} | MAPE: {mape:.1f}% | CV MAE (5-fold): {cv_mae:.2f}")

        results.append({
            "model": name, "test_mae": round(mae, 2), "test_rmse": round(rmse, 2),
            "test_mape_pct": round(mape, 1), "cv_mae": round(cv_mae, 2)
        })

        joblib.dump(model, processed_dir / f"model_{name}_{city}.joblib")

    results_df = pd.DataFrame(results)
    baseline_mae = results_df.loc[results_df["model"] == "LinearRegression", "test_mae"].values[0]
    results_df["pct_improvement_vs_linear"] = round(
        (baseline_mae - results_df["test_mae"]) / baseline_mae * 100, 1
    )
    print("\n=== Model Comparison ===")
    print(results_df)
    results_df.to_csv(out_dir / "model_comparison.csv", index=False)

    # ---- Residual analysis on best model (lowest test MAE) ----
    best_model_name = results_df.loc[results_df["test_mae"].idxmin(), "model"]
    print(f"\nBest model by test MAE: {best_model_name}")

    y_test_actual = np.expm1(y_test)
    best_pred = predictions[best_model_name]  # already converted to real scale above
    residuals = y_test_actual.values - best_pred

    residual_df = X_test.copy()
    residual_df["actual_price"] = y_test_actual.values
    residual_df["predicted_price"] = best_pred
    residual_df["residual"] = residuals
    residual_df["abs_pct_error"] = np.abs(residuals) / y_test_actual.values * 100

    print("\n=== Residuals by room type (mean AND median absolute % error) ===")
    for col in ["room_Hotel room", "room_Private room", "room_Shared room"]:
        if col in residual_df.columns:
            subset = residual_df[residual_df[col] == 1]
            if len(subset) > 0:
                print(f"{col}: n={len(subset)}, mean_abs_pct_error={subset['abs_pct_error'].mean():.1f}%, "
                      f"median_abs_pct_error={subset['abs_pct_error'].median():.1f}%, "
                      f"mean_abs_error_thb={subset['residual'].abs().mean():.2f}")
    entire_home_mask = (residual_df[["room_Hotel room", "room_Private room", "room_Shared room"]].sum(axis=1) == 0)
    subset = residual_df.loc[entire_home_mask]
    print(f"room_Entire home/apt (reference): n={len(subset)}, "
          f"mean_abs_pct_error={subset['abs_pct_error'].mean():.1f}%, "
          f"median_abs_pct_error={subset['abs_pct_error'].median():.1f}%, "
          f"mean_abs_error_thb={subset['residual'].abs().mean():.2f}")
    
    # Investigate Shared room anomaly: check for near-zero actual prices
    # that could be inflating percentage error disproportionately
    shared_room_mask = residual_df["room_Shared room"] == 1
    shared_subset = residual_df[shared_room_mask][["actual_price", "predicted_price", "residual", "abs_pct_error"]]
    print("\n=== Shared room diagnostic: sorted by abs_pct_error (highest first) ===")
    print(shared_subset.sort_values("abs_pct_error", ascending=False).head(10).to_string(index=False))
    print(f"\nShared room actual_price stats:\n{shared_subset['actual_price'].describe()}")


    residual_df.to_csv(out_dir / "residuals_detail.csv", index=False)

    plt.figure(figsize=(8, 6))
    plt.scatter(y_test_actual, best_pred, alpha=0.3, s=10)
    plt.plot([y_test_actual.min(), y_test_actual.max()], [y_test_actual.min(), y_test_actual.max()], "r--")
    plt.xlabel("Actual Price")
    plt.ylabel("Predicted Price")
    plt.title(f"Figure 7: Actual vs Predicted Price ({best_model_name})")
    plt.tight_layout()
    plt.savefig(fig_dir / "fig07_actual_vs_predicted_price.png")
    plt.close()
    print("Saved fig07_actual_vs_predicted_price.png")

    # ---- SHAP explainability on best model ----
    if best_model_name in ["RandomForest", "XGBoost"]:
        print("\n=== Computing SHAP values (best model) ===")
        best_model = models[best_model_name]
        explainer = shap.TreeExplainer(best_model)
        shap_values = explainer.shap_values(X_test)

        plt.figure()
        shap.summary_plot(shap_values, X_test, show=False, max_display=15)
        plt.tight_layout()
        plt.savefig(fig_dir / "fig08_shap_summary.png", bbox_inches="tight")
        plt.close()
        print("Saved fig08_shap_summary.png")
    else:
        print("Best model is LinearRegression — SHAP summary skipped (coefficients already interpretable directly).")

    # ---- Quick check on extreme price outliers (flagged from Figure 7 review) ----
    print("\n=== Top 5 highest-priced listings (outlier check) ===")
    outlier_check = df.nlargest(5, "price")[["listing_id", "price", "accommodates", "bedrooms", "room_Hotel room"]]
    print(outlier_check)
    outlier_check.to_csv(out_dir / "price_outlier_check.csv", index=False)

    print("\nSection 6.1 (Price Prediction) complete.")


if __name__ == "__main__":
    main()