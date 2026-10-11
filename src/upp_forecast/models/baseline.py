"""Baseline model placeholders."""

from typing import Any


def fit_baseline_model(training_data: Any) -> Any:
    """Fit a baseline forecasting model."""
    raise NotImplementedError("Baseline model fitting is not implemented yet.")


def predict_baseline(model: Any, horizon: int) -> Any:
    """Generate baseline forecasts for a forecast horizon."""
    raise NotImplementedError("Baseline prediction is not implemented yet.")
