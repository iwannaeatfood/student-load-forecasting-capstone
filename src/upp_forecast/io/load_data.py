"""Raw and prepared data loading entry points."""

from collections.abc import Mapping
from pathlib import Path
from typing import TYPE_CHECKING, Any

from upp_forecast.io.csv_loader import CsvLoader
from upp_forecast.io.csv_strategy import CsvLoadingStrategy
from upp_forecast.io.errors import DataLoadingError

if TYPE_CHECKING:
    from pyspark.sql import SparkSession


class DataLoader:
    """Main entry point for loading raw and processed UPP data."""

    def __init__(
        self,
        *,
        paths: Mapping[str, Any] | None = None,
        csv_loader: CsvLoader | None = None,
        strategy: CsvLoadingStrategy | None = None,
        spark: "SparkSession | None" = None,
    ) -> None:
        if csv_loader is not None and (strategy is not None or spark is not None):
            raise DataLoadingError("Pass either csv_loader or strategy/spark, not both.")

        self._paths = paths or {}
        self._csv_loader = csv_loader or CsvLoader(strategy=strategy, spark=spark)

    def load_raw_data(
        self,
        path: str | Path | None = None,
        **csv_options: Any,
    ) -> Any | dict[str, Any]:
        """Load raw UPP data from a configured location."""
        return self._csv_loader.load(
            self._data_path(path, "raw_data"),
            **csv_options,
        )

    def load_processed_data(
        self,
        path: str | Path | None = None,
        **csv_options: Any,
    ) -> Any | dict[str, Any]:
        """Load modeling-ready UPP data from a configured location."""
        return self._csv_loader.load(
            self._data_path(path, "processed_data"),
            **csv_options,
        )

    def _data_path(self, path: str | Path | None, key: str) -> str | Path:
        if path is not None:
            return path

        configured_path = self._paths.get(key)
        if configured_path is None:
            raise DataLoadingError(f"Missing configured data path: paths.{key}")
        return configured_path
