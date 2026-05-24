from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def test_outcome_estimand_matrix_contains_all_core_estimands() -> None:
    matrix = pd.read_csv(ROOT / "outputs" / "outcome_estimand_coefficient_matrix.csv")
    expected = {
        "Unweighted complete-case FE",
        "Population-weighted complete-case FE",
        "Balanced-outcome FE",
        "IPW complete-case FE",
        "MAR MI full-target FE",
    }
    for _, group in matrix.groupby("indicator_id"):
        assert expected == set(group["estimand"])


def test_primary_outcome_matrix_preserves_complete_case_count() -> None:
    matrix = pd.read_csv(ROOT / "outputs" / "outcome_estimand_coefficient_matrix.csv")
    primary = matrix[
        matrix["indicator_id"].eq("medical_population_combined")
        & matrix["estimand"].eq("Unweighted complete-case FE")
    ].iloc[0]
    assert int(primary["rows"]) == 282
    assert int(primary["countries"]) == 30
    assert primary["status"] == "estimated"


def test_need_denominator_complete_case_is_labelled_infeasible() -> None:
    matrix = pd.read_csv(ROOT / "outputs" / "outcome_estimand_coefficient_matrix.csv")
    need_cc = matrix[
        matrix["indicator_id"].eq("medical_need_combined")
        & matrix["estimand"].eq("Unweighted complete-case FE")
    ].iloc[0]
    assert str(need_cc["status"]).startswith("infeasible:")


def test_failure_classification_is_deterministic_and_present() -> None:
    classifications = pd.read_csv(ROOT / "outputs" / "outcome_failure_classification.csv")
    allowed = {
        "stable",
        "target-dependent",
        "denominator-dependent",
        "missingness-dependent",
        "imputation-model-dependent",
        "non-identifiable",
    }
    assert set(classifications["classification"]).issubset(allowed)
    assert classifications["indicator_id"].is_unique


def test_outcome_estimand_outputs_exist() -> None:
    required = [
        ROOT / "outputs" / "outcome_estimand_coefficient_matrix.csv",
        ROOT / "outputs" / "outcome_failure_classification.csv",
        ROOT / "tables" / "outcome_estimand_coefficient_matrix.tex",
        ROOT / "tables" / "outcome_failure_classification.tex",
        ROOT / "figures" / "outcome_estimand_coefficient_stability.pdf",
    ]
    missing = [path.as_posix() for path in required if not path.exists() or path.stat().st_size == 0]
    assert not missing
