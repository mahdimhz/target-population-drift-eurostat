from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from build_multi_outcome_indicator_registry import INDICATOR_SPECS


def test_indicator_registry_contains_requested_indicators_or_infeasibility() -> None:
    registry = pd.read_csv(ROOT / "outputs" / "multi_outcome_indicator_registry.csv")
    expected = {spec.indicator_id for spec in INDICATOR_SPECS if spec.required}
    observed = set(registry["indicator_id"])
    assert expected.issubset(observed)

    required_rows = registry[registry["indicator_id"].isin(expected)]
    invalid = required_rows[
        (required_rows["feasibility_status"] != "feasible")
        & (required_rows["infeasibility_reason"].fillna("").str.len() == 0)
    ]
    assert invalid.empty


def test_reason_codes_are_programmatically_verified_for_feasible_indicators() -> None:
    validation = pd.read_csv(ROOT / "outputs" / "eurostat_reason_code_validation.csv")
    feasible = validation[validation["feasibility_status"] == "feasible"]
    assert not feasible.empty
    assert feasible["reason_verified"].all()
    assert (feasible["observed_rows"] > 0).all()


def test_multi_outcome_rows_match_registry_counts() -> None:
    registry = pd.read_csv(ROOT / "outputs" / "multi_outcome_indicator_registry.csv")
    panel = pd.read_csv(ROOT / "data" / "processed" / "multi_outcome_unmet_care.csv")
    assert {"indicator_id", "geo", "year", "value_pc"}.issubset(panel.columns)

    counts = panel.groupby("indicator_id").size().rename("panel_rows").reset_index()
    merged = registry.merge(counts, on="indicator_id", how="left")
    feasible = merged[merged["feasibility_status"] == "feasible"]
    assert (feasible["observed_rows"] == feasible["panel_rows"]).all()
