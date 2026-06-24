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
    source = pd.read_csv(ROOT / "outputs" / "drift_stability_summary.csv")
    final = pd.read_csv(ROOT / "outputs" / "final_classification_eurostat_findings.csv")
    assert len(source) == len(final)
    assert set(source["final_label"]) == set(final["final_label"])


def test_final_classification_reports_stability_metrics_not_only_counts() -> None:
    final = pd.read_csv(ROOT / "outputs" / "final_classification_eurostat_findings.csv")
    required = {
        "finding",
        "denominator",
        "estimand_families",
        "theta_IQR",
        "directional_agreement",
        "CSI",
        "final_label",
        "secondary_flag",
        "secondary_evidence",
        "evidence_basis",
    }
    assert required.issubset(final.columns)
    assert final["CSI"].dropna().between(0, 1).all()
    assert final["directional_agreement"].dropna().between(0, 1).all()
    identifiable = final[final["final_label"].ne("non-identifiable")]
    non_identifiable = final[final["final_label"].eq("non-identifiable")]
    assert identifiable["evidence_basis"].str.contains("CSI=").all()
    assert identifiable["evidence_basis"].str.contains("theta IQR=").all()
    assert non_identifiable["CSI"].isna().all()
    assert non_identifiable["theta_IQR"].isna().all()
    assert non_identifiable["directional_agreement"].isna().all()
    assert non_identifiable["evidence_basis"].eq("not computed; fewer than 2 feasible estimand families").all()
    assert not non_identifiable["evidence_basis"].str.contains("CSI=1.000", regex=False).any()


def test_final_classification_primary_labels_are_not_replaced_by_secondary_flags() -> None:
    final = pd.read_csv(ROOT / "outputs" / "final_classification_eurostat_findings.csv")
    expected = {
        "Dental population": "missingness-dependent",
        "Medical cost": "missingness-dependent",
        "Medical distance": "missingness-dependent",
        "Medical population": "missingness-dependent",
        "Medical waiting": "target-dependent",
        "Dental need": "non-identifiable",
        "Medical need": "non-identifiable",
    }
    observed = dict(zip(final["finding"], final["final_label"]))
    assert observed == expected
    assert set(final["secondary_flag"]).issubset({"none", "MI-variant disagreement"})


def test_mi_variant_disagreement_is_secondary_for_primary_medical_outcome() -> None:
    final = pd.read_csv(ROOT / "outputs" / "final_classification_eurostat_findings.csv")
    flagged = final[final["secondary_flag"].eq("MI-variant disagreement")]
    assert flagged["finding"].tolist() == ["Medical population"]
    row = flagged.iloc[0]
    assert row["final_label"] == "missingness-dependent"
    assert "MI variant coefficient signs differ" in row["secondary_evidence"]
    assert "MI variant zero-exclusion differs" in row["secondary_evidence"]
    assert "MI variant coefficient range=" in row["secondary_evidence"]


def test_mi_variant_secondary_flags_output_exists() -> None:
    flags = pd.read_csv(ROOT / "outputs" / "mi_variant_secondary_flags.csv")
    assert set(flags.columns) == {"finding", "secondary_flag", "secondary_evidence"}
    assert flags["secondary_flag"].eq("MI-variant disagreement").all()


def test_final_classification_table_and_text_do_not_contradict_secondary_flags() -> None:
    table = (ROOT / "tables" / "final_classification_eurostat_findings.tex").read_text(encoding="utf-8")
    chapter = (ROOT / "chapters" / "discussion_conclusion.tex").read_text(encoding="utf-8")
    table_shows_secondary = "Secondary flag" in table
    text_points_to_output = "outputs/mi\\_variant\\_secondary\\_flags.csv" in chapter
    assert table_shows_secondary or text_points_to_output


def test_medical_waiting_evidence_basis_is_not_duplicated() -> None:
    table = (ROOT / "tables" / "final_classification_eurostat_findings.tex").read_text(encoding="utf-8")
    medical_waiting_line = next(line for line in table.splitlines() if line.startswith("Medical waiting"))
    assert medical_waiting_line.count("CSI=0.590") == 1
    assert "theta IQR=0.041" in medical_waiting_line
    assert "dir. agreement=1.000" in medical_waiting_line
