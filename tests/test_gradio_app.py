from upp_forecast.ui.gradio_app import (
    PLACEHOLDER_FORECAST,
    create_demo,
    load_acad_prog_choices,
    load_term_choices,
    load_year_choices,
    preview_forecast,
)


FIXTURES_DIR = "tests/fixtures"


def test_load_acad_prog_choices_removes_duplicates_and_preserves_codes():
    assert load_acad_prog_choices(f"{FIXTURES_DIR}/gradio_actuals.csv") == [
        "0350",
        "350",
    ]


def test_load_year_choices_keeps_years_from_2010_onward():
    assert load_year_choices(f"{FIXTURES_DIR}/gradio_terms.csv") == [
        2010,
        2011,
        2026,
    ]


def test_load_term_choices_returns_active_terms_for_year():
    assert load_term_choices(2026, f"{FIXTURES_DIR}/gradio_terms.csv") == [
        "Term 1",
        "Term 3",
    ]


def test_preview_forecast_returns_placeholder_without_using_inputs():
    assert preview_forecast("3778", 2026, "Term 1") == PLACEHOLDER_FORECAST
    assert preview_forecast("9999", "2030", "anything") == PLACEHOLDER_FORECAST


def test_create_demo_builds_gradio_interface():
    assert create_demo() is not None
