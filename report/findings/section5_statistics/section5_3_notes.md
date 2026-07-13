# Section 5.3 — Correlation & Driver Analysis

## Data Quality Note

Recomputed after excluding 290 price-artifact listings. The corrections below
are substantial — this is the section most affected by the data quality fix.

## Correlation Matrix (Corrected — Major Change)

| Variable | Correlation with Price (corrected) | Previous (uncorrected) |
|---|---|---|
| accommodates | 0.646 | 0.086 |
| bedrooms | 0.511 | 0.071 |
| bathrooms | 0.473 | 0.070 |
| beds | 0.436 | 0.064 |
| occupancy_rate_pct | 0.055 | -0.012 |
| review_scores_rating | 0.043 | -0.018 |
| number_of_reviews | 0.027 | -0.001 |

**This is a dramatic correction.** The original analysis concluded no
variable had a meaningful relationship with price. In reality, size-related
variables (accommodates, bedrooms, bathrooms, beds) have **strong**
correlations with price — the extreme artifact prices (up to 1,320,255 THB
on 1-3 bedroom listings) were actively breaking the correlation calculation
by pairing tiny size values with enormous prices, which is the opposite of
the genuine size-price relationship in the rest of the market.

## OLS Regression — Two Models (Corrected)

**Model 1 (raw price), corrected:** R² = 0.453 (previously 0.009) — now
explaining 45% of price variance. Skew dropped from 47.1 to 2.4, kurtosis
from 2,387 to 22.3 — still not perfectly normal, but a massive improvement.

**Model 2 (log price), corrected:** R² = 0.361 (previously 0.354 — this one
barely moved, since log-transformation was already handling much of the skew
even with the artifacts present). Skew is now -0.37 (was 0.598), kurtosis 5.4
(was 12.2) — closer to normal than Model 1.

**New nuance worth noting:** after correction, Model 1 (raw price) now has a
*higher* R² than Model 2 (log price) — 0.453 vs. 0.361, a reversal from the
pre-fix result. However, Model 2 still has better-behaved residuals (lower
skew and kurtosis). **Recommendation: report both, and use Model 2 for
statistical inference (its residuals better satisfy OLS assumptions) while
noting Model 1's higher explanatory power as a secondary observation** —
this is a genuine, disclosed trade-off between explanatory power and
statistical validity, not a case where one model is simply "better."

### Model 1 (raw price) Coefficients — all now significant

| Predictor | Coefficient | Interpretation |
|---|---|---|
| accommodates | +509.57 | Each additional guest capacity: +510 THB |
| bedrooms | +327.48 | Each additional bedroom: +327 THB |
| bathrooms | +259.92 | Each additional bathroom: +260 THB |
| review_scores_rating | +109.91 | Higher rating: modest price premium |
| occupancy_rate_pct | +3.09 | Small positive effect |
| beds | -152.69 | Negative, controlling for other size variables |
| number_of_reviews | -0.78 | Now significant but tiny — not practically meaningful |

### Model 2 (log price) Coefficients

| Predictor | Coefficient (% effect) | p-value |
|---|---|---|
| accommodates | +0.184 (~18-20%) | <0.001 |
| bedrooms | +0.099 (~9.9%) | <0.001 |
| review_scores_rating | +0.053 (~5.3%) | <0.001 |
| occupancy_rate_pct | +0.0024 | <0.001 |
| bathrooms | +0.014 (~1.4%) | 0.009 |
| beds | -0.065 (~-6.5%) | <0.001 |
| number_of_reviews | +0.0000518 | 0.364 (not significant) |

Both models now agree in direction on every major predictor — this
consistency across two model specifications is a good sign of a genuine,
stable relationship rather than a modeling artifact.

## Multicollinearity Check (VIF) — Unchanged, Still Clean

All VIFs remain under 2.5 for real predictors. No multicollinearity concern,
same conclusion as before the fix.

## Business Takeaways (Revised)

- **Size-related features are strong, reliable price drivers** — no longer a
  weak/uncertain finding, now a well-supported one (correlations 0.4-0.65).
- **Review score has a modest but consistent positive effect** across both
  models.
- **Review count still does not meaningfully affect price.**
- The corrected models now explain 36-45% of price variance — a substantial
  improvement from the original <1%, though still leaving room for
  unmeasured factors (amenities detail, exact location, listing quality)
  as a direction for future work.

## Data Note

This section's dramatic revision is itself a useful methodology story: the
original "no strong price drivers" conclusion was entirely an artifact of
undetected data quality issues, not a true market characteristic. This
demonstrates why verifying data quality — including checking against raw
source, as done in Section 6 — must happen before finalizing statistical
conclusions.