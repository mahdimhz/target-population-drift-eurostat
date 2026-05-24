from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]


def load_eurostat_panel(path: str | Path | None = None) -> pd.DataFrame:
    """Load the processed primary Eurostat country-year panel."""
    panel_path = Path(path) if path is not None else ROOT / "data" / "processed" / "panel_features_v2-3.csv"
    return pd.read_csv(panel_path)
