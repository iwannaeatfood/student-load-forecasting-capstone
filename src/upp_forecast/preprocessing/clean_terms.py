"""Normalize academic term labels for preprocessing."""

import pandas as pd

from upp_forecast.preprocessing.schema import TermCleaningSchema


TERM_ALIAS: dict[str, str] = {
    "Summer Term": "U1",
    "Term 1": "T1",
    "Term 2": "T2",
    "Term 3": "T3",
    "Summer Session": "Summer Session",
    "Semester 1": "S1",
    "Semester 2": "S2",
    "Winter Session": "Winter Session",
    "Summer Canberra": "ADFA Summer Semester",
    "Summer Semester": "ADFA Summer Semester",
    "Semester 1 Canberra": "ADFA S1",
    "Semester 2 Canberra": "ADFA S2",
    "Hexamester 1": "Hexa 1",
    "Hexamester 2": "Hexa 2",
    "Hexamester 3": "Hexa 3",
    "Hexamester 4": "Hexa 4",
    "Hexamester 5": "Hexa 5",
    "Hexamester 6": "Hexa 6",
}

TERM_SYSTEM: dict[str, str] = {
    "Summer Term": "sydney_term",
    "Term 1": "sydney_term",
    "Term 2": "sydney_term",
    "Term 3": "sydney_term",
    "Summer Session": "sydney_flexible_calendar",
    "Semester 1": "ambiguous_semester",
    "Semester 2": "ambiguous_semester",
    "Winter Session": "sydney_flexible_calendar",
    "Summer Canberra": "canberra_adfa",
    "Summer Semester": "canberra_adfa",
    "Semester 1 Canberra": "canberra_adfa",
    "Semester 2 Canberra": "canberra_adfa",
    "Hexamester 1": "unsw_online_hexamester",
    "Hexamester 2": "unsw_online_hexamester",
    "Hexamester 3": "unsw_online_hexamester",
    "Hexamester 4": "unsw_online_hexamester",
    "Hexamester 5": "unsw_online_hexamester",
    "Hexamester 6": "unsw_online_hexamester",
}

TERM_ORDER: dict[str, int] = {
    "U1": 0,
    "T1": 1,
    "T2": 2,
    "T3": 3,
    "S1": 1,
    "S2": 2,
    "Summer Session": 0,
    "Winter Session": 2,
    "ADFA Summer Semester": 0,
    "ADFA S1": 1,
    "ADFA S2": 2,
    "Hexa 1": 1,
    "Hexa 2": 2,
    "Hexa 3": 3,
    "Hexa 4": 4,
    "Hexa 5": 5,
    "Hexa 6": 6,
}

PERIOD_DELTA: dict[str, float | None] = {
    "U1": 36 / 365.25,
    "T1": 1 / 3,
    "T2": 1 / 3,
    "T3": 1 / 3,
    "S1": 1 / 2,
    "S2": 1 / 2,
    "Summer Session": None,
    "Winter Session": None,
    "ADFA Summer Semester": 70 / 365.25,
    "ADFA S1": 1 / 2,
    "ADFA S2": 1 / 2,
    "Hexa 1": 1 / 6,
    "Hexa 2": 1 / 6,
    "Hexa 3": 1 / 6,
    "Hexa 4": 1 / 6,
    "Hexa 5": 1 / 6,
    "Hexa 6": 1 / 6,
}

PERIOD_START_FRACTION: dict[str, float | None] = {
    "U1": 0.00,
    "T1": 0.12,
    "T2": 0.42,
    "T3": 0.70,
    "S1": 0.13,
    "S2": 0.55,
    "Summer Session": 0.00,
    "Winter Session": 0.45,
    "ADFA Summer Semester": 0.00,
    "ADFA S1": 0.14,
    "ADFA S2": 0.55,
    "Hexa 1": 0 / 6,
    "Hexa 2": 1 / 6,
    "Hexa 3": 2 / 6,
    "Hexa 4": 3 / 6,
    "Hexa 5": 4 / 6,
    "Hexa 6": 5 / 6,
}

TERM_SCHEMA = TermCleaningSchema()


def clean_terms(
    records: pd.DataFrame,
    schema: TermCleaningSchema = TERM_SCHEMA,
) -> pd.DataFrame:
    missing_columns = set(schema.required_input_columns) - set(records.columns)
    if missing_columns:
        raise KeyError(f"Missing required term columns: {sorted(missing_columns)}")

    cleaned = records.copy()
    cleaned[schema.term_academic_year_col] = pd.to_numeric(
        cleaned[schema.academic_year_col],
        errors="coerce",
    ).astype("Int64")

    cleaned[schema.raw_term_col] = cleaned[schema.term_col]
    cleaned[schema.teaching_period_label_col] = cleaned[schema.term_col].map(
        TERM_ALIAS,
    )
    cleaned[schema.calendar_system_col] = cleaned[schema.term_col].map(TERM_SYSTEM)
    cleaned[schema.term_order_col] = (
        cleaned[schema.teaching_period_label_col].map(TERM_ORDER).astype("Int64")
    )

    cleaned[schema.period_delta_col] = cleaned[schema.teaching_period_label_col].map(
        PERIOD_DELTA
    )

    cleaned[schema.period_start_fraction_col] = cleaned[
        schema.teaching_period_label_col
    ].map(PERIOD_START_FRACTION)

    cleaned[schema.period_time_col] = cleaned[schema.term_academic_year_col].astype(
        "Float64"
    ) + cleaned[schema.period_start_fraction_col].astype("Float64")

    has_term_key = (
        cleaned[schema.term_academic_year_col].notna()
        & cleaned[schema.calendar_system_col].notna()
        & cleaned[schema.teaching_period_label_col].notna()
    )
    cleaned[schema.term_key_col] = pd.Series(
        pd.NA,
        index=cleaned.index,
        dtype="string",
    )
    cleaned.loc[has_term_key, schema.term_key_col] = (
        cleaned.loc[has_term_key, schema.term_academic_year_col].astype("string")
        + ":"
        + cleaned.loc[has_term_key, schema.calendar_system_col].astype("string")
        + ":"
        + cleaned.loc[has_term_key, schema.teaching_period_label_col].astype(
            "string",
        )
    )

    return cleaned
