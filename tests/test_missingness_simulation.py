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
        ROOT / "outputs" / "simulation_validation_summary.csv",
        ROOT / "outputs" / "simulation_runtime_notes.txt",
        ROOT / "tables" / "simulation_main_summary.tex",
        ROOT / "tables" / "simulation_validation_summary.tex",
        ROOT / "figures" / "simulation_bias_by_mechanism.pdf",
        ROOT / "figures" / "simulation_target_distance_vs_error.pdf",
        ROOT / "figures" / "simulation_tdi_vs_error.pdf",
        ROOT / "figures" / "simulation_wrong_conclusion_by_tdi.pdf",
        ROOT / "figures" / "simulation_tdi_validation_combined.pdf",
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
        "mar_observed",
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
    cols = ["mechanism", "replicate", "estimator", "status", "coef", "rows", "target_distance", "TDI"]
    pd.testing.assert_frame_equal(first[cols], second[cols], check_exact=False, rtol=1e-10, atol=1e-10)


def test_simulation_reports_drift_validation_metrics() -> None:
    results = pd.read_csv(ROOT / "outputs" / "simulation_results.csv")
    required = {
        "absolute_coefficient_error",
        "Delta_row",
        "Delta_country",
        "Delta_year",
        "Delta_weight",
        "Delta_balance",
        "TDI",
        "wrong_conclusion",
    }
    assert required.issubset(results.columns)
    estimated = results[results["status"].eq("estimated")]
    assert estimated["TDI"].notna().all()
    assert estimated["TDI"].ge(0).all()


def test_simulation_validation_summary_has_required_schema() -> None:
    summary = pd.read_csv(ROOT / "outputs" / "simulation_validation_summary.csv")
    required = [
        "mechanism",
        "estimator",
        "mean_TDI",
        "mean_bias",
        "median_absolute_error",
        "sign_reversal_rate",
        "ci_coverage_rate",
        "wrong_conclusion_rate",
        "number_of_successful_replicates",
        "number_of_failed_replicates",
    ]
    assert list(summary.columns) == required
    assert summary["number_of_successful_replicates"].ge(0).all()
    assert summary["number_of_failed_replicates"].ge(0).all()


def test_simulation_main_table_uses_readable_labels() -> None:
    table = (ROOT / "tables" / "simulation_main_summary.tex").read_text(encoding="utf-8")
    assert "MNAR high-pov./unmet" in table
    assert "CC FE" in table
    assert "PMM MI" in table
    assert "MNAR-shift MI" in table
    assert "mnar\\_high\\_poverty\\_unmet" not in table
    assert "complete\\_case\\_fe" not in table
    assert "pmm\\_mi\\_fe" not in table
    assert "mnar\\_shift\\_mi\\_fe" not in table
