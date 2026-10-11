"""Markov forecasting placeholders."""

from typing import Any


def build_transition_matrix(records: Any) -> Any:
    """Build a transition matrix from state-level records."""
    raise NotImplementedError("Markov transition estimation is not implemented yet.")


def forecast_markov(transition_matrix: Any, initial_state: Any, horizon: int) -> Any:
    """Generate a Markov forecast from a transition matrix."""
    raise NotImplementedError("Markov forecasting is not implemented yet.")
