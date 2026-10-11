"""Tests for strategy-backed CSV loading."""

from collections.abc import Iterator
from pathlib import Path
import shutil
from typing import Any, cast

import pandas as pd
import pytest

from upp_forecast.io import (
    CsvLoader,
    DataLoader,
    DataLoadingError,
    PandasCsvLoadingStrategy,
    SparkCsvLoadingStrategy,
)


class FakeReader:
    def __init__(self) -> None:
        self.csv_calls: list[str] = []
        self.option_calls: list[dict[str, object]] = []

    def options(self, **options: object) -> "FakeReader":
        self.option_calls.append(options)
        return self

    def csv(self, path: str) -> dict[str, object]:
        self.csv_calls.append(path)
        return {"path": path, "options": self.option_calls[-1]}


class FakeSpark:
    def __init__(self) -> None:
        self.read = FakeReader()


@pytest.fixture
def data_dir() -> Iterator[Path]:
    path = Path(__file__).parent / ".tmp_load_data"
    if path.exists():
        shutil.rmtree(path)
    path.mkdir()
    yield path
    shutil.rmtree(path)


def _pandas_frame(value: object) -> pd.DataFrame:
    assert isinstance(value, pd.DataFrame)
    return value


def _pandas_tables(value: object) -> dict[str, pd.DataFrame]:
    assert isinstance(value, dict)
    return cast(dict[str, pd.DataFrame], value)


def _spark_frame(value: object) -> dict[str, object]:
    assert isinstance(value, dict)
    return cast(dict[str, object], value)


def test_load_csv_data_uses_pandas_by_default(data_dir: Path):
    csv_path = data_dir / "Actuals Data.csv"
    csv_path.write_text("id,value\n1,2\n", encoding="utf-8")

    data_frame = _pandas_frame(CsvLoader().load(csv_path))

    assert data_frame.to_dict("records") == [{"id": 1, "value": 2}]


def test_csv_loader_loads_csv_directory_as_pandas_tables(data_dir: Path):
    (data_dir / "Actuals Data.csv").write_text("id,value\n1,2\n", encoding="utf-8")
    (data_dir / "NAC HC - Term Years.csv").write_text(
        "term,year\nT1,2024\n",
        encoding="utf-8",
    )

    tables = _pandas_tables(CsvLoader().load(data_dir))

    assert sorted(tables) == ["actuals_data", "nac_hc_term_years"]
    assert tables["actuals_data"].to_dict("records") == [{"id": 1, "value": 2}]
    assert tables["nac_hc_term_years"].to_dict("records") == [
        {"term": "T1", "year": 2024},
    ]


def test_load_csv_data_accepts_explicit_pandas_strategy_options(data_dir: Path):
    csv_path = data_dir / "no_header.csv"
    csv_path.write_text("1,2\n", encoding="utf-8")

    data_frame = _pandas_frame(
        CsvLoader(strategy=PandasCsvLoadingStrategy()).load(
            csv_path,
            header=None,
        ),
    )

    assert data_frame.to_dict("records") == [{0: 1, 1: 2}]


def test_load_csv_data_accepts_spark_strategy(data_dir: Path):
    csv_path = data_dir / "Actuals Data.csv"
    csv_path.write_text("id,value\n1,2\n", encoding="utf-8")
    spark = FakeSpark()

    data_frame = _spark_frame(
        CsvLoader(
            strategy=SparkCsvLoadingStrategy(spark=cast(Any, spark)),
        ).load(csv_path),
    )

    assert data_frame["path"] == csv_path.resolve().as_posix()
    assert data_frame["options"] == {"header": True, "inferSchema": True}
    assert spark.read.csv_calls == [csv_path.resolve().as_posix()]


def test_load_csv_data_uses_spark_strategy_when_spark_is_provided(data_dir: Path):
    csv_path = data_dir / "Actuals Data.csv"
    csv_path.write_text("id,value\n1,2\n", encoding="utf-8")
    spark = FakeSpark()

    data_frame = _spark_frame(
        CsvLoader(spark=cast(Any, spark)).load(
            csv_path,
            inferSchema=False,
        ),
    )

    assert data_frame["options"] == {"header": True, "inferSchema": False}


def test_load_csv_data_rejects_conflicting_strategy_inputs(data_dir: Path):
    csv_path = data_dir / "Actuals Data.csv"
    csv_path.write_text("id,value\n1,2\n", encoding="utf-8")

    with pytest.raises(DataLoadingError, match="either strategy or spark"):
        CsvLoader(
            strategy=PandasCsvLoadingStrategy(),
            spark=cast(Any, FakeSpark()),
        )


def test_load_csv_data_rejects_missing_path(data_dir: Path):
    with pytest.raises(FileNotFoundError, match="Data path does not exist"):
        CsvLoader(spark=cast(Any, FakeSpark())).load(
            data_dir / "missing.csv",
        )


def test_load_csv_data_rejects_directory_without_csv(data_dir: Path):
    with pytest.raises(FileNotFoundError, match="No CSV files found"):
        CsvLoader(spark=cast(Any, FakeSpark())).load(data_dir)


def test_data_loader_uses_configured_raw_data_path(data_dir: Path):
    raw_dir = data_dir / "raw"
    raw_dir.mkdir()
    (raw_dir / "Actuals Data.csv").write_text("id,value\n1,2\n", encoding="utf-8")

    tables = _pandas_tables(DataLoader(paths={"raw_data": raw_dir}).load_raw_data())

    assert sorted(tables) == ["actuals_data"]
    assert tables["actuals_data"].to_dict("records") == [{"id": 1, "value": 2}]


def test_data_loader_uses_configured_processed_data_path(data_dir: Path):
    processed_dir = data_dir / "processed"
    processed_dir.mkdir()
    (processed_dir / "model_ready.csv").write_text(
        "cohort,load\nA,12\n",
        encoding="utf-8",
    )

    tables = _pandas_tables(
        DataLoader(paths={"processed_data": processed_dir}).load_processed_data(),
    )

    assert sorted(tables) == ["model_ready"]
    assert tables["model_ready"].to_dict("records") == [{"cohort": "A", "load": 12}]


def test_data_loader_explicit_path_overrides_configured_path(data_dir: Path):
    configured_dir = data_dir / "configured"
    explicit_dir = data_dir / "explicit"
    configured_dir.mkdir()
    explicit_dir.mkdir()
    (configured_dir / "wrong.csv").write_text("id\n1\n", encoding="utf-8")
    (explicit_dir / "right.csv").write_text("id\n2\n", encoding="utf-8")

    tables = _pandas_tables(
        DataLoader(paths={"raw_data": configured_dir}).load_raw_data(explicit_dir),
    )

    assert sorted(tables) == ["right"]
    assert tables["right"].to_dict("records") == [{"id": 2}]


def test_data_loader_rejects_missing_default_path():
    with pytest.raises(DataLoadingError, match="paths.raw_data"):
        DataLoader().load_raw_data()
