from __future__ import annotations

import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import statsmodels.formula.api as smf
from sklearn.linear_model import LogisticRegression

from eurodrift.classification import classify_drift, classify_feasibility
from eurodrift.targets import country_group
from run_missingness_robustness import pmm_completed_dataset, rubin_pool


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
FEASIBILITY_MIN_ROWS = 100
FEASIBILITY_MIN_COUNTRIES = 15
FEASIBILITY_MIN_YEARS = 5
MI_IMPUTATIONS = 10

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


def load_panel() -> pd.DataFrame:
    outcomes = pd.read_csv(DATA_PROCESSED / "multi_outcome_unmet_care.csv")
    features = pd.read_csv(DATA_PROCESSED / "panel_features_v2-3.csv").drop(columns=["unmet_need_pc", "status"], errors="ignore")
    panel = outcomes.rename(columns={"value_pc": OUTCOME}).merge(features, on=["geo", "year"], how="left")
    panel["country_group"] = panel["geo"].map(country_group)
    panel["indicator_label"] = panel["indicator_id"].map(LABELS).fillna(panel["indicator_id"])
    return panel


def complete_case(df: pd.DataFrame, require_weight: bool = False) -> pd.DataFrame:
    required = [OUTCOME] + BASELINE_COVARS
    if require_weight:
        required.append(POP_WEIGHT)
    return df.dropna(subset=required).copy()


def feasibility(df: pd.DataFrame) -> tuple[bool, str]:
    return classify_feasibility(
        df,
        country_col="geo",
        year_col="year",
    )


def fit_fe(df: pd.DataFrame, weights: pd.Series | None = None):
    formula = f"{OUTCOME} ~ {' + '.join(BASELINE_COVARS)} + C(geo) + C(year)"
    if weights is None:
        return smf.ols(formula, data=df).fit(
            cov_type="cluster",
            cov_kwds={"groups": df["geo"], "use_correction": True},
        )
    return smf.wls(formula, data=df, weights=weights).fit(
        cov_type="cluster",
        cov_kwds={"groups": df["geo"], "use_correction": True},
    )


def summarize_result(
    indicator_id: str,
    indicator_label: str,
    estimand: str,
    df: pd.DataFrame,
    result=None,
    status: str = "estimated",
    note: str = "",
) -> dict[str, object]:
    row: dict[str, object] = {
        "indicator_id": indicator_id,
        "indicator_label": indicator_label,
        "estimand": estimand,
        "rows": int(len(df)),
        "countries": int(df["geo"].nunique()) if "geo" in df.columns else 0,
        "years": int(df["year"].nunique()) if "year" in df.columns else 0,
        "coef": np.nan,
        "se": np.nan,
        "ci_low": np.nan,
        "ci_high": np.nan,
        "p_value": np.nan,
        "status": status,
        "note": note,
    }
    if result is not None and TERM in result.params:
        conf = result.conf_int().loc[TERM]
        row.update(
            {
                "coef": float(result.params[TERM]),
                "se": float(result.bse[TERM]),
                "ci_low": float(conf.iloc[0]),
                "ci_high": float(conf.iloc[1]),
                "p_value": float(result.pvalues[TERM]),
                "rows": int(result.nobs),
            }
        )
    return row


def balanced_outcome_subset(group: pd.DataFrame) -> pd.DataFrame:
    years = set(group["year"].dropna().astype(int).unique())
    countries = []
    for geo, country_rows in group.groupby("geo"):
        observed_years = set(country_rows.loc[country_rows[OUTCOME].notna(), "year"].dropna().astype(int))
        valid_weights = POP_WEIGHT in country_rows.columns and country_rows[POP_WEIGHT].notna().all()
        if years.issubset(observed_years) and valid_weights:
            countries.append(geo)
    return group[group["geo"].isin(countries)].copy()


def ipw_weights(target: pd.DataFrame, complete: pd.DataFrame) -> pd.Series | None:
    work = target[[OUTCOME, "year", "geo", "country_group"]].copy()
    complete_keys = set(zip(complete["geo"], complete["year"]))
    work["included"] = [int((geo, year) in complete_keys) for geo, year in zip(work["geo"], work["year"])]
    if work["included"].nunique() < 2:
        return None
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
    complete_index = work.index[work["included"].eq(1)]
    return weights.loc[complete_index].reset_index(drop=True)


def imputation_matrix(base: pd.DataFrame) -> pd.DataFrame:
    matrix = base[[OUTCOME] + BASELINE_COVARS].copy()
    year_dummies = pd.get_dummies(base["year"].astype(int), prefix="year", drop_first=True, dtype=float)
    group_dummies = pd.get_dummies(base["geo"].map(country_group), prefix="group", drop_first=True, dtype=float)
    return pd.concat([matrix, year_dummies, group_dummies], axis=1).apply(pd.to_numeric, errors="coerce")


