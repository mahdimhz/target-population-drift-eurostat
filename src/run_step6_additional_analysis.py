from __future__ import annotations

import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

ROOT = Path(__file__).resolve().parents[1]
DATA_PROCESSED = ROOT / "data" / "processed"
OUTPUTS = ROOT / "outputs"
FIGURES = ROOT / "figures"
TABLES = ROOT / "tables"
ERROR_LOG = OUTPUTS / "analysis_errors.log"

for folder in [OUTPUTS, FIGURES, TABLES]:
    folder.mkdir(parents=True, exist_ok=True)

OUTCOME = "unmet_need_pc"
BASELINE_COVARS = [
    "log_gdp_per_capita",
    "unemployment_rate_pc",
    "poverty_or_social_exclusion_pc",
    "government_health_expenditure_gdp_pc",
    "compulsory_health_financing_gdp_pc",
]


def log_error(message: str) -> None:
    existing = ERROR_LOG.read_text(encoding="utf-8") if ERROR_LOG.exists() else ""
    if existing.strip() == "No errors encountered.":
        existing = ""
    ERROR_LOG.write_text(existing + message.rstrip() + "\n", encoding="utf-8")


def ensure_clean_error_log_if_empty() -> None:
    if not ERROR_LOG.exists() or ERROR_LOG.read_text(encoding="utf-8").strip() == "":
        ERROR_LOG.write_text("No errors encountered.\n", encoding="utf-8")


def write_latex(df: pd.DataFrame, path: Path, caption: str, label: str) -> None:
    path.write_text(
        df.to_latex(
            index=False,
            escape=True,
            caption=caption,
            label=label,
            float_format=lambda x: f"{x:.3f}",
            na_rep="",
        ),
        encoding="utf-8",
    )


def format_p_value(p_value: float) -> str:
    if pd.isna(p_value):
        return ""
    if p_value < 0.001:
        return "<0.001"
    return f"{p_value:.3f}"


def year_and_trend(panel: pd.DataFrame) -> None:
    summary = (
        panel.dropna(subset=[OUTCOME])
        .groupby("year")[OUTCOME]
        .agg(
            mean="mean",
            median="median",
            p10=lambda s: s.quantile(0.10),
            p90=lambda s: s.quantile(0.90),
            countries="count",
        )
        .reset_index()
    )
    summary.to_csv(OUTPUTS / "year_trend_summary.csv", index=False)

    tau, p_value = stats.kendalltau(summary["year"], summary["mean"])
    slope, intercept, r_value, slope_p, stderr = stats.linregress(summary["year"], summary["mean"])
    direction = "decline" if slope < 0 else "increase"
    significant = p_value < 0.05
    text = [
        "Trend test for annual mean unmet medical need.",
        "Method: scipy Kendall tau as Mann-Kendall style monotonic trend test.",
        f"Kendall tau: {tau:.6f}",
        f"p-value: {p_value:.6f}",
        f"Linear slope: {slope:.6f} percentage points per year",
        f"Linear slope p-value: {format_p_value(slope_p)}",
        f"Conclusion: {'significant' if significant else 'not significant'} monotonic {direction} at alpha=0.05.",
    ]
    (OUTPUTS / "trend_test_results.txt").write_text("\n".join(text) + "\n", encoding="utf-8")

    plt.figure(figsize=(8.5, 4.8))
    plt.fill_between(summary["year"], summary["p10"], summary["p90"], color="#56B4E9", alpha=0.25, label="p10-p90")
    plt.plot(summary["year"], summary["mean"], marker="o", color="#0072B2", linewidth=2, label="Mean")
    plt.plot(summary["year"], summary["median"], marker="s", color="#009E73", linewidth=1.5, label="Median")
    plt.xlabel("Year")
    plt.ylabel("Unmet medical need (%)")
    plt.legend(frameon=False)
    plt.grid(axis="y", alpha=0.25)
    plt.tight_layout()
    plt.savefig(FIGURES / "descriptive_trend_with_bands.pdf", dpi=300)
    plt.close()


