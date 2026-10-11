"""Single entry point that chains the forecasting pipeline end-to-end."""

# Implemented for H11CBREAD-11

import argparse
import json
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from upp_forecast.config import ExecutionRequestFactory, PipelineExecutionRequest
from upp_forecast.io import DataLoader
from upp_forecast.preprocessing.save_processed_data import save_processed_data
from upp_forecast.preprocessing.transform_load import transform_load

RAW_RECORDS_TABLE = "actuals_data"
PROCESSED_TABLE_NAME = "cohort_state_table"
FORECAST_OUTPUT_NAME = "forecast_output"

ModelStage = Callable[[pd.DataFrame, dict], pd.DataFrame]


def default_model_stage(processed: pd.DataFrame, config: dict) -> pd.DataFrame:
    """Placeholder model stage.

    Passes the processed table through unchanged. H11CBREAD-34 wires in the
    real CTMC + NAC combined forecasting module (H11CBREAD-35) here once it
    lands; this default only proves the pipeline shape end-to-end.
    """
    return processed


@dataclass(frozen=True)
class PipelineRunResult:
    """Artifacts and metadata produced by one pipeline run."""

    request: PipelineExecutionRequest
    processed_path: Path
    forecast_path: Path
    metadata_path: Path
    metadata: dict


def run_pipeline(
    config_path: str | Path,
    *,
    run_id: str | None = None,
    model_stage: ModelStage = default_model_stage,
) -> PipelineRunResult:
    """Run raw data -> preprocessing -> model stage -> forecast output from a config file."""
    request = ExecutionRequestFactory().create(config_path, run_id=run_id)
    run_date = datetime.now(timezone.utc)

    paths = request.config.get("paths", {})
    raw_data_path = Path(paths.get("raw_data", "data/raw"))
    processed_data_path = Path(paths.get("processed_data", "data/processed"))

    raw_tables = DataLoader(paths=paths).load_raw_data()
    if RAW_RECORDS_TABLE not in raw_tables:
        raise KeyError(
            f"Missing required raw table '{RAW_RECORDS_TABLE}' in {raw_data_path}"
        )
    records = raw_tables[RAW_RECORDS_TABLE]

    processed = transform_load(records)
    processed_path = save_processed_data(
        processed,
        PROCESSED_TABLE_NAME,
        output_dir=processed_data_path,
    )

    model_output = model_stage(processed, request.config)

    run_output_dir = request.output_path / request.run_id
    run_output_dir.mkdir(parents=True, exist_ok=True)
    forecast_path = run_output_dir / f"{FORECAST_OUTPUT_NAME}.csv"
    model_output.to_csv(forecast_path, index=False)

    metadata = {
        "run_id": request.run_id,
        "run_date": run_date.isoformat(),
        "input_data_path": str(raw_data_path),
        "config_path": str(request.config_path),
        "config_version": request.config_version,
        "model_version": request.config.get("model", {}).get("name", "unknown"),
        "output_path": str(run_output_dir),
        "processed_data_path": str(processed_path),
        "forecast_output_path": str(forecast_path),
    }
    metadata_path = run_output_dir / "run_metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    return PipelineRunResult(
        request=request,
        processed_path=processed_path,
        forecast_path=forecast_path,
        metadata_path=metadata_path,
        metadata=metadata,
    )


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the UPP forecasting pipeline end-to-end.",
    )
    parser.add_argument(
        "--config",
        default="configs/default.yaml",
        help="Path to the run config YAML file.",
    )
    parser.add_argument(
        "--run-id",
        default=None,
        help="Optional explicit run id (defaults to a generated UUID).",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> None:
    args = _parse_args(argv)
    result = run_pipeline(args.config, run_id=args.run_id)
    print(f"run_id: {result.request.run_id}")
    print(f"processed data: {result.processed_path}")
    print(f"forecast output: {result.forecast_path}")
    print(f"run metadata: {result.metadata_path}")


if __name__ == "__main__":
    main()
