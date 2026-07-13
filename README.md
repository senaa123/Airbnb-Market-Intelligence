# Bangkok Airbnb Market Intelligence

An end-to-end data engineering, statistical analysis, and machine learning
project on Bangkok Airbnb listings, built for the Expernetic Data Engineer
Intern Talent Assessment.

**Start here, in this order:**
1. This README (setup + how to run everything)
2. `Bangkok_Airbnb_Technical_Assessment_Report.pdf` — the full report
3. `dashboard/` — interactive Streamlit dashboard
4. `decision_log.md` — every major technical decision, with reasoning

---

## What This Project Does

Analyzes 28,697 Bangkok Airbnb listings (from 31,069 raw, after a verified
data quality correction — see `decision_log.md`) across:
- A config-driven, reproducible ingestion → cleaning → star schema pipeline
- Exploratory data analysis (pricing, geography, seasonality)
- Statistical hypothesis testing (5 hypotheses, effect sizes throughout)
- Machine learning (XGBoost price prediction, K-Means segmentation)
- Applied AI/NLP (multilingual sentiment analysis, LLM-generated summaries)
- An interactive Streamlit dashboard

## Repository Structure

```
├── config.yaml                  # City selection, data URLs, pipeline settings
├── requirements.txt
├── run_pipeline.py               # Runs the entire pipeline end-to-end
├── src/
│   ├── utils/config.py           # Shared config loader
│   ├── ingestion/                # Download pipeline (retry + logging)
│   ├── processing/               # Cleaning, calendar aggregation, enrichment
│   ├── modeling/                 # Star schema construction (DuckDB)
│   └── analysis/
│       ├── eda/                  # Sections 4.1–4.5 exploratory analysis
│       ├── statistics/           # Section 5 hypothesis testing & regression
│       ├── datascience/          # Section 6 ML (price prediction, segmentation)
│       └── ai/                   # Section 7 sentiment analysis & LLM summary
├── dashboard/
│   └── app.py                    # Streamlit dashboard (5 tabs)
├── data/
│   ├── raw/                      # Downloaded source files (git-ignored)
│   └── processed/                # Cleaned data, star schema, trained models (git-ignored)
├── report/
│   └── findings/                 # All analysis notes, organized by section
├── logs/                         # Pipeline run logs (git-ignored)
└── decision_log.md               # Consolidated engineering/analytical decisions
```

## Setup

**1. Clone and enter the project folder, then create a virtual environment:**
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

**2. Install dependencies:**
```bash
pip install -r requirements.txt
```

**3. Configure your target city and data URLs in `config.yaml`:**
Get download URLs from https://insideairbnb.com/get-the-data/ for your
chosen city, and paste them into `config.yaml` (default city: Bangkok).

**4. Set up API keys (only needed for the AI/NLP section):**
Create a `.env` file in the project root:
```
GROQ_API_KEY=your-key-here
```
Get a free key at https://console.groq.com/keys

## Running the Pipeline

**Run everything end-to-end, in order:**
```bash
python run_pipeline.py
```
This ingests, cleans, builds the star schema, and runs every EDA,
statistics, ML, and AI script in sequence. It halts on first failure rather
than silently continuing with partial data. Expect 10–20 minutes total,
depending on connection speed (the sentiment analysis model download is the
largest single component, ~1.1GB, one-time only).

**Run an individual stage** (useful if you only want to re-run one part):
```bash
python src/processing/clean_listings.py
python src/analysis/datascience/price_prediction.py
# etc. — see run_pipeline.py for the full ordered list
```

## Running the Dashboard

```bash
streamlit run dashboard/app.py
```
Opens automatically in your browser (default: `localhost:8501`). Requires
the pipeline to have been run at least once first, since the dashboard
reads from `data/processed/`.

## Key Outputs

- `data/processed/bangkok_warehouse.duckdb` — the star schema, queryable directly with any DuckDB client
- `data/processed/model_XGBoost_bangkok.joblib` — the trained price prediction model
- `report/findings/` — every analysis section's notes, tables, and figures
- `report/figures/` — all generated charts (numbered, referenced in the report)

## Reproducibility Notes

- All intermediate outputs are cached to disk — `data/raw/` and
  `data/processed/` are git-ignored since they're fully regeneratable by
  running `run_pipeline.py` from scratch.
- Every pipeline run produces a timestamped log file in `logs/`.
- The pipeline is not currently idempotent in the incremental sense — it
  reprocesses all data on every run rather than skipping unchanged inputs.
  Acceptable for this assignment's scope; see the report's "Future
  Improvements" section for the production-readiness path.

## AI Usage Disclosure

Full disclosure is in the report's Appendix A. In brief: this project was
built with AI-assisted development (Claude, used throughout for code
generation and debugging guidance) plus two specific AI tools used for
Section 7 (Groq/Llama for summarization, a Hugging Face multilingual model
for sentiment analysis). All AI output was run, verified, and in several
documented cases corrected or rejected — see Appendix A for specifics.

## Developer

**Senan Jayasinghe**  
[senandulneth1@gmail.com](mailto:senandulneth1@gmail.com)  

This project was developed as part of the **Expernetic (Pvt) Ltd** Data Engineer Intern Talent Assessment Program.