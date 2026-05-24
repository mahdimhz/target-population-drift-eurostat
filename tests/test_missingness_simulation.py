from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def test_simulation_outputs_exist_and_are_nonempty() -> None:
    required = [
        ROOT / "outputs" / "simulation_results.csv",
        ROOT / "outputs" / "simulation_reference_estimand.csv",
        ROOT / "outputs" / "simulation_bias_summary.csv",
        ROOT / "outputs" / "simulation_sign_reversal.csv",
        ROOT / "outputs" / "simulation_ci_coverage.csv",
        ROOT / "outputs" / "simulation_wrong_conclusion.csv",
        ROOT / "tables" / "simulation_main_summary.tex",
        ROOT / "figures" / "simulation_bias_by_mechanism.pdf",
        ROOT / "figures" / "simulation_target_distance_vs_error.pdf",
    ]
    missing = [path.as_posix() for path in required if not path.exists() or path.stat().st_size == 0]
    assert not missing


def test_simulation_reference_estimand_uses_complete_primary_panel() -> None:
    reference = pd.read_csv(ROOT / "outputs" / "simulation_reference_estimand.csv")
    assert int(reference.loc[0, "reference_rows"]) == 282
    assert int(reference.loc[0, "reference_countries"]) == 30
    assert int(reference.loc[0, "reference_years"]) == 10


def test_simulation_contains_required_mechanisms_and_estimators() -> None:
    results = pd.read_csv(ROOT / "outputs" / "simulation_results.csv")
    mechanisms = {
        "mcar",
        "early_year",
        "country_group",
        "covariate_block",
        "mnar_high_poverty_unmet",
        "eurostat_realistic",
    }
    estimators = {
        "complete_case_fe",
        "population_weighted_fe",
        "ipw_fe",
        "pmm_mi_fe",
        "mnar_shift_mi_fe",
    }
    assert mechanisms.issubset(set(results["mechanism"]))
    assert estimators.issubset(set(results["estimator"]))


def test_simulation_reproducible_under_seed_42() -> None:
    first = pd.read_csv(ROOT / "outputs" / "smoke_simulation_results.csv")
    second = pd.read_csv(ROOT / "outputs" / "smoke_repeat_simulation_results.csv")
    cols = ["mechanism", "replicate", "estimator", "status", "coef", "rows", "target_distance"]
    pd.testing.assert_frame_equal(first[cols], second[cols], check_exact=False, rtol=1e-10, atol=1e-10)
