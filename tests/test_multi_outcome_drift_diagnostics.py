from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def test_multi_outcome_attrition_preserves_primary_608_to_282_drift() -> None:
    matrix = pd.read_csv(ROOT / "outputs" / "multi_outcome_attrition_matrix.csv")
    primary = matrix[matrix["indicator_id"].eq("medical_population_combined")].iloc[0]
    assert int(primary["outcome_observed_rows"]) == 608
    assert int(primary["baseline_complete_case_rows"]) == 282


def test_multi_outcome_drift_outputs_exist() -> None:
    required = [
        ROOT / "outputs" / "multi_outcome_attrition_matrix.csv",
        ROOT / "outputs" / "multi_outcome_attrition_long.csv",
        ROOT / "outputs" / "multi_outcome_country_group_retention.csv",
        ROOT / "outputs" / "multi_outcome_included_excluded_smd.csv",
        ROOT / "tables" / "multi_outcome_attrition_matrix.tex",
        ROOT / "tables" / "multi_outcome_primary_attrition_waterfall.tex",
        ROOT / "tables" / "multi_outcome_included_excluded_smd_top.tex",
        ROOT / "figures" / "multi_outcome_retention_heatmap.pdf",
        ROOT / "figures" / "multi_outcome_primary_attrition_waterfall.pdf",
    ]
    missing = [path.as_posix() for path in required if not path.exists() or path.stat().st_size == 0]
    assert not missing


def test_multi_outcome_attrition_steps_are_monotone_by_indicator() -> None:
    long = pd.read_csv(ROOT / "outputs" / "multi_outcome_attrition_long.csv")
    for _, group in long.groupby("indicator_id"):
        rows = group["rows"].tolist()
        assert rows == sorted(rows, reverse=True)


def test_multi_outcome_smd_has_included_and_excluded_counts() -> None:
    smd = pd.read_csv(ROOT / "outputs" / "multi_outcome_included_excluded_smd.csv")
    primary_outcome = smd[
        smd["indicator_id"].eq("medical_population_combined")
        & smd["variable"].eq("outcome_value_pc")
    ].iloc[0]
    assert int(primary_outcome["complete_case_rows"]) == 282
    assert int(primary_outcome["excluded_rows"]) == 326
