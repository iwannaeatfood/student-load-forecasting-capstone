"""Pipeline execution request model."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class PipelineExecutionRequest:
    """Layer 1 request passed to pipeline orchestration."""

    run_id: str
    config_version: str
    input_data_version: str
    output_path: Path
    config_path: Path
    config: dict[str, Any]
