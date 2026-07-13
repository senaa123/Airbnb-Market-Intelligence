### SOURCE: section4_1_notes
* section4_1_notes.md: Mean price is 2,222.22 THB, which is a ~25% drop from the original mean of 2,955.96 before removing 290 "artifact" prices, indicating the removed listings substantially inflated the average.
* section4_1_notes.md: The price distribution remains right-skewed, but less extremely than before correction, with Q1 at 1,037.22 and Q3 at 2,496.00.
* section4_1_notes.md: The top 1% of hosts (79 hosts) control 6,781 listings, which is 21.8% of total supply, a finding that is unchanged by the price correction and indicates a small number of professional operators control over a fifth of all supply.
* section4_1_notes.md: ANOVA test of the relationship between price and neighbourhood (H4) shows a medium effect size (eta-squared = 0.0612), directly supporting a location-based pricing strategy over a flat citywide rate.
* section4_1_notes.md: The data quality issue due to "artifact" prices, which was a limitation, has been addressed by removing 290 listings with non-genuine prices, resulting in a corrected dataset of 28,697 listings, down from 28,987.
* section4_1_notes.md: A data artifact, which was a duplicate-price cluster and internal placeholder listings, was discovered and corrected, affecting the original mean price and confirming the importance of data quality checks.

---

### SOURCE: section4_2_notes
* section4_2_notes.md: Correlation between distance-from-center and price: -0.153, indicating a modest negative relationship where listings farther from the geometric center tend to be somewhat cheaper.
* section4_2_notes.md: The near-zero correlation originally found (0.032) was distorted by extreme artifact prices, which broke the expected relationship between location and price, and is now considered a data artifact.
* section4_2_notes.md: Limitation to note in the report: the distance calculation used a simple degrees-to-km approximation (×111) around the data's centroid, not the true city-center coordinate or actual travel distance, flagged as a future improvement.
* section4_2_notes.md: Top 5 neighbourhoods by average rating: Thung khru (4.88), Bangkok Yai (4.83), Thon buri (4.83), Chatu Chak (4.80), and Taling Chan (4.78), with Thung khru having the highest average rating of 4.88.
* section4_2_notes.md: Bottom 5 neighbourhoods by average rating: Dusit (4.61), Lat Krabang (4.60), Pra Wet (4.60), Phra Nakhon (4.59), and Lat Phrao (4.48), with Phra Nakhon having a notable low average rating of 4.59 despite being a well-known, high-volume tourist district.
* section4_2_notes.md: The number of listings with valid coordinates dropped slightly from 31,069 to 30,779 after correcting the price artifact issue, reflecting the removal of 290 listings.
* section4_2_notes.md: A small-sample issue was avoided by only considering neighbourhoods with at least 30 listings when calculating average review scores, to prevent small-sample noise.

---

### SOURCE: section4_3_notes
* section4_3_notes.md: Booked-day percentage ranges from 12% (September 2026) to 35-41% (April-July 2027), with an outlier-high 54.6% in June 2026, but this reflects a mix of recency artifact and genuine seasonality.
* section4_3_notes.md: The average minimum nights stay is stable year-round at roughly 13-14 nights, with an apparent jump to 20.76 in July 2027, but this jump is a small-sample edge effect and not a real policy shift.
* section4_3_notes.md: Reviews grew steadily from 2011 (5) to 2019 (56,179), then collapsed in 2020 (17,119) and 2021 (4,924) due to COVID-19, and recovered strongly from 2022 (38,738) onward, peaking in 2025 (163,144), but 2026's figure (99,308) is a partial year and should not be compared directly to full-year 2025.
* section4_3_notes.md: The minimum nights policy is stable at 13.4-13.9 nights for nearly the entire window, which is notably high for a short-term rental platform, suggesting a strong presence of longer-stay listings or hosts using long minimum stays as an implicit anti-short-booking filter.
* section4_3_notes.md: The review volume trend shows a clear COVID-19 travel-shutdown signature in 2020-2021, but the market fully recovered and grew beyond pre-pandemic levels by 2023-2025, with a peak in 2025 (163,144), indicating a strong growth story for the Bangkok short-term rental demand.
* section4_3_notes.md: The booking rate analysis is limited by the fact that it uses a single-scrape future availability snapshot, not historical bookings, which means it may not reflect actual demand trends, and should not be conflated with the review volume analysis, which uses genuine historical dates.
* section4_3_notes.md: The data has a limitation due to the single-snapshot dataset, which does not provide a true historical seasonality analysis, and would require multiple scrapes over time (longitudinal data) to confirm the findings.

