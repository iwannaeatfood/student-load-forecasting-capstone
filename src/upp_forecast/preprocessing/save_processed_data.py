"""Validate and persist processed preprocessing outputs to a consistent location."""

# Implemented for H11CBREAD-32 by Yanyan Zhu (z5565492@ad.unsw.edu.au)

from pathlib import Path

import pandas as pd

from upp_forecast.preprocessing.build_cohorts import COHORT_COLUMNS, STATE_COLUMNS
from upp_forecast.preprocessing.clean_terms import TERM_SCHEMA
from upp_forecast.preprocessing.transform_load import STUDENT_LOAD_MEASURE_COL


REQUIRED_MODELLING_COLUMNS = [
    *COHORT_COLUMNS,
    *STATE_COLUMNS,
    "state",
    STUDENT_LOAD_MEASURE_COL,
    TERM_SCHEMA.period_time_col,
]

DEFAULT_PROCESSED_DIR = Path("data/processed")


def validate_modelling_columns(records: pd.DataFrame) -> None:
    """Raise if required modelling input columns are missing."""
    missing_columns = sorted(set(REQUIRED_MODELLING_COLUMNS) - set(records.columns))
    if missing_columns:
        raise KeyError(f"Missing required modelling columns: {missing_columns}")


def save_processed_data(
    records: pd.DataFrame,
    name: str,
    *,
    output_dir: Path | str = DEFAULT_PROCESSED_DIR,
) -> Path:
    """Validate and save a processed table to a consistent processed-data path."""
    validate_modelling_columns(records)
    output_path = Path(output_dir) / f"{name}.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    records.to_csv(output_path, index=False)
    return output_path
