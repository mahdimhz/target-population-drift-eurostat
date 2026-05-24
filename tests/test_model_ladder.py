from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import run_full_thesis_analysis as full


def test_eu27_filter_has_27_members() -> None:
    assert len(full.EU27) == 27
    assert {"AT", "DE", "FR", "IT", "PL"}.issubset(full.EU27)
    assert "NO" not in full.EU27


def test_model_ladder_marks_small_samples_infeasible() -> None:
    df = pd.DataFrame(
        {
            "geo": ["A", "A", "B", "B"],
            "year": [2020, 2021, 2020, 2021],
            "unmet_need_pc": [1.0, 1.1, 2.0, 2.1],
            "poverty_or_social_exclusion_pc": [20.0, 21.0, 22.0, 23.0],
        }
    )

    row = full.model_ladder_row(
        "A",
        "Poverty only",
        df,
        ["poverty_or_social_exclusion_pc"],
        "test infeasible row",
    )

    assert row["status"].startswith("infeasible:")
    assert row["rows"] == 4


def test_model_sample_with_covars_requires_weights_when_requested() -> None:
    df = pd.DataFrame(
        {
            "geo": ["A", "A", "B"],
            "year": [2020, 2021, 2020],
            "unmet_need_pc": [1.0, 1.2, 2.0],
            "poverty_or_social_exclusion_pc": [20.0, 21.0, 22.0],
            "population_weight_year_norm": [0.4, None, 0.6],
        }
    )

    unweighted = full.model_sample_with_covars(df, ["poverty_or_social_exclusion_pc"], require_weight=False)
    weighted = full.model_sample_with_covars(df, ["poverty_or_social_exclusion_pc"], require_weight=True)

    assert len(unweighted) == 3
    assert len(weighted) == 2