def convergence_analysis(panel: pd.DataFrame) -> None:
    observed = panel.dropna(subset=[OUTCOME]).copy()
    sigma = observed.groupby("year", as_index=False)[OUTCOME].std().rename(columns={OUTCOME: "sd_unmet_need_pc"})
    sigma["countries"] = observed.groupby("year")[OUTCOME].count().values
    sigma.to_csv(OUTPUTS / "convergence_sigma.csv", index=False)

    plt.figure(figsize=(8, 4.5))
    plt.plot(sigma["year"], sigma["sd_unmet_need_pc"], marker="o", color="#D55E00", linewidth=2)
    plt.xlabel("Year")
    plt.ylabel("Cross-country SD of unmet medical need (%)")
    plt.grid(axis="y", alpha=0.25)
    plt.tight_layout()
    plt.savefig(FIGURES / "convergence_sigma.pdf", dpi=300)
    plt.close()

    first = observed.sort_values("year").groupby("geo", as_index=False).first()[["geo", "year", OUTCOME]]
    last = observed.sort_values("year").groupby("geo", as_index=False).last()[["geo", "year", OUTCOME]]
    beta = first.merge(last, on="geo", suffixes=("_initial", "_final"))
    beta = beta[beta["year_final"] > beta["year_initial"]].copy()
    beta["change_unmet_need_pc"] = beta[f"{OUTCOME}_final"] - beta[f"{OUTCOME}_initial"]
    x = sm.add_constant(beta[[f"{OUTCOME}_initial"]])
    model = sm.OLS(beta["change_unmet_need_pc"], x).fit()
    coef = model.params[f"{OUTCOME}_initial"]
    conclusion = "beta-convergence pattern" if coef < 0 else "no beta-convergence pattern"
    text = [
        "Beta-convergence regression: change in unmet_need_pc on initial unmet_need_pc.",
        f"N countries: {int(model.nobs)}",
        f"Initial-level coefficient: {coef:.6f}",
        f"SE: {model.bse[f'{OUTCOME}_initial']:.6f}",
        f"p-value: {format_p_value(model.pvalues[f'{OUTCOME}_initial'])}",
        f"R2: {model.rsquared:.6f}",
        f"Conclusion: {conclusion}.",
    ]
    (OUTPUTS / "convergence_beta_result.txt").write_text("\n".join(text) + "\n", encoding="utf-8")