---

### SOURCE: section5_1_hypothesis_notes
* section5_1_hypothesis_notes.md: The Mann-Whitney U test for H1 ( Entire home listings vs. Private room listings — price ) yielded a p-value < 0.001 and a Cohen's d = 0.235, indicating a statistically significant but small effect.
* section5_1_hypothesis_notes.md: The test for H2 ( Superhost vs. non-superhost — review scores ) resulted in a p-value < 0.001 and a Cohen's d = 0.562, showing a medium effect, with mean rating Superhost 4.857 vs. non-superhost 4.563.
* section5_1_hypothesis_notes.md: The Mann-Whitney U test for H3 ( Listings with >10 reviews vs. ≤10 reviews — price ) gave a p-value < 0.001 and a Cohen's d = 0.039, indicating a statistically significant but negligible effect.
* section5_1_hypothesis_notes.md: The one-way ANOVA test for H4 ( Neighbourhood average price differences ) yielded a p-value < 0.001 and an Eta-squared = 0.0612, indicating a statistically significant medium effect, reversing the original conclusion that neighbourhood did not matter in price variation.
* section5_1_hypothesis_notes.md: The test for H5 ( Weekend vs. weekday minimum-nights policy ) resulted in a p-value = 0.535 and a Cohen's d = 0.000, showing no significant effect, with minimum-night policy not varying by day of week.

---

### SOURCE: section5_2_notes
* section5_2_notes.md: The 95% confidence interval for the mean price of Entire home/apt is [2,373.66, 2,438.70] with a mean price of 2,406.18, based on 19,068 samples.
* section5_2_notes.md: The 95% confidence interval for the mean price of Hotel room is [2,314.49, 2,917.73] with a mean price of 2,616.11, based on 274 samples, which is a notable improvement over the previously reported wide interval [1,547.50, 5,847.51] due to the removal of price-artifact listings.
* section5_2_notes.md: The 95% confidence interval for the mean price of Private room is [1,864.33, 1,939.46] with a mean price of 1,901.90, based on 8,857 samples.
* section5_2_notes.md: The 95% confidence interval for the mean price of Shared room is [559.18, 758.97] with a mean price of 659.08, based on 498 samples.
* section5_2_notes.md: After removing 290 price-artifact listings, the data quality has improved, allowing for more reliable price estimates for all four room types.
* section5_2_notes.md: The hypothesis H1 (room type) has a small-but-real effect size (exact value not specified in this file, see section5_1_hypothesis_notes.md for details).
* section5_2_notes.md: The hypothesis H4 (neighbourhood) has a medium effect size (exact value not specified in this file, see section5_1_hypothesis_notes.md for details), which was previously reported as negligible due to a data quality issue.

---

### SOURCE: section5_3_notes
* section5_3_notes.md: The correlation between the variable "accommodates" and price is 0.646, indicating a strong positive relationship.
* section5_3_notes.md: The OLS regression Model 1 (raw price) has an R² of 0.453, explaining 45% of price variance, with a skew of 2.4 and kurtosis of 22.3.
* section5_3_notes.md: The OLS regression Model 2 (log price) has an R² of 0.361, explaining 36% of price variance, with a skew of -0.37 and kurtosis of 5.4.
* section5_3_notes.md: In Model 1, the coefficient for "accommodates" is +509.57, indicating that each additional guest capacity increases price by approximately 510 THB.
* section5_3_notes.md: In Model 2, the coefficient for "accommodates" is +0.184, with a p-value of <0.001, indicating a significant positive effect of approximately 18-20% on log price.
* section5_3_notes.md: The multicollinearity check (VIF) shows all VIFs remain under 2.5 for real predictors, indicating no multicollinearity concern.
* section5_3_notes.md: The data quality fix removed 290 price-artifact listings, which were actively breaking the correlation calculation by pairing tiny size values with enormous prices, a data artifact that has been corrected.