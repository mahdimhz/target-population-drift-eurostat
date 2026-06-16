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
            estimates = {
                "complete_case_fe": fit_twfe_fast(complete),
                "population_weighted_fe": fit_twfe_fast(complete, weights=complete[POP_WEIGHT] if POP_WEIGHT in complete.columns else None),
                "ipw_fe": fit_twfe_fast(complete, weights=ipw_weights(observed)),
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
                wrong_conclusion = bool(sign_reversal or (estimated and np.sign(float(coef)) != np.sign(reference_coef) and not (float(ci_low) <= 0 <= float(ci_high))))
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
                        "sign_reversal": sign_reversal if estimated else pd.NA,
                        "ci_coverage": ci_coverage if estimated else pd.NA,
                        "row_retention": len(complete) / len(reference),
                        "country_retention": complete["geo"].nunique() / reference["geo"].nunique() if not complete.empty else 0.0,
                        "year_retention": complete["year"].nunique() / reference["year"].nunique() if not complete.empty else 0.0,
                        "target_distance": distance,
                        "wrong_conclusion": wrong_conclusion if estimated else pd.NA,
                    }
                )
    return pd.DataFrame(rows), reference_rows


def summarize(results: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    estimated = results[results["status"].eq("estimated")].copy()
    summary = (
        estimated.groupby(["mechanism", "estimator"], as_index=False)
        .agg(
            mean_bias=("bias", "mean"),
            median_abs_error=("abs_error", "median"),
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
    return summary, sign, coverage, wrong


def write_tables(summary: pd.DataFrame, sign: pd.DataFrame, coverage: pd.DataFrame, wrong: pd.DataFrame) -> None:
    main = summary.merge(sign, on=["mechanism", "estimator"], how="left").merge(coverage, on=["mechanism", "estimator"], how="left")
    main = main.merge(wrong, on=["mechanism", "estimator"], how="left")
    main_display = main[main["estimator"].isin(["complete_case_fe", "pmm_mi_fe", "mnar_shift_mi_fe"])].copy()
    _write_tabular(
        main_display,
        ["mechanism", "estimator", "mean_bias", "median_abs_error", "sign_reversal_rate", "ci_coverage_rate", "wrong_conclusion_rate"],
        ["Mechanism", "Estimator", "Mean bias", "Med. abs. error", "Sign rev.", "CI cov.", "Wrong concl."],
        TABLES / "simulation_main_summary.tex",
        r"p{0.19\linewidth}p{0.18\linewidth}rrrrr",
    )
    _write_tabular(
        summary[summary["estimator"].eq("complete_case_fe")],
        ["mechanism", "mean_bias", "median_abs_error", "mean_rows", "mean_target_distance", "estimated_replicates"],
        ["Mechanism", "Mean bias", "Med. abs. error", "Rows", "Target dist.", "Reps"],
        TABLES / "simulation_complete_case_bias.tex",
        r"p{0.28\linewidth}rrrrr",
    )


def save_figures(results: pd.DataFrame, summary: pd.DataFrame) -> None:
    estimated = results[results["status"].eq("estimated")].copy()
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


def write_outputs(results: pd.DataFrame, reference: pd.DataFrame, prefix: str = "") -> None:
    stem = f"{prefix}_" if prefix else ""
    results.to_csv(OUTPUTS / f"{stem}simulation_results.csv", index=False)
    reference.to_csv(OUTPUTS / f"{stem}simulation_reference_estimand.csv", index=False)
    summary, sign, coverage, wrong = summarize(results)
    summary.to_csv(OUTPUTS / f"{stem}simulation_bias_summary.csv", index=False)
    sign.to_csv(OUTPUTS / f"{stem}simulation_sign_reversal.csv", index=False)
    coverage.to_csv(OUTPUTS / f"{stem}simulation_ci_coverage.csv", index=False)
    wrong.to_csv(OUTPUTS / f"{stem}simulation_wrong_conclusion.csv", index=False)
    if not prefix:
        write_tables(summary, sign, coverage, wrong)
        save_figures(results, summary)


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