def mi_result(indicator_id: str, indicator_label: str, target: pd.DataFrame) -> dict[str, object]:
    target = target.dropna(subset=[OUTCOME]).copy().reset_index(drop=True)
    ok, reason = feasibility(target)
    if not ok:
        return summarize_result(indicator_id, indicator_label, "MAR MI full-target FE", target, status=reason, note="MI target infeasible")
    matrix = imputation_matrix(target)
    coefs = []
    ses = []
    fit_rows = []
    for i in range(MI_IMPUTATIONS):
        completed = pmm_completed_dataset(target, matrix, seed=4200 + i, n_iter=4, k_pmm=20)
        fit_df = completed[["geo", "year", OUTCOME] + BASELINE_COVARS].dropna().copy()
        ok_fit, reason_fit = feasibility(fit_df)
        if not ok_fit:
            return summarize_result(
                indicator_id,
                indicator_label,
                "MAR MI full-target FE",
                fit_df,
                status=reason_fit,
                note="imputed fit sample infeasible",
            )
        result = fit_fe(fit_df)
        coefs.append(float(result.params[TERM]))
        ses.append(float(result.bse[TERM]))
        fit_rows.append(fit_df)
    pooled = rubin_pool(coefs, ses)
    ref = fit_rows[0]
    return {
        "indicator_id": indicator_id,
        "indicator_label": indicator_label,
        "estimand": "MAR MI full-target FE",
        "rows": int(np.mean([len(df) for df in fit_rows])),
        "countries": int(np.mean([df["geo"].nunique() for df in fit_rows])),
        "years": int(np.mean([df["year"].nunique() for df in fit_rows])),
        "coef": pooled["estimate"],
        "se": pooled["se"],
        "ci_low": pooled["estimate"] - 1.96 * pooled["se"],
        "ci_high": pooled["estimate"] + 1.96 * pooled["se"],
        "p_value": pooled["p_value"],
        "status": "estimated",
        "note": f"PMM MAR sensitivity with {MI_IMPUTATIONS} imputations; first fit rows {len(ref)}",
    }


def estimate_indicator(indicator_id: str, group: pd.DataFrame) -> list[dict[str, object]]:
    indicator_label = LABELS.get(indicator_id, indicator_id)
    rows: list[dict[str, object]] = []
    target = group.dropna(subset=[OUTCOME]).copy()

    cc = complete_case(target)
    ok, reason = feasibility(cc)
    if ok:
        rows.append(summarize_result(indicator_id, indicator_label, "Unweighted complete-case FE", cc, fit_fe(cc)))
    else:
        rows.append(summarize_result(indicator_id, indicator_label, "Unweighted complete-case FE", cc, status=reason))

    weighted = complete_case(target, require_weight=True)
    ok, reason = feasibility(weighted)
    if ok:
        rows.append(
            summarize_result(
                indicator_id,
                indicator_label,
                "Population-weighted complete-case FE",
                weighted,
                fit_fe(weighted, weights=weighted[POP_WEIGHT]),
            )
        )
    else:
        rows.append(summarize_result(indicator_id, indicator_label, "Population-weighted complete-case FE", weighted, status=reason))

    balanced = complete_case(balanced_outcome_subset(target))
    ok, reason = feasibility(balanced)
    if ok:
        rows.append(summarize_result(indicator_id, indicator_label, "Balanced-outcome FE", balanced, fit_fe(balanced)))
    else:
        rows.append(summarize_result(indicator_id, indicator_label, "Balanced-outcome FE", balanced, status=reason))

    ipw_sample = complete_case(target)
    ok, reason = feasibility(ipw_sample)
    weights = ipw_weights(target, ipw_sample) if ok else None
    if ok and weights is not None:
        rows.append(
            summarize_result(
                indicator_id,
                indicator_label,
                "IPW complete-case FE",
                ipw_sample,
                fit_fe(ipw_sample, weights=weights),
                note="selection-diagnostic weights from outcome, year, and country group",
            )
        )
    else:
        rows.append(summarize_result(indicator_id, indicator_label, "IPW complete-case FE", ipw_sample, status=reason if not ok else "infeasible: IPW propensity failed"))

    rows.append(mi_result(indicator_id, indicator_label, target))
    return rows


