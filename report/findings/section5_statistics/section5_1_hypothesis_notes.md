# Section 5.1 — Hypothesis Testing

## Data Quality Note

This section was re-run after discovering and correcting a price data quality
issue (290 listings with non-genuine "artifact" prices, verified against raw
source — see Section 6 documentation). All price-based hypotheses below
reflect corrected results.

---

## H1: Entire home listings vs. Private room listings — price

**Test used:** Mann-Whitney U

**Result (corrected):**
- p-value < 0.001 — statistically significant
- Cohen's d = 0.235 (previously 0.040) — still a small effect by convention,
  but nearly 6x larger than the uncorrected result
- Median price: Entire home 1,707.37 vs. Private room 1,386.00

**Interpretation:** The artifact prices were suppressing the true difference
between room types. The corrected effect size is still modest, but no longer
negligible — room type is a more meaningful price factor than the original
(distorted) analysis suggested.

---

## H2: Superhost vs. non-superhost — review scores (Unchanged)

Not price-based, unaffected by the data quality fix.

**Result:** p-value < 0.001, Cohen's d = 0.562 (medium effect), mean rating
Superhost 4.857 vs. non-superhost 4.563. Interpretation unchanged from
original analysis — this remains the strongest, most practically meaningful
finding in this section.

---

## H3: Listings with >10 reviews vs. ≤10 reviews — price

**Test used:** Mann-Whitney U

**Result (corrected):**
- p-value < 0.001 — statistically significant
- Cohen's d = 0.039 (previously -0.007) — still negligible
- Median price: >10 reviews 1,694.00 vs. ≤10 reviews 1,521.00

**Interpretation:** Conclusion unchanged — review count still does not
meaningfully drive price, even after correcting the data.

---

## H4: Neighbourhood average price differences (ANOVA)

**Test used:** One-way ANOVA, 45 neighbourhoods (≥30 listings each)

**Result (corrected — conclusion changes):**
- p-value < 0.001 — statistically significant
- Eta-squared = 0.0612 (previously 0.0027) — a **medium** effect by
  convention (small=0.01, medium=0.06, large=0.14), not negligible

**This reverses the original conclusion.** The near-zero effect size
originally found was itself an artifact of extreme price outliers distorting
the variance calculation. With corrected data, neighbourhood explains a
meaningful share of price variation — location does matter in this market,
contrary to what the uncorrected analysis suggested.

---

## H5 (adapted): Weekend vs. weekday minimum-nights policy — Unchanged

Not price-based (uses minimum_nights from calendar), unaffected by the fix.

**Result:** p-value = 0.535 — not significant, Cohen's d = 0.000.
Interpretation unchanged — minimum-night policy doesn't vary by day of week.

---

## Cross-Hypothesis Pattern (Revised)

The original pattern — "significant p-values with negligible effect sizes
across H1, H3, H4" — no longer fully holds after correcting the price data.
**H4 (neighbourhood) now shows a genuine medium effect**, and H1 (room type)
shows a small-but-real effect. Only H3 (review count) remains negligible.

**Revised takeaway for the report:** Price in this market is more meaningfully
explained by neighbourhood and room type than the initial (artifact-distorted)
analysis suggested. Review count remains unrelated to price. Host reputation
(H2, Superhost status) remains the single strongest individual factor tested.
This correction is itself a useful narrative for the report: it demonstrates
why data quality verification must happen before drawing statistical
conclusions, not after.