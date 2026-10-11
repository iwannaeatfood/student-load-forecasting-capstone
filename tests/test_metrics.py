"""Smoke tests for metric placeholders."""

from upp_forecast.evaluation.metrics import calculate_metrics


def test_calculate_metrics_returns_empty_placeholder():
    assert calculate_metrics(actual=[], predicted=[]) == {}
