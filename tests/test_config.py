"""Tests for run configuration loading."""

from collections.abc import Iterator
from pathlib import Path
import shutil

import pytest

from upp_forecast.config import (
    ConfigError,
    ConfigLoader,
    ExecutionRequestFactory,
)


@pytest.fixture
def config_dir() -> Iterator[Path]:
    path = Path(__file__).parent / ".tmp_config"
    if path.exists():
        shutil.rmtree(path)
    path.mkdir()
    yield path
    shutil.rmtree(path)


def test_config_loader_merges_extended_yaml(config_dir: Path):
    base_path = config_dir / "base.yaml"
    base_path.write_text(
        """
project:
  name: base
paths:
  outputs: outputs
model:
  name: baseline
  horizon_terms: 1
evaluation:
  metrics:
    - mae
""".strip(),
        encoding="utf-8",
    )
    child_path = config_dir / "child.yaml"
    child_path.write_text(
        f"""
extends: {base_path.as_posix()}
model:
  name: markov
evaluation:
  metrics:
    - rmse
""".strip(),
        encoding="utf-8",
    )

    config = ConfigLoader().load(child_path)

    assert config["project"]["name"] == "base"
    assert config["model"] == {"name": "markov", "horizon_terms": 1}
    assert config["evaluation"]["metrics"] == ["rmse"]
    assert "extends" not in config


def test_config_loader_class_merges_extended_yaml(config_dir: Path):
    base_path = config_dir / "base.yaml"
    base_path.write_text(
        """
paths:
  outputs: outputs
model:
  name: baseline
  horizon_terms: 1
""".strip(),
        encoding="utf-8",
    )
    child_path = config_dir / "child.yaml"
    child_path.write_text(
        """
extends: base.yaml
model:
  name: markov
""".strip(),
        encoding="utf-8",
    )

    config = ConfigLoader().load(child_path)

    assert config["paths"] == {"outputs": "outputs"}
    assert config["model"] == {"name": "markov", "horizon_terms": 1}


def test_config_loader_resolves_extends_from_parent_directories(config_dir: Path):
    project_dir = config_dir / "project"
    nested_config_dir = project_dir / "configs"
    nested_config_dir.mkdir(parents=True)
    base_path = nested_config_dir / "default.yaml"
    base_path.write_text(
        """
paths:
  outputs: outputs
run:
  input_data_version: local
""".strip(),
        encoding="utf-8",
    )
    child_path = nested_config_dir / "experiment.yaml"
    child_path.write_text(
        """
extends: configs/default.yaml
run:
  input_data_version: experiment
""".strip(),
        encoding="utf-8",
    )

    config = ConfigLoader().load(child_path)

    assert config["paths"] == {"outputs": "outputs"}
    assert config["run"]["input_data_version"] == "experiment"


def test_execution_request_factory_matches_uml_request_fields(config_dir: Path):
    config_path = config_dir / "default.yaml"
    config_path.write_text(
        """
paths:
  outputs: outputs
run:
  input_data_version: raw-local
""".strip(),
        encoding="utf-8",
    )

    request = ExecutionRequestFactory().create(config_path, run_id="test-run")

    assert request.run_id == "test-run"
    assert request.input_data_version == "raw-local"
    assert request.output_path == Path("outputs")
    assert len(request.config_version) == 12
    assert request.config_path == config_path


def test_execution_request_factory_uses_injected_config_loader():
    class StubConfigLoader:
        def load(self, path: str | Path) -> dict[str, object]:
            return {
                "paths": {"outputs": "custom-outputs"},
                "run": {"input_data_version": "stub-version"},
            }

    request = ExecutionRequestFactory(StubConfigLoader()).create(
        "config.yaml",
        run_id="stub-run",
    )

    assert request.run_id == "stub-run"
    assert request.input_data_version == "stub-version"
    assert request.output_path == Path("custom-outputs")


def test_config_loader_rejects_non_mapping_yaml(config_dir: Path):
    config_path = config_dir / "bad.yaml"
    config_path.write_text("- not\n- a\n- mapping\n", encoding="utf-8")

    with pytest.raises(ConfigError, match="must contain a mapping"):
        ConfigLoader().load(config_path)
