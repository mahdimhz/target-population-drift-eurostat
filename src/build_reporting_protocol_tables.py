from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = ROOT / "outputs"
TABLES = ROOT / "tables"


def _latex_escape(value: object) -> str:
    text = "" if pd.isna(value) else str(value)
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def write_tabular(df: pd.DataFrame, columns: list[str], headers: list[str], path: Path, colspec: str) -> None:
    lines = [rf"\begin{{tabular}}{{{colspec}}}", r"\toprule", " & ".join(headers) + r" \\", r"\midrule"]
    for _, row in df[columns].iterrows():
        lines.append(" & ".join(_latex_escape(row[column]) for column in columns) + r" \\")
    lines.extend([r"\bottomrule", r"\end{tabular}", ""])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def write_tabularx(df: pd.DataFrame, columns: list[str], headers: list[str], path: Path, colspec: str) -> None:
    lines = [
        r"\begingroup",
        r"\scriptsize",
        r"\setlength{\tabcolsep}{3pt}",
        rf"\begin{{tabularx}}{{\linewidth}}{{{colspec}}}",
        r"\toprule",
        " & ".join(headers) + r" \\",
        r"\midrule",
    ]
    for _, row in df[columns].iterrows():
        lines.append(" & ".join(_latex_escape(row[column]) for column in columns) + r" \\")
    lines.extend([r"\bottomrule", r"\end{tabularx}", r"\endgroup", ""])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _format_float(value: object, digits: int = 3) -> str:
    return "NA" if pd.isna(value) else f"{float(value):.{digits}f}"


def _evidence_basis(row: pd.Series) -> str:
    if row["final_label"] == "non-identifiable" and pd.isna(row["CSI"]):
        return "not computed; fewer than 2 feasible estimand families"
    return (
        f"CSI={float(row['CSI']):.3f}; "
        f"theta IQR={float(row['theta_IQR']):.3f}; "
        f"dir. agreement={float(row['directional_agreement']):.3f}; "
        f"{row['rule_reason_short']}"
    )


def build_checklist() -> pd.DataFrame:
    rows = [
        {
            "item": "Target definition",
            "required_report": "Unit, indicator, denominator, country universe, time window, and weighting rule.",
            "thesis_output": "Public-data estimand registry and country-universe table.",
        },
        {
            "item": "Monitoring benchmark",
            "required_report": "Unweighted and population-weighted trends by indicator and universe before modelling.",
            "thesis_output": "Multi-outcome monitoring benchmark and coverage tables.",
        },
        {
            "item": "Coverage drift",
            "required_report": "Rows, countries, and years retained after each covariate or weight requirement.",
            "thesis_output": "Attrition matrix, retention heatmap, and primary waterfall.",
        },
        {
            "item": "Selection distortion",
            "required_report": "Included-versus-excluded differences in outcome, covariates, country groups, and time periods.",
            "thesis_output": "SMD tables, selection model, and inclusion-probability figure.",
        },
        {
            "item": "Estimand stability",
            "required_report": "Coefficient across complete-case, weighted, balanced, IPW, MAR MI, and MNAR sensitivity targets.",
            "thesis_output": "Outcome-by-estimand matrix and main sensitivity ladder.",
        },
        {
            "item": "Simulation stress test",
            "required_report": "Bias, sign reversal, interval coverage, and wrong-conclusion rates under controlled missingness.",
            "thesis_output": "Semi-synthetic missingness simulation.",
        },
        {
            "item": "Final label",
            "required_report": "Stable, target-dependent, denominator-dependent, missingness-dependent, imputation-model-dependent, or non-identifiable.",
            "thesis_output": "Final classification table.",
        },
    ]
    out = pd.DataFrame(rows)
    out.to_csv(OUTPUTS / "target_population_drift_reporting_checklist.csv", index=False)
    write_tabular(
        out,
        ["item", "required_report", "thesis_output"],
        ["Protocol item", "Required report", "Thesis output"],
        TABLES / "target_population_drift_reporting_checklist.tex",
        r"p{0.18\linewidth}p{0.39\linewidth}p{0.33\linewidth}",
    )
    return out


