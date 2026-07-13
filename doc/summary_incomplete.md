# Summary: Incomplete Work

## Section 6.2 — Demand & Availability Forecasting: Not attempted
Reason: Optional, lower rubric weight. Time was prioritized toward sections
with higher rubric weight and higher reuse value (the price model and
segmentation both feed directly into the dashboard).

## Section 6.4 — Full Cross-City Bias & Generalization Testing: Partially complete
Done: Residual bias-by-segment analysis (price model underperforms on
Hotel room listings due to small sample size).
Not done: True cross-city transfer testing (train on City A, evaluate on
City B) — requires running the full pipeline on a second city, judged too
large an addition given the one-week timeframe.

## Section 3.6 — Cloud-Native / Advanced Topics: Not attempted
Reason: Expert-tier and explicitly optional. Docker, cloud deployment, and
CDC strategy were deprioritized in favor of full depth on mandatory/
recommended sections.

## Section 8 — Open Innovation Challenge: Substituted
Done instead: An interactive Streamlit dashboard, directly reusing the
star schema and trained models.
Not done: Other inspiration-list items (automated PDF reporting, RAG Q&A
interface, MLOps workflow) — the dashboard was judged the highest-value
single addition given time available.

## Automated Testing: Not attempted
Reason: Listed as optional in the assignment; no unit test suite or
data-quality-as-code framework was built.

## Multi-language Sentiment Validation: Partial
Done: Verified sentiment output on specific divergence cases (found and
disclosed 2 real misclassifications).
Not done: A systematic, larger-scale multilingual validation benchmark —
current verification is a spot-check, not a full benchmark.

---
Every item above is a disclosed, deliberate decision — see decision_log.md
and the report's Section 2 (Objectives & Scope) and Section 14 (Future
Improvements) for full reasoning.