def citizenship_gap_analysis(panel: pd.DataFrame, cit: pd.DataFrame) -> None:
    wide = cit.pivot_table(index=["country", "year"], columns="citizen_group", values=OUTCOME, aggfunc="mean")
    gap = wide.reset_index()
    if "NEU_FOR" not in gap.columns or "NAT" not in gap.columns:
        raise ValueError("Citizenship data lacks NAT or NEU_FOR columns.")
    gap["gap_neu_for_minus_nat"] = gap["NEU_FOR"] - gap["NAT"]
    gap_out = gap[["country", "year", "NAT", "NEU_FOR", "gap_neu_for_minus_nat"]].dropna(subset=["gap_neu_for_minus_nat"])
    gap_out.to_csv(OUTPUTS / "citizenship_gap_by_country_year.csv", index=False)

    intercept = smf.ols("gap_neu_for_minus_nat ~ 1", data=gap_out).fit(
        cov_type="cluster",
        cov_kwds={"groups": gap_out["country"], "use_correction": True},
    )
    year_adjusted = smf.ols("gap_neu_for_minus_nat ~ C(year)", data=gap_out).fit(
        cov_type="cluster",
        cov_kwds={"groups": gap_out["country"], "use_correction": True},
    )
    clustered_rows = []
    for label, model in [
        ("Intercept-only paired country-year gap", intercept),
        ("Year-adjusted paired country-year gap", year_adjusted),
    ]:
        clustered_rows.append(
            {
                "model": label,
                "term": "Intercept",
                "coef": float(model.params["Intercept"]),
                "se": float(model.bse["Intercept"]),
                "t_stat": float(model.tvalues["Intercept"]),
                "p_value_two_sided": float(model.pvalues["Intercept"]),
                "nobs": int(model.nobs),
                "countries": gap_out["country"].nunique(),
            }
        )
    clustered = pd.DataFrame(clustered_rows)
    clustered.to_csv(OUTPUTS / "citizenship_gap_clustered.csv", index=False)
    clustered_table = clustered.copy()
    clustered_table["p_value_two_sided"] = clustered_table["p_value_two_sided"].map(format_p_value)
    write_latex(
        clustered_table,
        TABLES / "citizenship_gap_clustered.tex",
        "Clustered paired country-year citizenship-gap models",
        "tab:citizenship_gap_clustered",
    )

    mean_gap = gap_out["gap_neu_for_minus_nat"].mean()
    text = [
        "Clustered paired country-year models for citizenship gap (NEU_FOR minus NAT).",
        f"N country-years: {len(gap_out)}",
        f"N countries: {gap_out['country'].nunique()}",
        f"Mean gap: {mean_gap:.6f}",
        f"Intercept-only clustered coefficient: {clustered_rows[0]['coef']:.6f}",
        f"Intercept-only clustered SE: {clustered_rows[0]['se']:.6f}",
        f"Intercept-only two-sided p-value: {format_p_value(clustered_rows[0]['p_value_two_sided'])}",
        f"Year-adjusted clustered coefficient: {clustered_rows[1]['coef']:.6f}",
        f"Year-adjusted clustered SE: {clustered_rows[1]['se']:.6f}",
        f"Year-adjusted two-sided p-value: {format_p_value(clustered_rows[1]['p_value_two_sided'])}",
    ]
    (OUTPUTS / "citizenship_gap_ttest.txt").write_text("\n".join(text) + "\n", encoding="utf-8")

    panel_country = (
        panel.groupby("geo", as_index=False)[
            [
                "log_gdp_per_capita",
                "gdp_per_capita_eur",
                "oop_health_expenditure_share_pc",
                "gini_income",
                "government_health_expenditure_gdp_pc",
                "poverty_or_social_exclusion_pc",
            ]
        ]
        .mean()
        .rename(columns={"geo": "country"})
    )
    gap_country = gap_out.groupby("country", as_index=False)["gap_neu_for_minus_nat"].mean()
    merged = gap_country.merge(panel_country, on="country", how="inner")
    reg_df = merged[["gap_neu_for_minus_nat", "log_gdp_per_capita", "oop_health_expenditure_share_pc"]].dropna()
    model = smf.ols("gap_neu_for_minus_nat ~ log_gdp_per_capita + oop_health_expenditure_share_pc", data=reg_df).fit()
    rows = []
    for term in model.params.index:
        rows.append(
            {
                "term": term,
                "coef": model.params[term],
                "se": model.bse[term],
                "t_stat": model.tvalues[term],
                "p_value": model.pvalues[term],
                "nobs": int(model.nobs),
                "r2": model.rsquared,
            }
        )
    reg_out = pd.DataFrame(rows)
    reg_out.to_csv(OUTPUTS / "citizenship_gap_regression.csv", index=False)
    write_latex(
        reg_out,
        TABLES / "citizenship_gap_regression.tex",
        "Cross-national regression of citizenship gaps in unmet medical need",
        "tab:citizenship_gap_regression",
    )

    corr_vars = [
        "gdp_per_capita_eur",
        "oop_health_expenditure_share_pc",
        "gini_income",
        "government_health_expenditure_gdp_pc",
        "poverty_or_social_exclusion_pc",
    ]
    corr_rows = []
    for var in corr_vars:
        temp = merged[["gap_neu_for_minus_nat", var]].dropna()
        r, p = stats.pearsonr(temp["gap_neu_for_minus_nat"], temp[var]) if len(temp) >= 3 else (np.nan, np.nan)
        corr_rows.append({"variable": var, "pearson_r": r, "p_value": p, "n": len(temp)})
    corr = pd.DataFrame(corr_rows)
    corr.to_csv(OUTPUTS / "citizenship_gap_correlations.csv", index=False)

    heat = corr.set_index("variable")[["pearson_r"]]
    plt.figure(figsize=(4.8, 3.4))
    sns.heatmap(heat, annot=True, fmt=".2f", cmap="vlag", vmin=-1, vmax=1, center=0, cbar_kws={"label": "Pearson r"})
    plt.ylabel("")
    plt.tight_layout()
    plt.savefig(FIGURES / "citizenship_gap_correlations.pdf", dpi=300)
    plt.close()


