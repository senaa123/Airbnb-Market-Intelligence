# Section 5.2 — Confidence Intervals & Effect Sizes

## Data Quality Note

Recomputed after excluding 290 price-artifact listings (see Section 6
documentation for verification details).

## Confidence Intervals for Mean Price by Room Type (Corrected)

| Room Type | Mean Price | 95% CI | n |
|---|---|---|---|
| Entire home/apt | 2,406.18 | [2,373.66, 2,438.70] | 19,068 |
| Hotel room | 2,616.11 | [2,314.49, 2,917.73] | 274 |
| Private room | 1,901.90 | [1,864.33, 1,939.46] | 8,857 |
| Shared room | 659.08 | [559.18, 758.97] | 498 |

**Interpretation:** Every interval is now dramatically tighter than before.
Hotel room's interval — previously flagged as too wide to trust ([1,547.50,
5,847.51], a >4,000 THB spread) — is now [2,314.49, 2,917.73], a spread of
just ~600 THB. The extreme artifact prices were the direct cause of that
earlier imprecision; with them removed, all four room-type price estimates
are now reliable enough to quote with confidence.

## Note on Effect Sizes

See `section5_1_hypothesis_notes.md` for the corrected effect sizes. Notably,
H4 (neighbourhood) moved from negligible to medium effect, and H1 (room type)
moved from negligible to small-but-real — both corrections stemming from the
same underlying data quality fix.