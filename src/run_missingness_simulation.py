from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.linear_model import LogisticRegression

from eurodrift import (
    average_absolute_smd,
    jensen_shannon_divergence,
    support_loss,
    target_population_drift_index,
)
from run_missingness_robustness import apply_delta_shift, pmm_completed_dataset, rubin_pool


ROOT = Path(__file__).resolve().parents[1]
DATA_PROCESSED = ROOT / "data" / "processed"
OUTPUTS = ROOT / "outputs"
FIGURES = ROOT / "figures"
TABLES = ROOT / "tables"

RANDOM_SEED = 42
OUTCOME = "unmet_need_pc"
TERM = "poverty_or_social_exclusion_pc"
POP_WEIGHT = "population_weight_year_norm"
BASELINE_COVARS = [
    "log_gdp_per_capita",
    "unemployment_rate_pc",
    TERM,
    "government_health_expenditure_gdp_pc",
    "compulsory_health_financing_gdp_pc",
]
FINANCING_COVARS = [
    "government_health_expenditure_gdp_pc",
    "compulsory_health_financing_gdp_pc",
]
SIM_MECHANISMS = [
    "mcar",
    "early_year",
    "country_group",
    "covariate_block",
    "mar_observed",
    "mnar_high_poverty_unmet",
    "eurostat_realistic",
]
ESTIMATORS = [
    "complete_case_fe",
    "population_weighted_fe",
    "ipw_fe",
    "pmm_mi_fe",
    "mnar_shift_mi_fe",
]
MECHANISM_LABELS = {
    "mcar": "MCAR",
    "early_year": "Early-year",
    "country_group": "Country group",
    "covariate_block": "Covariate block",
    "mar_observed": "MAR observed",
    "mnar_high_poverty_unmet": "MNAR high-pov./unmet",
    "eurostat_realistic": "Eurostat-realistic",
}
ESTIMATOR_LABELS = {
    "complete_case_fe": "CC FE",
    "population_weighted_fe": "Pop.-weighted FE",
    "ipw_fe": "IPW FE",
    "pmm_mi_fe": "PMM MI",
    "mnar_shift_mi_fe": "MNAR-shift MI",
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


def country_group(geo: str) -> str:
    if geo in {"AT", "BE", "CH", "DE", "DK", "FI", "FR", "IE", "IS", "LU", "NL", "NO", "SE", "UK"}:
        return "Western/Northern"
    if geo in {"AL", "BA", "BG", "CY", "CZ", "EE", "EL", "ES", "HR", "HU", "IT", "LT", "LV", "ME", "MK", "MT", "PL", "PT", "RO", "RS", "SI", "SK", "TR", "XK"}:
        return "Eastern/Southern"
    return "Other"


def load_reference_panel() -> tuple[pd.DataFrame, pd.DataFrame]:
    target = pd.read_csv(DATA_PROCESSED / "panel_features_v2-3.csv")
    complete = target.dropna(subset=[OUTCOME] + BASELINE_COVARS + [POP_WEIGHT]).copy()
    complete["country_group"] = complete["geo"].map(country_group)
    target["country_group"] = target["geo"].map(country_group)
    complete["_row_id"] = np.arange(len(complete))
    target["_row_id"] = np.arange(len(target))
    return complete.reset_index(drop=True), target.reset_index(drop=True)


def fit_twfe_fast(df: pd.DataFrame, weights: pd.Series | None = None) -> dict[str, float | int | str]:
    required = [OUTCOME] + BASELINE_COVARS
    work = df.dropna(subset=required).copy()
    if len(work) < 50 or work["geo"].nunique() < 8 or work["year"].nunique() < 3:
        return {"status": "infeasible", "coef": np.nan, "se": np.nan, "ci_low": np.nan, "ci_high": np.nan, "rows": len(work), "countries": work["geo"].nunique(), "years": work["year"].nunique()}

    y = work[OUTCOME].to_numpy(dtype=float)
    x_parts = [pd.Series(1.0, index=work.index, name="intercept"), work[BASELINE_COVARS].astype(float)]
    x_parts.append(pd.get_dummies(work["geo"], prefix="geo", drop_first=True, dtype=float))
    x_parts.append(pd.get_dummies(work["year"].astype(int), prefix="year", drop_first=True, dtype=float))
    x = pd.concat(x_parts, axis=1)
    keep_columns = x.var(axis=0).fillna(0).gt(0) | (x.columns == "intercept")
    x = x.loc[:, keep_columns]
    columns = x.columns.tolist()
    x_np = x.to_numpy(dtype=float)
    if weights is None:
        w = np.ones(len(work))
    else:
        w = pd.Series(weights).reset_index(drop=True).reindex(range(len(work))).fillna(1.0).to_numpy(dtype=float)
    sqrt_w = np.sqrt(w)
    xw = x_np * sqrt_w[:, None]
    yw = y * sqrt_w
    try:
        beta, *_ = np.linalg.lstsq(xw, yw, rcond=None)
        residuals = y - x_np @ beta
        rank = np.linalg.matrix_rank(xw)
        df_resid = max(len(work) - rank, 1)
        sigma2 = float(np.sum(w * residuals**2) / df_resid)
        xtwx_inv = np.linalg.pinv(xw.T @ xw)
        covariance = sigma2 * xtwx_inv
        term_idx = columns.index(TERM)
        coef = float(beta[term_idx])
        se = float(np.sqrt(max(covariance[term_idx, term_idx], 0.0)))
        return {
            "status": "estimated",
            "coef": coef,
            "se": se,
            "ci_low": coef - 1.96 * se,
            "ci_high": coef + 1.96 * se,
            "rows": int(len(work)),
            "countries": int(work["geo"].nunique()),
            "years": int(work["year"].nunique()),
        }
    except Exception as exc:  # pragma: no cover - defensive for singular simulation draws
        return {"status": f"failed: {type(exc).__name__}", "coef": np.nan, "se": np.nan, "ci_low": np.nan, "ci_high": np.nan, "rows": len(work), "countries": work["geo"].nunique(), "years": work["year"].nunique()}


def missingness_mask(reference: pd.DataFrame, target: pd.DataFrame, mechanism: str, rng: np.random.Generator) -> pd.DataFrame:
    mask = pd.DataFrame(False, index=reference.index, columns=BASELINE_COVARS)
    if mechanism == "mcar":
        mask.loc[:, BASELINE_COVARS] = rng.random((len(reference), len(BASELINE_COVARS))) < 0.25
    elif mechanism == "early_year":
        early_years = sorted(reference["year"].unique())[:3]
        mask.loc[reference["year"].isin(early_years), BASELINE_COVARS] = True
    elif mechanism == "country_group":
        eastern = reference["country_group"].eq("Eastern/Southern")
        mask.loc[eastern & (rng.random(len(reference)) < 0.45), BASELINE_COVARS] = True
    elif mechanism == "covariate_block":
        affected = rng.random(len(reference)) < 0.35
        mask.loc[affected, FINANCING_COVARS] = True
    elif mechanism == "mar_observed":
        poverty_rank = reference[TERM].rank(pct=True)
        unemployment_rank = reference["unemployment_rate_pc"].rank(pct=True)
        gdp_rank = reference["log_gdp_per_capita"].rank(pct=True)
        year_rank = reference["year"].rank(pct=True)
        probability = (0.05 + 0.45 * ((poverty_rank + unemployment_rank + (1 - gdp_rank) + year_rank) / 4)).clip(0.05, 0.65)
        affected = rng.random(len(reference)) < probability.to_numpy()
        mask.loc[affected, BASELINE_COVARS] = True
    elif mechanism == "mnar_high_poverty_unmet":
        poverty_rank = reference[TERM].rank(pct=True)
        outcome_rank = reference[OUTCOME].rank(pct=True)
        probability = (0.05 + 0.55 * ((poverty_rank + outcome_rank) / 2)).clip(0, 0.75)
        affected = rng.random(len(reference)) < probability.to_numpy()
        mask.loc[affected, BASELINE_COVARS] = True
    elif mechanism == "eurostat_realistic":
        for covar in BASELINE_COVARS:
            year_missing = target.groupby("year")[covar].apply(lambda values: float(values.isna().mean()))
            probs = reference["year"].map(year_missing).fillna(float(target[covar].isna().mean())).clip(0.05, 0.75)
            mask[covar] = rng.random(len(reference)) < probs.to_numpy()
    else:
        raise ValueError(f"Unknown mechanism: {mechanism}")
    return mask


def apply_mask(reference: pd.DataFrame, mask: pd.DataFrame) -> pd.DataFrame:
    observed = reference.copy()
    for covar in BASELINE_COVARS:
        observed.loc[mask[covar], covar] = np.nan
        if covar == "log_gdp_per_capita" and "gdp_per_capita_eur" in observed.columns:
            observed.loc[mask[covar], "gdp_per_capita_eur"] = np.nan
    return observed


def ipw_weights(observed: pd.DataFrame) -> pd.Series | None:
    inclusion = observed[[OUTCOME] + BASELINE_COVARS].notna().all(axis=1).astype(int)
    if inclusion.nunique() < 2:
        return None
    design = pd.concat(
        [
            observed[[OUTCOME, "year"]].apply(pd.to_numeric, errors="coerce"),
            pd.get_dummies(observed["country_group"], prefix="group", drop_first=True, dtype=float),
        ],
        axis=1,
    ).fillna(0.0)
    model = LogisticRegression(max_iter=1000, solver="lbfgs")
    model.fit(design, inclusion)
    propensity = pd.Series(model.predict_proba(design)[:, 1], index=observed.index).clip(0.02, 0.98)
    weights = inclusion.mean() / propensity
    lower, upper = weights.quantile([0.01, 0.99])
    return weights.clip(lower, upper).loc[inclusion.eq(1)]


def imputation_matrix(observed: pd.DataFrame) -> pd.DataFrame:
    matrix = observed[[OUTCOME] + BASELINE_COVARS].copy()
    year_dummies = pd.get_dummies(observed["year"].astype(int), prefix="year", drop_first=True, dtype=float)
    group_dummies = pd.get_dummies(observed["country_group"], prefix="group", drop_first=True, dtype=float)
    return pd.concat([matrix, year_dummies, group_dummies], axis=1).apply(pd.to_numeric, errors="coerce")


def fit_pmm(observed: pd.DataFrame, mask: pd.DataFrame, seed: int, m: int, mnar: bool) -> dict[str, float | int | str]:
    matrix = imputation_matrix(observed)
    coefs, ses = [], []
    last_rows = 0
    last_countries = 0
    last_years = 0
    for i in range(m):
        completed = pmm_completed_dataset(observed, matrix, seed=seed + i, n_iter=2, k_pmm=10)
        if mnar:
            completed = apply_delta_shift(
                completed,
                observed,
                {
                    TERM: 5.0,
                    "unemployment_rate_pc": 2.0,
                    "gdp_per_capita_eur": -0.10,
                },
            )
        fit = fit_twfe_fast(completed)
        if fit["status"] != "estimated":
            return fit
        coefs.append(float(fit["coef"]))
        ses.append(float(fit["se"]))
        last_rows = int(fit["rows"])
        last_countries = int(fit["countries"])
        last_years = int(fit["years"])
    pooled = rubin_pool(coefs, ses)
    return {
        "status": "estimated",
        "coef": pooled["estimate"],
        "se": pooled["se"],
        "ci_low": pooled["estimate"] - 1.96 * pooled["se"],
        "ci_high": pooled["estimate"] + 1.96 * pooled["se"],
        "rows": last_rows,
        "countries": last_countries,
        "years": last_years,
    }


def target_distance(reference: pd.DataFrame, observed: pd.DataFrame) -> float:
    retained = observed[[OUTCOME] + BASELINE_COVARS].notna().all(axis=1)
    retained_df = reference.loc[retained].copy()
    if retained_df.empty:
        return np.nan
    row_component = abs(1.0 - len(retained_df) / len(reference))
    country_component = abs(1.0 - retained_df["geo"].nunique() / reference["geo"].nunique())
    year_component = abs(1.0 - retained_df["year"].nunique() / reference["year"].nunique())
    smds = []
    for var in [OUTCOME, TERM, "log_gdp_per_capita", "unemployment_rate_pc"]:
        pooled_sd = reference[var].std(ddof=1)
        if pooled_sd and not pd.isna(pooled_sd):
            smds.append(abs((retained_df[var].mean() - reference[var].mean()) / pooled_sd))
    smd_component = float(np.mean(smds)) if smds else 0.0
    return float(row_component + country_component + year_component + smd_component)


def _row_weight_distribution(
    reference: pd.DataFrame,
    analytical: pd.DataFrame,
    weights: pd.Series | None = None,
) -> tuple[pd.Series, pd.Series]:
    reference_ids = reference["_row_id"].astype(str)
    ref_dist = pd.Series(1.0, index=reference_ids)
    analytical_ids = analytical["_row_id"].astype(str) if "_row_id" in analytical.columns else pd.Series(dtype=str)
    if weights is None:
        ana_dist = pd.Series(1.0, index=analytical_ids)
    else:
        weight_values = pd.to_numeric(pd.Series(weights).reset_index(drop=True), errors="coerce").fillna(0.0)
        ana_dist = pd.Series(weight_values.to_numpy(dtype=float), index=analytical_ids.reset_index(drop=True))
    all_ids = ref_dist.index.union(ana_dist.index)
    return ref_dist.reindex(all_ids, fill_value=0.0), ana_dist.reindex(all_ids, fill_value=0.0)


def simulation_drift_components(
    reference: pd.DataFrame,
    analytical: pd.DataFrame,
    weights: pd.Series | None = None,
) -> dict[str, float]:
    if analytical.empty:
        components = {
            "Delta_row": 1.0,
            "Delta_country": 1.0,
            "Delta_year": 1.0,
            "Delta_weight": np.nan,
            "Delta_balance": np.nan,
        }
        components["TDI"] = target_population_drift_index(components)
        return components

    ref_dist, ana_dist = _row_weight_distribution(reference, analytical, weights=weights)
    components = {
        "Delta_row": support_loss(len(analytical), len(reference)),
        "Delta_country": support_loss(analytical["geo"].nunique(), reference["geo"].nunique()),
        "Delta_year": support_loss(analytical["year"].nunique(), reference["year"].nunique()),
        "Delta_weight": jensen_shannon_divergence(ref_dist, ana_dist),
        "Delta_balance": average_absolute_smd(reference, analytical, [OUTCOME, TERM, "log_gdp_per_capita", "unemployment_rate_pc"]),
    }
    components["TDI"] = target_population_drift_index(components)
    return components


def estimator_target_frame(
    estimator: str,
    reference: pd.DataFrame,
    observed: pd.DataFrame,
    complete: pd.DataFrame,
) -> pd.DataFrame:
    if estimator in {"pmm_mi_fe", "mnar_shift_mi_fe"}:
        return reference.copy()
    return complete.copy()


def estimator_weights(estimator: str, observed: pd.DataFrame, complete: pd.DataFrame) -> pd.Series | None:
    if estimator == "population_weighted_fe" and POP_WEIGHT in complete.columns:
        return complete[POP_WEIGHT]
    if estimator == "ipw_fe":
        return ipw_weights(observed)
    return None


def simulate(replicates: int, m: int, seed: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    reference, target = load_reference_panel()
    reference_fit = fit_twfe_fast(reference)
    reference_coef = float(reference_fit["coef"])
    reference_rows = pd.DataFrame(
        [
            {
                "reference_coef": reference_coef,
                "reference_se": reference_fit["se"],
                "reference_rows": reference_fit["rows"],
                "reference_countries": reference_fit["countries"],
                "reference_years": reference_fit["years"],
            }
        ]
    )
    rows = []
    for mechanism in SIM_MECHANISMS:
        for replicate in range(replicates):
            rng = np.random.default_rng(seed + 1000 * SIM_MECHANISMS.index(mechanism) + replicate)
            mask = missingness_mask(reference, target, mechanism, rng)
            observed = apply_mask(reference, mask)
            complete = observed.dropna(subset=[OUTCOME] + BASELINE_COVARS).copy()
            distance = target_distance(reference, observed)
            estimator_weight_values = {
                "complete_case_fe": None,
                "population_weighted_fe": complete[POP_WEIGHT] if POP_WEIGHT in complete.columns else None,
                "ipw_fe": estimator_weights("ipw_fe", observed, complete),
                "pmm_mi_fe": None,
                "mnar_shift_mi_fe": None,
            }
            estimates = {
                "complete_case_fe": fit_twfe_fast(complete),
                "population_weighted_fe": fit_twfe_fast(complete, weights=estimator_weight_values["population_weighted_fe"]),
                "ipw_fe": fit_twfe_fast(complete, weights=estimator_weight_values["ipw_fe"]),
                "pmm_mi_fe": fit_pmm(observed, mask, seed=seed + replicate * 10, m=m, mnar=False),
                "mnar_shift_mi_fe": fit_pmm(observed, mask, seed=seed + replicate * 10 + 500, m=m, mnar=True),
            }
            for estimator, fit in estimates.items():
                coef = fit.get("coef", np.nan)
                ci_low = fit.get("ci_low", np.nan)
                ci_high = fit.get("ci_high", np.nan)
                estimated = fit.get("status") == "estimated" and pd.notna(coef)
                sign_reversal = bool(estimated and np.sign(float(coef)) != np.sign(reference_coef))
                ci_coverage = bool(estimated and float(ci_low) <= reference_coef <= float(ci_high))
                wrong_direction_excludes_zero = bool(
                    estimated
                    and (
                        (float(ci_low) > 0 and reference_coef < 0)
                        or (float(ci_high) < 0 and reference_coef > 0)
                    )
                )
                wrong_conclusion = bool(sign_reversal or wrong_direction_excludes_zero)
                analytical_target = estimator_target_frame(estimator, reference, observed, complete)
                drift = simulation_drift_components(
                    reference,
                    analytical_target,
                    weights=estimator_weight_values.get(estimator),
                )
                rows.append(
                    {
                        "mechanism": mechanism,
                        "replicate": replicate + 1,
                        "estimator": estimator,
                        "status": fit.get("status"),
                        "coef": coef,
                        "se": fit.get("se", np.nan),
                        "ci_low": ci_low,
                        "ci_high": ci_high,
                        "rows": fit.get("rows", 0),
                        "countries": fit.get("countries", 0),
                        "years": fit.get("years", 0),
                        "reference_coef": reference_coef,
                        "bias": float(coef) - reference_coef if estimated else np.nan,
                        "abs_error": abs(float(coef) - reference_coef) if estimated else np.nan,
                        "absolute_coefficient_error": abs(float(coef) - reference_coef) if estimated else np.nan,
                        "sign_reversal": sign_reversal if estimated else pd.NA,
                        "ci_coverage": ci_coverage if estimated else pd.NA,
                        "row_retention": len(complete) / len(reference),
                        "country_retention": complete["geo"].nunique() / reference["geo"].nunique() if not complete.empty else 0.0,
                        "year_retention": complete["year"].nunique() / reference["year"].nunique() if not complete.empty else 0.0,
                        "target_distance": distance,
                        "Delta_row": drift["Delta_row"],
                        "Delta_country": drift["Delta_country"],
                        "Delta_year": drift["Delta_year"],
                        "Delta_weight": drift["Delta_weight"],
                        "Delta_balance": drift["Delta_balance"],
                        "TDI": drift["TDI"],
                        "wrong_conclusion": wrong_conclusion if estimated else pd.NA,
                    }
                )
    return pd.DataFrame(rows), reference_rows


def summarize(results: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    estimated = results[results["status"].eq("estimated")].copy()
    counts = (
        results.assign(estimated=results["status"].eq("estimated"))
        .groupby(["mechanism", "estimator"], as_index=False)
        .agg(
            number_of_successful_replicates=("estimated", "sum"),
            total_replicates=("estimated", "size"),
        )
    )
    counts["number_of_failed_replicates"] = counts["total_replicates"] - counts["number_of_successful_replicates"]
    summary = (
        estimated.groupby(["mechanism", "estimator"], as_index=False)
        .agg(
            mean_TDI=("TDI", "mean"),
            mean_bias=("bias", "mean"),
            median_absolute_error=("abs_error", "median"),
            mean_rows=("rows", "mean"),
            mean_target_distance=("target_distance", "mean"),
            estimated_replicates=("coef", "size"),
        )
        .round(4)
    )
    sign = (
        estimated.groupby(["mechanism", "estimator"], as_index=False)["sign_reversal"]
        .mean()
        .rename(columns={"sign_reversal": "sign_reversal_rate"})
        .round(4)
    )
    coverage = (
        estimated.groupby(["mechanism", "estimator"], as_index=False)["ci_coverage"]
        .mean()
        .rename(columns={"ci_coverage": "ci_coverage_rate"})
        .round(4)
    )
    wrong = (
        estimated.groupby(["mechanism", "estimator"], as_index=False)["wrong_conclusion"]
        .mean()
        .rename(columns={"wrong_conclusion": "wrong_conclusion_rate"})
        .round(4)
    )
    validation = (
        counts.merge(summary, on=["mechanism", "estimator"], how="left")
        .merge(sign, on=["mechanism", "estimator"], how="left")
        .merge(coverage, on=["mechanism", "estimator"], how="left")
        .merge(wrong, on=["mechanism", "estimator"], how="left")
    )
    validation = validation[
        [
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
    ].round(4)
    return summary, sign, coverage, wrong, validation


def write_tables(summary: pd.DataFrame, sign: pd.DataFrame, coverage: pd.DataFrame, wrong: pd.DataFrame, validation: pd.DataFrame) -> None:
    main = summary.merge(sign, on=["mechanism", "estimator"], how="left").merge(coverage, on=["mechanism", "estimator"], how="left")
    main = main.merge(wrong, on=["mechanism", "estimator"], how="left")
    main_display = main[main["estimator"].isin(["complete_case_fe", "pmm_mi_fe", "mnar_shift_mi_fe"])].copy()
    main_display["mechanism_label"] = main_display["mechanism"].map(MECHANISM_LABELS).fillna(main_display["mechanism"])
    main_display["estimator_label"] = main_display["estimator"].map(ESTIMATOR_LABELS).fillna(main_display["estimator"])
    _write_tabular(
        main_display,
        ["mechanism_label", "estimator_label", "mean_bias", "median_absolute_error", "sign_reversal_rate", "ci_coverage_rate", "wrong_conclusion_rate"],
        ["Mechanism", "Estimator", "Mean bias", "Med. abs. error", "Sign rev.", "CI cov.", "Wrong concl."],
        TABLES / "simulation_main_summary.tex",
        r"p{0.19\linewidth}p{0.18\linewidth}rrrrr",
    )
    _write_tabular(
        summary[summary["estimator"].eq("complete_case_fe")],
        ["mechanism", "mean_bias", "median_absolute_error", "mean_rows", "mean_target_distance", "estimated_replicates"],
        ["Mechanism", "Mean bias", "Med. abs. error", "Rows", "Target dist.", "Reps"],
        TABLES / "simulation_complete_case_bias.tex",
        r"p{0.28\linewidth}rrrrr",
    )
    _write_tabular(
        validation,
        [
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
        ],
        ["Mechanism", "Estimator", "Mean TDI", "Mean bias", "Med. abs. error", "Sign rev.", "CI cov.", "Wrong concl.", "OK", "Failed"],
        TABLES / "simulation_validation_summary.tex",
        r"p{0.15\linewidth}p{0.14\linewidth}rrrrrrrr",
    )


def save_figures(results: pd.DataFrame, summary: pd.DataFrame) -> None:
    estimated = results[results["status"].eq("estimated")].copy()
    estimator_labels = {
        "complete_case_fe": "Complete-case FE",
        "population_weighted_fe": "Population-weighted FE",
        "ipw_fe": "IPW FE",
        "pmm_mi_fe": "PMM MI FE",
        "mnar_shift_mi_fe": "MNAR-shift MI FE",
    }
    mechanism_labels = {
        "mcar": "MCAR",
        "early_year": "Early-year",
        "country_group": "Country group",
        "covariate_block": "Covariate block",
        "mar_observed": "MAR observed",
        "mnar_high_poverty_unmet": "MNAR high poverty/unmet",
        "eurostat_realistic": "Eurostat-realistic",
    }
    estimated["estimator_label"] = estimated["estimator"].map(estimator_labels).fillna(estimated["estimator"])
    estimated["mechanism_label"] = estimated["mechanism"].map(mechanism_labels).fillna(estimated["mechanism"])
    plt.figure(figsize=(11, 5.8))
    sns.barplot(data=summary, x="mechanism", y="mean_bias", hue="estimator")
    plt.axhline(0, color="0.25", linewidth=1, linestyle=":")
    plt.xticks(rotation=25, ha="right")
    plt.ylabel("Mean bias relative to reference estimand")
    plt.xlabel("Missingness mechanism")
    plt.legend(title="", fontsize=7, ncol=2)
    plt.tight_layout()
    FIGURES.mkdir(parents=True, exist_ok=True)
    plt.savefig(FIGURES / "simulation_bias_by_mechanism.pdf")
    plt.close()

    plt.figure(figsize=(8.5, 5.8))
    sns.scatterplot(data=estimated, x="target_distance", y="abs_error", hue="mechanism", style="estimator", alpha=0.7)
    plt.xlabel("Target-distance score")
    plt.ylabel("Absolute coefficient error")
    plt.legend(title="", fontsize=7, bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.tight_layout()
    plt.savefig(FIGURES / "simulation_target_distance_vs_error.pdf")
    plt.close()

    tdi_summary_for_combined = pd.DataFrame()
    wrong_by_bin_for_combined = pd.DataFrame()
    estimator_order_for_combined: list[str] = []
    mechanism_order_for_combined: list[str] = []
    palette_for_combined: dict[str, object] = {}
    markers_for_combined: dict[str, str] = {}

    tdi_plot = estimated.dropna(subset=["TDI", "abs_error"]).copy()
    if not tdi_plot.empty:
        from matplotlib.lines import Line2D

        tdi_summary = (
            tdi_plot.groupby(["mechanism_label", "estimator_label"], as_index=False)
            .agg(
                mean_TDI=("TDI", "mean"),
                median_absolute_error=("abs_error", "median"),
                replicates=("abs_error", "size"),
            )
        )
        estimator_order = sorted(tdi_summary["estimator_label"].dropna().unique())
        mechanism_order = sorted(tdi_summary["mechanism_label"].dropna().unique())
        palette = dict(zip(estimator_order, sns.color_palette("tab10", n_colors=len(estimator_order))))
        marker_values = ["o", "s", "D", "^", "P", "X", "*", "v", "<", ">"]
        markers = dict(zip(mechanism_order, marker_values[: len(mechanism_order)]))
        tdi_summary_for_combined = tdi_summary.copy()
        estimator_order_for_combined = estimator_order
        mechanism_order_for_combined = mechanism_order
        palette_for_combined = palette
        markers_for_combined = markers

        fig, ax = plt.subplots(figsize=(7.2, 5.8))
        ax = sns.scatterplot(
            data=tdi_summary,
            x="mean_TDI",
            y="median_absolute_error",
            hue="estimator_label",
            style="mechanism_label",
            hue_order=estimator_order,
            style_order=mechanism_order,
            palette=palette,
            markers=markers,
            s=95,
            alpha=0.92,
            edgecolor="0.2",
            linewidth=0.45,
            legend=False,
            ax=ax,
        )
        ax.grid(True, color="0.88", linewidth=0.7)
        ax.tick_params(axis="both", labelsize=10)
        ax.set_xlabel("Mean Target-Population Drift Index (TDI)", fontsize=11)
        ax.set_ylabel("Median absolute coefficient error", fontsize=11)
        ax.set_title("Target drift and coefficient error by mechanism-estimator cell", fontsize=11.5, pad=8)
        ax.set_xlim(left=-0.01)
        ax.set_ylim(bottom=-0.01)
        estimator_handles = [
            Line2D(
                [0],
                [0],
                marker="o",
                color="white",
                label=label,
                markerfacecolor=palette[label],
                markeredgecolor="0.25",
                markersize=9,
                linestyle="None",
            )
            for label in estimator_order
        ]
        mechanism_handles = [
            Line2D(
                [0],
                [0],
                marker=markers[label],
                color="0.35",
                label=label,
                markerfacecolor="0.35",
                markeredgecolor="0.25",
                markersize=8.5,
                linestyle="None",
            )
            for label in mechanism_order
        ]
        estimator_legend = ax.legend(
            handles=estimator_handles,
            title="Estimator",
            fontsize=7.8,
            title_fontsize=8.6,
            ncol=3,
            loc="upper center",
            bbox_to_anchor=(0.5, -0.17),
            frameon=False,
        )
        ax.add_artist(estimator_legend)
        ax.legend(
            handles=mechanism_handles,
            title="Missingness mechanism",
            fontsize=7.5,
            title_fontsize=8.3,
            ncol=4,
            loc="upper center",
            bbox_to_anchor=(0.5, -0.32),
            frameon=False,
        )
        fig.subplots_adjust(left=0.12, right=0.98, top=0.90, bottom=0.35)
        fig.savefig(FIGURES / "simulation_tdi_vs_error.pdf", bbox_inches="tight", pad_inches=0.08)
        fig.savefig(FIGURES / "simulation_tdi_vs_error.png", dpi=300, bbox_inches="tight", pad_inches=0.08)
        plt.close()

    binned = estimated.dropna(subset=["TDI", "wrong_conclusion"]).copy()
    if not binned.empty:
        binned["TDI_bin"] = pd.cut(
            binned["TDI"],
            bins=[-0.001, 0.05, 0.10, 0.20, 0.40, np.inf],
            labels=["0-0.05", "0.05-0.10", "0.10-0.20", "0.20-0.40", ">0.40"],
        )
        wrong_by_bin = (
            binned.dropna(subset=["TDI_bin"])
            .groupby(["TDI_bin", "estimator"], observed=True)["wrong_conclusion"]
            .mean()
            .reset_index()
        )
        wrong_by_bin["estimator_label"] = wrong_by_bin["estimator"].map(estimator_labels).fillna(wrong_by_bin["estimator"])
        wrong_by_bin_for_combined = wrong_by_bin.copy()
        plt.figure(figsize=(7.2, 4.6))
        ax = sns.barplot(
            data=wrong_by_bin,
            x="TDI_bin",
            y="wrong_conclusion",
            hue="estimator_label",
            edgecolor="0.25",
            linewidth=0.4,
        )
        plt.xlabel("TDI bin")
        plt.ylabel("Wrong-conclusion probability")
        y_max = min(1.0, max(0.25, float(wrong_by_bin["wrong_conclusion"].max()) + 0.05))
        plt.ylim(0, y_max)
        plt.grid(axis="y", color="0.88", linewidth=0.6)
        ax.tick_params(axis="both", labelsize=10)
        ax.set_xlabel("TDI bin", fontsize=11)
        ax.set_ylabel("Wrong-conclusion probability", fontsize=11)
        plt.legend(
            title="Estimator",
            fontsize=8.6,
            title_fontsize=9.4,
            ncol=3,
            loc="upper center",
            bbox_to_anchor=(0.5, -0.16),
            frameon=False,
        )
        plt.tight_layout(rect=[0, 0.08, 1, 1])
        plt.savefig(FIGURES / "simulation_wrong_conclusion_by_tdi.pdf", bbox_inches="tight")
        plt.savefig(FIGURES / "simulation_wrong_conclusion_by_tdi.png", dpi=300, bbox_inches="tight")
        plt.close()

    if not tdi_summary_for_combined.empty and not wrong_by_bin_for_combined.empty:
        fig, axes = plt.subplots(1, 2, figsize=(11.4, 4.8), gridspec_kw={"width_ratios": [1.05, 1]})
        sns.scatterplot(
            data=tdi_summary_for_combined,
            x="mean_TDI",
            y="median_absolute_error",
            hue="estimator_label",
            style="mechanism_label",
            hue_order=estimator_order_for_combined,
            style_order=mechanism_order_for_combined,
            palette=palette_for_combined,
            markers=markers_for_combined,
            s=74,
            alpha=0.92,
            edgecolor="0.2",
            linewidth=0.4,
            legend=False,
            ax=axes[0],
        )
        axes[0].grid(True, color="0.88", linewidth=0.7)
        axes[0].set_title("A. TDI and coefficient error", fontsize=10.5)
        axes[0].set_xlabel("Mean TDI")
        axes[0].set_ylabel("Median absolute coefficient error")
        axes[0].set_xlim(left=-0.01)
        axes[0].set_ylim(bottom=-0.01)

        sns.barplot(
            data=wrong_by_bin_for_combined,
            x="TDI_bin",
            y="wrong_conclusion",
            hue="estimator_label",
            hue_order=estimator_order_for_combined,
            edgecolor="0.25",
            linewidth=0.35,
            ax=axes[1],
        )
        axes[1].grid(axis="y", color="0.88", linewidth=0.6)
        axes[1].set_title("B. Wrong conclusions by TDI bin", fontsize=10.5)
        axes[1].set_xlabel("TDI bin")
        axes[1].set_ylabel("Wrong-conclusion probability")
        y_max = min(1.0, max(0.25, float(wrong_by_bin_for_combined["wrong_conclusion"].max()) + 0.05))
        axes[1].set_ylim(0, y_max)
        axes[1].tick_params(axis="x", labelrotation=20)
        axes[1].get_legend().remove()

        from matplotlib.lines import Line2D

        estimator_handles = [
            Line2D(
                [0],
                [0],
                marker="o",
                color="white",
                label=label,
                markerfacecolor=palette_for_combined[label],
                markeredgecolor="0.25",
                markersize=7.8,
                linestyle="None",
            )
            for label in estimator_order_for_combined
        ]
        fig.legend(
            handles=estimator_handles,
            title="Estimator",
            fontsize=7.8,
            title_fontsize=8.5,
            ncol=5,
            loc="lower center",
            bbox_to_anchor=(0.5, -0.01),
            frameon=False,
        )
        fig.tight_layout(rect=[0, 0.10, 1, 1])
        fig.savefig(FIGURES / "simulation_tdi_validation_combined.pdf", bbox_inches="tight", pad_inches=0.08)
        fig.savefig(FIGURES / "simulation_tdi_validation_combined.png", dpi=300, bbox_inches="tight", pad_inches=0.08)
        plt.close()


def update_generation_map() -> None:
    map_path = OUTPUTS / "table_figure_generation_map.csv"
    new_rows = pd.DataFrame(
        [
            {
                "chapter_or_use": "chapters/modeling_strategy_results.tex",
                "output_type": "table",
                "output_file": "tables/simulation_validation_summary.tex",
                "script": "src/run_missingness_simulation.py",
                "input_file": "data/processed/panel_features_v2-3.csv",
            },
            {
                "chapter_or_use": "chapters/modeling_strategy_results.tex",
                "output_type": "figure",
                "output_file": "figures/simulation_tdi_validation_combined.pdf",
                "script": "src/run_missingness_simulation.py",
                "input_file": "data/processed/panel_features_v2-3.csv",
            },
            {
                "chapter_or_use": "outputs",
                "output_type": "figure",
                "output_file": "figures/simulation_bias_by_mechanism.pdf",
                "script": "src/run_missingness_simulation.py",
                "input_file": "data/processed/panel_features_v2-3.csv",
            },
            {
                "chapter_or_use": "outputs",
                "output_type": "figure",
                "output_file": "figures/simulation_tdi_vs_error.pdf",
                "script": "src/run_missingness_simulation.py",
                "input_file": "data/processed/panel_features_v2-3.csv",
            },
            {
                "chapter_or_use": "outputs",
                "output_type": "figure",
                "output_file": "figures/simulation_wrong_conclusion_by_tdi.pdf",
                "script": "src/run_missingness_simulation.py",
                "input_file": "data/processed/panel_features_v2-3.csv",
            },
        ]
    )
    if map_path.exists():
        existing = pd.read_csv(map_path)
        existing = existing[~existing["output_file"].isin(new_rows["output_file"])]
        updated = pd.concat([existing, new_rows], ignore_index=True)
    else:
        updated = new_rows
    updated.sort_values(["chapter_or_use", "output_type", "output_file"]).to_csv(map_path, index=False)


def write_outputs(results: pd.DataFrame, reference: pd.DataFrame, prefix: str = "") -> None:
    stem = f"{prefix}_" if prefix else ""
    results.to_csv(OUTPUTS / f"{stem}simulation_results.csv", index=False)
    reference.to_csv(OUTPUTS / f"{stem}simulation_reference_estimand.csv", index=False)
    summary, sign, coverage, wrong, validation = summarize(results)
    summary.to_csv(OUTPUTS / f"{stem}simulation_bias_summary.csv", index=False)
    sign.to_csv(OUTPUTS / f"{stem}simulation_sign_reversal.csv", index=False)
    coverage.to_csv(OUTPUTS / f"{stem}simulation_ci_coverage.csv", index=False)
    wrong.to_csv(OUTPUTS / f"{stem}simulation_wrong_conclusion.csv", index=False)
    validation.to_csv(OUTPUTS / f"{stem}simulation_validation_summary.csv", index=False)
    if not prefix:
        write_tables(summary, sign, coverage, wrong, validation)
        save_figures(results, summary)
        update_generation_map()
        (OUTPUTS / "simulation_runtime_notes.txt").write_text(
            "The semi-synthetic simulation reports a reference estimand from the complete artificial panel. "
            "Imputation-based estimators are included as sensitivity benchmarks; the default low imputation count "
            "is used for reproducible thesis-runtime feasibility and should not be interpreted as a definitive MI "
            "stability analysis by itself.\n",
            encoding="utf-8",
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run semi-synthetic missingness simulation.")
    parser.add_argument("--replicates", type=int, default=100)
    parser.add_argument("--imputations", type=int, default=2)
    parser.add_argument("--seed", type=int, default=RANDOM_SEED)
    parser.add_argument("--prefix", default="")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    TABLES.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    results, reference = simulate(args.replicates, args.imputations, args.seed)
    write_outputs(results, reference, args.prefix)
    print(f"simulation replicates per mechanism: {args.replicates}")
    print(f"reference coef: {reference.loc[0, 'reference_coef']:.6f}")
    print(f"estimated rows: {(results['status'] == 'estimated').sum()} / {len(results)}")


if __name__ == "__main__":
    main()
