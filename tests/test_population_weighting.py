from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from run_missingness_robustness import POP_WEIGHT, balanced_outcome_countries, ensure_population_weights


def test_year_normalized_population_weights_sum_to_one() -> None:
    df = pd.DataFrame(
        {
            "geo": ["A", "B", "A", "B"],
            "year": [2020, 2020, 2021, 2021],
            "unmet_need_pc": [1.0, 2.0, 1.5, 2.5],
            "population_total": [10.0, 30.0, 20.0, 20.0],
        }
    )

    out = ensure_population_weights(df)

    sums = out.groupby("year")[POP_WEIGHT].sum()
    assert all(abs(value - 1.0) < 1e-12 for value in sums)
    assert out.loc[(out["geo"] == "B") & (out["year"] == 2020), POP_WEIGHT].iloc[0] == 0.75


def test_balanced_outcome_requires_all_years_and_valid_weights() -> None:
    df = pd.DataFrame(
        {
            "geo": ["A", "A", "B"],
            "year": [2020, 2021, 2020],
            "unmet_need_pc": [1.0, 1.2, 2.0],
            POP_WEIGHT: [0.4, 0.5, 0.6],
        }
    )

    assert balanced_outcome_countries(df) == ["A"]
