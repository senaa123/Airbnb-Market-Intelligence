# Executive Summary

## Key Findings

* The mean price of Bangkok Airbnb listings is 2,222.22 THB, a 25% drop from the original mean of 2,955.96 THB after removing 290 non-genuine "artifact" listings (section4_1_notes).
* Neighbourhood has a medium effect on price (eta-squared = 0.0612, p < 0.001, ANOVA across 45 neighbourhoods) — location is a real but not dominant price factor (section5_1_hypothesis_notes).
* There is a statistically significant difference in price between entire home and private room listings (p < 0.001), with a small-but-real effect size (Cohen's d = 0.235) (section5_1_hypothesis_notes).
* The correlation between distance-from-center and price is -0.153, indicating a modest negative relationship where listings farther from the geometric center tend to be somewhat cheaper (section4_2_notes).
* Regression analysis shows accommodates, bedrooms, and bathrooms are the strongest price drivers, with two model specifications explaining 36-45% of price variance (R² = 0.453 raw price, R² = 0.361 log price) (section5_3_notes).
* K-Means clustering (k=6, silhouette score 0.435) identified six distinct host/listing segments, including "Premium/Niche Listings," "High-Demand Performers," and "Underperforming/At-Risk Listings" (section6_3_notes).
* Cluster 0 ("Premium/Niche Listings") has a price of 9,372.26 THB — 4-5x every other cluster — with low occupancy (16.82%) and high rating (4.82) (section6_3_notes).
* The XGBoost price prediction model achieved a Test MAE of 702.64 THB and Test MAPE of 41.9%, outperforming a Linear Regression baseline by 21.2% (section6_1_note).
* The top 1% of hosts (79 hosts) control 6,781 listings — 21.8% of total supply — a finding unaffected by the price data correction (section4_1_notes).

## Actionable Recommendations

* Hosts should prioritize listing capacity (accommodates, bedrooms, bathrooms) over amenities count or review count when trying to increase price, since these are the strongest, most reliable price drivers found in this analysis (section5_3_notes).
* Entire home/apt and private room listings are different economic categories (median ~2,406 THB vs. ~1,902 THB) — hosts and investors should choose deliberately based on target guest segment and available capital, not treat them as interchangeable (section5_2_notes).
* The XGBoost model can support pricing guidance (Test MAPE 41.9%), but is notably less reliable for Hotel room listings due to smaller sample size — it should not be used for confident automated pricing in underrepresented segments without more data (section6_1_note).
* Investors and platform operators should think in terms of the six identified segments rather than city-wide averages — "High-Demand Performers" (63.7% occupancy) and "Premium/Niche" (high price, low volume) represent two different, equally valid strategies (section6_3_notes).
* Given rating compression (59.5% of listings rated ≥4.8), scores below 4.7 should be treated as a stronger warning sign than they appear at face value (section4_1_notes).

## Notable Limitations

* 290 listings (~1%) were excluded as verified non-genuine prices, confirmed against raw source data — disclosed and documented, not silently dropped (section6_1_note).
* The distance-from-center calculation used a simple degrees-to-km approximation around the data's centroid, not a verified city-center landmark — flagged as a future improvement (section4_2_notes).
* The silhouette score for k=3 to k=6 (0.376, 0.396, 0.417, 0.435) was still rising at the top of the tested range — k=6 is the best result within a reasonable search window, not a proven optimal cluster count (section6_3_notes).
* Sentiment analysis used a 5,000-review sample and a general-purpose multilingual model; manual verification found occasional misclassification on short or context-dependent text, so listing-level sentiment scores should not be used for automated decisions without further validation (section7_1_notes).
* This analysis covers a single city and a single data snapshot; findings may not generalize to other markets or time periods without further validation.