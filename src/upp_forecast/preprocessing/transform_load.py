"""Transform cleaned records into a time-indexed student load table."""

# Implemented for H11CBREAD-30

import pandas as pd

from upp_forecast.preprocessing.build_cohorts import build_cohorts
from upp_forecast.preprocessing.clean_terms import TERM_SCHEMA, clean_terms
from upp_forecast.preprocessing.schema import TermCleaningSchema


STUDENT_LOAD_MEASURE_COL = "student_hc"


def transform_load(
    records: pd.DataFrame,
    *,
    term_schema: TermCleaningSchema = TERM_SCHEMA,
) -> pd.DataFrame:
    """Transform raw records into a time-indexed student load table."""
    cleaned = clean_terms(records, schema=term_schema)
    cohorts = build_cohorts(cleaned, term_schema=term_schema)
    return cohorts.sort_values(term_schema.period_time_col, kind="stable").reset_index(drop=True)
