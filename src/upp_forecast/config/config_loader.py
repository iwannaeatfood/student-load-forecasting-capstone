"""YAML run configuration loading."""

from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml

from upp_forecast.config.errors import ConfigError


class ConfigLoader:
    """Load YAML run configurations with optional inheritance."""

    def load(self, path: str | Path) -> dict[str, Any]:
        """Load a YAML run config, applying any inherited base config."""
        return self._load_config(Path(path), seen=set())

    def _load_config(self, path: Path, seen: set[Path]) -> dict[str, Any]:
        resolved_path = path.resolve()
        if resolved_path in seen:
            raise ConfigError(f"Circular config inheritance detected: {path}")
        if not path.exists():
            raise FileNotFoundError(f"Config file does not exist: {path}")

        seen.add(resolved_path)
        config = self._read_yaml(path)

        extends = config.pop("extends", None)
        if not extends:
            return config

        base_path = self._resolve_extends_path(str(extends), path)
        base_config = self._load_config(base_path, seen)
        return self._deep_merge(base_config, config)

    def _read_yaml(self, path: Path) -> dict[str, Any]:
        with path.open("r", encoding="utf-8") as stream:
            loaded = yaml.safe_load(stream) or {}
        if not isinstance(loaded, dict):
            raise ConfigError(f"Config file must contain a mapping: {path}")
        return loaded

    def _resolve_extends_path(self, extends: str, config_path: Path) -> Path:
        extends_path = Path(extends)
        if extends_path.is_absolute():
            return extends_path

        candidates = [config_path.parent / extends_path]
        candidates.extend(parent / extends_path for parent in config_path.parents)
        candidates.append(extends_path)

        seen: set[Path] = set()
        for candidate in candidates:
            resolved_candidate = candidate.resolve()
            if resolved_candidate in seen:
                continue
            seen.add(resolved_candidate)
            if candidate.exists():
                return candidate
        return candidates[0]

    def _deep_merge(
        self,
        base: dict[str, Any],
        override: dict[str, Any],
    ) -> dict[str, Any]:
        merged = deepcopy(base)
        for key, value in override.items():
            if isinstance(value, dict) and isinstance(merged.get(key), dict):
                merged[key] = self._deep_merge(merged[key], value)
            else:
                merged[key] = deepcopy(value)
        return merged
