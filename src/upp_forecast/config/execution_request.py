"""Create reproducible pipeline execution requests."""

import hashlib
import json
from pathlib import Path
from typing import Any, Protocol
from uuid import uuid4

from upp_forecast.config.config_loader import ConfigLoader
from upp_forecast.config.errors import ConfigError
from upp_forecast.config.request import PipelineExecutionRequest


class ConfigSource(Protocol):
    """Minimal config loader interface used by execution request creation."""

    def load(self, path: str | Path) -> dict[str, Any]:
        """Load a run config."""
        ...


class ExecutionRequestFactory:
    """Create reproducible pipeline execution requests from config files."""

    def __init__(self, config_loader: ConfigSource | None = None) -> None:
        self.config_loader = config_loader or ConfigLoader()

    def create(
        self,
        path: str | Path,
        *,
        run_id: str | None = None,
    ) -> PipelineExecutionRequest:
        """Create the reproducible execution request described by the UML."""
        config_path = Path(path)
        config = self.config_loader.load(config_path)
        paths = self._required_mapping(config, "paths")
        run = self._required_mapping(config, "run")

        output_path = Path(paths.get("outputs", "outputs"))
        input_data_version = str(run.get("input_data_version", "unversioned"))

        return PipelineExecutionRequest(
            run_id=run_id or str(uuid4()),
            config_version=self._hash_config(config),
            input_data_version=input_data_version,
            output_path=output_path,
            config_path=config_path,
            config=config,
        )

    def _hash_config(self, config: dict[str, Any]) -> str:
        serialized = json.dumps(config, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()[:12]

    def _required_mapping(self, config: dict[str, Any], key: str) -> dict[str, Any]:
        value = config.get(key)
        if not isinstance(value, dict):
            raise ConfigError(f"Config section must be a mapping: {key}")
        return value
