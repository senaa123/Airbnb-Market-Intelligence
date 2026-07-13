"""
generate_executive_summary.py
Section 7.2: Two-stage LLM summarization with debug visibility into stage 1
output, and stricter instructions to prevent metric conflation and dropped
caveats observed in earlier attempts.
Usage: python src/analysis/ai/generate_executive_summary.py
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[3]))

import os
import time
from dotenv import load_dotenv
load_dotenv()

from groq import Groq

FINDINGS_DIR = Path("report/findings")
OUTPUT_PATH = Path("report/findings/section7_ai/llm_executive_summary.md")
DEBUG_PATH = Path("report/findings/section7_ai/llm_stage1_debug.md")
PROMPT_LOG_PATH = Path("report/findings/section7_ai/llm_prompts_used.md")

MODEL_NAME = "llama-3.3-70b-versatile"


def summarize_file(client, filename, content):
    prompt = f"""Extract the 5-7 most important factual findings from this data
analysis notes file, prefixed with the source filename so it's traceable later.

Rules:
- If this file mentions regression, R-squared, model performance (MAE/RMSE/MAPE),
  clustering/segments, or correlation coefficients, include them with their exact
  numbers and what they measure.
- If this file mentions a hypothesis test result, ALWAYS state both the p-value
  AND the effect size together in the same bullet (never p-value alone).
- If this file explicitly flags something as a data artifact, small-sample
  issue, or limitation, PRESERVE that caveat word-for-word in your bullet —
  do not drop it or present the number as a clean trend.
- If this file describes named clusters/segments, list each cluster name and
  its single most distinguishing number.

Plain bullet points only, each bullet self-contained (a reader should not need
another bullet to understand what a number refers to).

--- SOURCE FILE: {filename} ---
{content[:4000]}
"""
    response = client.chat.completions.create(
        model=MODEL_NAME,
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


def main():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("ERROR: Set GROQ_API_KEY in your .env file.")
        return

    client = Groq(api_key=api_key)

    EXCLUDE_FILES = {"llm_executive_summary.md", "llm_prompts_used.md", "llm_stage1_debug.md"}
    md_files = sorted(f for f in FINDINGS_DIR.rglob("*.md") if f.name not in EXCLUDE_FILES)
    print(f"Found {len(md_files)} findings files. Summarizing each individually first...")

    mini_summaries = []
    debug_lines = []
    for md_file in md_files:
        content = md_file.read_text(encoding="utf-8")
        print(f"  Summarizing {md_file.relative_to(FINDINGS_DIR)}...")
        try:
            summary = summarize_file(client, md_file.name, content)
            labeled = f"### SOURCE: {md_file.stem}\n{summary}"
            mini_summaries.append(labeled)
            debug_lines.append(labeled)
        except Exception as e:
            print(f"  Skipped {md_file.name} due to error: {e}")
        time.sleep(2)

    # Save stage 1 output so we can actually SEE what each file produced,
    # instead of guessing why something is missing from the final summary.
    DEBUG_PATH.write_text("\n\n---\n\n".join(debug_lines), encoding="utf-8")
    print(f"\nSaved stage 1 debug output to {DEBUG_PATH} — check this file if anything is still missing from the final summary.")

    combined_summaries = "\n\n".join(mini_summaries)
    print(f"Condensed all files into {len(combined_summaries)} characters. Generating final executive summary...")

    final_prompt = f"""You are helping summarize a data analysis project on Bangkok Airbnb
listings for a business audience. Below are condensed findings from each
section of the analysis, each labeled with its source file.

Write a 1-page executive summary with these sections:

1. Key Findings (7-9 bullet points). You MUST include at least one bullet
   from each of these categories, and you MUST NOT combine numbers from
   different source files into a single claim — if two files both mention
   "neighbourhood," keep their findings in SEPARATE bullets, each citing its
   own source file's specific metric:
   - Descriptive pricing/market stats
   - Hypothesis testing (always with both p-value AND effect size)
   - Regression/price-driver analysis
   - Price prediction model performance
   - Host/listing segmentation (name at least 2-3 actual cluster names)

2. Actionable Recommendations (4-5 points, each citing a specific number
   from the findings, not generic advice)

3. Notable Limitations (include any data artifact or small-sample caveats
   found in the source material — do not omit these even if they complicate
   the narrative)

All price figures are in Thai Baht (THB). Never use a dollar sign ($).

--- CONDENSED FINDINGS (labeled by source file) ---
{combined_summaries}
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        max_tokens=2200,
        messages=[{"role": "user", "content": final_prompt}]
    )
    summary_text = response.choices[0].message.content

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(summary_text, encoding="utf-8")
    print(f"\nSaved executive summary to {OUTPUT_PATH}")

    PROMPT_LOG_PATH.write_text(
        f"# LLM Prompts Used — Section 7.2\n\n"
        f"**Model:** {MODEL_NAME} (via Groq API)\n\n"
        f"**Approach:** Two-stage summarization with source-file labeling and "
        f"explicit anti-conflation, effect-size, and caveat-preservation rules, "
        f"added after two prior attempts showed metric conflation and dropped "
        f"caveats. Stage 1 output saved separately for debugging traceability.\n",
        encoding="utf-8"
    )

    print("\n=== Generated Executive Summary ===\n")
    print(summary_text)


if __name__ == "__main__":
    main()