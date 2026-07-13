"""
run_pipeline.py
Runs the full data pipeline end-to-end, in order.
Usage: python run_pipeline.py
"""

import subprocess
import sys

STEPS = [
    "src/ingestion/ingest.py",
    "src/processing/clean_listings.py",
    "src/processing/process_calendar.py",
    "src/processing/enrich_listings.py",
    "src/modeling/build_star_schema.py",
    "src/analysis/eda/eda_distributions.py",
    "src/analysis/eda/eda_geographic.py",
    "src/analysis/eda/eda_temporal.py",
    "src/analysis/statistics/hypothesis_tests.py",
    "src/analysis/statistics/regression_analysis.py",
    "src/analysis/datascience/price_quality_check.py",
    "src/analysis/datascience/feature_engineering.py",
    "src/analysis/datascience/price_prediction.py",
    "src/analysis/datascience/segmentation.py",
    "src/analysis/ai/sentiment_analysis.py",
    "src/analysis/ai/generate_executive_summary.py",
]

for step in STEPS:
    print(f"\n{'='*60}\nRunning: {step}\n{'='*60}")
    result = subprocess.run([sys.executable, step])
    if result.returncode != 0:
        print(f"Pipeline failed at {step}. Stopping.")
        sys.exit(1)

print("\nPipeline completed successfully.")