def classify_by_indicator(results: pd.DataFrame, panel: pd.DataFrame) -> pd.DataFrame:
    records = []
    estimand_key = {
        "Unweighted complete-case FE": "complete_case",
        "Population-weighted complete-case FE": "population_weighted",
        "Balanced-outcome FE": "balanced",
        "IPW complete-case FE": "ipw",
        "MAR MI full-target FE": "mi",
    }
    for indicator_id, group in results.groupby("indicator_id", sort=True):
        target = panel[panel["indicator_id"].eq(indicator_id)].dropna(subset=[OUTCOME, TERM])
        poverty_iqr = float(target[TERM].quantile(0.75) - target[TERM].quantile(0.25)) if not target.empty else np.nan
        outcome_sd = float(target[OUTCOME].std(ddof=1)) if not target.empty else np.nan
        estimates = {
            estimand_key[row["estimand"]]: row["coef"]
            for _, row in group.iterrows()
            if row["estimand"] in estimand_key and row["status"] == "estimated" and pd.notna(row["coef"])
        }
        label = (
            classify_drift(estimates, poverty_iqr=poverty_iqr, outcome_sd=outcome_sd)
            if estimates and pd.notna(poverty_iqr) and pd.notna(outcome_sd) and outcome_sd > 0
            else "non-identifiable"
        )
        records.append(
            {
                "indicator_id": indicator_id,
                "indicator_label": LABELS.get(indicator_id, indicator_id),
                "poverty_iqr": poverty_iqr,
                "outcome_sd": outcome_sd,
                "estimated_estimands": len(estimates),
                "classification": label,
            }
        )
    return pd.DataFrame(records)


def write_tables(results: pd.DataFrame, classifications: pd.DataFrame) -> None:
    display = results.copy()
    for column in ["coef", "ci_low", "ci_high", "p_value"]:
        display[column] = display[column].map(lambda value: "" if pd.isna(value) else f"{value:.3f}")
    display["ci"] = np.where(display["ci_low"].eq(""), "", "[" + display["ci_low"] + ", " + display["ci_high"] + "]")
    _write_tabular(
        display,
        ["indicator_label", "estimand", "rows", "countries", "years", "coef", "ci", "p_value", "status"],
        ["Indicator", "Estimand", "Rows", "Countries", "Years", "Coef.", "95\\% CI", "p", "Status"],
        TABLES / "outcome_estimand_coefficient_matrix.tex",
        r"p{0.15\linewidth}p{0.23\linewidth}rrrp{0.07\linewidth}p{0.15\linewidth}p{0.06\linewidth}p{0.14\linewidth}",
    )

    class_display = classifications.copy()
    for column in ["poverty_iqr", "outcome_sd"]:
        class_display[column] = class_display[column].map(lambda value: "" if pd.isna(value) else f"{value:.3f}")
    _write_tabular(
        class_display,
        ["indicator_label", "poverty_iqr", "outcome_sd", "estimated_estimands", "classification"],
        ["Indicator", "Poverty IQR", "Outcome SD", "Estimated estimands", "Classification"],
        TABLES / "outcome_failure_classification.tex",
        r"p{0.28\linewidth}rrrp{0.22\linewidth}",
    )


def save_plot(results: pd.DataFrame) -> None:
    plot = results[results["status"].eq("estimated")].copy()
    if plot.empty:
        return
    order = list(LABELS.values())
    plt.figure(figsize=(10.5, 6.2))
    sns.pointplot(
        data=plot,
        x="coef",
        y="indicator_label",
        hue="estimand",
        order=[label for label in order if label in set(plot["indicator_label"])],
        dodge=0.55,
        join=False,
        errorbar=None,
    )
    for _, row in plot.iterrows():
        y_labels = [label.get_text() for label in plt.gca().get_yticklabels()]
        if row["indicator_label"] not in y_labels:
            continue
        y = y_labels.index(row["indicator_label"])
        plt.plot([row["ci_low"], row["ci_high"]], [y, y], color="0.55", linewidth=0.8, alpha=0.8)
    plt.axvline(0, color="0.25", linewidth=1, linestyle=":")
    plt.xlabel("Poverty/social-exclusion coefficient")
    plt.ylabel("Outcome")
    plt.title("Outcome-by-estimand coefficient stability")
    plt.legend(title="", fontsize=7, loc="best")
    plt.tight_layout()
    FIGURES.mkdir(parents=True, exist_ok=True)
    plt.savefig(FIGURES / "outcome_estimand_coefficient_stability.pdf")
    plt.savefig(FIGURES / "outcome_estimand_coefficient_stability.png", dpi=180)
    plt.close()


def main() -> None:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    TABLES.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)

    panel = load_panel()
    rows = []
    for indicator_id, group in panel.groupby("indicator_id", sort=True):
        rows.extend(estimate_indicator(indicator_id, group))
    results = pd.DataFrame(rows)
    classifications = classify_by_indicator(results, panel)
    results = results.merge(classifications[["indicator_id", "classification"]], on="indicator_id", how="left")
    results.to_csv(OUTPUTS / "outcome_estimand_coefficient_matrix.csv", index=False)
    classifications.to_csv(OUTPUTS / "outcome_failure_classification.csv", index=False)
    write_tables(results, classifications)
    save_plot(results)
    print(f"saved {OUTPUTS / 'outcome_estimand_coefficient_matrix.csv'}")
    print(f"saved {OUTPUTS / 'outcome_failure_classification.csv'}")
    print(f"estimated rows: {(results['status'] == 'estimated').sum()} / {len(results)}")


if __name__ == "__main__":
    main()
