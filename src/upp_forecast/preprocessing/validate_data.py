"""Validate Actuals data before forecasting preprocessing."""

from typing import Any

import pandas as pd


ALLOWED_BUSINESS_MISSING_COLUMNS = {
    "PROGRAM_COMPLETION_YEAR",
    "COMMENCING_PRIOR_ACAD_PROG",
}

REQUIRED_COLUMNS = {
    "ACAD_PROG",
    "ACADEMIC_YEAR",
    "TERM",
    "PROGRAM_COMMENCING_YEAR",
    "PROGRAM_COMMENCING_TERM",
    "STUDENT_STATUS",
    "STUDENT_HC",
    "ACTUAL_EFTSL",
}

MEASURE_COLUMNS = ["STUDENT_HC", "ACTUAL_EFTSL"]
STATUS_COLUMN = "STUDENT_STATUS"
EXPECTED_STATUSES = {"NAC", "Cont", "TransIn"}


def get_required_column_summary(records: pd.DataFrame) -> dict[str, Any]:
    """Check whether required forecasting columns are present."""
    missing_columns = sorted(REQUIRED_COLUMNS - set(records.columns))

    return {
        "required_columns": sorted(REQUIRED_COLUMNS),
        "missing_required_columns": missing_columns,
    }


def get_missing_value_summary(records: pd.DataFrame) -> dict[str, Any]:
    """Return missing value counts and identify unexpected missing columns."""
    missing_counts = records.isna().sum()
    missing_counts = missing_counts[missing_counts > 0].to_dict()

    unexpected_missing = {
        col: count
        for col, count in missing_counts.items()
        if col not in ALLOWED_BUSINESS_MISSING_COLUMNS
    }

    return {
        "missing_counts": missing_counts,
        "allowed_business_missing_columns": sorted(ALLOWED_BUSINESS_MISSING_COLUMNS),
        "unexpected_missing": unexpected_missing,
    }


def get_duplicate_summary(records: pd.DataFrame) -> dict[str, int]:
    """Return duplicate row summary."""
    return {
        "duplicate_rows": int(records.duplicated().sum()),
    }


def get_invalid_measure_summary(records: pd.DataFrame) -> dict[str, int]:
    """Return invalid HC and EFTSL measure checks."""
    summary: dict[str, int] = {}

    for col in MEASURE_COLUMNS:
        if col not in records.columns:
            summary[f"missing_column_{col}"] = 1
            continue

        numeric_col = pd.to_numeric(records[col], errors="coerce")
        summary[f"{col}_missing"] = int(numeric_col.isna().sum())
        summary[f"{col}_negative"] = int((numeric_col < 0).sum())

    return summary


def get_status_distribution(records: pd.DataFrame) -> dict[str, int]:
    """Return student status distribution."""
    if STATUS_COLUMN not in records.columns:
        return {}

    return records[STATUS_COLUMN].value_counts(dropna=False).to_dict()


def get_invalid_status_summary(records: pd.DataFrame) -> dict[str, Any]:
    """Check for unexpected student status values."""
    if STATUS_COLUMN not in records.columns:
        return {
            "expected_statuses": sorted(EXPECTED_STATUSES),
            "unexpected_statuses": [],
        }

    observed_statuses = set(records[STATUS_COLUMN].dropna().unique())
    unexpected_statuses = sorted(observed_statuses - EXPECTED_STATUSES)

    return {
        "expected_statuses": sorted(EXPECTED_STATUSES),
        "unexpected_statuses": unexpected_statuses,
    }


def validate_actuals(records: pd.DataFrame) -> dict[str, Any]:
    """Run data quality checks for Actuals data."""
    required_columns = get_required_column_summary(records)
    missing_values = get_missing_value_summary(records)
    duplicate_rows = get_duplicate_summary(records)
    invalid_measures = get_invalid_measure_summary(records)
    invalid_statuses = get_invalid_status_summary(records)

    issues: list[str] = []

    if required_columns["missing_required_columns"]:
        issues.append("missing_required_columns")

    if missing_values["unexpected_missing"]:
        issues.append("unexpected_missing_values")

    if duplicate_rows["duplicate_rows"] > 0:
        issues.append("duplicate_rows")

    if any(count > 0 for count in invalid_measures.values()):
        issues.append("invalid_measure_values")

    if invalid_statuses["unexpected_statuses"]:
        issues.append("unexpected_student_statuses")

    return {
        "is_valid": len(issues) == 0,
        "issue_count": len(issues),
        "issues": issues,
        "row_count": len(records),
        "column_count": len(records.columns),
        "required_columns": required_columns,
        "missing_values": missing_values,
        "duplicate_rows": duplicate_rows,
        "invalid_measures": invalid_measures,
        "status_distribution": get_status_distribution(records),
        "invalid_statuses": invalid_statuses,
    }