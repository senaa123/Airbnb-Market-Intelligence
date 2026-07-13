# Section 7.2 — LLM-Generated Executive Summary

## Method

Findings notes across all sections were condensed via a two-stage LLM
process (Groq, llama-3.3-70b-versatile): each section's notes summarized
individually first, then combined into one final executive summary. This
two-stage approach was necessary to stay within Groq's free-tier rate
limit — a single-pass summary of all findings exceeded the per-minute
token limit.

## Critical Assessment of LLM Output

**First attempt:** produced a reasonable draft, but omitted the project's
most technically substantial findings (regression analysis, price
prediction modeling, and segmentation results) — the two-stage compression
favored simpler descriptive statistics over more complex modeling content.

**Second attempt:** prompts were revised to require source-file labeling
on every claim and explicit rules preventing metric conflation (e.g.
requiring p-values and effect sizes to always be reported together).
This successfully surfaced all major findings, including regression,
price prediction, and segmentation results with correct source attribution
for nearly every claim.

**One remaining issue found through manual verification:** one
recommendation conflated a real Section 5.3 regression finding (review
score positively affects price) with a fabricated citation to a Section
5.1 hypothesis test that does not test this relationship. This was
corrected manually — Section 5.1 tests Superhost status against review
score, not review score against price.

## Conclusion

The final executive summary combines the LLM's second-attempt draft with
manual corrections identified through this verification process. This
demonstrates the critical assessment of AI outputs required by the
assignment's AI Usage Disclosure section (10.1): the LLM was useful for
first-draft synthesis and correct on the large majority of claims, but
required human verification to catch and correct one conflated citation
before use in the final report.