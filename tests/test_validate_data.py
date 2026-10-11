import pandas as pd

from upp_forecast.preprocessing.validate_data import validate_actuals


def test_validate_actuals_clean_data():
    df = pd.DataFrame(
        {
            "ACAD_PROG": [123],
            "ACADEMIC_YEAR": [2024],
            "TERM": ["T1"],
            "PROGRAM_COMMENCING_YEAR": [2024],
            "PROGRAM_COMMENCING_TERM": ["T1"],
            "STUDENT_STATUS": ["Cont"],
            "STUDENT_HC": [1],
            "ACTUAL_EFTSL": [0.5],
        }
    )

    result = validate_actuals(df)

    assert result["is_valid"] is True
    assert result["issue_count"] == 0

def test_validate_actuals_negative_eftsl():
    df = pd.DataFrame(
        {
            "ACAD_PROG": [123],
            "ACADEMIC_YEAR": [2024],
            "TERM": ["T1"],
            "PROGRAM_COMMENCING_YEAR": [2024],
            "PROGRAM_COMMENCING_TERM": ["T1"],
            "STUDENT_STATUS": ["Cont"],
            "STUDENT_HC": [1],
            "ACTUAL_EFTSL": [-1],
        }
    )

    result = validate_actuals(df)

    assert result["is_valid"] is False

def test_validate_actuals_negative_eftsl():
    df = pd.DataFrame(
        {
            "ACAD_PROG": [123],
            "ACADEMIC_YEAR": [2024],
            "TERM": ["T1"],
            "PROGRAM_COMMENCING_YEAR": [2024],
            "PROGRAM_COMMENCING_TERM": ["T1"],
            "STUDENT_STATUS": ["Cont"],
            "STUDENT_HC": [1],
            "ACTUAL_EFTSL": [-1],
        }
    )

    result = validate_actuals(df)

    assert result["is_valid"] is False

def test_validate_actuals_invalid_status():
    df = pd.DataFrame(
        {
            "ACAD_PROG": [123],
            "ACADEMIC_YEAR": [2024],
            "TERM": ["T1"],
            "PROGRAM_COMMENCING_YEAR": [2024],
            "PROGRAM_COMMENCING_TERM": ["T1"],
            "STUDENT_STATUS": ["BAD_STATUS"],
            "STUDENT_HC": [1],
            "ACTUAL_EFTSL": [0.5],
        }
    )

    result = validate_actuals(df)

    assert result["is_valid"] is False