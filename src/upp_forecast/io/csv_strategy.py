"""CSV loading strategies."""

from collections.abc import Mapping
from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from pandas import DataFrame as PandasDataFrame
    from pyspark.sql import DataFrame as SparkDataFrame
    from pyspark.sql import SparkSession


DEFAULT_SPARK_CSV_OPTIONS: dict[str, Any] = {
    "header": True,
    "inferSchema": True,
}


class CsvLoadingStrategy(Protocol):
    """Strategy interface for reading individual CSV files."""

    def read_csv(self, path: Path, **csv_options: Any) -> Any:
        """Read one CSV file."""
        ...


class PandasCsvLoadingStrategy:
    """CSV loading strategy backed by pandas."""

    def read_csv(self, path: Path, **csv_options: Any) -> "PandasDataFrame":
        """Read one CSV file into a pandas DataFrame."""
        import pandas as pd

        return pd.read_csv(path, **csv_options)


class SparkCsvLoadingStrategy:
    """CSV loading strategy backed by PySpark."""

    def __init__(
        self,
        *,
        spark: "SparkSession | None" = None,
        app_name: str = "upp-forecasting-prototype",
        default_options: Mapping[str, Any] | None = None,
    ) -> None:
        self._spark = spark
        self._app_name = app_name
        self._default_options = dict(default_options or DEFAULT_SPARK_CSV_OPTIONS)

    @property
    def spark(self) -> "SparkSession":
        """Return the configured Spark session, creating one if needed."""
        if self._spark is None:
            self._spark = self._create_spark_session()
        return self._spark

    def read_csv(self, path: Path, **csv_options: Any) -> "SparkDataFrame":
        """Read one CSV file into a Spark DataFrame."""
        options = self._default_options | csv_options
        spark_path = path.resolve().as_posix()
        return self.spark.read.options(**options).csv(spark_path)

    def _create_spark_session(self) -> "SparkSession":
        from pyspark.sql import SparkSession

        return SparkSession.builder.appName(self._app_name).getOrCreate()
