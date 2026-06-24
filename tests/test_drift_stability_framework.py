from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from eurodrift.drift import (
    conclusion_stability_index,
    directional_agreement,
    jensen_shannon_divergence,
    standardized_coefficient,
    support_loss,
    target_population_drift_index,
)


def test_drift_metric_helpers_are_bounded_and_reproducible() -> None:
    assert support_loss(75, 100) == 0.25
    jsd = jensen_shannon_divergence(
        pd.Series([0.5, 0.5, 0.0]),
        pd.Series([0.0, 0.5, 0.5]),
    )
    assert 0 <= jsd <= 1
    tdi = target_population_drift_index(
        {
            "Delta_row": 0.25,
            "Delta_country": 0.10,
            "Delta_year": 0.20,
            "Delta_weight": 0.30,
            "Delta_balance": 0.15,
        }
    )
    assert abs(tdi - 0.20) < 1e-12
    assert standardized_coefficient(0.2, 10.0, 5.0) == 0.4


def test_conclusion_stability_helpers_use_declared_tolerance() -> None:
    theta_iqr, csi = conclusion_stability_index([0.10, 0.12, 0.14, 0.16], delta=0.10)
    assert theta_iqr > 0
    assert 0 <= csi <= 1
    assert directional_agreement([0.10, 0.12, -0.01], reference_sign=1) == 2 / 3


def test_drift_stability_builder_outputs_expected_files() -> None:
    subprocess.run([sys.executable, "src/build_drift_stability_framework.py"], cwd=ROOT, check=True)
    required = [
        ROOT / "outputs" / "formal_estimand_components.csv",
        ROOT / "outputs" / "target_drift_components.csv",
        ROOT / "outputs" / "conclusion_stability.csv",
        ROOT / "outputs" / "drift_stability_theta.csv",
        ROOT / "outputs" / "drift_stability_summary.csv",
        ROOT / "tables" / "formal_estimand_components.tex",
        ROOT / "tables" / "target_drift_components.tex",
        ROOT / "tables" / "conclusion_stability.tex",
        ROOT / "tables" / "drift_stability_summary.tex",
        ROOT / "figures" / "drift_stability_map.pdf",
        ROOT / "figures" / "target_drift_components_heatmap.pdf",
        ROOT / "figures" / "conclusion_stability_by_outcome.pdf",
    ]
    missing = [path.as_posix() for path in required if not path.exists() or path.stat().st_size == 0]
    assert not missing


def test_primary_drift_metrics_preserve_reference_and_selected_counts() -> None:
    components = pd.read_csv(ROOT / "outputs" / "formal_estimand_components.csv")
    drift = pd.read_csv(ROOT / "outputs" / "target_drift_components.csv")
    theta = pd.read_csv(ROOT / "outputs" / "drift_stability_theta.csv")
    stability = pd.read_csv(ROOT / "outputs" / "conclusion_stability.csv")

    primary_cc = components[
        components["estimand_id"].eq("medical_population_combined__unweighted_complete_case_fe")
    ].iloc[0]
    assert int(primary_cc["rows"]) == 282
    assert int(primary_cc["countries"]) == 30

    primary_mi = drift[drift["estimand_id"].eq("medical_population_combined__mar_mi_full_target_fe")].iloc[0]
    assert int(primary_mi["rows"]) == 608
    assert primary_mi["TDI"] == 0

    assert theta["theta"].notna().any()
    assert stability["CSI"].dropna().between(0, 1).all()
    assert "missingness-dependent" in set(stability["final_label"])


def test_drift_stability_summary_reports_framework_metrics() -> None:
    summary = pd.read_csv(ROOT / "outputs" / "drift_stability_summary.csv")
    required = {
        "outcome",
        "denominator",
        "feasible_estimand_families",
        "median_theta",
        "theta_IQR",
        "directional_agreement",
        "CSI",
        "median_TDI",
        "max_TDI",
        "final_label",
        "rule_reason",
    }
    assert required.issubset(summary.columns)
    assert not summary.empty
    assert summary["CSI"].dropna().between(0, 1).all()
    assert summary["median_TDI"].dropna().between(0, 1).all()
    assert summary["rule_reason"].fillna("").str.len().gt(0).all()


def test_non_identifiable_outcomes_do_not_report_stability_metrics() -> None:
    summary = pd.read_csv(ROOT / "outputs" / "drift_stability_summary.csv")
    non_identifiable = summary[summary["final_label"].eq("non-identifiable")]
    assert not non_identifiable.empty
    assert (non_identifiable["feasible_estimand_families"] < 2).all()
    assert non_identifiable["theta_IQR"].isna().all()
    assert non_identifiable["directional_agreement"].isna().all()
    assert non_identifiable["CSI"].isna().all()
    assert set(non_identifiable["rule_reason"]) == {"fewer than 2 feasible estimand families"}
