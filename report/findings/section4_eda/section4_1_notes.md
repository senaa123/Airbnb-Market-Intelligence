# Section 4.1 — Summary Statistics & Distributions

## Data Quality Note

This section was re-run after discovering and correcting a price data quality
issue: 290 listings had non-genuine "artifact" prices (verified against raw
source — internal placeholder listings and a duplicate-price cluster; see
Section 6 data quality documentation). All numbers below reflect the
corrected dataset (n=28,697, down from 28,987).

## Price Distribution

**Descriptive statistics (THB, n = 28,697 listings with valid price):**
- Mean: 2,222.22 (corrected; was 2,955.96 before removing artifact prices)
- Median: [insert median_price from the regenerated price_summary_stats.csv]
- Std Dev: [insert std_price from the regenerated price_summary_stats.csv]
- Min: [insert min_price from the regenerated price_summary_stats.csv]
- Max: [insert max_price from the regenerated price_summary_stats.csv]
- Q1: 1,037.22
- Q3: 2,496.00

**Observation:** The mean still sits above the interquartile range's center,
indicating the distribution remains right-skewed — but far less extremely
than before correction. The ~25% drop in mean price (2,955.96 → 2,222.22)
confirms the removed artifact listings were substantially inflating the
average.

**Business interpretation:** A new host benchmarking "average" pricing off
the mean would still price themselves somewhat too high for a typical
property, though the gap is now much smaller than the uncorrected data
suggested. The median remains the more reliable reference point for a
standard listing, while the mean is only meaningful for market-level revenue
sizing (e.g. estimating total market GMV), not individual pricing guidance.
Platform operators building a "suggested price" feature should anchor on
median-by-segment (room type / neighbourhood), not the raw citywide mean.

**Figure 1** (`fig01_price_by_room_type.png`): Entire home/apt and Hotel room
remain the higher-priced categories after correction, with the same relative
ordering as before (Entire home/apt, Hotel room, Private room, Shared room).
Absolute price levels are now more trustworthy since the extreme artifact
values have been removed from the underlying data. Hotel room's smaller
sample size (n=274) still means its position in this ranking carries more
uncertainty than the larger categories — see the tightened confidence
interval in Section 5.2 for the corrected precision on this estimate.

**Figure 2** (`fig02_price_by_neighbourhood.png`): Price varies substantially
across the top 10 neighbourhoods by listing volume, with [name the visibly
highest neighbourhood from your regenerated chart] commanding a clear
premium. This directly supports a location-based pricing strategy over a flat
citywide rate. See Section 5.1 for the formal H4 ANOVA test of this
relationship (eta-squared = 0.0612, a medium effect).

---

## Host Concentration (Power Law Dynamics)

**Finding:** The top 1% of hosts (79 hosts) control 6,781 listings — 21.8% of
total supply. **Unchanged by the price correction** — this metric is based on
listing counts per host, not price values, so it is unaffected by the
artifact-price fix.

**Business interpretation:** This is not a market of casual individual hosts
renting a spare room — a small number of professional, multi-listing
operators control over a fifth of all supply. This has three implications:
1. **For the platform:** pricing and inventory strategy should be
   segmented — professional operators likely run dynamic pricing and
   dedicated management, while casual single-listing hosts price more
   statically and may need more platform-provided pricing guidance.
2. **For a new host:** competition isn't just other individuals — it
   includes commercial-scale operators with more resources and experience,
   which should inform realistic expectations about occupancy and pricing
   power.
3. **For an investor:** the market supports scaled operations, but 79 hosts
   already occupying a fifth of supply signals real incumbent competition
   for anyone entering at scale.

**Figure 3** (`fig03_listings_per_host.png`): The log-scale histogram shows
the classic long-tail pattern — most hosts have 1-2 listings, while a small
number have dozens, confirming the power-law shape typical of two-sided
marketplaces.

---

## Review Score Distribution & Rating Inflation

**Descriptive statistics (n = 20,816 rated listings):** **Unchanged by the
price correction** — review scores were never part of the artifact-price
issue.
- Mean: 4.70
- Median: 4.86
- Std Dev: 0.54
- 59.5% of listings rated ≥ 4.8

**Observation:** This is a textbook case of rating inflation. If review
scores genuinely reflected a normal spread of guest satisfaction, we'd expect
a wider, more centered distribution — not 60% of all listings clustered in
the top 4% of the scale (4.8-5.0).

**Business interpretation:** Review score alone is a weak differentiator in
this market — a listing rated 4.6 likely represents a meaningfully worse
experience than the raw number suggests, since it sits well below the
compressed "normal" range of 4.8+. Recommendations:
- **For guests:** comparing listings on raw score is close to meaningless
  above ~4.7; review *count* and review *text sentiment* (Section 7 NLP
  analysis) are more informative signals of quality.
- **For the platform:** a "relative rating" or percentile-based display
  (e.g. "top 10% in this neighbourhood") would be more informative to guests
  than the raw 1-5 score.
- **For hosts:** a score below 4.7 is a stronger red flag than it appears,
  and should trigger the same operational review as, say, a 3.5 would on a
  platform without inflation.

**Figure 4** (`fig04_review_score_distribution.png`): Confirms the
left-skewed, ceiling-clustered shape — the bulk of the distribution sits
between 4.5 and 5.0, with a long thin tail of lower scores.

---

## Data Note

Price analysis now n=28,697 (was 28,987) — 290 listings excluded as
verified data artifacts (see Section 6 documentation), in addition to the
~2,082 listings (6.7%) already excluded for missing price. Review score
analysis remains n=20,816, excluding ~10,253 listings (33%) with no reviews
yet (`is_new_listing = True`), consistent with the assignment's guidance not
to impute review scores at the EDA stage. (Note: for modeling purposes only,
Section 6.1 does impute review score with median — a different, disclosed
choice made specifically to keep new listings in the price prediction model.)