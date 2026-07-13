# Section 7.1 — Sentiment Analysis on Reviews

## Method

Initially attempted with VADER (lexicon-based); switched to a multilingual
transformer model (`cardiffnlp/twitter-xlm-roberta-base-sentiment`) after
verification revealed VADER could not correctly score non-English reviews
(see decision log — a German 5-star review was scored as strongly negative
by VADER purely due to language mismatch). Scored on a random sample of
5,000 reviews (out of 693,558 total), a smaller sample than the VADER
attempt since transformer inference is slower — a disclosed trade-off of
sample size for correctness on multilingual text.

## Sentiment Distribution

4,579 positive, 331 negative, 90 neutral (of 5,000 scored). Heavily
positive-skewed, consistent with the overall rating inflation pattern
already established in Section 4.1.

## Sentiment vs. Star Rating Correlation

**r = 0.238 (p < 0.001)** — statistically significant, weak-to-moderate,
and an improvement over the earlier VADER result (r = 0.166). Consistent
with the established finding that compressed star ratings don't track
closely with more expressive signals like review text.

## Verification of Divergence Cases — Mixed Result, Disclosed Honestly

Manually checking the review text behind the largest sentiment/rating
divergences (same verification discipline used for the price data quality
investigation) found a mixed picture — some correct, some genuine model
errors:

**Correctly scored:**
- A French-language review ("ideal accommodation for a layover in Bangkok")
  scored 0.851 — genuinely positive, confirms the multilingual fix works as
  intended for at least some non-English text.
- A review describing "broken mirror, dirty shower, synthetic towels"
  scored -0.925 — genuinely negative, correctly captured.

**Misclassified — genuine model limitations, not language issues this
time:**
- A review reading "AWFUL HOST AND PROPERTY!... REFUSED TO REFUND MY MONEY"
  scored only 0.040 (near-neutral) — a clear, severe underscoring of
  strongly negative text. Cause unclear from inspection alone; possibly
  the short review length or all-caps emphasis confusing the model.
- A review reading "Very private and secluded!" scored -0.889 (strongly
  negative) despite being a neutral-to-positive descriptive phrase — likely
  the word "secluded" carrying negative connotations (isolation) in the
  model's training data, despite being used here as a positive property
  feature.

## Honest Conclusion

Switching from a lexicon tool to a multilingual transformer model
meaningfully improved language coverage (confirmed: correctly scores
French and German text that VADER could not), but did not eliminate
sentiment misclassification generally — short reviews and words with
context-dependent connotations remain a real failure mode for automated
sentiment scoring on this dataset. The correlation figure (r=0.238) should
be read as directionally informative, not a precise measurement — some
individual "divergence" cases reflect model error rather than a genuine
gap between text sentiment and star rating.

## Business Interpretation

Automated sentiment scoring adds value at an aggregate level (the overall
positive skew and weak correlation with star rating are consistent,
believable patterns), but individual listing-level sentiment scores should
not be trusted without spot-checking, as demonstrated by the two
misclassification cases found here. A production system would need a
larger validation sample and likely a fine-tuned or higher-capacity model
before using sentiment scores for automated decisions (e.g. flagging
listings for review).

## Data Note

Sample of 5,000 reviews (random, seed=42) out of 693,558 total, scored with
`cardiffnlp/twitter-xlm-roberta-base-sentiment`. Divergence verification
performed on a small sample of extreme cases; broader validation was not
performed given time constraints and is noted as a direction for future
work.