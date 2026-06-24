from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.linear_model import LogisticRegression

from eurodrift.drift import (
    DriftWeights,
    average_absolute_smd,
    conclusion_stability_index,
    directional_agreement,
    jensen_shannon_divergence,
    standardized_coefficient,
    support_loss,
    target_population_drift_index,
)
from eurodrift.targets import country_group


ROOT = Path(__file__).resolve().parents[1]
DATA_PROCESSED = ROOT / "data" / "processed"
OUTPUTS = ROOT / "outputs"
FIGURES = ROOT / "figures"
TABLES = ROOT / "tables"

OUTCOME = "outcome_value_pc"
TERM = "poverty_or_social_exclusion_pc"
POP_WEIGHT = "population_weight_year_norm"
BASELINE_COVARS = [
    "log_gdp_per_capita",
    "unemployment_rate_pc",
    TERM,
    "government_health_expenditure_gdp_pc",
    "compulsory_health_financing_gdp_pc",
]
DRIFT_BALANCE_COVARS = BASELINE_COVARS
CSI_DELTA = 0.10
CSI_SENSITIVITY_DELTAS = [0.05, 0.10, 0.15, 0.20]
TDI_WEIGHT_SCHEMES = {
    "equal": DriftWeights(),
    "support_focused": DriftWeights(row=2.0, country=2.0, year=2.0, weight=1.0, balance=1.0),
    "balance_focused": DriftWeights(row=1.0, country=1.0, year=1.0, weight=1.0, balance=3.0),
}


ESTIMAND_METADATA = {
    "Unweighted complete-case FE": {
        "row_set": "Outcome and baseline covariates observed",
        "weighting_rule": "Equal country-year weight",
        "missing_data_assumption": "Complete-case selection",
        "model": "Country and year fixed effects",
        "interpretation": "Selected analytical panel",
        "family": "complete-case",
    },
    "Population-weighted complete-case FE": {
        "row_set": "Outcome and baseline covariates observed",
        "weighting_rule": "Year-normalized country population",
        "missing_data_assumption": "Complete-case selection",
        "model": "Population-weighted country and year fixed effects",
        "interpretation": "Resident-weighted selected panel",
        "family": "weighted",
    },
    "Balanced-outcome FE": {
        "row_set": "Balanced outcome and population-weight country set, covariate-complete rows",
        "weighting_rule": "Equal country-year weight",
        "missing_data_assumption": "Complete-case selection within balanced-outcome countries",
        "model": "Country and year fixed effects",
        "interpretation": "Coverage-restricted selected panel",
        "family": "balanced",
    },
    "IPW complete-case FE": {
        "row_set": "Outcome and baseline covariates observed",
        "weighting_rule": "Stabilized inverse-probability weights",
        "missing_data_assumption": "Selection model diagnostic",
        "model": "IPW-weighted country and year fixed effects",
        "interpretation": "Selection diagnostic among complete cases",
        "family": "ipw",
    },
    "MAR MI full-target FE": {
        "row_set": "Outcome-observed target",
        "weighting_rule": "Equal country-year weight",
        "missing_data_assumption": "MAR PMM imputation sensitivity",
        "model": "Country and year fixed effects pooled across imputations",
        "interpretation": "Model-based full-target sensitivity",
        "family": "mi",
    },
}


LABELS = {
    "medical_population_combined": "Medical population",
    "medical_need_combined": "Medical need",
    "dental_population_combined": "Dental population",
    "dental_need_combined": "Dental need",
    "medical_population_cost": "Medical cost",
    "medical_population_waiting": "Medical waiting",
    "medical_population_distance": "Medical distance",
}


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


def _write_tabular(df: pd.DataFrame, columns: list[str], headers: list[str], path: Path, colspec: str) -> None:
    lines = [rf"\begin{{tabular}}{{{colspec}}}", r"\toprule", " & ".join(headers) + r" \\", r"\midrule"]
    for _, row in df[columns].iterrows():
        lines.append(" & ".join(_latex_escape(row[column]) for column in columns) + r" \\")
    lines.extend([r"\bottomrule", r"\end{tabular}", ""])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _write_tabularx(df: pd.DataFrame, columns: list[str], headers: list[str], path: Path, colspec: str) -> None:
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


