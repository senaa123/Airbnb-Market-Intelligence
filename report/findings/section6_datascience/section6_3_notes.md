# Section 6.3 — Host & Listing Segmentation

## Method

K-Means clustering on 6 standardized features: host portfolio size
(`calculated_host_listings_count`), price, occupancy rate, review score,
review count, and availability. Features were standardized before
clustering, since K-Means is distance-based and these features sit on very
different scales (host listing counts in the hundreds vs. ratings on a 0-5
scale) — without standardizing, the algorithm would effectively cluster on
host portfolio size alone.

Tested k=3 through k=6, selected by silhouette score:

| k | Silhouette Score |
|---|---|
| 3 | 0.376 |
| 4 | 0.396 |
| 5 | 0.417 |
| 6 | 0.435 |

**k=6 scored highest**, but the score was still rising at the top of the
tested range rather than plateauing — this is disclosed honestly rather than
implying 6 is a provably optimal cluster count. A wider search (k=7-10) might
score even higher; k=6 is reported as the best result within a reasonable,
pre-defined search range, not as a definitive answer.

## Cluster Profiles

| Cluster | n | Host Listings | Price (THB) | Occupancy % | Rating | Reviews | Availability (days) |
|---|---|---|---|---|---|---|---|
| 0 | 1,416 | 18.97 | 9,372.26 | 16.82% | 4.82 | 17.99 | 303.61 |
| 1 | 938 | 16.22 | 2,231.98 | 26.02% | 4.80 | 257.92 | 270.04 |
| 2 | 17,018 | 21.12 | 1,691.25 | 8.27% | 4.80 | 14.01 | 334.80 |
| 3 | 6,047 | 18.20 | 2,089.23 | 63.73% | 4.81 | 23.04 | 132.31 |
| 4 | 2,584 | 159.79 | 2,228.26 | 8.34% | 4.81 | 6.16 | 334.53 |
| 5 | 694 | 35.85 | 1,777.21 | 17.83% | 2.42 | 1.91 | 299.93 |

## Named Segments

**Cluster 2 — "Typical/Baseline Listings" (17,018 listings, ~59% of market).**
No standout metric in either direction. This is the market's default
listing — average price, low-to-moderate occupancy, unremarkable rating.
Serves as the natural benchmark for comparing every other segment against.

**Cluster 3 — "High-Demand Performers" (6,047 listings, ~21% of market).**
Occupancy of 63.73% is dramatically higher than every other cluster (next
highest is 26%), with correspondingly low availability (132 days — these
listings are booked far more of the year). Price and rating are unremarkable.
This is the market's genuinely successful segment by booking volume, not by
price or luxury positioning.

**Cluster 4 — "Professional Multi-Property Operators" (2,584 listings, ~9%
of market).** Host portfolio size of 159.79 — 4 to 8 times larger than every
other cluster. Despite the scale, occupancy is low (8.34%) and review count
is the lowest of all clusters (6.16). Consistent with a "list many
properties, most see modest individual traction" commercial operating model
rather than a curated, high-touch one.

**Cluster 0 — "Premium/Niche Listings" (1,416 listings, ~5% of market).**
Price of 9,372.26 THB is 4-5x every other cluster. Occupancy is low
(16.82%), rating is high (4.82). Consistent with rare, expensive, low-
turnover listings (whole villas, luxury units) that book infrequently but
perform well when they do.

**Cluster 1 — "Established, High-Track-Record Listings" (938 listings, ~3%
of market).** Review count of 257.92 is dramatically higher than every other
cluster (next highest is 23). Long-running, well-established listings with
substantial accumulated guest history, at moderate price and occupancy.

**Cluster 5 — "Underperforming / At-Risk Listings" (694 listings, ~2% of
market).** Review score of 2.42 stands out sharply — every other cluster
sits at 4.8+. Verified this is a genuine quality signal, not an artifact of
imputation: all 694 listings in this cluster have real reviews
(`has_reviews = True`), so the low score reflects actual negative guest
feedback, not a placeholder value assigned to unreviewed listings.

## Business Interpretation

These six segments describe fundamentally different operating models, not
just price tiers:
- **Platform priority:** Cluster 5 (694 listings) represents a genuine
  quality risk pool worth flagging for host support or review, since low
  ratings are confirmed genuine rather than a data artifact.
- **Competitive dynamics:** Cluster 4's scale (159.79 listings/host) shows
  professional operators compete on breadth of inventory, not per-listing
  performance — a new host entering this market isn't just competing
  against similar-sized peers, but against operators running vastly larger
  portfolios with different economics.
- **What "success" looks like varies:** Cluster 3 (high occupancy) and
  Cluster 0 (high price, low volume) represent two entirely different,
  equally valid strategies — a new host should pick one model deliberately
  rather than aiming for an undifferentiated blend of both.

## Data Note

Clustering performed on the same corrected dataset used throughout Section 6
(290 price-artifact listings excluded). Cluster count (k=6) selected by
silhouette score within a tested range of 3-6; a wider search was not
performed given time constraints and is noted as a direction for future
refinement.