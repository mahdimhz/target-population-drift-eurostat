from __future__ import annotations

from pathlib import Path

import pandas as pd

from .coverage import coverage_audit


def generate_report(df: pd.DataFrame, variables: list[str], output_path: str | Path) -> Path:
    """Write a compact CSV coverage report for a target-population audit."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    coverage_audit(df, variables).to_csv(path, index=False)
    return path
