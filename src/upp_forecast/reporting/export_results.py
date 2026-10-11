"""Result export placeholders."""

from pathlib import Path
from typing import Any


def export_results(results: Any, output_path: str | Path) -> None:
    """Export forecast results to a configured output path."""
    raise NotImplementedError("Result export is not implemented yet.")
