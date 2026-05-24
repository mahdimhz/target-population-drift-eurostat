from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def test_reporting_protocol_outputs_exist() -> None:
    required = [
        ROOT / "outputs" / "target_population_drift_reporting_checklist.csv",
        ROOT / "outputs" / "failure_modes_public_aggregate_panels.csv",
        ROOT / "outputs" / "final_classification_eurostat_findings.csv",
        ROOT / "tables" / "target_population_drift_reporting_checklist.tex",
        ROOT / "tables" / "failure_modes_public_aggregate_panels.tex",
        ROOT / "tables" / "final_classification_eurostat_findings.tex",
    ]
    missing = [path.as_posix() for path in required if not path.exists() or path.stat().st_size == 0]
    assert not missing


def test_failure_modes_include_required_labels() -> None:
    modes = pd.read_csv(ROOT / "outputs" / "failure_modes_public_aggregate_panels.csv")
    required = {
        "Stable",
        "Target-dependent",
        "Denominator-dependent",
        "Missingness-dependent",
        "Imputation-model-dependent",
        "Non-identifiable",
    }
    assert required.issubset(set(modes["failure_mode"]))


def test_final_classification_uses_generated_outcome_labels() -> None:
    source = pd.read_csv(ROOT / "outputs" / "outcome_failure_classification.csv")
    final = pd.read_csv(ROOT / "outputs" / "final_classification_eurostat_findings.csv")
    assert len(source) == len(final)
    assert set(source["classification"]) == set(final["final_label"])
