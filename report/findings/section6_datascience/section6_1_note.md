# Section 6.1 — Price Prediction

## Data Quality Fix Applied

Before modeling, 290 listings (~1% of the dataset) were excluded as likely data
artifacts — verified against the raw source (see price_quality_check.py):
Chinese-language internal placeholder listings ("room swap standby," "not for
sale") and a cluster of 5 unrelated listings sharing an identical $300,000
price to the cent. This fix was applied upstream in the cleaning stage and
propagated through the full pipeline, correcting statistics in Sections 4 and
5 as well (see updated notes in those sections).

## Model Comparison

| Model | Test MAE (THB) | Test RMSE | Test MAPE | vs. Linear |
|---|---|---|---|---|
| Linear Regression | 891.54 | 1,693.19 | 52.4% | baseline |
| Random Forest | 734.42 | 1,424.45 | 43.8% | +17.6% |
| XGBoost | 702.64 | 1,366.62 | 41.9% | +21.2% |

**XGBoost is the best model**, consistent with tree-based methods typically
outperforming linear models on tabular data with non-linear structure. All
three models improved substantially after removing the price artifacts —
RMSE for XGBoost dropped from 21,211 (pre-fix) to 1,367, confirming those
outliers were the primary driver of the earlier, unreasonably high RMSE.

## Residual Analysis by Room Type (Bias Check)

Mean percentage error is misleading for this comparison — Shared room's
initial mean of 389.6% was driven entirely by a single listing priced at 1 THB
(model predicted 345 THB; a reasonable absolute miss that becomes an extreme
percentage on a near-zero base). Median percentage error and mean absolute
error in THB are reported instead, since they aren't distorted by this kind of
outlier.

| Room Type | n | Median % Error | Mean Abs. Error (THB) |
|---|---|---|---|
| Shared room | 97 | 14.8% | 260.55 |
| Entire home/apt | 3,848 | 21.1% | 718.94 |
| Private room | 1,748 | 26.3% | 681.41 |
| Hotel room | 47 | 34.2% | 1,070.57 |

**Finding:** Hotel room is the model's weakest-performing segment, not Shared
room as the raw mean initially suggested. This lines up with sample size —
Hotel room has by far the fewest listings (47 in the test set), giving the
model the least data to learn pricing patterns for that category. This is the
bias-check finding requested by Section 6.4: the model systematically performs
worse on underrepresented segments, and should not be used for confident
pricing guidance on Hotel room listings without either more data or a
segment-specific model.

## Business Interpretation

A MAPE around 42% (best model) reflects real, expected variance in short-term
rental pricing that structural features alone can't fully capture — factors
like listing photos, exact micro-location desirability, and host-specific
dynamic pricing strategy aren't present in this dataset. This is a realistic,
usable result for pricing *guidance* (e.g. "similar listings in this category
typically price around X"), not for precise automated pricing.

## Data Note

Feature engineering excludes the 290 flagged price-artifact listings before
model training (see `feature_engineering.py`, `WHERE NOT price_likely_artifact`).
SHAP analysis (Figure 8) and full model comparison detail are saved alongside
this file.