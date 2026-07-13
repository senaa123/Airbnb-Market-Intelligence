# Decision Log

Every significant technical or analytical decision made during this
project, with the reasoning behind it and the trade-offs accepted. Grouped
by area; roughly chronological within each group.

---

## Scope & Prioritization

- **Single city (Bangkok), not multi-city.** Chosen to allow full analytical
  depth on one market rather than partial coverage across several, per the
  assignment's own "quality over quantity" guidance.
- **Sections 6.2 (demand forecasting) and full 6.4 (cross-city bias
  testing) deferred.** Lower rubric weight relative to time cost; the
  residual-bias-by-segment portion of 6.4 was still completed within
  Section 6.1's price prediction work.
- **Cloud-native / Open Innovation sections descoped in favor of an
  interactive dashboard.** Judged higher business value given time
  constraints than the expert-tier, optional cloud deployment tasks.

## Data Cleaning

- **`price` field's "$" prefix confirmed to represent THB, not USD.**
  Verified by comparing typical price magnitudes (median ~1,578) against
  realistic Bangkok market rates — the "$" is a generic template character
  in Inside Airbnb's export, not a currency indicator.
- **`price_missing` flagged, not dropped.** ~6.7% of listings have no
  price; these are retained and flagged so they remain usable for
  non-price analyses (host behavior, reviews, geography), and excluded
  only at the point of price-specific analysis.
- **`host_since` and `host_total_listings_count` dropped entirely.**
  Confirmed 100% null in this scrape via profiling — no data to recover.
  `calculated_host_listings_count` (0% null) used instead for host
  portfolio size.
- **`review_scores_rating` imputed with median, not dropped or zero-filled,
  for modeling purposes.** Preserves ~33% of listings (new, unreviewed) for
  price prediction — arguably the most realistic use case for a pricing
  tool. A `has_reviews` flag is retained so models can still distinguish
  imputed from genuine values. EDA/statistics sections do NOT impute this
  field — they exclude unreviewed listings entirely, since imputing would
  distort rating distributions.

## Data Quality — The Price Artifact Investigation

- **290 listings flagged and excluded (`price_likely_artifact`) after
  verification against raw source data**, not a blind percentile cut.
  Evidence: Chinese-language internal placeholder listing names
  ("room swap standby," "not for sale") and five unrelated listings
  sharing an identical $300,000 price to the cent.
- **Fix applied at the cleaning stage, not just in the modeling script.**
  Ensures every downstream analysis (EDA, statistics, ML) benefits from
  the same correction, rather than patching only the model that first
  surfaced the problem.
- **Bug found and fixed: `price_likely_artifact` silently included
  missing-price rows.** `price_clean > threshold` evaluates `False` for
  NaN values in pandas (not NaN), so rows with missing price were
  incorrectly treated as "not an artifact" — inflating dashboard totals by
  ~2,082 rows. Fixed by requiring `price IS NOT NULL` alongside the
  artifact flag in every query.

## Data Modeling

- **Star schema uses listing-grain fact table, not daily-grain.** This is
  a single-scrape snapshot, not longitudinal transactional data — a date
  dimension would be largely redundant. Trade-off: no day-by-day occupancy
  analysis at the fact-table level; occupancy is pre-aggregated instead.
- **DuckDB chosen for calendar aggregation (11.3M rows)** over loading the
  full file into pandas — queries the compressed file directly without
  exhausting memory.

## Statistical Analysis

- **Non-parametric tests (Mann-Whitney U) used instead of t-tests** for
  price comparisons, since price is right-skewed and violates the
  normality assumption a t-test requires.
- **Effect sizes reported alongside every p-value.** With ~28,700
  listings, statistical significance is close to guaranteed regardless of
  practical importance — effect size is what actually answers "does this
  matter."
- **Log-price transformation applied after diagnosing severe residual
  non-normality** in an initial raw-price OLS regression (skew 47.1,
  kurtosis 2,387, pre-correction). Both raw-price and log-price models are
  retained and compared, rather than presenting only the "fixed" version —
  demonstrates the diagnostic process, not just the outcome.
- **`neighbourhood_median_price` used as a regression feature despite
  disclosed mild target leakage** (it's a group aggregate including each
  listing's own price). Accepted given time constraints; a leave-one-out
  version is noted as a future improvement rather than silently ignored.

## Machine Learning

- **`property_type` bucketed to top 10 + "Other"** (from 76 raw
  categories) before one-hot encoding. Most categories had single-digit
  sample sizes, insufficient for reliable model coefficients — a
  disclosed trade-off of granularity for model stability.
- **Median error, not mean error, used to evaluate the "Shared room"
  segment.** Mean percentage error (389.6%) was found to be driven
  entirely by a single 1-THB-priced listing; median (14.8%) revealed this
  segment was actually one of the model's best-performing, not worst.
- **K-Means k=6 selected by silhouette score**, but explicitly disclosed as
  not necessarily optimal — the score was still rising at the top of the
  tested range (k=3–6); a wider search was not performed given time
  constraints.
- **Cluster 5's low rating (2.42) verified as genuine**, not an
  imputation artifact, by confirming all 694 listings in that cluster have
  `has_reviews = True` before reporting it as a real quality-risk finding.

## AI / NLP

- **VADER (lexicon-based sentiment) replaced with a multilingual
  transformer model** after verification found VADER scored a genuinely
  positive German-language review as strongly negative — a language
  coverage failure, not a real finding.
- **The replacement model's own failures were also verified and
  disclosed** (e.g., misclassifying "Very private and secluded!" as
  strongly negative) — both tools' limitations are reported, not just the
  improved one's success.
- **LLM executive summary built as a two-stage pipeline** (per-file
  condensation, then final synthesis) after a single-pass request exceeded
  Groq's per-minute token limit.
- **Prompt iterated three times** after finding: (1) omitted regression/ML
  results entirely, (2) conflated two separate findings under one
  citation, (3) an apparent remaining error was traced — using saved
  intermediate output — to a genuine duplication bug in a hand-written
  source notes file, not an LLM hallucination.

## Dashboard

- **Dark theme with a single monochromatic slate-blue palette**, chosen
  over a multi-color/neon style after reviewing reference images and
  determining they read as consumer-product decoration rather than
  analytical rigor — a mismatch with the stated preference for clean,
  minimal design.
- **No pie charts, no gauge/dial widgets.** Both are weak choices for
  accurate data comparison (humans read bar length more accurately than
  arc angle) and read as decorative rather than analytical.
- **Map colored on log(price), not raw price.** Raw price coloring
  compressed nearly all listings into one visual shade, since most prices
  cluster in a narrow low range relative to a few high outliers — log
  scaling restores visible differentiation among typical listings.
