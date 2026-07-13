# Section 4.2 — Geographic & Spatial Analysis

## Data Quality Note

Re-run after correcting the price artifact issue (290 listings excluded —
see Section 6 documentation). Listings with valid coordinates dropped
slightly, from 31,069 to 30,779, reflecting the removed rows.

## Listing Density (Figure/Map 1)

**Map:** `map01_listing_density.png` (screenshot of `map01_listing_density.html`)

**Unchanged by the price correction** — density is based on listing location
only, not price.

**Observation:** Listing density is heavily concentrated in central Bangkok,
with the brightest hotspots (green/cyan) clustering around the city core and
thinning out sharply toward the outer ring (Rangsit, Samut Prakan, Nonthaburi
fringe). Density roughly follows the river and central business/tourist
corridor rather than spreading evenly across the metro area.

**Business interpretation:** Supply is already saturated in the central
core. A host or investor looking to differentiate rather than compete
head-on in the densest zones might find better risk-adjusted returns in
adjacent, lower-density areas that still have reasonable access to the
center — assuming demand (bookings/occupancy) follows a similar or gentler
drop-off than supply does. This is worth cross-checking against occupancy
data (already computed) rather than assuming low density automatically means
opportunity — it could also mean low demand.

---

## Price Gradient by Distance from Center

**Finding (corrected — conclusion changes):** Correlation between
distance-from-center and price: **-0.153** (previously -0.032 before the
price fix).

**This reverses the original conclusion.** The near-zero correlation
originally found was itself distorted by the extreme artifact prices (up to
1,320,255 THB on small, centrally-located listings), which broke the
expected relationship between location and price. With those removed, a
real, if still modest, negative relationship emerges: listings farther from
the geometric center tend to be somewhat cheaper.

**Business interpretation:** There is a genuine "closer to center costs
more" effect in this market after all — the original conclusion that
location doesn't matter for pricing was an artifact of undetected data
quality issues, not a true market characteristic. This should be read
alongside the neighbourhood median price rankings (Figure 2, Section 4.1)
for a fuller picture, since neighbourhood identity likely captures this
effect more precisely than raw geometric distance.

**Limitation to note in the report (still applies):** the distance
calculation used a simple degrees-to-km approximation (×111) around the
data's centroid, not the true city-center coordinate (e.g. the Grand Palace
or a named CBD landmark) or actual travel distance. A more rigorous version
would geocode a known central landmark and recompute — flagged here as a
future improvement rather than re-run now, given time constraints.

---

## Review Scores by Neighbourhood

**Unchanged by the price correction** — based on review scores, not price.

**Top 5 neighbourhoods by average rating (min. 30 listings, to avoid
small-sample noise):**
| Neighbourhood | Avg Rating | Listing Count |
|---|---|---|
| Thung khru | 4.88 | 34 |
| Bangkok Yai | 4.83 | 149 |
| Thon buri | 4.83 | 540 |
| Chatu Chak | 4.80 | 882 |
| Taling Chan | 4.78 | 56 |

**Bottom 5 neighbourhoods by average rating (min. 30 listings):**
| Neighbourhood | Avg Rating | Listing Count |
|---|---|---|
| Dusit | 4.61 | 128 |
| Lat Krabang | 4.60 | 275 |
| Pra Wet | 4.60 | 221 |
| Phra Nakhon | 4.59 | 1,353 |
| Lat Phrao | 4.48 | 85 |

**Business interpretation:** Guest satisfaction is not uniform across the
city even after excluding low-sample neighbourhoods. Notably, Phra Nakhon —
a well-known, high-volume tourist district (1,353 listings) — appears in the
bottom 5, suggesting that popularity/tourist-center status does not
guarantee guest satisfaction, possibly due to noise, crowding, or
overtourism effects common in dense historic districts. This is actionable
for hosts in that area: operating in a high-demand neighbourhood does not
exempt a listing from needing to compete on quality.

The full range across all 45 neighbourhoods spans only 4.48–4.88 — under
half a point on a 5-point scale — reinforcing the earlier finding that
review scores are compressed near the ceiling. Even the "lowest-rated"
neighbourhood (Lat Phrao, 4.48) would read as a strong score in absolute
terms; the ranking here is only meaningful in relative, not absolute, terms.

---

## Property & Room Type Geographic Clustering

**Unchanged by the price correction** — based on listing counts by category
and location, not price.

**File:** `room_type_by_neighbourhood.csv` — full breakdown of room type
counts per neighbourhood.

**Observation:** While Entire home/apt and Private room listings are broadly
distributed across all neighbourhoods (roughly proportional to each
neighbourhood's total listing count), Hotel room listings cluster sharply in
a small set of central, tourist/business-district neighbourhoods — Bang Rak
(44), Parthum Wan (34), Phra Nakhon (33), Ratchathewi (31), Khlong Toei (30),
and Vadhana (26) — together accounting for the large majority of all
hotel-room inventory citywide, while most other neighbourhoods have 0-3 such
listings.

**Business interpretation:** Hotel-style commercial operators are
concentrating investment in established central tourist/business corridors
rather than distributing across the city — consistent with these being
Bangkok's traditional hospitality zones (Silom/Bang Rak, Siam/Parthum Wan,
the old city/Phra Nakhon). For a platform operator, this signals where
professional, brand-style inventory growth is already happening; for an
individual host considering a private-room or entire-home listing in these
same districts, competition includes not just other hosts but
semi-professional hotel-style operators — a different competitive dynamic
than in outer, more residential neighbourhoods where peer-to-peer hosting
still dominates entirely.

---

## Data Note

Distance-from-center correlation now reflects the corrected dataset (290
artifact listings excluded — see Section 6 documentation) and uses a
geometric centroid of all listing coordinates as a proxy for "center," not
a verified city-center landmark — see limitation above. Rating-based and
count-based findings in this section (review scores by neighbourhood, room
type clustering) are unaffected by the price fix and unchanged from the
original analysis. Neighbourhood rating comparison restricted to
neighbourhoods with ≥30 listings to avoid small-sample distortion.