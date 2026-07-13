"""
config.py
Shared configuration loader used across the pipeline.
"""

import yaml
from pathlib import Path


def load_config(config_path: str = "config.yaml") -> dict:
    """Loads project config.yaml. Path is relative to wherever the script is run from
    (we always run from the project root, e.g. `python src/processing/clean_listings.py`)."""
    with open(config_path, "r") as f:
        return yaml.safe_load(f)