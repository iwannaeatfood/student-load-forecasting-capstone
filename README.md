# UPP Forecasting Prototype

Team capstone project (university course). I served as Scrum Master and also contributed to the data preprocessing pipeline (`transform_load`, `save_processed_data`) and the client-facing output schema.

Original team repository (private): https://github.com/unsw-cse-comp99-3900/capstone-project-9900-26t2-h11c-bread — visible to team members and course staff only; this folder is a curated, code-only excerpt for public sharing. Large data files, generated outputs, and formal team-submitted reports are not included here.

Placeholder project skeleton for a UPP forecasting prototype.

The repository is organized for iterative development of data loading,
preprocessing, cohort construction, Markov-style forecasting, evaluation,
explainability, and reporting workflows. This initial scaffold intentionally
does not include real data or production model logic.

## Structure

- `configs/`: default and experiment-specific YAML configuration.
- `data/raw/`: raw input data placeholder. Do not commit real source data.
- `data/interim/`: intermediate tables produced during preprocessing.
- `data/processed/`: modeling-ready tables.
- `notebooks/`: exploration and error-analysis notebooks.
- `src/upp_forecast/`: importable Python package.
- `tests/`: smoke tests for imports and placeholder behavior.
- `outputs/`: generated forecasts, metrics, and figures.
- `docs/`: methodology, assumptions, data dictionary, and UML diagrams.

## Setup

This project targets Python 3.13, Java 21, PySpark 4, and Pandas 3.

```powershell
uv sync --group dev
```

## Validation

```powershell
uv run pytest
```

## Docker

Build the image:

```powershell
docker compose build
```

Open an interactive shell:

```powershell
docker compose run --rm app
```

Run tests inside the container:

```powershell
docker compose run --rm app uv run pytest
```

Check PySpark inside the container:

```powershell
docker compose run --rm app uv run python -c "import pyspark; print(pyspark.__version__)"
```

The Docker image excludes local data and generated outputs. `compose.yaml`
mounts `./data` and `./outputs` at runtime so real data stays on the host
machine.

## Development Notes

The current Python modules are placeholders. Functions either raise
`NotImplementedError` or return an empty placeholder structure where that is
less misleading for downstream smoke tests.
