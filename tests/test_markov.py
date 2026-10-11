"""Smoke tests for Markov model placeholders."""

import pytest

from upp_forecast.models.markov import build_transition_matrix, forecast_markov


def test_build_transition_matrix_placeholder_is_explicit():
    with pytest.raises(NotImplementedError):
        build_transition_matrix([])


def test_forecast_markov_placeholder_is_explicit():
    with pytest.raises(NotImplementedError):
        forecast_markov(transition_matrix={}, initial_state={}, horizon=1)
