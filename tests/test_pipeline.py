"""Tests for the pipeline entry point (H11CBREAD-11)."""

import json
from pathlib import Path

import pandas as pd
import pytest

from upp_forecast.pipeline.run_forecast import run_pipeline


RAW_CSV = """ACAD_PROG,ACADEMIC_CAREER,FUNDING_GROUP,PROGRAM_COMMENCING_YEAR,PROGRAM_COMMENCING_TERM,ACADEMIC_YEAR,TERM,STUDENT_STATUS,TERM_UOC_BAND,Program_Completed,Program_Completed_This_Year,STUDENT_HC,ACTUAL_EFTSL
3778,UGRD,DOM,2025,Term 1,2025,Term 2,NAC,0-48,False,False,5,1.5
3778,UGRD,DOM,2025,Term 1,2025,Term 1,NAC,0-48,False,False,10,3.0
"""


@pytest.fixture
def project_dir(tmp_path: Path) -> Path:
    raw_dir = tmp_path / "data" / "raw"
    raw_dir.mkdir(parents=True)
    (raw_dir / "Actuals Data.csv").write_text(RAW_CSV, encoding="utf-8")

    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        f"""
paths:
  raw_data: {raw_dir.as_posix()}
  processed_data: {(tmp_path / "data" / "processed").as_posix()}
  outputs: {(tmp_path / "outputs").as_posix()}
run:
  input_data_version: test-fixture
model:
  name: baseline
""".strip(),
        encoding="utf-8",
    )
    return tmp_path


def test_run_pipeline_produces_processed_and_forecast_outputs(project_dir: Path):
    config_path = project_dir / "config.yaml"

    result = run_pipeline(config_path, run_id="test-run")

    assert result.processed_path.exists()
    assert result.forecast_path.exists()
    assert result.metadata_path.exists()

    processed = pd.read_csv(result.processed_path)
    assert list(processed["student_hc"]) == [10, 5]

    metadata = json.loads(result.metadata_path.read_text(encoding="utf-8"))
    assert metadata["run_id"] == "test-run"
    assert Path(metadata["input_data_path"]) == project_dir / "data" / "raw"
    assert metadata["model_version"] == "baseline"
    assert "run_date" in metadata


def test_run_pipeline_uses_custom_model_stage(project_dir: Path):
    config_path = project_dir / "config.yaml"
    calls: list[str] = []

    def custom_stage(processed: pd.DataFrame, config: dict) -> pd.DataFrame:
        calls.append(config["model"]["name"])
        return processed.assign(forecast_flag=True)

    result = run_pipeline(config_path, run_id="test-run-2", model_stage=custom_stage)

    forecast = pd.read_csv(result.forecast_path)
    assert forecast["forecast_flag"].all()
    assert calls == ["baseline"]


def test_run_pipeline_rejects_missing_actuals_table(tmp_path: Path):
    raw_dir = tmp_path / "data" / "raw"
    raw_dir.mkdir(parents=True)
    (raw_dir / "Other Data.csv").write_text("id,value\n1,2\n", encoding="utf-8")

    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        f"""
paths:
  raw_data: {raw_dir.as_posix()}
  processed_data: {(tmp_path / "data" / "processed").as_posix()}
  outputs: {(tmp_path / "outputs").as_posix()}
run:
  input_data_version: test-fixture
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(KeyError, match="Missing required raw table"):
        run_pipeline(config_path, run_id="test-run-3")