def load_panel() -> pd.DataFrame:
    outcomes = pd.read_csv(DATA_PROCESSED / "multi_outcome_unmet_care.csv")
    features = pd.read_csv(DATA_PROCESSED / "panel_features_v2-3.csv").drop(columns=["unmet_need_pc", "status"], errors="ignore")
    panel = outcomes.rename(columns={"value_pc": OUTCOME}).merge(features, on=["geo", "year"], how="left")
    panel["country_group"] = panel["geo"].map(country_group)
    panel["row_key"] = panel["geo"].astype(str) + "|" + panel["year"].astype(str)
    panel["indicator_label"] = panel["indicator_id"].map(LABELS).fillna(panel["indicator_id"])
    return panel


def complete_case(target: pd.DataFrame, require_weight: bool = False) -> pd.DataFrame:
    required = [OUTCOME] + BASELINE_COVARS
    if require_weight:
        required.append(POP_WEIGHT)
    return target.dropna(subset=required).copy()


def balanced_outcome_subset(target: pd.DataFrame) -> pd.DataFrame:
    years = set(target["year"].dropna().astype(int).unique())
    countries: list[str] = []
    for geo, group in target.groupby("geo"):
        observed_years = set(group.loc[group[OUTCOME].notna(), "year"].dropna().astype(int))
        valid_weights = POP_WEIGHT in group.columns and group[POP_WEIGHT].notna().all()
        if years.issubset(observed_years) and valid_weights:
            countries.append(str(geo))
    return target[target["geo"].isin(countries)].copy()


def ipw_complete_case_weights(target: pd.DataFrame, sample: pd.DataFrame) -> pd.Series:
    work = target[[OUTCOME, "year", "geo", "country_group", "row_key"]].copy()
    included_keys = set(sample["row_key"])
    work["included"] = work["row_key"].isin(included_keys).astype(int)
    if work["included"].nunique() < 2:
        return pd.Series(1.0, index=sample.index)
    design = pd.concat(
        [
            work[[OUTCOME, "year"]].apply(pd.to_numeric, errors="coerce"),
            pd.get_dummies(work["country_group"], prefix="group", drop_first=True, dtype=float),
        ],
        axis=1,
    ).fillna(0.0)
    model = LogisticRegression(max_iter=1000, solver="lbfgs")
    model.fit(design, work["included"])
    propensity = pd.Series(model.predict_proba(design)[:, 1], index=work.index).clip(0.02, 0.98)
    stabilized = work["included"].mean() / propensity
    lower, upper = stabilized.quantile([0.01, 0.99])
    weights = stabilized.clip(lower, upper)
    key_to_weight = dict(zip(work["row_key"], weights))
    return sample["row_key"].map(key_to_weight).fillna(1.0).astype(float)


def row_set_for_estimand(target: pd.DataFrame, estimand: str) -> tuple[pd.DataFrame, pd.Series | None]:
    if estimand == "Unweighted complete-case FE":
        return complete_case(target), None
    if estimand == "Population-weighted complete-case FE":
        sample = complete_case(target, require_weight=True)
        return sample, sample[POP_WEIGHT].astype(float)
    if estimand == "Balanced-outcome FE":
        return complete_case(balanced_outcome_subset(target)), None
    if estimand == "IPW complete-case FE":
        sample = complete_case(target)
        return sample, ipw_complete_case_weights(target, sample)
    if estimand == "MAR MI full-target FE":
        return target.dropna(subset=[OUTCOME]).copy(), None
    raise KeyError(f"Unsupported estimand: {estimand}")


def weights_on_reference_support(reference: pd.DataFrame, sample: pd.DataFrame, sample_weights: pd.Series | None) -> tuple[pd.Series, pd.Series]:
    reference_weights = pd.Series(1.0, index=reference["row_key"])
    analytical = pd.Series(0.0, index=reference["row_key"])
    if sample.empty:
        return reference_weights, analytical
    if sample_weights is None:
        sample_values = pd.Series(1.0, index=sample["row_key"])
    else:
        sample_values = pd.Series(pd.to_numeric(sample_weights, errors="coerce").fillna(0.0).to_numpy(), index=sample["row_key"])
    analytical.loc[analytical.index.intersection(sample_values.index)] = sample_values.groupby(level=0).sum()
    return reference_weights, analytical