def build_failure_modes() -> pd.DataFrame:
    rows = [
        {
            "failure_mode": "Stable",
            "definition": "Core estimand families agree in direction and IQR-scale magnitude.",
            "interpretation": "A cautious aggregate coefficient interpretation is supportable.",
        },
        {
            "failure_mode": "Target-dependent",
            "definition": "Observed-data estimates change materially under weighting, balanced coverage, or country-universe restriction.",
            "interpretation": "The coefficient is a property of a defined target, not of Europe in general.",
        },
        {
            "failure_mode": "Denominator-dependent",
            "definition": "Population-denominator and need-denominator indicators support different interpretations.",
            "interpretation": "The monitoring question must be restated before comparing coefficients.",
        },
        {
            "failure_mode": "Missingness-dependent",
            "definition": "Complete-case, IPW, MAR MI, or MNAR targets materially disagree.",
            "interpretation": "Covariate coverage and missing-data assumptions carry the empirical conclusion.",
        },
        {
            "failure_mode": "Imputation-model-dependent",
            "definition": "MI variants disagree strongly with each other.",
            "interpretation": "The imputed estimate is a model-dependent sensitivity result.",
        },
        {
            "failure_mode": "Non-identifiable",
            "definition": "Too few reliable estimand families are feasible, or estimands conflict too strongly.",
            "interpretation": "The public aggregate data do not support a coefficient interpretation.",
        },
    ]
    out = pd.DataFrame(rows)
    out.to_csv(OUTPUTS / "failure_modes_public_aggregate_panels.csv", index=False)
    write_tabular(
        out,
        ["failure_mode", "definition", "interpretation"],
        ["Mode", "Definition", "Interpretation"],
        TABLES / "failure_modes_public_aggregate_panels.tex",
        r"p{0.19\linewidth}p{0.39\linewidth}p{0.32\linewidth}",
    )
    return out


def build_final_classification() -> pd.DataFrame:
    stability = pd.read_csv(OUTPUTS / "drift_stability_summary.csv")
    classifications = stability.rename(
        columns={
            "outcome": "finding",
            "feasible_estimand_families": "estimand_families",
        }
    ).copy()
    classifications["evidence_basis"] = classifications.apply(_evidence_basis, axis=1)
    classifications["interpretation"] = classifications["final_label"].map(
        {
            "stable": "Observed estimands are sufficiently aligned for cautious aggregate interpretation.",
            "target-dependent": "Interpretation changes with target population, weighting, or missing-data assumptions.",
            "denominator-dependent": "Population and need denominator versions must not be collapsed.",
            "missingness-dependent": "Covariate missingness drives the substantive interpretation.",
            "imputation-model-dependent": "Imputation assumptions drive the substantive interpretation.",
            "non-identifiable": "Available public aggregate data do not support a coefficient interpretation.",
        }
    )
    out = classifications[
        [
            "finding",
            "denominator",
            "estimand_families",
            "theta_IQR",
            "directional_agreement",
            "CSI",
            "final_label",
            "evidence_basis",
            "interpretation",
        ]
    ].copy()
    out.to_csv(OUTPUTS / "final_classification_eurostat_findings.csv", index=False)
    display = out.copy()
    for column in ["theta_IQR", "directional_agreement", "CSI"]:
        display[column] = display[column].map(_format_float)
    write_tabularx(
        display,
        ["finding", "denominator", "estimand_families", "theta_IQR", "directional_agreement", "CSI", "final_label", "evidence_basis"],
        ["Finding", "Denom.", "Families", "$\\theta$ IQR", "Dir. agree", "CSI", "Final label", "Evidence basis"],
        TABLES / "final_classification_eurostat_findings.tex",
        r"@{}p{0.14\linewidth}p{0.08\linewidth}rrrrp{0.16\linewidth}Y@{}",
    )
    return out


def main() -> None:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    TABLES.mkdir(parents=True, exist_ok=True)
    build_checklist()
    build_failure_modes()
    final = build_final_classification()
    print(f"saved {TABLES / 'target_population_drift_reporting_checklist.tex'}")
    print(f"saved {TABLES / 'failure_modes_public_aggregate_panels.tex'}")
    print(f"saved {TABLES / 'final_classification_eurostat_findings.tex'}")
    print(f"classified findings: {len(final)}")


if __name__ == "__main__":
    main()
