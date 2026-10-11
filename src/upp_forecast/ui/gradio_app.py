"""Minimal Gradio shell for presentation demos."""

from pathlib import Path
from typing import Any

import gradio as gr
import pandas as pd


PLACEHOLDER_FORECAST = "Not connected"
PROJECT_ROOT = Path(__file__).resolve().parents[3]
ACTUALS_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "Actuals Data.csv"
TERMS_ACTIVE_YEARS_PATH = PROJECT_ROOT / "data" / "raw" / "Terms Active Years.csv"


def load_acad_prog_choices(path: Path = ACTUALS_DATA_PATH) -> list[str]:
    records = pd.read_csv(path, usecols=["ACAD_PROG"], dtype={"ACAD_PROG": "string"})
    return sorted(records["ACAD_PROG"].dropna().unique().tolist())


def load_year_choices(path: Path = TERMS_ACTIVE_YEARS_PATH) -> list[int]:
    records = pd.read_csv(path, nrows=0)
    return sorted(int(col) for col in records.columns if col.isdigit() and int(col) >= 2010)


def load_term_choices(
    year: int | str,
    path: Path = TERMS_ACTIVE_YEARS_PATH,
) -> list[str]:
    year_col = str(year)
    records = pd.read_csv(path, usecols=["Term", year_col])
    active = records[year_col].astype("string").str.upper() == "TRUE"
    return records.loc[active, "Term"].dropna().astype(str).tolist()


def preview_forecast(acad_prog: str, forecast_year: int | str, forecast_term: str) -> str:
    """Return a placeholder until forecasting is wired in."""
    return PLACEHOLDER_FORECAST


def create_demo() -> gr.Blocks:
    acad_prog_choices = load_acad_prog_choices()
    year_choices = load_year_choices()
    default_year = year_choices[-1] if year_choices else None
    term_choices = load_term_choices(default_year) if default_year else []

    with gr.Blocks(title="UPP Forecast Demo") as demo:
        gr.Markdown("# UPP Forecast Demo")
        gr.Markdown("Presentation shell only. Forecasting is not connected.")

        acad_prog = gr.Dropdown(
            choices=acad_prog_choices,
            value=acad_prog_choices[0] if acad_prog_choices else None,
            label="ACAD_PROG",
        )
        forecast_year = gr.Dropdown(
            choices=year_choices,
            value=default_year,
            label="Forecast Year",
        )
        forecast_term = gr.Dropdown(
            choices=term_choices,
            value=term_choices[0] if term_choices else None,
            label="Forecast Term",
        )
        forecast_hc = gr.Textbox(label="Forecast HC", interactive=False)
        submit = gr.Button("Submit")

        def update_terms(year: int | str) -> dict[str, Any]:
            choices = load_term_choices(year)
            return gr.update(choices=choices, value=choices[0] if choices else None)

        forecast_year.change(
            fn=update_terms,
            inputs=forecast_year,
            outputs=forecast_term,
        )
        submit.click(
            fn=preview_forecast,
            inputs=[acad_prog, forecast_year, forecast_term],
            outputs=forecast_hc,
        )

    return demo


if __name__ == "__main__":
    create_demo().launch()
