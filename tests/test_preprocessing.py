"""Smoke tests for preprocessing placeholders."""

import csv
from pathlib import Path

import pandas as pd
import pytest

from upp_forecast.preprocessing.build_cohorts import build_cohorts
from upp_forecast.preprocessing.clean_terms import (
    TERM_ALIAS,
    TERM_SCHEMA,
    clean_terms,
)
from upp_forecast.preprocessing.save_processed_data import (
    validate_modelling_columns,
    save_processed_data,
)
from upp_forecast.preprocessing.schema import TermCleaningSchema
from upp_forecast.preprocessing.transform_load import (
    STUDENT_LOAD_MEASURE_COL,
    transform_load,
)


def test_term_aliases_match_terms_active_years_raw_terms():
    terms_path = Path("data/raw/Terms Active Years.csv")
    with terms_path.open("r", encoding="utf-8-sig", newline="") as stream:
        raw_terms = {
            row["Term"]
            for row in csv.DictReader(stream)
            if row.get("Term")
        }

    assert set(TERM_ALIAS) == raw_terms


def test_term_cleaning_schema_defines_input_and_output_columns():
    schema = TermCleaningSchema()

    assert schema.required_input_columns == ("ACADEMIC_YEAR", "TERM")
    assert schema.output_columns == (
        "raw_term",
        "term_academic_year",
        "teaching_period_label",
        "calendar_system",
        "term_order",
        "period_delta",
        "period_start_fraction",
        "period_time",
        "term_key",
    )
    assert schema.metadata_columns == schema.output_columns


def test_clean_terms_adds_period_metadata_for_known_term():
    records = pd.DataFrame(
        {
            "ACADEMIC_YEAR": ["2025"],
            "TERM": ["Term 1"],
            "value": [1],
        },
    )

    cleaned = clean_terms(records)

    assert cleaned.loc[0, TERM_SCHEMA.term_academic_year_col] == 2025
    assert cleaned.loc[0, TERM_SCHEMA.raw_term_col] == "Term 1"
    assert cleaned.loc[0, TERM_SCHEMA.teaching_period_label_col] == "T1"
    assert cleaned.loc[0, TERM_SCHEMA.calendar_system_col] == "sydney_term"
    assert cleaned.loc[0, TERM_SCHEMA.term_order_col] == 1
    assert cleaned.loc[0, TERM_SCHEMA.period_delta_col] == 1 / 3
    assert cleaned.loc[0, TERM_SCHEMA.period_time_col] == 2025.12
    assert cleaned.loc[0, TERM_SCHEMA.term_key_col] == "2025:sydney_term:T1"
    assert "academic_year" not in cleaned.columns


def test_clean_terms_keeps_unknown_term_with_missing_metadata():
    records = pd.DataFrame(
        {
            "ACADEMIC_YEAR": ["2025"],
            "TERM": ["Unknown Term"],
        },
    )

    cleaned = clean_terms(records)

    assert cleaned.loc[0, TERM_SCHEMA.raw_term_col] == "Unknown Term"
    assert pd.isna(cleaned.loc[0, TERM_SCHEMA.teaching_period_label_col])
    assert pd.isna(cleaned.loc[0, TERM_SCHEMA.calendar_system_col])
    assert pd.isna(cleaned.loc[0, TERM_SCHEMA.term_order_col])
    assert pd.isna(cleaned.loc[0, TERM_SCHEMA.period_delta_col])
    assert pd.isna(cleaned.loc[0, TERM_SCHEMA.period_time_col])
    assert pd.isna(cleaned.loc[0, TERM_SCHEMA.term_key_col])


