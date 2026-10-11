"""Build cohort-level state tables for model inputs."""

from collections.abc import Sequence

import pandas as pd

from upp_forecast.preprocessing.clean_terms import TERM_SCHEMA
from upp_forecast.preprocessing.schema import TermCleaningSchema


COHORT_COLUMNS = [
    "ACAD_PROG",
    "ACADEMIC_CAREER",
    "FUNDING_GROUP",
    "PROGRAM_COMMENCING_YEAR",
    "PROGRAM_COMMENCING_TERM",
]

STATE_COLUMNS = [
    "STUDENT_STATUS",
    "TERM_UOC_BAND",
    "Program_Completed",
    "Program_Completed_This_Year",
]

MEASURE_COLUMNS = [
    "STUDENT_HC",
    "ACTUAL_EFTSL",
]


def build_cohorts(
    records: pd.DataFrame,
    *,
    cohort_cols: Sequence[str] = COHORT_COLUMNS,
    state_cols: Sequence[str] = STATE_COLUMNS,
    measure_cols: Sequence[str] = MEASURE_COLUMNS,
    term_schema: TermCleaningSchema = TERM_SCHEMA,
) -> pd.DataFrame:
    required_columns = (
        list(cohort_cols)
        + list(state_cols)
        + list(measure_cols)
        + [term_schema.academic_year_col]
        + list(term_schema.metadata_columns)
    )
    missing_columns = sorted(set(required_columns) - set(records.columns))
    if missing_columns:
        raise KeyError(f"Missing required cohort columns: {missing_columns}")

    table = records.copy()
    table["student_hc"] = pd.to_numeric(table[measure_cols[0]], errors="coerce")
    table["actual_eftsl"] = pd.to_numeric(table[measure_cols[1]], errors="coerce")

    state_parts = table[list(state_cols)].astype("string").fillna("<missing>")
    table["state"] = state_parts.agg(" | ".join, axis=1)
    table = table.dropna(subset=["student_hc", "actual_eftsl"])

    period_cols = [
        term_schema.academic_year_col,
        *term_schema.metadata_columns,
    ]
    period_cols = list(dict.fromkeys(period_cols))
    group_cols = list(cohort_cols) + period_cols + list(state_cols) + ["state"]

    return (
        table.groupby(group_cols, dropna=False, as_index=False)
        .agg(
            student_hc=("student_hc", "sum"),
            actual_eftsl=("actual_eftsl", "sum"),
            source_rows=(cohort_cols[0], "size"),
            raw_term_labels=(
                term_schema.raw_term_col,
                lambda values: " | ".join(sorted({str(value) for value in values})),
            ),
        )
        .sort_values(
            [
                cohort_cols[0],
                term_schema.academic_year_col,
                term_schema.calendar_system_col,
                term_schema.term_order_col,
                "state",
            ],
            kind="stable",
        )
        .reset_index(drop=True)
    )
