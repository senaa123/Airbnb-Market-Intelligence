# Section 4.3 — Temporal & Seasonal Trends

## Booking Rate by Month (Figure 5)

**Finding:** Booked-day percentage ranges from ~12% (September 2026) up to ~35-41%
(April-July 2027), with the near-term month (June 2026) showing an outlier-high 54.6%.

**Important caveat:** This calendar reflects future availability as of the scrape date
(2026-06-29 to 2027-06-28), not historical demand. Two effects are mixed together here:
1. **Recency artifact:** dates closer to the scrape date naturally show more confirmed
   bookings simply because guests book closer to their travel date — not necessarily
   because near-term demand is higher.
2. **Genuine seasonality:** the climb back toward 35-41% as the calendar approaches the
   one-year mark (April-July 2027) likely reflects real seasonal demand for that period,
   since it's far enough out that the recency effect shouldn't dominate as strongly.

**Business interpretation:** Rather than reading this as "low season Sept-March, high
season Apr-Jul," the safer conclusion is that hosts should expect booking rates for any
given future month to keep rising as that month approaches — meaning last-minute pricing
strategy (e.g. discounting unbooked near-term inventory) is likely more relevant here than
rigid seasonal pricing tiers. A true historical seasonality analysis would require multiple
scrapes over time (longitudinal data), which this single-snapshot dataset does not provide —
flagged as a limitation.

## Minimum Nights Policy (Table: monthly_min_nights.csv)

**Finding:** Average minimum nights stays flat around 13.4-13.9 nights for nearly the entire
window, with an apparent jump to 20.76 in July 2027.

**Caveat:** The July 2027 jump is a small-sample edge effect — that month has only 13,283
total listing-days recorded (vs. ~900,000+ for full months), since it's the last sliver of
the calendar's 365-day window. Not a real policy shift.

**Business interpretation:** Minimum-night requirements in this market are stable
year-round at roughly 13-14 nights on average — notably high for a short-term rental
platform, suggesting either a strong presence of longer-stay/relocation-style listings, or
hosts using long minimum stays as an implicit anti-short-booking filter. Worth a follow-up
question in the report: is this being pulled up by a subset of listings with very long
minimums (median vs mean check)? Recommendation: a platform operator could investigate
whether shorter minimum-stay inventory is underserved relative to demand.

## Review Volume Trend (Figure 6)

**Finding:** Reviews grew steadily from 2011 (5) through 2019 (56,179), collapsed in 2020
(17,119) and bottomed in 2021 (4,924), then recovered strongly from 2022 (38,738) onward,
peaking in 2025 (163,144).

**Caveat:** 2026's figure (99,308) is **not a decline** — it's a partial year, since the
scrape was taken mid-2026. Do not compare it directly to full-year 2025.

**Business interpretation:** The 2020-2021 collapse is a clear COVID-19 travel-shutdown
signature, and the market fully recovered and grew beyond pre-pandemic levels by 2023-2025 —
this is a strong growth story for a business audience: Bangkok's short-term rental demand
is not just recovered but expanding. For an investor, this recovery trajectory is a more
reassuring demand signal than the raw 2026 number would suggest at first glance.

## Data Note

Booking-rate and minimum-nights analysis use the calendar file (single-scrape future
availability snapshot, not historical bookings). Review volume uses reviews.csv.gz, which
does contain genuine historical dates and is the more reliable source for actual demand
trend analysis. These two sources should not be conflated in the report.