def test_build_cohorts_aggregates_matching_cohort_state_rows():
    raw = pd.DataFrame(
        {
            "ACAD_PROG": ["3778", "3778"],
            "ACADEMIC_CAREER": ["UGRD", "UGRD"],
            "FUNDING_GROUP": ["DOM", "DOM"],
            "PROGRAM_COMMENCING_YEAR": [2025, 2025],
            "PROGRAM_COMMENCING_TERM": ["Term 1", "Term 1"],
            "ACADEMIC_YEAR": [2025, 2025],
            "TERM": ["Term 1", "Term 1"],
            "STUDENT_STATUS": ["NAC", "NAC"],
            "TERM_UOC_BAND": ["0-48", "0-48"],
            "Program_Completed": [False, False],
            "Program_Completed_This_Year": [False, False],
            "STUDENT_HC": [10, 5],
            "ACTUAL_EFTSL": [3.0, 1.5],
        },
    )

    cohorts = build_cohorts(clean_terms(raw))

    assert len(cohorts) == 1
    assert cohorts.loc[0, "state"] == "NAC | 0-48 | False | False"
    assert cohorts.loc[0, "student_hc"] == 15
    assert cohorts.loc[0, "actual_eftsl"] == 4.5
    assert cohorts.loc[0, "source_rows"] == 2
    assert cohorts.loc[0, "raw_term_labels"] == "Term 1"


def test_build_cohorts_rejects_missing_required_columns():
    with pytest.raises(KeyError, match="Missing required cohort columns"):
        build_cohorts(pd.DataFrame({"ACAD_PROG": ["3778"]}))


def test_transform_load_produces_time_indexed_student_load_table():
    raw = pd.DataFrame(
        {
            "ACAD_PROG": ["3778", "3778"],
            "ACADEMIC_CAREER": ["UGRD", "UGRD"],
            "FUNDING_GROUP": ["DOM", "DOM"],
            "PROGRAM_COMMENCING_YEAR": [2025, 2025],
            "PROGRAM_COMMENCING_TERM": ["Term 1", "Term 1"],
            "ACADEMIC_YEAR": [2025, 2025],
            "TERM": ["Term 2", "Term 1"],
            "STUDENT_STATUS": ["NAC", "NAC"],
            "TERM_UOC_BAND": ["0-48", "0-48"],
            "Program_Completed": [False, False],
            "Program_Completed_This_Year": [False, False],
            "STUDENT_HC": [5, 10],
            "ACTUAL_EFTSL": [1.5, 3.0],
        },
    )

    load_table = transform_load(raw)

    assert list(load_table[STUDENT_LOAD_MEASURE_COL]) == [10, 5]
    assert load_table[TERM_SCHEMA.period_time_col].is_monotonic_increasing


def test_transform_load_rejects_missing_required_columns():
    with pytest.raises(KeyError, match="Missing required cohort columns"):
        transform_load(pd.DataFrame({"ACADEMIC_YEAR": [2025], "TERM": ["Term 1"]}))


def test_validate_modelling_columns_rejects_missing_columns():
    with pytest.raises(KeyError, match="Missing required modelling columns"):
        validate_modelling_columns(pd.DataFrame({"ACAD_PROG": ["3778"]}))


def test_save_processed_data_writes_csv_to_consistent_path(tmp_path):
    raw = pd.DataFrame(
        {
            "ACAD_PROG": ["3778", "3778"],
            "ACADEMIC_CAREER": ["UGRD", "UGRD"],
            "FUNDING_GROUP": ["DOM", "DOM"],
            "PROGRAM_COMMENCING_YEAR": [2025, 2025],
            "PROGRAM_COMMENCING_TERM": ["Term 1", "Term 1"],
            "ACADEMIC_YEAR": [2025, 2025],
            "TERM": ["Term 1", "Term 1"],
            "STUDENT_STATUS": ["NAC", "NAC"],
            "TERM_UOC_BAND": ["0-48", "0-48"],
            "Program_Completed": [False, False],
            "Program_Completed_This_Year": [False, False],
            "STUDENT_HC": [10, 5],
            "ACTUAL_EFTSL": [3.0, 1.5],
        },
    )
    load_table = transform_load(raw)

    output_path = save_processed_data(load_table, "test_table", output_dir=tmp_path)

    assert output_path == tmp_path / "test_table.csv"
    assert output_path.exists()
    reloaded = pd.read_csv(output_path)
    assert len(reloaded) == len(load_table)


def test_save_processed_data_rejects_missing_modelling_columns(tmp_path):
    with pytest.raises(KeyError, match="Missing required modelling columns"):
        save_processed_data(pd.DataFrame({"ACAD_PROG": ["3778"]}), "test_table", output_dir=tmp_path)
