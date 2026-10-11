"""CSV file and directory loading."""

from pathlib import Path
import re
from typing import TYPE_CHECKING, Any

from upp_forecast.io.csv_strategy import (
    CsvLoadingStrategy,
    PandasCsvLoadingStrategy,
    SparkCsvLoadingStrategy,
)
from upp_forecast.io.errors import DataLoadingError

if TYPE_CHECKING:
    from pyspark.sql import SparkSession


class CsvLoader:
    """Load one CSV file or a directory of CSV files."""

    def __init__(
        self,
        *,
        strategy: CsvLoadingStrategy | None = None,
        spark: "SparkSession | None" = None,
    ) -> None:
        self._strategy = self._resolve_strategy(strategy=strategy, spark=spark)

    def load(
        self,
        path: str | Path,
        **csv_options: Any,
    ) -> Any | dict[str, Any]:
        """Load one CSV file or every CSV file in a directory."""
        resolved_path = Path(path)
        if not resolved_path.exists():
            raise FileNotFoundError(f"Data path does not exist: {resolved_path}")

        if resolved_path.is_file():
            return self._strategy.read_csv(resolved_path, **csv_options)

        return self._load_directory(resolved_path, **csv_options)

    def _load_directory(
        self,
        path: Path,
        **csv_options: Any,
    ) -> dict[str, Any]:
        csv_files = sorted(path.glob("*.csv"))
        if not csv_files:
            raise FileNotFoundError(f"No CSV files found in directory: {path}")

        return {
            self._table_name_from_path(csv_path): self._strategy.read_csv(
                csv_path,
                **csv_options,
            )
            for csv_path in csv_files
        }

    def _resolve_strategy(
        self,
        *,
        strategy: CsvLoadingStrategy | None,
        spark: "SparkSession | None",
    ) -> CsvLoadingStrategy:
        if strategy is not None and spark is not None:
            raise DataLoadingError("Pass either strategy or spark, not both.")
        if strategy is not None:
            return strategy
        if spark is not None:
            return SparkCsvLoadingStrategy(spark=spark)
        return PandasCsvLoadingStrategy()

    def _table_name_from_path(self, path: Path) -> str:
        normalized = re.sub(r"[^0-9a-zA-Z]+", "_", path.stem).strip("_").lower()
        return normalized or "table"