def fe_coefficient_plot() -> None:
    fe_path = OUTPUTS / "regression_fe_full.csv"
    if not fe_path.exists():
        raise FileNotFoundError("outputs/regression_fe_full.csv not found.")
    fe = pd.read_csv(fe_path)
    plot = fe[fe["term"].isin(BASELINE_COVARS)].copy()
    if plot.empty:
        raise ValueError("No baseline covariates found in regression_fe_full.csv.")
    plot["ci_low"] = plot["coef"] - 1.96 * plot["se"]
    plot["ci_high"] = plot["coef"] + 1.96 * plot["se"]
    plot = plot.sort_values("coef")
    y = np.arange(len(plot))
    plt.figure(figsize=(8, 4.8))
    plt.errorbar(
        plot["coef"],
        y,
        xerr=[plot["coef"] - plot["ci_low"], plot["ci_high"] - plot["coef"]],
        fmt="o",
        color="#0072B2",
        ecolor="#555555",
        capsize=3,
    )
    plt.axvline(0, color="black", linestyle="--", linewidth=1)
    plt.yticks(y, plot["term"])
    plt.xlabel("Coefficient estimate with 95% CI")
    plt.tight_layout()
    plt.savefig(FIGURES / "regression_fe_coefficient_plot.pdf", dpi=300)
    plt.close()


def panel_heterogeneity(panel: pd.DataFrame) -> None:
    heter = (
        panel.dropna(subset=[OUTCOME])
        .groupby("geo", as_index=False)[OUTCOME]
        .agg(mean_unmet_need_pc="mean", sd_unmet_need_pc="std", years="count")
    )
    plt.figure(figsize=(8, 5.8))
    plt.scatter(heter["mean_unmet_need_pc"], heter["sd_unmet_need_pc"], color="#0072B2", alpha=0.8)
    for _, row in heter.iterrows():
        plt.text(row["mean_unmet_need_pc"], row["sd_unmet_need_pc"], row["geo"], fontsize=8, ha="left", va="bottom")
    plt.xlabel("Country mean unmet medical need (%)")
    plt.ylabel("Within-country SD")
    plt.grid(alpha=0.2)
    plt.tight_layout()
    plt.savefig(FIGURES / "panel_heterogeneity.pdf", dpi=300)
    plt.close()


def main() -> None:
    panel = pd.read_csv(DATA_PROCESSED / "panel_features_v2-3.csv")
    cit = pd.read_csv(DATA_PROCESSED / "citizenship_unmet_need.csv")

    for label, func in [
        ("Step 6a year and trend analysis", lambda: year_and_trend(panel)),
        ("Step 6b convergence analysis", lambda: convergence_analysis(panel)),
        ("Step 6c/6d citizenship gap analysis", lambda: citizenship_gap_analysis(panel, cit)),
        ("Step 6e FE coefficient plot", fe_coefficient_plot),
        ("Step 6f panel heterogeneity figure", lambda: panel_heterogeneity(panel)),
    ]:
        try:
            func()
        except Exception as exc:
            log_error(f"{label} failed: {exc}")

    ensure_clean_error_log_if_empty()
    print("STEP 6 COMPLETE")


if __name__ == "__main__":
    main()
