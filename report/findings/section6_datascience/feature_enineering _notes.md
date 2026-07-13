# Section 6 — Feature Engineering Notes

Shared feature set used for both Price Prediction (6.1) and Segmentation (6.3),
built once to avoid duplicating logic across two scripts.

## Data Source

Base features pulled from the star schema (`fact_listings`, `dim_property`,
`dim_host`, `dim_neighbourhood`), joined with `amenities`, `availability_365`,
and `calculated_host_listings_count` from the enriched master parquet, since
those columns weren't included in the star schema itself.

## Data Quality Filter (Added)

Listings flagged as likely price artifacts (`price_likely_artifact = True`,
290 listings — see `price_quality_check.py` for verification against raw
source) are excluded before feature engineering begins. This was discovered
during initial model training, when implausible error rates traced back to
a handful of non-genuine prices, then verified directly against the raw
scrape and confirmed as data artifacts (internal placeholder listings and a
duplicate-price cluster), not genuine luxury pricing.

## Engineered Features

**amenities_count** — parsed from the raw `amenities` string list into a
simple count. Proxy for listing completeness/quality.

**property_type bucketing** — reduced from 76 raw categories to the top 10 by
listing count + "Other." Most of the original 76 categories had single-digit
listing counts, insufficient to support reliable model coefficients or
splits. Deliberate, disclosed trade-off: granularity in rare property types
for a stable, generalizable feature space.

**accommodates_x_bedrooms interaction term** — captures combined "group size x
room count" effects that neither variable captures alone.

**neighbourhood_median_price** — strong location signal, with a documented
limitation: it's a group aggregate computed including the listing's own
price, introducing mild target leakage. Used as-is given time constraints,
with this caveat disclosed.

## Missing Data Handling

**review_scores_rating** — missing values (~33% of listings, all new/
unreviewed listings) are imputed with the dataset median rather than dropped,
so the model can still price brand-new listings — arguably the most useful
real-world use case for a price model. The `has_reviews` flag is retained
alongside the imputed value so models can learn "no review history yet" as
its own signal. Mirrors the median-imputation approach used for bathrooms/
bedrooms/beds during cleaning.

## Columns Rejected After Verification

Two columns suggested during planning were checked against the actual data
profile and rejected:
- **host_since** — 100% null in this scrape. Cannot derive host tenure from
  an entirely empty column.
- **host_total_listings_count** — also 100% null. `calculated_host_listings_count`
  (0% null) was used instead as the correct host-portfolio-size feature.

## Final Feature Set

**28,697 rows retained** (updated from an initial 28,987 — 290 rows excluded
as price artifacts, see Data Quality Filter above). 33 columns after
encoding, down from an initial 98 before property_type bucketing.