def drift_components(reference: pd.DataFrame, sample: pd.DataFrame, sample_weights: pd.Series | None) -> dict[str, float]:
    ref_weights, analytical_weights = weights_on_reference_support(reference, sample, sample_weights)
    components = {
        "Delta_row": support_loss(len(sample), len(reference)),
        "Delta_country": support_loss(sample["geo"].nunique(), reference["geo"].nunique()),
        "Delta_year": support_loss(sample["year"].nunique(), reference["year"].nunique()),
        "Delta_weight": jensen_shannon_divergence(ref_weights, analytical_weights),
        "Delta_balance": average_absolute_smd(reference, sample, DRIFT_BALANCE_COVARS),
    }
    components["TDI"] = target_population_drift_index(components)
    return components


def estimand_id(indicator_id: str, estimand: str) -> str:
    clean = estimand.lower().replace(" ", "_").replace("-", "_")
    return f"{indicator_id}__{clean}"


def build_tables(panel: pd.DataFrame, matrix: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    component_rows: list[dict[str, object]] = []
    drift_rows: list[dict[str, object]] = []
    theta_rows: list[dict[str, object]] = []

    for _, estimate in matrix.iterrows():
        indicator_id = estimate["indicator_id"]
        estimand = estimate["estimand"]
        metadata = ESTIMAND_METADATA[estimand]
        target = panel[panel["indicator_id"].eq(indicator_id)].dropna(subset=[OUTCOME]).copy()
        sample, sample_weights = row_set_for_estimand(target, estimand)
        components = drift_components(target, sample, sample_weights)

        x_iqr = float(pd.to_numeric(sample[TERM], errors="coerce").quantile(0.75) - pd.to_numeric(sample[TERM], errors="coerce").quantile(0.25)) if TERM in sample else np.nan
        y_iqr = float(pd.to_numeric(sample[OUTCOME], errors="coerce").quantile(0.75) - pd.to_numeric(sample[OUTCOME], errors="coerce").quantile(0.25)) if OUTCOME in sample else np.nan
        theta = standardized_coefficient(estimate.get("coef", np.nan), x_iqr, y_iqr)

        denominator = str(target["denominator"].dropna().iloc[0]) if "denominator" in target and target["denominator"].notna().any() else ""
        outcome_label = str(estimate["indicator_label"])
        eid = estimand_id(indicator_id, estimand)

        component_rows.append(
            {
                "estimand_id": eid,
                "outcome": outcome_label,
                "denominator": denominator,
                "country_universe": "Full Eurostat-available",
                "row_set": metadata["row_set"],
                "weighting_rule": metadata["weighting_rule"],
                "missing_data_assumption": metadata["missing_data_assumption"],
                "model": metadata["model"],
                "rows": int(estimate["rows"]),
                "countries": int(estimate["countries"]),
                "years": int(estimate["years"]),
                "interpretation": metadata["interpretation"],
                "status": estimate["status"],
            }
        )
        drift_rows.append(
            {
                "estimand_id": eid,
                "outcome": outcome_label,
                "estimand": estimand,
                "family": metadata["family"],
                "rows": int(estimate["rows"]),
                "countries": int(estimate["countries"]),
                "years": int(estimate["years"]),
                **components,
            }
        )
        theta_rows.append(
            {
                "indicator_id": indicator_id,
                "outcome": outcome_label,
                "denominator": denominator,
                "estimand_id": eid,
                "estimand": estimand,
                "family": metadata["family"],
                "status": estimate["status"],
                "coef": estimate.get("coef", np.nan),
                "theta": theta,
                "x_iqr": x_iqr,
                "y_iqr": y_iqr,
                "TDI": components["TDI"],
            }
        )

    theta_df = pd.DataFrame(theta_rows)
    stability_rows = []
    for (indicator_id, outcome, denominator), group in theta_df.groupby(["indicator_id", "outcome", "denominator"], sort=True):
        estimated = group[group["status"].eq("estimated") & group["theta"].notna()].copy()
        observed = estimated[~estimated["family"].eq("mi")]
        reference_values = observed["theta"] if not observed.empty else estimated["theta"]
        reference_sign = None
        if not reference_values.empty and reference_values.median() != 0:
            reference_sign = 1 if reference_values.median() > 0 else -1
        feasible_families = int(estimated["family"].nunique())
        if feasible_families < 2:
            theta_iqr = np.nan
            csi = np.nan
            agreement = np.nan
            label = "non-identifiable"
            reason = "fewer than 2 feasible estimand families"
        else:
            theta_iqr, csi = conclusion_stability_index(estimated["theta"], delta=CSI_DELTA)
            agreement = directional_agreement(estimated["theta"], reference_sign=reference_sign)
            label, reason = classify_stability_from_theta(estimated, csi, agreement)
        stability_rows.append(
            {
                "outcome": outcome,
                "denominator": denominator,
                "feasible_estimand_families": feasible_families,
                "median_theta": float(estimated["theta"].median()) if not estimated.empty else np.nan,
                "theta_IQR": theta_iqr,
                "directional_agreement": agreement,
                "CSI": csi,
                "final_label": label,
                "reason": reason,
            }
        )
    return pd.DataFrame(component_rows), pd.DataFrame(drift_rows), pd.DataFrame(stability_rows), theta_df


def classify_stability_from_theta_delta(estimated: pd.DataFrame, csi: float, agreement: float, delta: float) -> tuple[str, str]:
    if estimated["family"].nunique() < 2:
        return "non-identifiable", "fewer than 2 feasible estimand families"
    complete = estimated[estimated["family"].eq("complete-case")]
    mi = estimated[estimated["family"].eq("mi")]
    if not complete.empty and not mi.empty:
        gap = abs(float(complete["theta"].iloc[0]) - float(mi["theta"].iloc[0]))
        if gap > delta:
            return "missingness-dependent", f"complete-case and MAR MI theta differ by {gap:.3f}"
    observed = estimated[~estimated["family"].eq("mi")]
    if len(observed) >= 2:
        observed_range = float(observed["theta"].max() - observed["theta"].min())
        if observed_range > delta:
            return "target-dependent", f"observed-data theta range is {observed_range:.3f}"
    if pd.notna(csi) and pd.notna(agreement) and csi >= 0.75 and agreement >= 0.80:
        return "stable", f"CSI={csi:.3f} and directional agreement={agreement:.3f}"
    return "target-dependent", f"CSI={csi:.3f} and directional agreement={agreement:.3f}"


def classify_stability_from_theta(estimated: pd.DataFrame, csi: float, agreement: float) -> tuple[str, str]:
    return classify_stability_from_theta_delta(estimated, csi, agreement, CSI_DELTA)


def build_drift_stability_summary(stability: pd.DataFrame, theta: pd.DataFrame) -> pd.DataFrame:
    estimated = theta[theta["status"].eq("estimated") & theta["TDI"].notna()].copy()
    tdi = (
        estimated.groupby(["outcome", "denominator"], dropna=False)
        .agg(
            median_TDI=("TDI", "median"),
            max_TDI=("TDI", "max"),
        )
        .reset_index()
    )
    summary = stability.merge(tdi, on=["outcome", "denominator"], how="left")
    summary = summary.rename(columns={"reason": "rule_reason"})
    summary["rule_reason_short"] = summary["rule_reason"].map(_short_rule_reason)
    columns = [
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
        "rule_reason_short",
    ]
    return summary[columns].sort_values(["denominator", "outcome"]).reset_index(drop=True)


def weighted_tdi(row: pd.Series, weights: DriftWeights) -> float:
    return target_population_drift_index(
        {
            "Delta_row": row.get("Delta_row", np.nan),
            "Delta_country": row.get("Delta_country", np.nan),
            "Delta_year": row.get("Delta_year", np.nan),
            "Delta_weight": row.get("Delta_weight", np.nan),
            "Delta_balance": row.get("Delta_balance", np.nan),
        },
        weights=weights,
    )


def build_framework_parameter_sensitivity(
    stability_summary: pd.DataFrame,
    theta: pd.DataFrame,
    drift: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    drift_with_weights = drift.copy()
    for scheme, weights in TDI_WEIGHT_SCHEMES.items():
        drift_with_weights[f"TDI_{scheme}"] = drift_with_weights.apply(lambda row: weighted_tdi(row, weights), axis=1)

    tdi_summary = (
        drift_with_weights.groupby(["outcome", "family"], as_index=False)
        .agg(
            median_TDI_equal=("TDI_equal", "median"),
            median_TDI_support_focused=("TDI_support_focused", "median"),
            median_TDI_balance_focused=("TDI_balance_focused", "median"),
        )
    )

    rows: list[dict[str, object]] = []
    for (indicator_id, outcome, denominator), group in theta.groupby(["indicator_id", "outcome", "denominator"], sort=True):
        estimated = group[group["status"].eq("estimated") & group["theta"].notna()].copy()
        observed = estimated[~estimated["family"].eq("mi")]
        reference_values = observed["theta"] if not observed.empty else estimated["theta"]
        reference_sign = None
        if not reference_values.empty and reference_values.median() != 0:
            reference_sign = 1 if reference_values.median() > 0 else -1

        baseline = stability_summary[
            stability_summary["outcome"].eq(outcome) & stability_summary["denominator"].eq(denominator)
        ].iloc[0]
        row: dict[str, object] = {
            "indicator_id": indicator_id,
            "outcome": outcome,
            "denominator": denominator,
            "baseline_label": baseline["final_label"],
            "baseline_CSI": baseline["CSI"],
            "baseline_theta_IQR": baseline["theta_IQR"],
            "baseline_rule_reason": baseline["rule_reason"],
        }

        delta_labels: list[str] = []
        for delta in CSI_SENSITIVITY_DELTAS:
            if estimated["family"].nunique() < 2:
                theta_iqr = np.nan
                csi = np.nan
                agreement = np.nan
                label = "non-identifiable"
            else:
                theta_iqr, csi = conclusion_stability_index(estimated["theta"], delta=delta)
                agreement = directional_agreement(estimated["theta"], reference_sign=reference_sign)
                label, _ = classify_stability_from_theta_delta(estimated, csi, agreement, delta)
            key = f"delta_{delta:.2f}".replace(".", "_")
            row[f"{key}_label"] = label
            row[f"{key}_CSI"] = csi
            row[f"{key}_theta_IQR"] = theta_iqr
            row[f"{key}_directional_agreement"] = agreement
            delta_labels.append(label)

        outcome_tdi = tdi_summary[tdi_summary["outcome"].eq(outcome)]
        for scheme in TDI_WEIGHT_SCHEMES:
            column = f"median_TDI_{scheme}"
            values = outcome_tdi[column].dropna() if column in outcome_tdi else pd.Series(dtype=float)
            row[f"{column}_min"] = float(values.min()) if not values.empty else np.nan
            row[f"{column}_max"] = float(values.max()) if not values.empty else np.nan
        row["csi_delta_label_changed"] = any(label != row["baseline_label"] for label in delta_labels)
        row["tdi_weighting_label_changed"] = False
        row["tdi_weighting_note"] = "No label change; deterministic labels do not use TDI-weight thresholds."
        rows.append(row)

    detailed = pd.DataFrame(rows).sort_values(["denominator", "outcome"]).reset_index(drop=True)
    summary = detailed[
        [
            "outcome",
            "denominator",
            "baseline_label",
            "delta_0_05_label",
            "delta_0_10_label",
            "delta_0_15_label",
            "delta_0_20_label",
            "csi_delta_label_changed",
            "tdi_weighting_label_changed",
        ]
    ].copy()
    summary["csi_delta_label_changed"] = summary["csi_delta_label_changed"].map(lambda value: "Yes" if bool(value) else "No")
    summary["tdi_weighting_label_changed"] = summary["tdi_weighting_label_changed"].map(lambda value: "Yes" if bool(value) else "No")
    return detailed, summary


def _short_rule_reason(reason: object) -> str:
    text = "" if pd.isna(reason) else str(reason)
    if text.startswith("complete-case and MAR MI theta differ by "):
        value = text.rsplit(" ", 1)[-1]
        return f"CC--MI gap={value}"
    if text in {"fewer than two feasible estimand families", "fewer than 2 feasible estimand families"}:
        return "<2 estimand families"
    if text.startswith("CSI="):
        return text.replace("directional agreement", "dir. agree")
    return text


def write_outputs(components: pd.DataFrame, drift: pd.DataFrame, stability: pd.DataFrame, theta: pd.DataFrame) -> None:
    OUTPUTS.mkdir(exist_ok=True)
    TABLES.mkdir(exist_ok=True)
    FIGURES.mkdir(exist_ok=True)

    components.to_csv(OUTPUTS / "formal_estimand_components.csv", index=False)
    drift.to_csv(OUTPUTS / "target_drift_components.csv", index=False)
    stability.to_csv(OUTPUTS / "conclusion_stability.csv", index=False)
    theta.to_csv(OUTPUTS / "drift_stability_theta.csv", index=False)
    drift_summary = build_drift_stability_summary(stability, theta)
    drift_summary.to_csv(OUTPUTS / "drift_stability_summary.csv", index=False)
    sensitivity_detail, sensitivity_summary = build_framework_parameter_sensitivity(drift_summary, theta, drift)
    sensitivity_detail.to_csv(OUTPUTS / "framework_parameter_sensitivity.csv", index=False)
    sensitivity_summary.to_csv(OUTPUTS / "framework_parameter_sensitivity_summary.csv", index=False)

    component_display = components.copy()
    _write_tabular(
        component_display,
        ["outcome", "denominator", "row_set", "weighting_rule", "missing_data_assumption", "rows", "interpretation"],
        ["Outcome", "Denom.", "Row set", "Weighting", "Missing data", "Rows", "Interpretation"],
        TABLES / "formal_estimand_components.tex",
        r"p{0.13\linewidth}p{0.08\linewidth}p{0.22\linewidth}p{0.15\linewidth}p{0.18\linewidth}rp{0.16\linewidth}",
    )

    drift_display = drift.copy()
    for column in ["Delta_row", "Delta_country", "Delta_year", "Delta_weight", "Delta_balance", "TDI"]:
        drift_display[column] = drift_display[column].map(_format_float)
    _write_tabular(
        drift_display,
        ["outcome", "estimand", "Delta_row", "Delta_country", "Delta_year", "Delta_weight", "Delta_balance", "TDI"],
        ["Outcome", "Estimand", "$\\Delta_r$", "$\\Delta_c$", "$\\Delta_t$", "$\\Delta_w$", "$\\Delta_b$", "TDI"],
        TABLES / "target_drift_components.tex",
        r"p{0.16\linewidth}p{0.26\linewidth}rrrrrr",
    )

    stability_display = stability.copy()
    for column in ["median_theta", "theta_IQR", "directional_agreement", "CSI"]:
        stability_display[column] = stability_display[column].map(_format_float)
    _write_tabular(
        stability_display,
        ["outcome", "denominator", "feasible_estimand_families", "median_theta", "theta_IQR", "directional_agreement", "CSI", "final_label"],
        ["Outcome", "Denom.", "Families", "Median $\\theta$", "$\\theta$ IQR", "Dir. agree", "CSI", "Label"],
        TABLES / "conclusion_stability.tex",
        r"p{0.18\linewidth}p{0.10\linewidth}rrrrrp{0.18\linewidth}",
    )

    summary_display = drift_summary.copy()
    for column in ["median_theta", "theta_IQR", "directional_agreement", "CSI", "median_TDI", "max_TDI"]:
        summary_display[column] = summary_display[column].map(_format_float)
    _write_tabularx(
        summary_display,
        [
            "outcome",
            "denominator",
            "feasible_estimand_families",
            "median_theta",
            "theta_IQR",
            "directional_agreement",
            "CSI",
            "median_TDI",
            "final_label",
            "rule_reason_short",
        ],
        ["Outcome", "Denom.", "Families", "Median $\\theta$", "$\\theta$ IQR", "Dir. agree", "CSI", "Median TDI", "Label", "Rule reason"],
        TABLES / "drift_stability_summary.tex",
        r"@{}p{0.15\linewidth}p{0.08\linewidth}rrrrrp{0.08\linewidth}p{0.16\linewidth}p{0.14\linewidth}@{}",
    )

    sensitivity_display = sensitivity_summary.copy()
    label_map = {
        "missingness-dependent": "miss.-dep.",
        "target-dependent": "target-dep.",
        "non-identifiable": "non-ident.",
        "stable": "stable",
        "imputation-model-dependent": "imp.-dep.",
        "denominator-dependent": "denom.-dep.",
    }
    for column in ["baseline_label", "delta_0_05_label", "delta_0_10_label", "delta_0_15_label", "delta_0_20_label"]:
        sensitivity_display[column] = sensitivity_display[column].map(lambda value: label_map.get(str(value), str(value)))
    outcome_map = {
        "Dental population": "Dental pop.",
        "Medical cost": "Med. cost",
        "Medical distance": "Med. dist.",
        "Medical population": "Med. pop.",
        "Medical waiting": "Med. wait",
        "Dental need": "Dental need",
        "Medical need": "Med. need",
    }
    denominator_map = {"population": "pop.", "same_needs": "need"}
    sensitivity_display["outcome"] = sensitivity_display["outcome"].map(lambda value: outcome_map.get(str(value), str(value)))
    sensitivity_display["denominator"] = sensitivity_display["denominator"].map(lambda value: denominator_map.get(str(value), str(value)))
    _write_tabularx(
        sensitivity_display,
        [
            "outcome",
            "denominator",
            "baseline_label",
            "delta_0_05_label",
            "delta_0_10_label",
            "delta_0_15_label",
            "delta_0_20_label",
            "csi_delta_label_changed",
            "tdi_weighting_label_changed",
        ],
        ["Outcome", "Denom.", "Baseline", "$\\delta=.05$", "$\\delta=.10$", "$\\delta=.15$", "$\\delta=.20$", "CSI change?", "TDI change?"],
        TABLES / "framework_parameter_sensitivity_summary.tex",
        r"@{}p{0.12\linewidth}p{0.06\linewidth}p{0.14\linewidth}p{0.11\linewidth}p{0.11\linewidth}p{0.11\linewidth}p{0.11\linewidth}p{0.08\linewidth}p{0.08\linewidth}@{}",
    )

    save_figures(drift, stability, theta)
    update_generation_map()


def save_figures(drift: pd.DataFrame, stability: pd.DataFrame, theta: pd.DataFrame) -> None:
    plot = theta[theta["status"].eq("estimated") & theta["theta"].notna() & theta["TDI"].notna()].copy()
    if not plot.empty:
        plt.figure(figsize=(9.6, 5.8))
        sns.scatterplot(data=plot, x="TDI", y="theta", hue="family", style="denominator", s=70)
        for _, row in plot.iterrows():
            plt.text(row["TDI"] + 0.004, row["theta"], str(row["outcome"]).replace(" population", ""), fontsize=6)
        plt.axhline(0, color="0.35", linewidth=1, linestyle=":")
        plt.xlabel("Target-Population Drift Index")
        plt.ylabel("Standardized coefficient $\\theta$")
        plt.tight_layout()
        plt.savefig(FIGURES / "drift_stability_map.pdf")
        plt.savefig(FIGURES / "drift_stability_map.png", dpi=180)
        plt.close()

    heatmap = drift.copy()
    heatmap["row_label"] = heatmap["outcome"] + " | " + heatmap["estimand"].str.replace(" FE", "", regex=False)
    heatmap_data = heatmap.set_index("row_label")[["Delta_row", "Delta_country", "Delta_year", "Delta_weight", "Delta_balance"]]
    if not heatmap_data.empty:
        plt.figure(figsize=(7.5, max(5.5, 0.24 * len(heatmap_data))))
        sns.heatmap(heatmap_data, cmap="viridis", vmin=0, vmax=min(1.0, float(np.nanmax(heatmap_data.to_numpy()))), cbar_kws={"label": "Drift component"})
        plt.xlabel("")
        plt.ylabel("")
        plt.tight_layout()
        plt.savefig(FIGURES / "target_drift_components_heatmap.pdf")
        plt.savefig(FIGURES / "target_drift_components_heatmap.png", dpi=180)
        plt.close()

    csi_plot = stability.copy()
    if not csi_plot.empty:
        plt.figure(figsize=(8.8, 4.8))
        sns.barplot(data=csi_plot, x="CSI", y="outcome", hue="final_label", dodge=False)
        plt.xlim(0, 1)
        plt.xlabel("Conclusion Stability Index")
        plt.ylabel("")
        plt.legend(title="", fontsize=8, loc="lower right")
        plt.tight_layout()
        plt.savefig(FIGURES / "conclusion_stability_by_outcome.pdf")
        plt.savefig(FIGURES / "conclusion_stability_by_outcome.png", dpi=180)
        plt.close()


def update_generation_map() -> None:
    map_path = OUTPUTS / "table_figure_generation_map.csv"
    existing = pd.read_csv(map_path) if map_path.exists() else pd.DataFrame(columns=["chapter_or_use", "output_type", "output_file", "script", "input_file"])
    new_rows = pd.DataFrame(
        [
            ["chapters/framework.tex", "table", "tables/formal_estimand_components.tex", "src/build_drift_stability_framework.py", "outputs/outcome_estimand_coefficient_matrix.csv; data/processed/multi_outcome_unmet_care.csv"],
            ["chapters/framework.tex", "table", "tables/target_drift_components.tex", "src/build_drift_stability_framework.py", "outputs/outcome_estimand_coefficient_matrix.csv; data/processed/multi_outcome_unmet_care.csv"],
            ["chapters/framework.tex", "table", "tables/conclusion_stability.tex", "src/build_drift_stability_framework.py", "outputs/target_drift_components.csv; outputs/drift_stability_theta.csv"],
            ["chapters/modeling_strategy_results.tex", "table", "tables/drift_stability_summary.tex", "src/build_drift_stability_framework.py", "outputs/target_drift_components.csv; outputs/drift_stability_theta.csv; outputs/conclusion_stability.csv"],
            ["chapters/modeling_strategy_results.tex", "table", "tables/framework_parameter_sensitivity_summary.tex", "src/build_drift_stability_framework.py", "outputs/drift_stability_summary.csv; outputs/drift_stability_theta.csv; outputs/target_drift_components.csv"],
            ["chapters/framework.tex", "figure", "figures/drift_stability_map.pdf", "src/build_drift_stability_framework.py", "outputs/target_drift_components.csv; outputs/drift_stability_theta.csv"],
            ["chapters/framework.tex", "figure", "figures/target_drift_components_heatmap.pdf", "src/build_drift_stability_framework.py", "outputs/target_drift_components.csv"],
            ["chapters/framework.tex", "figure", "figures/conclusion_stability_by_outcome.pdf", "src/build_drift_stability_framework.py", "outputs/conclusion_stability.csv"],
        ],
        columns=["chapter_or_use", "output_type", "output_file", "script", "input_file"],
    )
    combined = pd.concat([existing[~existing["output_file"].isin(new_rows["output_file"])], new_rows], ignore_index=True)
    combined.to_csv(map_path, index=False)


def main() -> None:
    panel = load_panel()
    matrix = pd.read_csv(OUTPUTS / "outcome_estimand_coefficient_matrix.csv")
    components, drift, stability, theta = build_tables(panel, matrix)
    write_outputs(components, drift, stability, theta)
    print(f"saved {OUTPUTS / 'formal_estimand_components.csv'}")
    print(f"saved {OUTPUTS / 'target_drift_components.csv'}")
    print(f"saved {OUTPUTS / 'conclusion_stability.csv'}")
    print(f"saved {OUTPUTS / 'drift_stability_summary.csv'}")
    print(f"saved {OUTPUTS / 'framework_parameter_sensitivity.csv'}")


if __name__ == "__main__":
    main()
