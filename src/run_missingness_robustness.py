from __future__ import annotations

import math
import re
import warnings
from collections.abc import Iterable
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import statsmodels.formula.api as smf
from scipy import stats
from sklearn.impute import SimpleImputer
from sklearn.linear_model import BayesianRidge, LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

ROOT = Path(__file__).resolve().parents[1]
DATA_PROCESSED = ROOT / "data" / "processed"
OUTPUTS = ROOT / "outputs"
FIGURES = ROOT / "figures"
TABLES = ROOT / "tables"

for folder in [OUTPUTS, FIGURES, TABLES]:
    folder.mkdir(parents=True, exist_ok=True)

RANDOM_SEED = 42
OUTCOME = "unmet_need_pc"
POPULATION = "population_total"
POP_WEIGHT = "population_weight_year_norm"
BASELINE_COVARS = [
    "log_gdp_per_capita",
    "unemployment_rate_pc",
    "poverty_or_social_exclusion_pc",
    "government_health_expenditure_gdp_pc",
    "compulsory_health_financing_gdp_pc",
]
EU27 = {
    "AT",
    "BE",
    "BG",
    "CY",
    "CZ",
    "DE",
    "DK",
    "EE",
    "EL",
    "ES",
    "FI",
    "FR",
    "HR",
    "HU",
    "IE",
    "IT",
    "LT",
    "LU",
    "LV",
    "MT",
    "NL",
    "PL",
    "PT",
    "RO",
    "SE",
    "SI",
    "SK",
}
EEA_COUNTRIES = {"IS", "NO"}
SWITZERLAND = {"CH"}
UK_COUNTRIES = {"UK"}
CANDIDATE_POTENTIAL = {"AL", "BA", "ME", "MK", "RS", "TR", "XK"}
MIN_FE_ROWS = 50
MIN_FE_COUNTRIES = 8
MIN_FE_YEARS = 3
IMPUTE_VARS = [
    "log_gdp_per_capita",
    "unemployment_rate_pc",
    "poverty_or_social_exclusion_pc",
    "government_health_expenditure_gdp_pc",
    "compulsory_health_financing_gdp_pc",
    "gini_income",
    "physicians_per_100k",
    "hospital_beds_per_100k",
    "oop_health_expenditure_share_pc",
    "long_term_unemployment_rate_pc",
]
IMPUTATION_BOUNDS = {
    "log_gdp_per_capita": (7.0, 12.3),
    "gdp_per_capita_eur": (math.exp(7.0), math.exp(12.3)),
    "unemployment_rate_pc": (0.0, 40.0),
    "poverty_or_social_exclusion_pc": (0.0, 60.0),
    "government_health_expenditure_gdp_pc": (0.0, 15.0),
    "compulsory_health_financing_gdp_pc": (0.0, 15.0),
    "gini_income": (0.0, 60.0),
    "physicians_per_100k": (0.0, 1000.0),
    "hospital_beds_per_100k": (0.0, 1500.0),
    "oop_health_expenditure_share_pc": (0.0, 60.0),
    "long_term_unemployment_rate_pc": (0.0, 30.0),
    OUTCOME: (0.0, 100.0),
}
WEST_NORTH = {
    "AT",
    "BE",
    "CH",
    "DE",
    "DK",
    "FI",
    "FR",
    "IE",
    "IS",
    "LU",
    "NL",
    "NO",
    "SE",
    "UK",
}
EAST_SOUTH = {
    "AL",
    "BA",
    "BG",
    "CY",
    "CZ",
    "EE",
    "EL",
    "ES",
    "HR",
    "HU",
    "IT",
    "LT",
    "LV",
    "ME",
    "MK",
    "MT",
    "PL",
    "PT",
    "RO",
    "RS",
    "SI",
    "SK",
    "TR",
    "XK",
}


def effective_sample_size(weights: Iterable[float]) -> float:
    arr = np.asarray(list(weights), dtype=float)
    if arr.size == 0 or np.square(arr).sum() == 0:
        return float("nan")
    return float(np.square(arr.sum()) / np.square(arr).sum())


def rubin_components(estimates: Iterable[float], ses: Iterable[float]) -> dict[str, float]:
    q = pd.Series(list(estimates), dtype=float).dropna()
    u = pd.Series(list(ses), dtype=float).dropna() ** 2
    if len(q) == 0 or len(q) != len(u):
        return {
            "estimate": np.nan,
            "se": np.nan,
            "statistic": np.nan,
            "df": np.nan,
            "p_value": np.nan,
            "m": np.nan,
            "within_variance": np.nan,
            "between_variance": np.nan,
            "total_variance": np.nan,
            "relative_increase_variance": np.nan,
            "fraction_missing_information": np.nan,
        }
    m = len(q)
    q_bar = float(q.mean())
    u_bar = float(u.mean())
    between = float(q.var(ddof=1)) if m > 1 else 0.0
    total_var = u_bar + (1 + 1 / m) * between
    se = math.sqrt(total_var) if total_var >= 0 else np.nan
    statistic = q_bar / se if se and se > 0 else np.nan
    df = (m - 1) * (1 + u_bar / ((1 + 1 / m) * between)) ** 2 if between > 0 else np.inf
    p_value = (
        2 * (1 - stats.t.cdf(abs(statistic), df))
        if np.isfinite(df)
        else 2 * (1 - stats.norm.cdf(abs(statistic)))
    )
    relative_increase = ((1 + 1 / m) * between / u_bar) if u_bar > 0 else np.nan
    fraction_missing = ((1 + 1 / m) * between / total_var) if total_var > 0 else np.nan
    return {
        "estimate": q_bar,
        "se": se,
        "statistic": statistic,
        "df": float(df),
        "p_value": float(p_value),
        "m": float(m),
        "within_variance": u_bar,
        "between_variance": between,
        "total_variance": total_var,
        "relative_increase_variance": float(relative_increase),
        "fraction_missing_information": float(fraction_missing),
    }


def rubin_pool(estimates: Iterable[float], ses: Iterable[float]) -> dict[str, float]:
    pooled = rubin_components(estimates, ses)
    return {
        "estimate": pooled["estimate"],
        "se": pooled["se"],
        "statistic": pooled["statistic"],
        "df": pooled["df"],
        "p_value": pooled["p_value"],
    }


def format_p_value(p_value: float) -> str:
    if pd.isna(p_value):
        return ""
    if p_value < 0.001:
        return "<0.001"
    return f"{p_value:.3f}"


def country_group(geo: str) -> str:
    if geo in WEST_NORTH:
        return "Western/Northern"
    if geo in EAST_SOUTH:
        return "Eastern/Southern"
    return "Other"


def country_universe_category(geo: str) -> str:
    if geo in EU27:
        return "EU-27"
    if geo in EEA_COUNTRIES:
        return "EEA country"
    if geo in SWITZERLAND:
        return "Switzerland"
    if geo in UK_COUNTRIES:
        return "UK"
    if geo in CANDIDATE_POTENTIAL:
        return "Candidate/potential candidate"
    return "Other Eurostat-available national unit"


def bool_label(value: bool) -> str:
    return "yes" if value else "no"


def safe_patsy_column(name: object) -> str:
    cleaned = re.sub(r"\W+", "_", str(name)).strip("_")
    if not cleaned:
        cleaned = "x"
    if cleaned[0].isdigit():
        cleaned = f"x_{cleaned}"
    return cleaned


def model_sample(df: pd.DataFrame) -> pd.DataFrame:
    extra = [POP_WEIGHT] if POP_WEIGHT in df.columns else []
    return df[["geo", "year", OUTCOME] + BASELINE_COVARS + extra].dropna(subset=[OUTCOME] + BASELINE_COVARS).copy()


def fit_fe(df: pd.DataFrame, weights: np.ndarray | None = None):
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


def feasible_fe_sample(df: pd.DataFrame) -> tuple[bool, str]:
    if len(df) < MIN_FE_ROWS:
        return False, f"infeasible: fewer than {MIN_FE_ROWS} observations"
    if df["geo"].nunique() < MIN_FE_COUNTRIES:
        return False, f"infeasible: fewer than {MIN_FE_COUNTRIES} countries"
    if df["year"].nunique() < MIN_FE_YEARS:
        return False, f"infeasible: fewer than {MIN_FE_YEARS} years"
    return True, "estimated"


def fit_fe_with_covars(
    df: pd.DataFrame,
    covars: list[str],
    weights: np.ndarray | None = None,
    country_trends: bool = False,
):
    work = df.copy()
    trend_term = ""
    if country_trends:
        work["year_centered"] = work["year"] - work["year"].mean()
        trend_term = " + C(geo):year_centered"
    formula = f"{OUTCOME} ~ {' + '.join(covars)} + C(geo) + C(year){trend_term}"
    if weights is None:
        return smf.ols(formula, data=work).fit(
            cov_type="cluster",
            cov_kwds={"groups": work["geo"], "use_correction": True},
        )
    return smf.wls(formula, data=work, weights=weights).fit(
        cov_type="cluster",
        cov_kwds={"groups": work["geo"], "use_correction": True},
    )


def fit_pooled_year(df: pd.DataFrame):
    formula = f"{OUTCOME} ~ {' + '.join(BASELINE_COVARS)} + C(year)"
    return smf.ols(formula, data=df).fit(
        cov_type="cluster",
        cov_kwds={"groups": df["geo"], "use_correction": True},
    )


def fit_country_fe(df: pd.DataFrame):
    formula = f"{OUTCOME} ~ {' + '.join(BASELINE_COVARS)} + C(geo)"
    return smf.ols(formula, data=df).fit(
        cov_type="cluster",
        cov_kwds={"groups": df["geo"], "use_correction": True},
    )


def term_summary(label: str, result, df: pd.DataFrame, term: str = "poverty_or_social_exclusion_pc") -> dict[str, float | str]:
    return {
        "specification": label,
        "term": term,
        "coef": float(result.params[term]),
        "se": float(result.bse[term]),
        "p_value": float(result.pvalues[term]),
        "ci_low": float(result.conf_int().loc[term, 0]),
        "ci_high": float(result.conf_int().loc[term, 1]),
        "nobs": int(result.nobs),
        "countries": int(df["geo"].nunique()),
    }


def fe_formula(covars: list[str] | None = None, outcome: str = OUTCOME) -> str:
    covars = covars or BASELINE_COVARS
    return f"{outcome} ~ {' + '.join(covars)} + C(geo) + C(year)"


def within_r2(df: pd.DataFrame, covars: list[str] | None = None) -> float:
    covars = covars or BASELINE_COVARS
    resid = {}
    for var in [OUTCOME] + covars:
        resid[var] = smf.ols(f"{var} ~ C(geo) + C(year)", data=df).fit().resid
    y = resid[OUTCOME]
    x = pd.DataFrame({var: resid[var] for var in covars})
    fit = smf.ols("y ~ " + " + ".join([f"Q('{c}')" for c in x.columns]), data=pd.concat([y.rename("y"), x], axis=1)).fit()
    return float(fit.rsquared)


def between_r2(df: pd.DataFrame, covars: list[str] | None = None) -> float:
    covars = covars or BASELINE_COVARS
    means = df.groupby("geo", as_index=False)[[OUTCOME] + covars].mean(numeric_only=True).dropna()
    if len(means) <= len(covars) + 1:
        return np.nan
    fit = smf.ols(f"{OUTCOME} ~ {' + '.join(covars)}", data=means).fit()
    return float(fit.rsquared)


def fe_fit_diagnostics(df: pd.DataFrame, result) -> pd.DataFrame:
    years_per_country = df.groupby("geo")["year"].nunique()
    out = pd.DataFrame(
        [
            {
                "model": "Baseline complete-case country-and-year FE",
                "nobs": int(result.nobs),
                "countries": int(df["geo"].nunique()),
                "years": int(df["year"].nunique()),
                "avg_years_per_country": float(years_per_country.mean()),
                "min_years_per_country": int(years_per_country.min()),
                "max_years_per_country": int(years_per_country.max()),
                "within_r2": within_r2(df),
                "between_r2": between_r2(df),
                "overall_r2": float(result.rsquared),
            }
        ]
    )
    out.to_csv(OUTPUTS / "fe_fit_diagnostics.csv", index=False)

    row = out.iloc[0]
    lines = [
        r"\resizebox{\textwidth}{!}{%",
        r"\begin{tabular}{@{}lrrrrrrrrr@{}}",
        r"\toprule",
        r"Model & \(N\) & Countries & Years & Avg. years & Min years & Max years & Within \(R^2\) & Between \(R^2\) & Overall \(R^2\) \\",
        r"\midrule",
        (
            f"Baseline FE & {int(row['nobs'])} & {int(row['countries'])} & {int(row['years'])} & "
            f"{row['avg_years_per_country']:.1f} & {int(row['min_years_per_country'])} & "
            f"{int(row['max_years_per_country'])} & {row['within_r2']:.3f} & "
            f"{row['between_r2']:.3f} & {row['overall_r2']:.3f} \\\\"
        ),
        r"\bottomrule",
        r"\end{tabular}%",
        r"}",
        "",
        r"\vspace{0.2em}",
        (
            r"\begin{minipage}{0.94\textwidth}\scriptsize Notes: The baseline fixed-effects sample is the "
            r"complete-case panel used for the selected poverty coefficient. The within \(R^2\) is emphasized "
            r"because country and year effects absorb "
            r"much of the overall variation.\end{minipage}"
        ),
    ]
    (TABLES / "fe_fit_diagnostics.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def driscoll_kraay_result(df: pd.DataFrame, maxlags: int = 1):
    work = df.sort_values(["year", "geo"]).copy()
    return smf.ols(fe_formula(), data=work).fit(
        cov_type="hac-groupsum",
        cov_kwds={"time": work["year"].to_numpy(), "maxlags": maxlags, "use_correction": "cluster"},
    )


def wild_cluster_bootstrap(
    df: pd.DataFrame,
    term: str = "poverty_or_social_exclusion_pc",
    reps: int = 499,
    seed: int = RANDOM_SEED,
) -> dict[str, float | int | str]:
    work = df[["geo", "year", OUTCOME] + BASELINE_COVARS].dropna().copy()
    rng = np.random.default_rng(seed)
    unrestricted = smf.ols(fe_formula(), data=work).fit()
    restricted_covars = [c for c in BASELINE_COVARS if c != term]
    restricted = smf.ols(fe_formula(restricted_covars), data=work).fit()
    beta_hat = float(unrestricted.params[term])
    clusters = sorted(work["geo"].unique())
    restricted_fitted = restricted.fittedvalues.to_numpy()
    restricted_resid = restricted.resid.to_numpy()
    unrestricted_fitted = unrestricted.fittedvalues.to_numpy()
    unrestricted_resid = unrestricted.resid.to_numpy()
    cluster_labels = work["geo"].to_numpy()
    p_draws: list[float] = []
    ci_draws: list[float] = []

    for _ in range(reps):
        signs = {cluster: rng.choice([-1.0, 1.0]) for cluster in clusters}
        sign_vec = np.array([signs[cluster] for cluster in cluster_labels])

        p_work = work.copy()
        p_work["_boot_y"] = restricted_fitted + restricted_resid * sign_vec
        p_fit = smf.ols(fe_formula(outcome="_boot_y"), data=p_work).fit()
        if term in p_fit.params:
            p_draws.append(float(p_fit.params[term]))

        ci_work = work.copy()
        ci_work["_boot_y"] = unrestricted_fitted + unrestricted_resid * sign_vec
        ci_fit = smf.ols(fe_formula(outcome="_boot_y"), data=ci_work).fit()
        if term in ci_fit.params:
            ci_draws.append(float(ci_fit.params[term]))

    p_arr = np.asarray(p_draws, dtype=float)
    ci_arr = np.asarray(ci_draws, dtype=float)
    wild_p = float((np.sum(np.abs(p_arr) >= abs(beta_hat)) + 1) / (len(p_arr) + 1)) if len(p_arr) else np.nan
    ci_low, ci_high = (np.nan, np.nan)
    if len(ci_arr):
        ci_low, ci_high = np.percentile(ci_arr, [2.5, 97.5])
    return {
        "term": term,
        "bootstrap_reps_requested": reps,
        "bootstrap_reps_used": int(min(len(p_arr), len(ci_arr))),
        "wild_cluster_p_value": wild_p,
        "wild_cluster_ci_low": float(ci_low),
        "wild_cluster_ci_high": float(ci_high),
    }


def write_fe_inference_outputs(complete_sample: pd.DataFrame, complete_fit) -> pd.DataFrame:
    term = "poverty_or_social_exclusion_pc"
    dk = driscoll_kraay_result(complete_sample)
    boot = wild_cluster_bootstrap(complete_sample, term=term)
    cluster_ci = complete_fit.conf_int().loc[term]
    rows = [
        {
            "term": term,
            "coef": float(complete_fit.params[term]),
            "country_clustered_se": float(complete_fit.bse[term]),
            "country_clustered_p_value": float(complete_fit.pvalues[term]),
            "country_clustered_ci_low": float(cluster_ci.iloc[0]),
            "country_clustered_ci_high": float(cluster_ci.iloc[1]),
            "driscoll_kraay_se": float(dk.bse[term]),
            "driscoll_kraay_p_value": float(dk.pvalues[term]),
            "wild_cluster_p_value": boot["wild_cluster_p_value"],
            "wild_cluster_ci_low": boot["wild_cluster_ci_low"],
            "wild_cluster_ci_high": boot["wild_cluster_ci_high"],
            "bootstrap_reps_used": boot["bootstrap_reps_used"],
            "nobs": int(complete_fit.nobs),
            "countries": int(complete_sample["geo"].nunique()),
        }
    ]
    out = pd.DataFrame(rows)
    out.to_csv(OUTPUTS / "fe_inference_comparison.csv", index=False)

    row = out.iloc[0]
    lines = [
        r"\begin{tabular}{@{}lrrrrr@{}}",
        r"\toprule",
        r"Term & Coef. & Cluster SE & DK SE & Wild \(p\) & Wild 95\% CI \\",
        r"\midrule",
        (
            f"Poverty/social exclusion & {row['coef']:.3f} & {row['country_clustered_se']:.3f} & "
            f"{row['driscoll_kraay_se']:.3f} & {format_p_value(row['wild_cluster_p_value'])} & "
            f"[{row['wild_cluster_ci_low']:.3f}, {row['wild_cluster_ci_high']:.3f}] \\\\"
        ),
        r"\bottomrule",
        r"\end{tabular}",
        "",
        r"\vspace{0.2em}",
        (
            r"\begin{minipage}{0.94\textwidth}\scriptsize Notes: The coefficient is from the selected complete-case "
            r"country-and-year fixed-effects model. Cluster SE uses country clusters with finite-sample correction; "
            r"DK is Driscoll--Kraay with one lag; the wild-cluster bootstrap uses country-level Rademacher weights "
            r"and reports the bootstrap \(p\)-value and percentile interval.\end{minipage}"
        ),
    ]
    (TABLES / "fe_inference_comparison.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")
    fe_fit_diagnostics(complete_sample, complete_fit)
    return out


def leave_one_year_out_summary(sample: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for year in sorted(sample["year"].dropna().astype(int).unique()):
        row = poverty_robustness_result(
            f"Leave out {year}",
            "year influence",
            sample[sample["year"].ne(year)].copy(),
        )
        row["dropped_year"] = year
        rows.append(row)
    out = pd.DataFrame(rows)
    out.to_csv(OUTPUTS / "leave_one_year_out_poverty.csv", index=False)
    return out


def plot_influence_coefficients(df: pd.DataFrame, label_col: str, path: Path, title: str) -> None:
    plot = df[df["status"].eq("estimated") & df["coef"].notna()].copy()
    if plot.empty:
        return
    plot = plot.sort_values("coef").reset_index(drop=True)
    labels = plot[label_col].astype(str)
    y = np.arange(len(plot))
    plt.figure(figsize=(8.2, max(4.8, 0.24 * len(plot))))
    plt.axvline(0, color="#666666", linewidth=0.8)
    plt.errorbar(
        plot["coef"],
        y,
        xerr=[plot["coef"] - plot["ci_low"], plot["ci_high"] - plot["coef"]],
        fmt="o",
        color="#315f7d",
        ecolor="#8aa7bb",
        markersize=3.5,
        linewidth=1.0,
    )
    plt.yticks(y, labels)
    plt.xlabel("Poverty/social-exclusion coefficient")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(path, dpi=300)
    plt.close()


def write_influence_outputs(complete_sample: pd.DataFrame) -> None:
    loo_country = leave_one_country_out_summary(complete_sample)
    loo_year = leave_one_year_out_summary(complete_sample)
    plot_influence_coefficients(
        loo_country,
        "dropped_country",
        FIGURES / "leave_one_country_out_poverty.pdf",
        "Leave-one-country-out FE coefficient",
    )
    plot_influence_coefficients(
        loo_year,
        "dropped_year",
        FIGURES / "leave_one_year_out_poverty.pdf",
        "Leave-one-year-out FE coefficient",
    )


def ensure_population_weights(target: pd.DataFrame) -> pd.DataFrame:
    target = target.copy()
    if POPULATION not in target.columns:
        pop_path = DATA_PROCESSED / "feature_population_total.csv"
        if pop_path.exists():
            pop = pd.read_csv(pop_path)
            target = target.merge(pop[["geo", "year", POPULATION]], on=["geo", "year"], how="left")
    if POPULATION in target.columns:
        target[POP_WEIGHT] = target[POPULATION] / target.groupby("year")[POPULATION].transform("sum")
    return target


def balanced_outcome_countries(target: pd.DataFrame) -> list[str]:
    years = sorted(target["year"].dropna().astype(int).unique())
    rows = []
    for geo, g in target.groupby("geo"):
        has_years = set(g.loc[g[OUTCOME].notna(), "year"].astype(int))
        has_pop = POP_WEIGHT in g.columns and g[POP_WEIGHT].notna().all()
        if set(years).issubset(has_years) and has_pop:
            rows.append(str(geo))
    return sorted(rows)


def write_country_universe_table(target: pd.DataFrame, complete_sample: pd.DataFrame) -> pd.DataFrame:
    ml_path = DATA_PROCESSED / "modeling_dataset_5a_with_splits.csv"
    ml = pd.read_csv(ml_path) if ml_path.exists() else pd.DataFrame(columns=["geo", "year"])
    mi_target_countries = set(target["geo"].dropna().astype(str))
    complete_countries = set(complete_sample["geo"].dropna().astype(str))
    ml_countries = set(ml["geo"].dropna().astype(str)) if "geo" in ml.columns else set()
    countries = sorted(mi_target_countries | complete_countries | ml_countries)
    rows = []
    for geo in countries:
        target_g = target[target["geo"].eq(geo)]
        complete_g = complete_sample[complete_sample["geo"].eq(geo)]
        ml_g = ml[ml["geo"].eq(geo)] if "geo" in ml.columns else pd.DataFrame()
        rows.append(
            {
                "geo": geo,
                "universe_category": country_universe_category(geo),
                "in_outcome_observed_panel": bool_label(not target_g.empty),
                "outcome_observed_rows": int(len(target_g)),
                "in_complete_case_fe": bool_label(not complete_g.empty),
                "complete_case_rows": int(len(complete_g)),
                "in_mi_target": bool_label(geo in mi_target_countries),
                "mi_target_rows": int(len(target_g)),
                "in_ml_sample": bool_label(not ml_g.empty),
                "ml_rows": int(len(ml_g)),
            }
        )
    out = pd.DataFrame(rows)
    out.to_csv(OUTPUTS / "country_universe.csv", index=False)

    summary = (
        out.groupby("universe_category", as_index=False)
        .agg(
            countries=("geo", "nunique"),
            outcome_rows=("outcome_observed_rows", "sum"),
            complete_case_rows=("complete_case_rows", "sum"),
            ml_rows=("ml_rows", "sum"),
        )
        .sort_values("universe_category")
    )
    summary.to_csv(OUTPUTS / "country_universe_summary.csv", index=False)

    display = out.copy()
    lines = [
        r"\resizebox{\textwidth}{!}{%",
        r"\begin{tabular}{@{}llrrrr@{}}",
        r"\toprule",
        r"Country & Universe category & Outcome rows & CC rows & MI rows & ML rows \\",
        r"\midrule",
    ]
    for _, row in display.iterrows():
        lines.append(
            f"{row['geo']} & {row['universe_category']} & {row['outcome_observed_rows']} & {row['complete_case_rows']} & {row['mi_target_rows']} & {row['ml_rows']} \\\\"
        )
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}%",
            r"}",
            "",
            r"\vspace{0.2em}",
            r"\begin{minipage}{0.96\textwidth}\scriptsize Notes: Country universe categories distinguish EU-27 members, EEA countries, Switzerland, the UK, candidate or potential-candidate countries, and other Eurostat-available national units. CC rows are baseline complete-case fixed-effects rows; MI rows are outcome-observed target rows.\end{minipage}",
        ]
    )
    (TABLES / "country_universe.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def inclusion_design(target: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    design = target[["geo", "year", OUTCOME, "log_gdp_per_capita", "unemployment_rate_pc"]].copy()
    design["country_group"] = design["geo"].map(country_group)
    for var in BASELINE_COVARS:
        design[f"{var}_observed"] = target[var].notna().astype(int)
    for var in ["log_gdp_per_capita", "unemployment_rate_pc"]:
        design[f"{var}_missing"] = design[var].isna().astype(int)
    design["year_centered"] = design["year"] - design["year"].mean()
    dummies = pd.get_dummies(design["country_group"], prefix="group", drop_first=True, dtype=float)
    design = pd.concat([design.drop(columns=["geo", "year", "country_group"]), dummies], axis=1)
    features = [c for c in design.columns if c != OUTCOME]
    return design, [OUTCOME] + features


def estimate_inclusion_probabilities(target: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    target = target.copy()
    included_keys = set(zip(model_sample(target)["geo"], model_sample(target)["year"]))
    target["included_complete_case"] = [int(key in included_keys) for key in zip(target["geo"], target["year"])]
    design, columns = inclusion_design(target)
    x = design[columns].copy()
    y = target["included_complete_case"].to_numpy()
    model = Pipeline(
        [
            ("impute", SimpleImputer(strategy="median")),
            ("scale", StandardScaler()),
            ("logit", LogisticRegression(max_iter=2000, C=1.0, random_state=RANDOM_SEED)),
        ]
    )
    model.fit(x, y)
    target["inclusion_probability"] = model.predict_proba(x)[:, 1]
    target["inclusion_probability"] = target["inclusion_probability"].clip(0.01, 0.99)

    coefs = model.named_steps["logit"].coef_[0]
    summary = pd.DataFrame({"term": columns, "logit_coef": coefs}).sort_values("logit_coef", ascending=False)
    summary.loc[len(summary)] = ["target_rows", float(len(target))]
    summary.loc[len(summary)] = ["complete_case_rows", float(target["included_complete_case"].sum())]
    summary.to_csv(OUTPUTS / "missingness_model_summary.csv", index=False)
    return target, summary


def complete_case_selection_model(target: pd.DataFrame) -> pd.DataFrame:
    df = target.copy()
    df["country_group"] = df["geo"].map(country_group)
    for var in ["log_gdp_per_capita", "unemployment_rate_pc"]:
        df[f"{var}_missing"] = df[var].isna().astype(int)
        df[var] = df[var].fillna(df[var].median())
    df["year_centered"] = df["year"] - df["year"].mean()
    formula = (
        "included_complete_case ~ unmet_need_pc + log_gdp_per_capita + "
        "unemployment_rate_pc + log_gdp_per_capita_missing + "
        "unemployment_rate_pc_missing + year_centered + C(country_group)"
    )
    result = smf.ols(formula, data=df).fit(
        cov_type="cluster",
        cov_kwds={"groups": df["geo"], "use_correction": True},
    )
    conf = result.conf_int()
    rows = []
    for term in result.params.index:
        rows.append(
            {
                "term": term,
                "coef": float(result.params[term]),
                "se": float(result.bse[term]),
                "p_value": float(result.pvalues[term]),
                "ci_low": float(conf.loc[term, 0]),
                "ci_high": float(conf.loc[term, 1]),
                "nobs": int(result.nobs),
                "complete_case_rows": int(df["included_complete_case"].sum()),
            }
        )
    out = pd.DataFrame(rows)
    out.to_csv(OUTPUTS / "complete_case_selection_model.csv", index=False)

    display_terms = {
        "unmet_need_pc": "Unmet need",
        "log_gdp_per_capita": "Log GDP",
        "unemployment_rate_pc": "Unemployment",
        "year_centered": "Year",
        "log_gdp_per_capita_missing": "GDP missing",
        "unemployment_rate_pc_missing": "Unemployment missing",
    }
    table = out[out["term"].isin(display_terms)].copy()
    table["Term"] = table["term"].map(display_terms)
    table["Coef."] = table["coef"].map(lambda x: f"{x:.3f}")
    table["SE"] = table["se"].map(lambda x: f"{x:.3f}")
    table["p-value"] = table["p_value"].map(format_p_value)
    lines = [
        r"\begin{tabular}{@{}lrrr@{}}",
        r"\toprule",
        r"Predictor & Coef. & SE & p-value \\",
        r"\midrule",
    ]
    for _, row in table.iterrows():
        lines.append(f"{row['Term']} & {row['Coef.']} & {row['SE']} & {row['p-value']} \\\\")
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}",
            "",
            r"\vspace{0.2em}",
            r"\begin{minipage}{0.92\textwidth}\scriptsize Notes: Linear probability model for inclusion in the baseline complete-case regression sample among the 608 outcome-observed rows, with country-clustered standard errors. GDP and unemployment are median-imputed for this diagnostic and accompanied by missingness indicators.\end{minipage}",
        ]
    )
    (TABLES / "complete_case_selection_model.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def add_ipw_weights(target: pd.DataFrame) -> pd.DataFrame:
    target = target.copy()
    marginal = target["included_complete_case"].mean()
    target["ipw_raw"] = marginal / target["inclusion_probability"]
    lower = target.loc[target["included_complete_case"].eq(1), "ipw_raw"].quantile(0.01)
    upper = target.loc[target["included_complete_case"].eq(1), "ipw_raw"].quantile(0.99)
    target["ipw_truncated"] = target["ipw_raw"].clip(lower, upper)
    return target


def weighted_mean(df: pd.DataFrame, variable: str, weight: str | None = None) -> float:
    temp = df[[variable] + ([weight] if weight else [])].dropna()
    if temp.empty:
        return np.nan
    if weight is None:
        return float(temp[variable].mean())
    return float(np.average(temp[variable], weights=temp[weight]))


def balance_table(target: pd.DataFrame) -> pd.DataFrame:
    complete = target[target["included_complete_case"].eq(1)].copy()
    rows = []
    for var in [OUTCOME, "gdp_per_capita_eur", "unemployment_rate_pc", "poverty_or_social_exclusion_pc"]:
        rows.append(
            {
                "variable": var,
                "target_mean": weighted_mean(target, var),
                "complete_case_mean": weighted_mean(complete, var),
                "ipw_weighted_mean": weighted_mean(complete, var, "ipw_truncated"),
                "complete_minus_target": weighted_mean(complete, var) - weighted_mean(target, var),
                "ipw_minus_target": weighted_mean(complete, var, "ipw_truncated") - weighted_mean(target, var),
            }
        )
    out = pd.DataFrame(rows)
    out.to_csv(OUTPUTS / "ipw_balance.csv", index=False)
    return out


def weight_summary(target: pd.DataFrame) -> pd.DataFrame:
    complete = target[target["included_complete_case"].eq(1)].copy()
    rows = []
    for weight in ["ipw_raw", "ipw_truncated"]:
        s = complete[weight]
        rows.append(
            {
                "weight": weight,
                "mean": s.mean(),
                "sd": s.std(),
                "min": s.min(),
                "p01": s.quantile(0.01),
                "median": s.median(),
                "p99": s.quantile(0.99),
                "max": s.max(),
                "effective_sample_size": effective_sample_size(s),
            }
        )
    out = pd.DataFrame(rows)
    out.to_csv(OUTPUTS / "ipw_weight_summary.csv", index=False)
    return out


def plot_inclusion_probability(target: pd.DataFrame) -> None:
    plot = target.copy()
    plot["sample"] = np.where(plot["included_complete_case"].eq(1), "Included complete case", "Excluded outcome-observed")
    plt.figure(figsize=(8, 4.8))
    sns.histplot(data=plot, x="inclusion_probability", hue="sample", bins=30, element="step", stat="density", common_norm=False)
    plt.xlabel("Estimated probability of complete-case inclusion")
    plt.ylabel("Density")
    plt.tight_layout()
    plt.savefig(FIGURES / "missingness_inclusion_probability.pdf", dpi=300)
    plt.close()


def summarise_values(values: pd.Series) -> dict[str, float | int]:
    clean = pd.to_numeric(values, errors="coerce").dropna()
    if clean.empty:
        return {
            "n": 0,
            "mean": np.nan,
            "sd": np.nan,
            "min": np.nan,
            "p05": np.nan,
            "median": np.nan,
            "p95": np.nan,
            "max": np.nan,
        }
    return {
        "n": int(clean.size),
        "mean": float(clean.mean()),
        "sd": float(clean.std(ddof=1)) if clean.size > 1 else 0.0,
        "min": float(clean.min()),
        "p05": float(clean.quantile(0.05)),
        "median": float(clean.median()),
        "p95": float(clean.quantile(0.95)),
        "max": float(clean.max()),
    }


def imputation_matrix(
    base: pd.DataFrame,
    include_outcome: bool = True,
    country_structure: str = "group",
    year_effects: bool = True,
    lagged_predictors: bool = False,
) -> pd.DataFrame:
    matrix_cols = [v for v in IMPUTE_VARS if v in base.columns]
    if include_outcome and OUTCOME in base.columns:
        matrix_cols = [OUTCOME] + matrix_cols
    matrix = base[matrix_cols].copy()
    if not year_effects:
        matrix["year"] = base["year"].astype(float)
    else:
        year_dummies = pd.get_dummies(base["year"].astype(int), prefix="year", drop_first=True, dtype=float)
        matrix = pd.concat([matrix, year_dummies], axis=1)
    if country_structure == "group":
        dummy_source = pd.DataFrame({"country_group": base["geo"].map(country_group)})
        dummies = pd.get_dummies(dummy_source, prefix="group", drop_first=True, dtype=float)
    elif country_structure == "country":
        dummies = pd.get_dummies(base["geo"], prefix="geo", drop_first=True, dtype=float)
    else:
        dummies = pd.DataFrame(index=base.index)
    matrix = pd.concat([matrix, dummies], axis=1)
    if lagged_predictors:
        ordered = base.sort_values(["geo", "year"]).copy()
        lag_rows = pd.DataFrame(index=ordered.index)
        for var in [v for v in BASELINE_COVARS if v in ordered.columns]:
            lag_rows[f"lag1_{var}"] = ordered.groupby("geo")[var].shift(1)
        lag_rows = lag_rows.reindex(base.index)
        matrix = pd.concat([matrix, lag_rows], axis=1)
    matrix = matrix.rename(columns={col: safe_patsy_column(col) for col in matrix.columns})
    return matrix.apply(pd.to_numeric, errors="coerce")


def fast_pmm_fill(matrix: pd.DataFrame, seed: int, n_iter: int = 5, k_pmm: int = 20) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    raw = matrix.apply(pd.to_numeric, errors="coerce").copy()
    filled = raw.copy()
    missing_masks = {col: raw[col].isna() for col in raw.columns}
    for col in raw.columns:
        if filled[col].isna().any():
            median = filled[col].median()
            filled[col] = filled[col].fillna(0.0 if pd.isna(median) else median)
    impute_columns = [col for col, mask in missing_masks.items() if mask.any() and raw[col].notna().sum() >= 3]
    for _ in range(n_iter):
        for col in impute_columns:
            missing = missing_masks[col]
            observed = ~missing
            if not missing.any():
                continue
            x_obs = filled.loc[observed].drop(columns=[col])
            x_miss = filled.loc[missing].drop(columns=[col])
            y_obs = raw.loc[observed, col]
            if x_obs.empty or x_miss.empty:
                continue
            model = BayesianRidge()
            model.fit(x_obs, y_obs)
            pred_obs = model.predict(x_obs)
            pred_miss = model.predict(x_miss)
            donor_values = y_obs.to_numpy()
            replacements = []
            donor_count = min(k_pmm, len(donor_values))
            for pred in pred_miss:
                nearest = np.argpartition(np.abs(pred_obs - pred), donor_count - 1)[:donor_count]
                replacements.append(float(rng.choice(donor_values[nearest])))
            filled.loc[missing, col] = replacements
    return filled


def pmm_donor_diagnostics(matrix: pd.DataFrame, k_pmm: int = 20) -> pd.DataFrame:
    raw = matrix.apply(pd.to_numeric, errors="coerce")
    rows = []
    for col in raw.columns:
        missing_n = int(raw[col].isna().sum())
        observed_n = int(raw[col].notna().sum())
        if missing_n == 0:
            continue
        rows.append(
            {
                "matrix_column": col,
                "observed_n": observed_n,
                "missing_n": missing_n,
                "requested_k_pmm": k_pmm,
                "effective_donor_pool": int(min(k_pmm, observed_n)) if observed_n else 0,
                "donor_warning": "yes" if observed_n < k_pmm else "no",
            }
        )
    return pd.DataFrame(rows)


def pmm_completed_dataset(
    base: pd.DataFrame,
    matrix: pd.DataFrame,
    seed: int,
    n_iter: int = 5,
    k_pmm: int = 20,
) -> pd.DataFrame:
    filled = fast_pmm_fill(matrix, seed=seed, n_iter=n_iter, k_pmm=k_pmm)
    df = base.copy()
    for var in [v for v in IMPUTE_VARS if v in df.columns and v in filled.columns]:
        lower, upper = IMPUTATION_BOUNDS.get(var, (0.0, np.inf))
        df[var] = filled[var].clip(lower, upper)
    if "log_gdp_per_capita" in df.columns:
        gdp_lower, gdp_upper = IMPUTATION_BOUNDS["gdp_per_capita_eur"]
        derived = np.exp(df["log_gdp_per_capita"]).clip(gdp_lower, gdp_upper)
        if "gdp_per_capita_eur" in df.columns:
            df.loc[base["gdp_per_capita_eur"].isna(), "gdp_per_capita_eur"] = derived.loc[base["gdp_per_capita_eur"].isna()]
        else:
            df["gdp_per_capita_eur"] = derived
    return df


def apply_delta_shift(df: pd.DataFrame, base: pd.DataFrame, shifts: dict[str, float]) -> pd.DataFrame:
    shifted = df.copy()
    for var, delta in shifts.items():
        if var not in shifted.columns:
            continue
        mask = base[var].isna() if var in base.columns else pd.Series(False, index=shifted.index)
        if var == "gdp_per_capita_eur":
            if "log_gdp_per_capita" in shifted.columns:
                log_delta = math.log(max(1e-6, 1.0 + delta))
                log_mask = base["log_gdp_per_capita"].isna() if "log_gdp_per_capita" in base.columns else mask
                shifted.loc[log_mask, "log_gdp_per_capita"] = shifted.loc[log_mask, "log_gdp_per_capita"] + log_delta
                lower, upper = IMPUTATION_BOUNDS["log_gdp_per_capita"]
                shifted["log_gdp_per_capita"] = shifted["log_gdp_per_capita"].clip(lower, upper)
                gdp_lower, gdp_upper = IMPUTATION_BOUNDS["gdp_per_capita_eur"]
                shifted.loc[log_mask, "gdp_per_capita_eur"] = np.exp(shifted.loc[log_mask, "log_gdp_per_capita"]).clip(gdp_lower, gdp_upper)
            continue
        lower, upper = IMPUTATION_BOUNDS.get(var, (-np.inf, np.inf))
        shifted.loc[mask, var] = (shifted.loc[mask, var] + delta).clip(lower, upper)
    return shifted


def fit_imputed_dataset(df: pd.DataFrame, imputation: int, label: str) -> list[dict[str, float | str | int]]:
    fit_df = df[["geo", "year", OUTCOME] + BASELINE_COVARS].dropna().copy()
    result = fit_fe(fit_df)
    rows = []
    for term in BASELINE_COVARS:
        rows.append(
            {
                "imputation": imputation,
                "variant": label,
                "term": term,
                "coef": float(result.params[term]),
                "se": float(result.bse[term]),
                "p_value": float(result.pvalues[term]),
                "nobs": int(result.nobs),
                "countries": int(fit_df["geo"].nunique()),
            }
        )
    return rows


def improved_imputation(
    target: pd.DataFrame,
    m: int = 30,
    include_outcome: bool = True,
    country_structure: str = "group",
    year_effects: bool = True,
    lagged_predictors: bool = False,
    delta_shifts: dict[str, float] | None = None,
    label: str = "baseline",
) -> pd.DataFrame:
    base = target.copy()
    base["country_group"] = base["geo"].map(country_group)
    matrix = imputation_matrix(
        base,
        include_outcome=include_outcome,
        country_structure=country_structure,
        year_effects=year_effects,
        lagged_predictors=lagged_predictors,
    )
    pooled_rows = []
    imputation_rows = []
    distribution_rows = []
    imputed_first: pd.DataFrame | None = None
    for i in range(m):
        df = pmm_completed_dataset(base, matrix, seed=RANDOM_SEED + i, n_iter=5, k_pmm=20)
        if delta_shifts:
            df = apply_delta_shift(df, base, delta_shifts)
        if i == 0:
            imputed_first = df.copy()
        imputation_rows.extend(fit_imputed_dataset(df, i + 1, label))
    imp = pd.DataFrame(imputation_rows)
    imp.to_csv(OUTPUTS / f"improved_mi_fe_results_{label}.csv", index=False)
    for term, group in imp.groupby("term"):
        pooled = rubin_pool(group["coef"], group["se"])
        pooled_rows.append(
            {
                "variant": label,
                "term": term,
                "coef": pooled["estimate"],
                "se": pooled["se"],
                "statistic": pooled["statistic"],
                "df": pooled["df"],
                "p_value": pooled["p_value"],
                "imputations": m,
                "mean_nobs": group["nobs"].mean(),
                "mean_countries": group["countries"].mean(),
            }
        )
    out = pd.DataFrame(pooled_rows)
    out.to_csv(OUTPUTS / f"improved_mi_pooled_results_{label}.csv", index=False)

    if imputed_first is not None:
        if "gdp_per_capita_eur" in imputed_first.columns and "log_gdp_per_capita" in imputed_first.columns:
            raw_missing = base["gdp_per_capita_eur"].isna() if "gdp_per_capita_eur" in base.columns else pd.Series(False, index=base.index)
            derived = np.exp(imputed_first["log_gdp_per_capita"])
            diff = (imputed_first.loc[raw_missing, "gdp_per_capita_eur"] - derived.loc[raw_missing]).abs()
            pd.DataFrame(
                [
                    {
                        "variant": label,
                        "raw_gdp_imputed_independently": False,
                        "raw_gdp_missing_rows": int(raw_missing.sum()),
                        "max_abs_difference_raw_vs_exp_log": float(diff.max()) if not diff.empty else 0.0,
                    }
                ]
            ).to_csv(OUTPUTS / f"mi_gdp_consistency_{label}.csv", index=False)
        for var in [v for v in IMPUTE_VARS if v in base.columns]:
            observed = base[var].dropna()
            imputed_missing = imputed_first.loc[base[var].isna(), var].dropna()
            distribution_rows.append(
                {
                    "variant": label,
                    "variable": var,
                    "observed_n": int(observed.size),
                    "imputed_n": int(imputed_missing.size),
                    "observed_mean": float(observed.mean()) if not observed.empty else np.nan,
                    "imputed_mean": float(imputed_missing.mean()) if not imputed_missing.empty else np.nan,
                    "observed_p05": float(observed.quantile(0.05)) if not observed.empty else np.nan,
                    "imputed_p05": float(imputed_missing.quantile(0.05)) if not imputed_missing.empty else np.nan,
                    "observed_p95": float(observed.quantile(0.95)) if not observed.empty else np.nan,
                    "imputed_p95": float(imputed_missing.quantile(0.95)) if not imputed_missing.empty else np.nan,
                }
            )
        dist = pd.DataFrame(distribution_rows)
        dist.to_csv(OUTPUTS / f"mi_observed_vs_imputed_{label}.csv", index=False)
        if label == "baseline_pmm":
            dist.to_csv(OUTPUTS / "mi_observed_vs_imputed_baseline.csv", index=False)
        if label == "baseline_pmm":
            group_year_rows = []
            enriched = base[["geo", "year"]].copy()
            enriched["country_group"] = base["geo"].map(country_group)
            enriched["period"] = np.where(enriched["year"].lt(2015), "pre-2015", "2015-onward")
            for var in [v for v in IMPUTE_VARS if v in base.columns]:
                for group_value, period_value in [
                    ("All", "All"),
                    *sorted({(str(g), "All") for g in enriched["country_group"].dropna().unique()}),
                    *sorted({("All", str(p)) for p in enriched["period"].dropna().unique()}),
                    *sorted(
                        {
                            (str(g), str(p))
                            for g, p in zip(enriched["country_group"], enriched["period"], strict=False)
                            if pd.notna(g) and pd.notna(p)
                        }
                    ),
                ]:
                    mask = pd.Series(True, index=base.index)
                    if group_value != "All":
                        mask &= enriched["country_group"].eq(group_value)
                    if period_value != "All":
                        mask &= enriched["period"].eq(period_value)
                    observed_stats = summarise_values(base.loc[mask & base[var].notna(), var])
                    imputed_stats = summarise_values(imputed_first.loc[mask & base[var].isna(), var])
                    for source, stats_row in [("Observed", observed_stats), ("Imputed where missing", imputed_stats)]:
                        group_year_rows.append(
                            {
                                "variant": label,
                                "variable": var,
                                "country_group": group_value,
                                "period": period_value,
                                "source": source,
                                **stats_row,
                            }
                        )
            pd.DataFrame(group_year_rows).to_csv(OUTPUTS / "mi_observed_vs_imputed_by_group_year.csv", index=False)
        plausibility_rows = []
        for var in [v for v in IMPUTE_VARS if v in base.columns]:
            lower, upper = IMPUTATION_BOUNDS.get(var, (0.0, np.inf))
            vals = imputed_first.loc[base[var].isna(), var].dropna()
            plausibility_rows.append(
                {
                    "variant": label,
                    "variable": var,
                    "lower_bound": lower,
                    "upper_bound": upper,
                    "imputed_n": int(vals.size),
                    "imputed_min": float(vals.min()) if not vals.empty else np.nan,
                    "imputed_max": float(vals.max()) if not vals.empty else np.nan,
                    "outside_bounds": int(((vals < lower) | (vals > upper)).sum()) if not vals.empty else 0,
                }
            )
        plausibility = pd.DataFrame(plausibility_rows)
        plausibility.to_csv(OUTPUTS / f"mi_plausibility_checks_{label}.csv", index=False)
        if label == "baseline_pmm":
            plausibility.to_csv(OUTPUTS / "mi_plausibility_checks_baseline.csv", index=False)
        plot_vars = ["poverty_or_social_exclusion_pc", "log_gdp_per_capita", "unemployment_rate_pc", "government_health_expenditure_gdp_pc"]
        plot_rows = []
        for var in [v for v in plot_vars if v in base.columns]:
            plot_rows.extend({"variable": var, "source": "Observed", "value": v} for v in base[var].dropna())
            plot_rows.extend({"variable": var, "source": "Imputed where missing", "value": v} for v in imputed_first.loc[base[var].isna(), var].dropna())
        if plot_rows:
            plot = pd.DataFrame(plot_rows)
            g = sns.FacetGrid(plot, col="variable", hue="source", col_wrap=2, sharex=False, sharey=False, height=3.1)
            g.map_dataframe(sns.kdeplot, x="value", fill=False, common_norm=False)
            g.add_legend()
            g.set_axis_labels("")
            g.tight_layout()
            g.savefig(FIGURES / f"mi_observed_vs_imputed_{label}.pdf", dpi=300)
            if label == "baseline_pmm":
                g.savefig(FIGURES / "mi_observed_vs_imputed_baseline.pdf", dpi=300)
            plt.close("all")

        share = pd.DataFrame(
            {
                "geo": base["geo"],
                "year": base["year"],
                "imputed_share": base[[v for v in IMPUTE_VARS if v in base.columns]].isna().mean(axis=1),
            }
        )
        matrix = share.pivot_table(index="geo", columns="year", values="imputed_share", aggfunc="mean").sort_index()
        plt.figure(figsize=(12, max(6, 0.22 * len(matrix))))
        sns.heatmap(matrix, cmap="rocket_r", vmin=0, vmax=1, linewidths=0.08, linecolor="white", cbar_kws={"label": "Share of imputed covariates"})
        plt.xlabel("Year")
        plt.ylabel("Country")
        plt.tight_layout()
        plt.savefig(FIGURES / f"mi_imputed_share_heatmap_{label}.pdf", dpi=300)
        if label == "baseline_pmm":
            plt.savefig(FIGURES / "mi_imputed_share_heatmap_baseline.pdf", dpi=300)
        plt.close()

    if label == "baseline_pmm":
        imp.to_csv(OUTPUTS / "improved_mi_fe_results.csv", index=False)
        out.to_csv(OUTPUTS / "improved_mi_pooled_results.csv", index=False)
    return out


def pool_imputation_rows(rows: pd.DataFrame, label_column: str = "variant") -> pd.DataFrame:
    pooled_rows = []
    for (variant, term), group in rows.groupby([label_column, "term"]):
        pooled = rubin_pool(group["coef"], group["se"])
        pooled_rows.append(
            {
                label_column: variant,
                "term": term,
                "coef": pooled["estimate"],
                "se": pooled["se"],
                "statistic": pooled["statistic"],
                "df": pooled["df"],
                "p_value": pooled["p_value"],
                "imputations": int(group["imputation"].nunique()),
                "mean_nobs": group["nobs"].mean(),
                "mean_countries": group["countries"].mean(),
            }
        )
    return pd.DataFrame(pooled_rows)


def mnar_shift_scenarios() -> dict[str, dict[str, float]]:
    return {
        "poverty_plus2": {"poverty_or_social_exclusion_pc": 2.0},
        "poverty_plus5": {"poverty_or_social_exclusion_pc": 5.0},
        "poverty_plus10": {"poverty_or_social_exclusion_pc": 10.0},
        "gdp_down5": {"gdp_per_capita_eur": -0.05},
        "gdp_down10": {"gdp_per_capita_eur": -0.10},
        "gdp_down20": {"gdp_per_capita_eur": -0.20},
        "unemployment_plus2": {"unemployment_rate_pc": 2.0},
        "unemployment_plus5": {"unemployment_rate_pc": 5.0},
        "mnar_pessimistic_combo": {
            "poverty_or_social_exclusion_pc": 5.0,
            "gdp_per_capita_eur": -0.10,
            "unemployment_rate_pc": 2.0,
        },
        "mnar_optimistic_combo": {
            "poverty_or_social_exclusion_pc": -2.0,
            "gdp_per_capita_eur": 0.05,
            "unemployment_rate_pc": -1.0,
        },
    }


def mnar_sensitivity_summary(target: pd.DataFrame, m: int = 30) -> pd.DataFrame:
    base = target.copy()
    base["country_group"] = base["geo"].map(country_group)
    matrix = imputation_matrix(base, include_outcome=True, country_structure="group", year_effects=True, lagged_predictors=False)
    rows = []
    scenarios = mnar_shift_scenarios()
    for i in range(m):
        completed = pmm_completed_dataset(base, matrix, seed=RANDOM_SEED + 1000 + i, n_iter=5, k_pmm=20)
        for scenario, shifts in scenarios.items():
            shifted = apply_delta_shift(completed, base, shifts)
            rows.extend(fit_imputed_dataset(shifted, i + 1, scenario))
    fe_rows = pd.DataFrame(rows)
    fe_rows.to_csv(OUTPUTS / "mnar_imputation_fe_results.csv", index=False)
    pooled = pool_imputation_rows(fe_rows)
    poverty = pooled[pooled["term"].eq("poverty_or_social_exclusion_pc")].copy()
    poverty["ci_low"] = poverty["coef"] - 1.96 * poverty["se"]
    poverty["ci_high"] = poverty["coef"] + 1.96 * poverty["se"]
    poverty.to_csv(OUTPUTS / "mnar_sensitivity_results.csv", index=False)

    label_map = {
        "poverty_plus2": "Poverty +2 pp",
        "poverty_plus5": "Poverty +5 pp",
        "poverty_plus10": "Poverty +10 pp",
        "gdp_down5": "GDP -5\\%",
        "gdp_down10": "GDP -10\\%",
        "gdp_down20": "GDP -20\\%",
        "unemployment_plus2": "Unemployment +2 pp",
        "unemployment_plus5": "Unemployment +5 pp",
        "mnar_pessimistic_combo": "Pessimistic combo",
        "mnar_optimistic_combo": "Optimistic combo",
    }
    table = poverty.copy()
    table["Scenario"] = table["variant"].map(label_map)
    table["Coef. [95\\% CI]"] = table.apply(lambda r: f"{r['coef']:.3f} [{r['ci_low']:.3f}, {r['ci_high']:.3f}]", axis=1)
    table["p-value"] = table["p_value"].map(format_p_value)
    lines = [
        r"\resizebox{\textwidth}{!}{%",
        r"\begin{tabular}{@{}lrrrl@{}}",
        r"\toprule",
        r"Scenario & Coef. [95\% CI] & p-value & \(M\) & Interpretation \\",
        r"\midrule",
    ]
    for _, row in table.iterrows():
        lines.append(
            f"{row['Scenario']} & {row['Coef. [95\\% CI]']} & {row['p-value']} & {int(row['imputations'])} & MNAR stress test \\\\"
        )
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}%",
            r"}",
            "",
            r"\vspace{0.2em}",
            r"\begin{minipage}{0.96\textwidth}\scriptsize Notes: MNAR scenarios apply documented shifts only to originally missing values after the PMM MAR imputation. They are stress tests for model dependence and should not be read as corrected estimates.\end{minipage}",
        ]
    )
    (TABLES / "mnar_sensitivity_results.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return poverty


def mnar_tipping_point_analysis(
    target: pd.DataFrame,
    complete_case_coef: float,
    m: int = 30,
    deltas: Iterable[float] | None = None,
) -> pd.DataFrame:
    """Grid-search poverty shifts on originally missing cells and compare with the complete-case coefficient."""
    if deltas is None:
        deltas = [-10, -5, 0, 2, 5, 10, 15, 20, 25, 30, 40]
    delta_values = [float(d) for d in deltas]
    base = target.copy()
    base["country_group"] = base["geo"].map(country_group)
    matrix = imputation_matrix(base, include_outcome=True, country_structure="group", year_effects=True, lagged_predictors=False)
    rows = []
    for i in range(m):
        completed = pmm_completed_dataset(base, matrix, seed=RANDOM_SEED + 3000 + i, n_iter=5, k_pmm=20)
        for delta in delta_values:
            shifted = apply_delta_shift(completed, base, {"poverty_or_social_exclusion_pc": delta})
            rows.extend(fit_imputed_dataset(shifted, i + 1, f"poverty_shift_{delta:g}"))
    fe_rows = pd.DataFrame(rows)
    fe_rows.to_csv(OUTPUTS / "mnar_tipping_point_fe_results.csv", index=False)
    pooled = pool_imputation_rows(fe_rows)
    poverty = pooled[pooled["term"].eq("poverty_or_social_exclusion_pc")].copy()
    poverty["poverty_shift_pp"] = poverty["variant"].str.replace("poverty_shift_", "", regex=False).astype(float)
    poverty["ci_low"] = poverty["coef"] - 1.96 * poverty["se"]
    poverty["ci_high"] = poverty["coef"] + 1.96 * poverty["se"]
    poverty["complete_case_coef"] = float(complete_case_coef)
    poverty["distance_from_complete_case"] = (poverty["coef"] - complete_case_coef).abs()
    poverty = poverty.sort_values("poverty_shift_pp")

    estimate = np.nan
    status = "not reached within grid"
    sorted_rows = poverty[["poverty_shift_pp", "coef"]].dropna().sort_values("poverty_shift_pp")
    for (_, left), (_, right) in zip(sorted_rows.iloc[:-1].iterrows(), sorted_rows.iloc[1:].iterrows(), strict=False):
        left_diff = float(left["coef"] - complete_case_coef)
        right_diff = float(right["coef"] - complete_case_coef)
        if left_diff == 0:
            estimate = float(left["poverty_shift_pp"])
            status = "exact grid match"
            break
        if left_diff * right_diff <= 0 and right["coef"] != left["coef"]:
            fraction = (complete_case_coef - float(left["coef"])) / (float(right["coef"]) - float(left["coef"]))
            estimate = float(left["poverty_shift_pp"] + fraction * (right["poverty_shift_pp"] - left["poverty_shift_pp"]))
            status = "interpolated within grid"
            break
    closest = poverty.loc[poverty["distance_from_complete_case"].idxmin()].to_dict() if not poverty.empty else {}
    poverty["tipping_point_shift_estimate_pp"] = estimate
    poverty["tipping_point_status"] = status
    poverty["closest_grid_shift_pp"] = float(closest.get("poverty_shift_pp", np.nan))
    poverty["closest_grid_coef"] = float(closest.get("coef", np.nan))
    poverty.to_csv(OUTPUTS / "mnar_tipping_point_results.csv", index=False)

    table = poverty.copy()
    table["Shift"] = table["poverty_shift_pp"].map(lambda x: f"{x:.0f} pp")
    table["Coef. [95\\% CI]"] = table.apply(lambda r: f"{r['coef']:.3f} [{r['ci_low']:.3f}, {r['ci_high']:.3f}]", axis=1)
    table["Distance"] = table["distance_from_complete_case"].map(lambda x: f"{x:.3f}")
    table["p-value"] = table["p_value"].map(format_p_value)
    lines = [
        r"\begin{tabular}{@{}lrrrl@{}}",
        r"\toprule",
        r"Poverty shift & Coef. [95\% CI] & Distance & p-value & Status \\",
        r"\midrule",
    ]
    for _, row in table.iterrows():
        lines.append(f"{row['Shift']} & {row['Coef. [95\\% CI]']} & {row['Distance']} & {row['p-value']} & grid point \\\\")
    note_estimate = f"{estimate:.2f} percentage points" if pd.notna(estimate) else "not reached within the grid"
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}",
            "",
            r"\vspace{0.2em}",
            rf"\begin{{minipage}}{{0.92\textwidth}}\scriptsize Notes: Shifts are applied only to originally missing poverty/social-exclusion cells after PMM imputation. The complete-case target coefficient is {complete_case_coef:.3f}. Tipping-point status: {status}; estimated shift: {note_estimate}.\end{{minipage}}",
        ]
    )
    (TABLES / "mnar_tipping_point_results.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")

    plt.figure(figsize=(7.2, 4.4))
    plt.plot(poverty["poverty_shift_pp"], poverty["coef"], marker="o", color="#0072B2", linewidth=1.8)
    plt.axhline(complete_case_coef, color="#9B2D30", linestyle="--", linewidth=1.3, label="Complete-case coefficient")
    plt.axhline(0, color="#444444", linestyle=":", linewidth=1)
    if pd.notna(estimate):
        plt.axvline(estimate, color="#009E73", linestyle="--", linewidth=1.2, label="Estimated tipping point")
    plt.xlabel("Shift applied to originally missing poverty values (percentage points)")
    plt.ylabel("Pooled poverty coefficient")
    plt.legend(frameon=False)
    plt.grid(alpha=0.22)
    plt.tight_layout()
    plt.savefig(FIGURES / "mnar_tipping_point_curve.pdf", dpi=300)
    plt.close()
    return poverty


def imputation_variant_summary(target: pd.DataFrame) -> pd.DataFrame:
    (OUTPUTS / "mi_method_notes.txt").write_text(
        "Predictive mean matching is implemented with iterative Bayesian-ridge prediction and donor matching "
        "(k=20, five update cycles per imputation). statsmodels MICEData(k_pmm=20) was evaluated but was too slow "
        "for the full MAR/MNAR sensitivity grid in this local pipeline. Raw GDP is not imputed independently; "
        "GDP per capita is derived from the imputed log-GDP value for originally missing raw GDP cells.\n",
        encoding="utf-8",
    )
    variants = [
        ("baseline_pmm", True, "group", True, False, 30),
        ("no_outcome_pmm", False, "group", True, False, 30),
        ("country_dummies_pmm", True, "country", True, False, 30),
        ("lagged_predictors_pmm", True, "group", True, True, 30),
        ("baseline_pmm_m50", True, "group", True, False, 50),
    ]
    rows = []
    for label, include_outcome, country_structure, year_effects, lagged_predictors, m in variants:
        pooled = improved_imputation(
            target,
            m=m,
            include_outcome=include_outcome,
            country_structure=country_structure,
            year_effects=year_effects,
            lagged_predictors=lagged_predictors,
            label=label,
        )
        poverty = pooled[pooled["term"].eq("poverty_or_social_exclusion_pc")].iloc[0]
        rows.append(
            {
                "variant": label,
                "include_outcome": include_outcome,
                "country_structure": country_structure,
                "year_effects": year_effects,
                "lagged_predictors": lagged_predictors,
                "imputations": m,
                "coef": float(poverty["coef"]),
                "se": float(poverty["se"]),
                "p_value": float(poverty["p_value"]),
                "mean_nobs": float(poverty["mean_nobs"]),
                "mean_countries": float(poverty["mean_countries"]),
            }
        )
    out = pd.DataFrame(rows)
    out.to_csv(OUTPUTS / "mi_variant_summary.csv", index=False)
    table = out.copy()
    table["Variant"] = table["variant"].map(
        {
            "baseline_pmm": "Baseline PMM MI",
            "no_outcome_pmm": "No-outcome PMM MI",
            "country_dummies_pmm": "Country-FE PMM MI",
            "lagged_predictors_pmm": "Lagged-predictor PMM MI",
            "baseline_pmm_m50": "50-imputation PMM check",
        }
    )
    table["Coef."] = table["coef"].map(lambda x: f"{x:.4f}")
    table["SE"] = table["se"].map(lambda x: f"{x:.4f}")
    table["p-value"] = table["p_value"].map(format_p_value)
    table["M"] = table["imputations"].astype(int).astype(str)
    lines = [
        r"\begin{tabular}{@{}lrrrr@{}}",
        r"\toprule",
        r"Variant & Coef. & SE & p-value & \(M\) \\",
        r"\midrule",
    ]
    for _, row in table.iterrows():
        lines.append(f"{row['Variant']} & {row['Coef.']} & {row['SE']} & {row['p-value']} & {row['M']} \\\\")
    lines.extend([r"\bottomrule", r"\end{tabular}", ""])
    (TABLES / "mi_variant_summary.tex").write_text("\n".join(lines), encoding="utf-8")
    return out


def write_pmm_donor_diagnostics(target: pd.DataFrame) -> pd.DataFrame:
    base = target.copy()
    base["country_group"] = base["geo"].map(country_group)
    matrix = imputation_matrix(base, include_outcome=True, country_structure="group", year_effects=True, lagged_predictors=False)
    diagnostics = pmm_donor_diagnostics(matrix, k_pmm=20)
    diagnostics.to_csv(OUTPUTS / "mi_pmm_donor_diagnostics.csv", index=False)

    display = diagnostics.copy()
    if display.empty:
        lines = [
            r"\begin{tabular}{@{}lrrrr@{}}",
            r"\toprule",
            r"Matrix column & Observed & Missing & Donor pool & Warning \\",
            r"\midrule",
            r"No imputed matrix columns & 0 & 0 & 0 & no \\",
            r"\bottomrule",
            r"\end{tabular}",
            "",
        ]
    else:
        display["Column"] = display["matrix_column"].str.replace("_", r"\_", regex=False)
        display["Observed"] = display["observed_n"].astype(int).astype(str)
        display["Missing"] = display["missing_n"].astype(int).astype(str)
        display["Donor pool"] = display["effective_donor_pool"].astype(int).astype(str)
        display["Warning"] = display["donor_warning"]
        lines = [
            r"\begin{tabular}{@{}lrrrr@{}}",
            r"\toprule",
            r"Matrix column & Observed & Missing & Donor pool & Warning \\",
            r"\midrule",
        ]
        for _, row in display.iterrows():
            lines.append(f"{row['Column']} & {row['Observed']} & {row['Missing']} & {row['Donor pool']} & {row['Warning']} \\\\")
        lines.extend([r"\bottomrule", r"\end{tabular}", ""])
    lines.extend(
        [
            r"\vspace{0.2em}",
            r"\begin{minipage}{0.92\textwidth}\scriptsize Notes: Donor diagnostics describe the baseline PMM matrix before imputation. The effective donor pool is the smaller of \(k=20\) and the number of observed values for a matrix column. Warnings indicate columns where fewer than 20 observed donor values were available.\end{minipage}",
        ]
    )
    (TABLES / "mi_pmm_donor_diagnostics.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return diagnostics


def write_mi_diagnostics(target: pd.DataFrame, variants: pd.DataFrame) -> None:
    label_map = {
        "log_gdp_per_capita": "Log GDP",
        "gdp_per_capita_eur": "GDP per capita",
        "unemployment_rate_pc": "Unemployment",
        "poverty_or_social_exclusion_pc": "Poverty/social exclusion",
        "government_health_expenditure_gdp_pc": "Government health expenditure",
        "compulsory_health_financing_gdp_pc": "Compulsory financing",
        "gini_income": "Gini",
        "physicians_per_100k": "Physicians",
        "hospital_beds_per_100k": "Hospital beds",
        "oop_health_expenditure_share_pc": "OOP share",
        "long_term_unemployment_rate_pc": "Long-term unemployment",
    }
    diagnostics_rows = []
    observed_imputed = pd.read_csv(OUTPUTS / "mi_observed_vs_imputed_baseline.csv")
    plausibility = pd.read_csv(OUTPUTS / "mi_plausibility_checks_baseline.csv")
    observed_imputed = observed_imputed.set_index("variable")
    plausibility = plausibility.set_index("variable")
    for var in [v for v in IMPUTE_VARS if v in target.columns]:
        observed = target.loc[target[var].notna(), ["geo", "year", var]]
        lower, upper = IMPUTATION_BOUNDS.get(var, (np.nan, np.nan))
        dist = observed_imputed.loc[var] if var in observed_imputed.index else pd.Series(dtype=float)
        plaus = plausibility.loc[var] if var in plausibility.index else pd.Series(dtype=float)
        diagnostics_rows.append(
            {
                "variable": var,
                "label": label_map.get(var, var),
                "observed_n": int(observed[var].notna().sum()),
                "missing_n": int(target[var].isna().sum()),
                "missing_pct": float(target[var].isna().mean() * 100),
                "first_observed_year": int(observed["year"].min()) if not observed.empty else np.nan,
                "last_observed_year": int(observed["year"].max()) if not observed.empty else np.nan,
                "countries_observed": int(observed["geo"].nunique()) if not observed.empty else 0,
                "lower_bound": lower,
                "upper_bound": upper,
                "imputed_n": int(plaus.get("imputed_n", 0)) if not plaus.empty else 0,
                "imputed_min": float(plaus.get("imputed_min", np.nan)) if not plaus.empty else np.nan,
                "imputed_max": float(plaus.get("imputed_max", np.nan)) if not plaus.empty else np.nan,
                "outside_bounds": int(plaus.get("outside_bounds", 0)) if not plaus.empty else 0,
                "observed_mean": float(dist.get("observed_mean", np.nan)) if not dist.empty else np.nan,
                "imputed_mean": float(dist.get("imputed_mean", np.nan)) if not dist.empty else np.nan,
                "observed_p05": float(dist.get("observed_p05", np.nan)) if not dist.empty else np.nan,
                "imputed_p05": float(dist.get("imputed_p05", np.nan)) if not dist.empty else np.nan,
                "observed_p95": float(dist.get("observed_p95", np.nan)) if not dist.empty else np.nan,
                "imputed_p95": float(dist.get("imputed_p95", np.nan)) if not dist.empty else np.nan,
            }
        )
    diagnostics = pd.DataFrame(diagnostics_rows)
    diagnostics.to_csv(OUTPUTS / "mi_diagnostics_summary.csv", index=False)

    fmi_rows = []
    for variant in variants["variant"]:
        path = OUTPUTS / f"improved_mi_fe_results_{variant}.csv"
        if not path.exists():
            continue
        imp = pd.read_csv(path)
        poverty = imp[imp["term"].eq("poverty_or_social_exclusion_pc")].copy()
        if poverty.empty:
            continue
        pooled = rubin_components(poverty["coef"], poverty["se"])
        variant_meta = variants[variants["variant"].eq(variant)].iloc[0].to_dict()
        fmi_rows.append(
            {
                "variant": variant,
                "imputations": int(variant_meta["imputations"]),
                "coef": pooled["estimate"],
                "se": pooled["se"],
                "p_value": pooled["p_value"],
                "within_variance": pooled["within_variance"],
                "between_variance": pooled["between_variance"],
                "total_variance": pooled["total_variance"],
                "relative_increase_variance": pooled["relative_increase_variance"],
                "fraction_missing_information": pooled["fraction_missing_information"],
                "min_coef": float(poverty["coef"].min()),
                "median_coef": float(poverty["coef"].median()),
                "max_coef": float(poverty["coef"].max()),
            }
        )
        if variant in {"baseline_pmm", "baseline"}:
            poverty.to_csv(OUTPUTS / "mi_coefficient_distribution.csv", index=False)
    fmi = pd.DataFrame(fmi_rows)
    fmi.to_csv(OUTPUTS / "mi_fmi_poverty.csv", index=False)

    coef_dist_path = OUTPUTS / "mi_coefficient_distribution.csv"
    if coef_dist_path.exists():
        coef_dist = pd.read_csv(coef_dist_path)
        plt.figure(figsize=(7.0, 4.2))
        sns.histplot(coef_dist["coef"], bins=12, color="#3f6f8f", edgecolor="white")
        pooled_baseline = fmi.loc[fmi["variant"].isin(["baseline_pmm", "baseline"]), "coef"]
        if not pooled_baseline.empty:
            plt.axvline(float(pooled_baseline.iloc[0]), color="#9b2d30", linewidth=1.6, label="Rubin pooled estimate")
            plt.legend(frameon=False)
        plt.xlabel("Poverty coefficient across baseline imputations")
        plt.ylabel("Number of imputations")
        plt.tight_layout()
        plt.savefig(FIGURES / "mi_coefficient_distribution.pdf", dpi=300)
        plt.close()

    table = diagnostics.copy()
    table["Missing"] = table["missing_pct"].map(lambda x: f"{x:.1f}\\%")
    table["Bounds"] = table.apply(lambda r: f"[{r['lower_bound']:.1f}, {r['upper_bound']:.1f}]", axis=1)
    table["Viol."] = table["outside_bounds"].astype(int).astype(str)
    table["Obs. mean"] = table["observed_mean"].map(lambda x: f"{x:.2f}" if pd.notna(x) else "")
    table["Imp. mean"] = table["imputed_mean"].map(lambda x: f"{x:.2f}" if pd.notna(x) else "")
    lines = [
        r"\resizebox{\textwidth}{!}{%",
        r"\begin{tabular}{@{}lrrrrr@{}}",
        r"\toprule",
        r"Variable & Missing & Bounds & Viol. & Obs. mean & Imp. mean \\",
        r"\midrule",
    ]
    for _, row in table.iterrows():
        lines.append(
            f"{row['label']} & {row['Missing']} & {row['Bounds']} & {row['Viol.']} & {row['Obs. mean']} & {row['Imp. mean']} \\\\"
        )
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}%",
            r"}",
            "",
            r"\vspace{0.2em}",
            r"\begin{minipage}{0.96\textwidth}\scriptsize Notes: Diagnostics refer to the baseline 30-imputation model over the 608 outcome-observed country-years. Bounds are the plausible ranges imposed before fitting the fixed-effects model. Viol. counts imputed values outside those bounds after clipping and should be zero.\end{minipage}",
        ]
    )
    (TABLES / "mi_diagnostics_summary.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_missingness_table(rows: pd.DataFrame) -> None:
    display = rows.copy()
    display["Coef."] = display["coef"].map(lambda x: f"{x:.4f}" if pd.notna(x) else "")
    display["SE"] = display["se"].map(lambda x: f"{x:.4f}" if pd.notna(x) else "")
    display["p-value"] = display["p_value"].map(format_p_value)
    display["N"] = display["nobs"].map(lambda x: f"{int(round(x))}" if pd.notna(x) else "")
    lines = [
        r"\begin{tabular}{@{}lrrrr@{}}",
        r"\toprule",
        r"Specification & Coef. & SE & p-value & \(N\) \\",
        r"\midrule",
    ]
    for _, row in display.iterrows():
        lines.append(f"{row['specification']} & {row['Coef.']} & {row['SE']} & {row['p-value']} & {row['N']} \\\\")
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}",
            "",
            r"\vspace{0.2em}",
            r"\begin{minipage}{0.92\textwidth}",
            r"\scriptsize Notes: All rows report the poverty or social exclusion coefficient from country-and-year fixed-effects models. "
            r"Complete-case and IPW rows use country-clustered standard errors. IPW weights are stabilized and truncated at the 1st and 99th percentiles. "
            r"The improved multiple-imputation row pools 30 imputed full outcome-observed panels using Rubin's rules.",
            r"\end{minipage}",
        ]
    )
    (TABLES / "missingness_robustness_results.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


def sensitivity_row(
    target_population: str,
    weighting: str,
    missingness: str,
    interpretation: str,
    result,
    df: pd.DataFrame,
    term: str = "poverty_or_social_exclusion_pc",
    universe: str = "Full Eurostat-available",
) -> dict[str, float | str | int]:
    conf = result.conf_int().loc[term]
    return {
        "universe": universe,
        "target_population": target_population,
        "weighting": weighting,
        "missingness_handling": missingness,
        "countries": int(df["geo"].nunique()),
        "rows": int(result.nobs),
        "poverty_coef": float(result.params[term]),
        "ci_low": float(conf.iloc[0]),
        "ci_high": float(conf.iloc[1]),
        "p_value": float(result.pvalues[term]),
        "interpretation_label": interpretation,
    }


def mi_sensitivity_row(mi_row: pd.Series) -> dict[str, float | str | int]:
    coef = float(mi_row["coef"])
    se = float(mi_row["se"])
    return {
        "universe": "Full Eurostat-available",
        "target_population": "Full outcome-observed",
        "weighting": "Unweighted",
        "missingness_handling": "30-imputation PMM MI",
        "countries": int(round(float(mi_row["mean_countries"]))),
        "rows": int(round(float(mi_row["mean_nobs"]))),
        "poverty_coef": coef,
        "ci_low": coef - 1.96 * se,
        "ci_high": coef + 1.96 * se,
        "p_value": float(mi_row["p_value"]),
        "interpretation_label": "model-based full-target sensitivity",
    }


def universe_sensitivity_row(label: str, countries: set[str], target: pd.DataFrame) -> dict[str, float | str | int]:
    subset = model_sample(target[target["geo"].isin(countries)].copy())
    feasible, status = feasible_fe_sample(subset)
    row: dict[str, float | str | int] = {
        "universe": label,
        "countries": int(subset["geo"].nunique()) if "geo" in subset.columns else 0,
        "rows": int(len(subset)),
        "status": status,
        "poverty_coef": np.nan,
        "ci_low": np.nan,
        "ci_high": np.nan,
        "p_value": np.nan,
    }
    if not feasible:
        return row
    result = fit_fe(subset)
    conf = result.conf_int().loc["poverty_or_social_exclusion_pc"]
    row.update(
        {
            "rows": int(result.nobs),
            "poverty_coef": float(result.params["poverty_or_social_exclusion_pc"]),
            "ci_low": float(conf.iloc[0]),
            "ci_high": float(conf.iloc[1]),
            "p_value": float(result.pvalues["poverty_or_social_exclusion_pc"]),
            "status": "estimated",
        }
    )
    return row


def write_universe_sensitivity_table(target: pd.DataFrame) -> pd.DataFrame:
    full_countries = set(target["geo"].dropna().astype(str))
    universes = [
        ("Full Eurostat-available", full_countries),
        ("EU-27", EU27),
        ("EEA countries", EEA_COUNTRIES),
        ("Extended Europe", EU27 | EEA_COUNTRIES | SWITZERLAND | UK_COUNTRIES | CANDIDATE_POTENTIAL),
        ("Candidate/potential candidate", CANDIDATE_POTENTIAL),
    ]
    rows = pd.DataFrame([universe_sensitivity_row(label, countries, target) for label, countries in universes])
    rows.to_csv(OUTPUTS / "universe_sensitivity_results.csv", index=False)

    display = rows.copy()
    display["universe"] = display["universe"].replace(
        {
            "Full Eurostat-available": "Full",
            "Extended Europe": "Extended",
            "Candidate/potential candidate": "Candidates",
        }
    )
    display["status"] = display["status"].replace(
        {
            "infeasible: fewer than 50 observations": "infeasible (<50 rows)",
        }
    )
    display["Coef. [95\\% CI]"] = display.apply(
        lambda r: (
            f"{r['poverty_coef']:.3f} [{r['ci_low']:.3f}, {r['ci_high']:.3f}]"
            if pd.notna(r["poverty_coef"])
            else ""
        ),
        axis=1,
    )
    display["p-value"] = display["p_value"].map(format_p_value)
    lines = [
        r"\begingroup",
        r"\small",
        r"\begin{tabular}{@{}lrrll@{}}",
        r"\toprule",
        r"Universe & Countries & Rows & Coef. [95\% CI] & Status \\",
        r"\midrule",
    ]
    for _, row in display.iterrows():
        lines.append(
            f"{row['universe']} & {int(row['countries'])} & {int(row['rows'])} & {row['Coef. [95\\% CI]']} & {row['status']} \\\\"
        )
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}",
            "",
            r"\vspace{0.2em}",
            r"\begin{minipage}{0.92\textwidth}\scriptsize Notes: Rows report the poverty/social-exclusion coefficient from unweighted country-and-year fixed-effects models estimated on available covariate-complete rows within each country universe. Infeasible rows are not forced when the universe has too few complete-case countries, years, or rows.\end{minipage}",
            r"\endgroup",
        ]
    )
    (TABLES / "universe_sensitivity_results.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return rows


def write_estimand_framework_table(target: pd.DataFrame, complete_sample: pd.DataFrame, balanced_sample: pd.DataFrame) -> None:
    rows = [
        {
            "Label": "Outcome-observed",
            "Target population": "All country-years with observed \\texttt{hlth\\_silc\\_08}",
            "Countries": target["geo"].nunique(),
            "Rows": len(target),
            "Weighting": "None",
            "Interpretation": "Average-country monitoring target before covariate attrition.",
        },
        {
            "Label": "Population-weighted",
            "Target population": "Outcome-observed or selected rows with valid \\texttt{demo\\_pjan}",
            "Countries": target.loc[target[POP_WEIGHT].notna(), "geo"].nunique() if POP_WEIGHT in target.columns else 0,
            "Rows": int(target[POP_WEIGHT].notna().sum()) if POP_WEIGHT in target.columns else 0,
            "Weighting": "Year-normalized population",
            "Interpretation": "Average-resident monitoring target; not inherently more correct.",
        },
        {
            "Label": "Complete-case FE",
            "Target population": "Outcome and all baseline regression covariates observed",
            "Countries": complete_sample["geo"].nunique(),
            "Rows": len(complete_sample),
            "Weighting": "None",
            "Interpretation": "Selected analytical panel for the baseline FE coefficient.",
        },
        {
            "Label": "Balanced-outcome",
            "Target population": "Countries with complete primary-outcome and population-weight coverage",
            "Countries": balanced_sample["geo"].nunique(),
            "Rows": len(balanced_sample),
            "Weighting": "Optional",
            "Interpretation": "Coverage-restricted target; not automatically covariate-balanced.",
        },
        {
            "Label": "IPW CC",
            "Target population": "Complete cases reweighted by predicted complete-case inclusion",
            "Countries": complete_sample["geo"].nunique(),
            "Rows": len(complete_sample),
            "Weighting": "Stabilized truncated IPW",
            "Interpretation": "Selection diagnostic; cannot recover structurally missing covariates.",
        },
        {
            "Label": "MAR MI",
            "Target population": "Outcome-observed rows with model-imputed covariates",
            "Countries": target["geo"].nunique(),
            "Rows": len(target),
            "Weighting": "Usually none",
            "Interpretation": "Model-based sensitivity target under imputation assumptions.",
        },
        {
            "Label": "MNAR sensitivity",
            "Target population": "Outcome-observed rows with shifted imputed values",
            "Countries": target["geo"].nunique(),
            "Rows": len(target),
            "Weighting": "Scenario-specific",
            "Interpretation": "Stress test for departures from MAR; implemented in Step 2.",
        },
    ]
    lines = [
        r"\resizebox{\textwidth}{!}{%",
        r"\begin{tabular}{@{}p{0.16\textwidth}p{0.25\textwidth}rrp{0.20\textwidth}p{0.25\textwidth}@{}}",
        r"\toprule",
        r"Label & Target population & Countries & Rows & Weighting & Interpretation \\",
        r"\midrule",
    ]
    for row in rows:
        lines.append(
            f"{row['Label']} & {row['Target population']} & {int(row['Countries'])} & {int(row['Rows'])} & {row['Weighting']} & {row['Interpretation']} \\\\"
        )
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}%",
            r"}",
            "",
            r"\vspace{0.2em}",
            r"\begin{minipage}{0.96\textwidth}\scriptsize Notes: Row counts refer to the generated thesis pipeline. Balanced-outcome means balanced for the primary outcome and population weights, not for every regression covariate. MAR and MNAR imputation estimates are sensitivity estimates, not true coefficients.\end{minipage}",
        ]
    )
    (TABLES / "estimand_framework.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_target_sensitivity_table(rows: pd.DataFrame) -> None:
    rows.to_csv(OUTPUTS / "target_population_sensitivity_results.csv", index=False)
    display = rows.copy()
    spec_labels = []
    for _, row in display.iterrows():
        if "MI" in str(row["missingness_handling"]):
            spec_labels.append("MI full")
        elif row["target_population"] == "Balanced-outcome" and row["weighting"] == "Year-normalized population":
            spec_labels.append("Balanced pop.")
        elif row["target_population"] == "Balanced-outcome":
            spec_labels.append("Balanced")
        elif row.get("universe", "Full Eurostat-available") == "EU-27":
            spec_labels.append("EU-27 CC")
        elif row["weighting"] == "Year-normalized population":
            spec_labels.append("CC pop.")
        else:
            spec_labels.append("CC")
    display["Spec."] = spec_labels
    if "universe" not in display.columns:
        display["universe"] = "Full Eurostat-available"
    display["Universe"] = display["universe"].map(
        {
            "Full Eurostat-available": "Full available",
            "EU-27": "EU-27",
        }
    ).fillna(display["universe"])
    display["Target"] = display["target_population"].map(
        {
            "Selected complete-case": "Selected CC",
            "Balanced-outcome": "Balanced outcome",
            "Full outcome-observed": "Full observed",
        }
    )
    display["Weight"] = display["weighting"].map(
        {
            "Unweighted": "Unweighted",
            "Year-normalized population": "Population",
        }
    )
    display["Countries"] = display["countries"].astype(int).astype(str)
    display["Rows"] = display["rows"].astype(int).astype(str)
    display["Coef. [95\\% CI]"] = display.apply(lambda r: f"{r['poverty_coef']:.3f} [{r['ci_low']:.3f}, {r['ci_high']:.3f}]", axis=1)
    display["p-value"] = display["p_value"].map(format_p_value)
    display["Reading"] = display["interpretation_label"].map(
        {
            "selected complete-case result": "selected panel",
            "population-weighted selected result": "selected resident-weighted",
            "balanced-outcome restriction": "observed-panel restriction",
            "balanced-outcome weighted restriction": "weighted restriction",
            "EU-27 complete-case result": "EU-27 selected panel",
            "model-based full-target sensitivity": "model-based sensitivity",
        }
    )
    table = display[["Spec.", "Universe", "Target", "Weight", "Countries", "Rows", "Coef. [95\\% CI]", "p-value", "Reading"]]
    lines = [
        r"\resizebox{\textwidth}{!}{%",
        r"\begin{tabular}{@{}lllcrrp{0.22\textwidth}lp{0.17\textwidth}@{}}",
        r"\toprule",
        r"Spec. & Universe & Target & Weight & Countries & Rows & Coef. [95\% CI] & p-value & Reading \\",
        r"\midrule",
    ]
    for _, row in table.iterrows():
        lines.append(
            f"{row['Spec.']} & {row['Universe']} & {row['Target']} & {row['Weight']} & {row['Countries']} & {row['Rows']} & {row['Coef. [95\\% CI]']} & {row['p-value']} & {row['Reading']} \\\\"
        )
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}%",
            r"}",
            "",
            r"\vspace{0.2em}",
            r"\begin{minipage}{0.96\textwidth}\scriptsize Notes: The coefficient is for poverty or social exclusion in country-and-year fixed-effects models with country-clustered standard errors, except the MI row, which pools fixed-effects estimates using Rubin's rules. Full available means all Eurostat-available national units in the outcome-observed panel; EU-27 restricts to current EU member states. Population weights are country-year total population from \texttt{demo\_pjan}, normalized within year.\end{minipage}",
        ]
    )
    (TABLES / "target_population_sensitivity_results.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


def ladder_estimated_row(
    step: str,
    target: str,
    weighting: str,
    missing_assumption: str,
    interpretation: str,
    result,
    df: pd.DataFrame,
    term: str = "poverty_or_social_exclusion_pc",
) -> dict[str, float | str | int]:
    conf = result.conf_int().loc[term]
    return {
        "step": step,
        "target": target,
        "rows": int(result.nobs),
        "countries": int(df["geo"].nunique()),
        "weighting": weighting,
        "missing_data_assumption": missing_assumption,
        "term": term,
        "coef": float(result.params[term]),
        "ci_low": float(conf.iloc[0]),
        "ci_high": float(conf.iloc[1]),
        "p_value": float(result.pvalues[term]),
        "interpretation": interpretation,
        "status": "estimated",
    }


def ladder_infeasible_row(
    step: str,
    target: str,
    weighting: str,
    missing_assumption: str,
    interpretation: str,
    df: pd.DataFrame,
    status: str,
    term: str = "poverty_or_social_exclusion_pc",
) -> dict[str, float | str | int]:
    return {
        "step": step,
        "target": target,
        "rows": int(len(df)),
        "countries": int(df["geo"].nunique()) if "geo" in df.columns and not df.empty else 0,
        "weighting": weighting,
        "missing_data_assumption": missing_assumption,
        "term": term,
        "coef": np.nan,
        "ci_low": np.nan,
        "ci_high": np.nan,
        "p_value": np.nan,
        "interpretation": interpretation,
        "status": status,
    }


def ladder_from_sample(
    step: str,
    target: str,
    weighting: str,
    missing_assumption: str,
    interpretation: str,
    df: pd.DataFrame,
    fit_func,
) -> dict[str, float | str | int]:
    sample = model_sample(df)
    feasible, status = feasible_fe_sample(sample)
    if not feasible:
        return ladder_infeasible_row(step, target, weighting, missing_assumption, interpretation, sample, status)
    try:
        return ladder_estimated_row(step, target, weighting, missing_assumption, interpretation, fit_func(sample), sample)
    except Exception as exc:  # noqa: BLE001 - this table must record failed sensitivities.
        return ladder_infeasible_row(
            step,
            target,
            weighting,
            missing_assumption,
            interpretation,
            sample,
            f"infeasible: {type(exc).__name__}",
        )


def ladder_from_robustness(
    summary: pd.DataFrame,
    specification: str,
    step: str,
    target: str,
    weighting: str,
    missing_assumption: str,
    interpretation: str,
) -> dict[str, float | str | int]:
    row = summary[summary["specification"].eq(specification)]
    if row.empty:
        return ladder_infeasible_row(step, target, weighting, missing_assumption, interpretation, pd.DataFrame(), "infeasible: missing robustness row")
    r = row.iloc[0]
    return {
        "step": step,
        "target": target,
        "rows": int(r["nobs"]),
        "countries": int(r["countries"]),
        "weighting": weighting,
        "missing_data_assumption": missing_assumption,
        "term": r.get("term", "poverty_or_social_exclusion_pc"),
        "coef": float(r["coef"]) if pd.notna(r["coef"]) else np.nan,
        "ci_low": float(r["ci_low"]) if pd.notna(r["ci_low"]) else np.nan,
        "ci_high": float(r["ci_high"]) if pd.notna(r["ci_high"]) else np.nan,
        "p_value": float(r["p_value"]) if pd.notna(r["p_value"]) else np.nan,
        "interpretation": interpretation,
        "status": str(r["status"]),
    }


def ladder_from_mi(
    step: str,
    target: str,
    weighting: str,
    missing_assumption: str,
    interpretation: str,
    row: pd.Series,
) -> dict[str, float | str | int]:
    coef = float(row["coef"])
    se = float(row["se"])
    return {
        "step": step,
        "target": target,
        "rows": int(round(float(row["mean_nobs"]))),
        "countries": int(round(float(row["mean_countries"]))),
        "weighting": weighting,
        "missing_data_assumption": missing_assumption,
        "term": "poverty_or_social_exclusion_pc",
        "coef": coef,
        "ci_low": float(row["ci_low"]) if "ci_low" in row.index and pd.notna(row["ci_low"]) else coef - 1.96 * se,
        "ci_high": float(row["ci_high"]) if "ci_high" in row.index and pd.notna(row["ci_high"]) else coef + 1.96 * se,
        "p_value": float(row["p_value"]),
        "interpretation": interpretation,
        "status": "estimated",
    }


def write_main_sensitivity_ladder(
    target: pd.DataFrame,
    complete_sample: pd.DataFrame,
    complete_fit,
    pop_fit,
    balanced_sample: pd.DataFrame,
    ipw_fit,
    improved_poverty: pd.Series,
    mnar: pd.DataFrame,
    poverty_summary: pd.DataFrame,
) -> pd.DataFrame:
    rows: list[dict[str, float | str | int]] = []
    rows.append(
        ladder_from_sample(
            "Pooled complete-case",
            "selected complete-case rows",
            "unweighted",
            "available covariate complete cases",
            "associational baseline before country FE",
            complete_sample,
            fit_pooled_year,
        )
    )
    rows.append(
        ladder_from_sample(
            "Country FE",
            "selected complete-case rows",
            "unweighted",
            "available covariate complete cases",
            "absorbs persistent country differences",
            complete_sample,
            fit_country_fe,
        )
    )
    rows.append(
        ladder_estimated_row(
            "Country + year FE",
            "selected complete-case rows",
            "unweighted",
            "available covariate complete cases",
            "selected-panel primary FE estimate",
            complete_fit,
            complete_sample,
        )
    )
    rows.append(
        ladder_estimated_row(
            "Population-weighted FE",
            "selected complete-case rows",
            "year-normalized population",
            "available covariate complete cases",
            "resident-weighted selected-panel estimand",
            pop_fit,
            complete_sample,
        )
    )
    rows.append(
        ladder_from_sample(
            "Balanced-outcome FE",
            "balanced outcome/population country set",
            "unweighted",
            "available covariate complete cases",
            "coverage-restricted monitoring target",
            balanced_sample,
            fit_fe,
        )
    )
    rows.append(
        ladder_estimated_row(
            "Full Eurostat-available FE",
            "full Eurostat-available complete-case rows",
            "unweighted",
            "available covariate complete cases",
            "full operational Europe universe",
            complete_fit,
            complete_sample,
        )
    )
    rows.append(
        ladder_from_sample(
            "EU-27 FE",
            "EU-27 complete-case rows",
            "unweighted",
            "available covariate complete cases",
            "EU institutional universe sensitivity",
            target[target["geo"].isin(EU27)].copy(),
            fit_fe,
        )
    )
    for label, countries in [
        ("Extended Europe FE", EU27 | EEA_COUNTRIES | SWITZERLAND | UK_COUNTRIES | CANDIDATE_POTENTIAL),
        ("EEA-country FE", EEA_COUNTRIES),
        ("Candidate FE", CANDIDATE_POTENTIAL),
    ]:
        rows.append(
            ladder_from_sample(
                label,
                f"{label.replace(' FE', '').lower()} complete-case rows",
                "unweighted",
                "available covariate complete cases",
                "additional country-universe sensitivity",
                target[target["geo"].isin(countries)].copy(),
                fit_fe,
            )
        )
    rows.append(
        ladder_from_robustness(
            poverty_summary,
            "Lagged covariates",
            "Lagged covariates",
            "outcome-observed rows with lag-complete covariates",
            "unweighted",
            "lagged available covariate complete cases",
            "temporal-ordering check",
        )
    )
    rows.append(
        ladder_from_robustness(
            poverty_summary,
            "Excluding 2015",
            "Excluding 2015",
            "selected complete-case rows excluding 2015",
            "unweighted",
            "available covariate complete cases",
            "measurement-break diagnostic",
        )
    )
    rows.append(
        ladder_from_robustness(
            poverty_summary,
            "Excluding COVID years",
            "Excluding COVID years",
            "selected complete-case rows excluding 2020--2022",
            "unweighted",
            "available covariate complete cases",
            "crisis-period sensitivity",
        )
    )
    rows.append(
        ladder_from_robustness(
            poverty_summary,
            "Country-specific trends",
            "Country trends",
            "selected complete-case rows",
            "unweighted",
            "available covariate complete cases plus trends",
            "conservative over-control sensitivity",
        )
    )
    rows.append(
        ladder_estimated_row(
            "IPW",
            "selected complete-case rows",
            "stabilized truncated IPW",
            "selection model adequate; positivity holds",
            "selection diagnostic, not structural correction",
            ipw_fit,
            complete_sample,
        )
    )
    rows.append(
        ladder_from_mi(
            "MAR MI",
            "608 outcome-observed rows",
            "unweighted",
            "baseline PMM MAR-type sensitivity",
            "model-based broader target",
            improved_poverty,
        )
    )
    for variant, step, interpretation in [
        ("mnar_pessimistic_combo", "MNAR pessimistic", "missing rows shifted toward worse macro-social conditions"),
        ("mnar_optimistic_combo", "MNAR optimistic", "missing rows shifted toward less severe macro-social conditions"),
    ]:
        mnar_row = mnar[mnar["variant"].eq(variant)]
        if mnar_row.empty:
            rows.append(ladder_infeasible_row(step, "608 outcome-observed rows", "unweighted", "MNAR delta shift", interpretation, pd.DataFrame(), "infeasible: missing MNAR row"))
        else:
            rows.append(ladder_from_mi(step, "608 outcome-observed rows", "unweighted", "PMM plus MNAR delta shift", interpretation, mnar_row.iloc[0]))

    out = pd.DataFrame(rows)
    out.to_csv(OUTPUTS / "main_sensitivity_ladder.csv", index=False)

    table = out.copy()
    table["Coef. [95\\% CI]"] = table.apply(
        lambda r: (
            f"{r['coef']:.3f} [{r['ci_low']:.3f}, {r['ci_high']:.3f}]"
            if pd.notna(r["coef"]) and pd.notna(r["ci_low"]) and pd.notna(r["ci_high"])
            else "not estimated"
        ),
        axis=1,
    )
    table["Rows"] = table["rows"].astype(int).astype(str)
    table["Countries"] = table["countries"].astype(int).astype(str)
    lines = [
        r"\resizebox{\textwidth}{!}{%",
        r"\begin{tabular}{@{}p{0.18\textwidth}p{0.23\textwidth}rrp{0.16\textwidth}p{0.22\textwidth}@{}}",
        r"\toprule",
        r"Step & Target & Countries & Rows & Coef. [95\% CI] & Interpretation \\",
        r"\midrule",
    ]
    for _, row in table.iterrows():
        lines.append(
            f"{row['step']} & {row['target']} & {row['Countries']} & {row['Rows']} & {row['Coef. [95\\% CI]']} & {row['interpretation']} \\\\"
        )
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}%",
            r"}",
            "",
            r"\vspace{0.2em}",
            r"\begin{minipage}{0.96\textwidth}\scriptsize Notes: The ladder follows the poverty/social-exclusion coefficient as the model, country universe, weighting rule, selection adjustment, and imputation assumption change. Infeasible rows are retained when fixed-effects estimation has too few rows, countries, or years. MAR and MNAR rows are model-based sensitivity estimands, not corrected truth.\end{minipage}",
        ]
    )
    (TABLES / "main_sensitivity_ladder.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def poverty_robustness_result(
    label: str,
    interpretation: str,
    df: pd.DataFrame,
    covars: list[str] | None = None,
    term: str = "poverty_or_social_exclusion_pc",
    weights: np.ndarray | None = None,
    country_trends: bool = False,
) -> dict[str, float | str | int]:
    covars = covars or BASELINE_COVARS
    needed = ["geo", "year", OUTCOME] + covars
    sample = df[needed].dropna().copy()
    feasible, status = feasible_fe_sample(sample)
    row: dict[str, float | str | int] = {
        "specification": label,
        "interpretation": interpretation,
        "term": term,
        "coef": np.nan,
        "se": np.nan,
        "p_value": np.nan,
        "ci_low": np.nan,
        "ci_high": np.nan,
        "nobs": int(len(sample)),
        "countries": int(sample["geo"].nunique()) if not sample.empty else 0,
        "years": int(sample["year"].nunique()) if not sample.empty else 0,
        "status": status,
    }
    if not feasible:
        return row
    try:
        fit_weights = None
        if weights is not None:
            aligned_weights = pd.Series(weights, index=df.index)
            fit_weights = aligned_weights.loc[sample.index].to_numpy()
        result = fit_fe_with_covars(sample, covars, weights=fit_weights, country_trends=country_trends)
        conf = result.conf_int().loc[term]
        row.update(
            {
                "coef": float(result.params[term]),
                "se": float(result.bse[term]),
                "p_value": float(result.pvalues[term]),
                "ci_low": float(conf.iloc[0]),
                "ci_high": float(conf.iloc[1]),
                "nobs": int(result.nobs),
                "countries": int(sample["geo"].nunique()),
                "years": int(sample["year"].nunique()),
                "status": "estimated",
            }
        )
    except Exception as exc:  # noqa: BLE001 - diagnostics must record unstable FE fits.
        row["status"] = f"infeasible: {type(exc).__name__}"
    return row


def leave_one_country_out_summary(sample: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for geo in sorted(sample["geo"].dropna().unique()):
        fit_sample = sample[sample["geo"].ne(geo)].copy()
        row = poverty_robustness_result(
            f"Leave out {geo}",
            "country influence",
            fit_sample,
        )
        row["dropped_country"] = geo
        rows.append(row)
    out = pd.DataFrame(rows)
    out.to_csv(OUTPUTS / "leave_one_country_out_poverty.csv", index=False)
    return out


def measurement_break_diagnostics(complete_sample: pd.DataFrame) -> pd.DataFrame:
    rows = [
        poverty_robustness_result(
            "Excluding 2015",
            "2015 measurement-change diagnostic",
            complete_sample[complete_sample["year"].ne(2015)].copy(),
        ),
        poverty_robustness_result(
            "2016 onward",
            "post-2015 restriction",
            complete_sample[complete_sample["year"].ge(2016)].copy(),
        ),
        poverty_robustness_result(
            "2016-2019",
            "pre-COVID period",
            complete_sample[complete_sample["year"].between(2016, 2019)].copy(),
        ),
        poverty_robustness_result(
            "2020-2024",
            "COVID/post-COVID period",
            complete_sample[complete_sample["year"].between(2020, 2024)].copy(),
        ),
    ]
    out = pd.DataFrame(rows)
    out.to_csv(OUTPUTS / "measurement_break_2015_poverty.csv", index=False)
    return out


def lagged_covariate_sample(target: pd.DataFrame, lag: int = 1) -> tuple[pd.DataFrame, list[str]]:
    work = target.sort_values(["geo", "year"]).copy()
    lagged_covars = []
    for covar in BASELINE_COVARS:
        lag_name = f"lag{lag}_{covar}"
        work[lag_name] = work.groupby("geo")[covar].shift(lag)
        lagged_covars.append(lag_name)
    return work, lagged_covars


def high_low_unmet_rows(complete_sample: pd.DataFrame) -> list[dict[str, float | str | int]]:
    country_means = complete_sample.groupby("geo", as_index=False)[OUTCOME].mean().sort_values(OUTCOME)
    low = set(country_means.head(3)["geo"])
    high = set(country_means.tail(3)["geo"])
    return [
        poverty_robustness_result(
            "Excluding high-unmet countries",
            f"influence check; dropped {', '.join(sorted(high))}",
            complete_sample[~complete_sample["geo"].isin(high)].copy(),
        ),
        poverty_robustness_result(
            "Excluding low-unmet countries",
            f"influence check; dropped {', '.join(sorted(low))}",
            complete_sample[~complete_sample["geo"].isin(low)].copy(),
        ),
    ]


def write_poverty_robustness_outputs(
    target: pd.DataFrame,
    complete_sample: pd.DataFrame,
    improved_poverty: pd.Series,
) -> pd.DataFrame:
    rows: list[dict[str, float | str | int]] = []
    rows.append(poverty_robustness_result("Baseline complete-case FE", "selected panel", complete_sample))
    rows.append(
        poverty_robustness_result(
            "Population-weighted CC FE",
            "resident-weighted selected panel",
            complete_sample,
            weights=complete_sample[POP_WEIGHT].to_numpy() if POP_WEIGHT in complete_sample.columns else None,
        )
    )
    lagged_target, lagged_covars = lagged_covariate_sample(target, lag=1)
    rows.append(
        poverty_robustness_result(
            "Lagged covariates",
            "temporal ordering check",
            lagged_target,
            covars=lagged_covars,
            term="lag1_poverty_or_social_exclusion_pc",
        )
    )
    rows.append(
        poverty_robustness_result(
            "Excluding COVID years",
            "crisis-period sensitivity; excludes 2020-2022",
            complete_sample[~complete_sample["year"].between(2020, 2022)].copy(),
        )
    )
    rows.extend(measurement_break_diagnostics(complete_sample).to_dict("records"))
    rows.extend(high_low_unmet_rows(complete_sample))
    loo = leave_one_country_out_summary(complete_sample)
    estimated_loo = loo[loo["status"].eq("estimated")].copy()
    if estimated_loo.empty:
        rows.append(
            {
                "specification": "Leave-one-country-out range",
                "interpretation": "country influence",
                "term": "poverty_or_social_exclusion_pc",
                "coef": np.nan,
                "se": np.nan,
                "p_value": np.nan,
                "ci_low": np.nan,
                "ci_high": np.nan,
                "nobs": int(len(complete_sample)),
                "countries": int(complete_sample["geo"].nunique()),
                "years": int(complete_sample["year"].nunique()),
                "status": "infeasible: no stable leave-one-country fits",
            }
        )
    else:
        min_row = estimated_loo.loc[estimated_loo["coef"].idxmin()]
        max_row = estimated_loo.loc[estimated_loo["coef"].idxmax()]
        rows.append(
            {
                "specification": "Leave-one-country-out range",
                "interpretation": f"country influence; min drops {min_row['dropped_country']}, max drops {max_row['dropped_country']}",
                "term": "poverty_or_social_exclusion_pc",
                "coef": float(estimated_loo["coef"].median()),
                "se": np.nan,
                "p_value": np.nan,
                "ci_low": float(estimated_loo["coef"].min()),
                "ci_high": float(estimated_loo["coef"].max()),
                "nobs": int(estimated_loo["nobs"].median()),
                "countries": int(estimated_loo["countries"].median()),
                "years": int(estimated_loo["years"].median()),
                "status": "estimated range",
            }
        )
    rows.append(
        poverty_robustness_result(
            "Country-specific trends",
            "conservative over-control sensitivity",
            complete_sample,
            country_trends=True,
        )
    )
    rows.append(
        {
            "specification": "MI full target",
            "interpretation": "model-based broader target",
            "term": "poverty_or_social_exclusion_pc",
            "coef": float(improved_poverty["coef"]),
            "se": float(improved_poverty["se"]),
            "p_value": float(improved_poverty["p_value"]),
            "ci_low": float(improved_poverty["coef"] - 1.96 * improved_poverty["se"]),
            "ci_high": float(improved_poverty["coef"] + 1.96 * improved_poverty["se"]),
            "nobs": int(round(float(improved_poverty["mean_nobs"]))),
            "countries": int(round(float(improved_poverty["mean_countries"]))),
            "years": int(target["year"].nunique()),
            "status": "estimated",
        }
    )
    summary = pd.DataFrame(rows)
    summary.to_csv(OUTPUTS / "poverty_robustness_summary.csv", index=False)

    table = summary.copy()
    table["Coef. [95\\% CI]"] = table.apply(
        lambda r: (
            f"{r['coef']:.3f} [{r['ci_low']:.3f}, {r['ci_high']:.3f}]"
            if pd.notna(r["coef"]) and pd.notna(r["ci_low"]) and pd.notna(r["ci_high"])
            else "not estimated"
        ),
        axis=1,
    )
    table["p-value"] = table["p_value"].map(format_p_value)
    table["N"] = table["nobs"].astype(int).astype(str)
    table["Countries"] = table["countries"].astype(int).astype(str)
    lines = [
        r"\resizebox{\textwidth}{!}{%",
        r"\begin{tabular}{@{}lp{0.25\textwidth}rrlp{0.20\textwidth}@{}}",
        r"\toprule",
        r"Check & Interpretation & Countries & \(N\) & Coef. [95\% CI] & Status \\",
        r"\midrule",
    ]
    for _, row in table.iterrows():
        lines.append(
            f"{row['specification']} & {row['interpretation']} & {row['Countries']} & {row['N']} & {row['Coef. [95\\% CI]']} & {row['status']} \\\\"
        )
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}%",
            r"}",
            "",
            r"\vspace{0.2em}",
            r"\begin{minipage}{0.96\textwidth}\scriptsize Notes: All estimated rows report the poverty/social-exclusion coefficient from country-and-year fixed-effects models with country-clustered standard errors, except the MI row, which uses Rubin pooling. Specifications with too few observations, countries, years, or unstable fixed-effects estimation are reported as infeasible rather than forced.\end{minipage}",
        ]
    )
    (TABLES / "poverty_robustness_summary.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")

    plot = summary[summary["status"].isin(["estimated", "estimated range"]) & summary["coef"].notna()].copy()
    if not plot.empty:
        plot = plot.iloc[::-1].reset_index(drop=True)
        y = np.arange(len(plot))
        plt.figure(figsize=(8.5, max(4.8, 0.34 * len(plot))))
        plt.axvline(0, color="#4c4c4c", linewidth=0.9)
        for idx, row in plot.iterrows():
            color = "#9b2d30" if row["specification"] == "MI full target" else "#3f6f8f"
            if pd.notna(row["ci_low"]) and pd.notna(row["ci_high"]):
                plt.plot([row["ci_low"], row["ci_high"]], [idx, idx], color=color, linewidth=1.6)
            plt.scatter(row["coef"], idx, color=color, s=28, zorder=3)
        plt.yticks(y, plot["specification"])
        plt.xlabel("Poverty/social-exclusion coefficient")
        plt.tight_layout()
        plt.savefig(FIGURES / "poverty_robustness_forest.pdf", dpi=300)
        plt.close()
    return summary


def main() -> None:
    panel = pd.read_csv(DATA_PROCESSED / "panel_features_v2-3.csv")
    target = ensure_population_weights(panel.dropna(subset=[OUTCOME]).copy())
    target, _ = estimate_inclusion_probabilities(target)
    complete_case_selection_model(target)
    target = add_ipw_weights(target)
    target.to_csv(OUTPUTS / "missingness_inclusion_probabilities.csv", index=False)
    balance_table(target)
    weight_summary(target)
    plot_inclusion_probability(target)

    complete_sample = model_sample(target)
    country_universe = write_country_universe_table(target, complete_sample)
    universe_sensitivity = write_universe_sensitivity_table(target)
    complete = target[target["included_complete_case"].eq(1)].copy()
    complete_fit = fit_fe(complete_sample)
    inference_comparison = write_fe_inference_outputs(complete_sample, complete_fit)
    write_influence_outputs(complete_sample)
    pop_fit = fit_fe(complete_sample, weights=complete_sample[POP_WEIGHT].to_numpy() if POP_WEIGHT in complete_sample.columns else None)
    ipw_fit = fit_fe(complete_sample, weights=complete["ipw_truncated"].to_numpy())
    cc_row = term_summary("Complete-case two-way FE", complete_fit, complete_sample)
    pop_row = term_summary("Population-weighted complete-case FE", pop_fit, complete_sample)
    ipw_row = term_summary("IPW two-way FE", ipw_fit, complete_sample)
    pd.DataFrame([ipw_row]).to_csv(OUTPUTS / "ipw_fe_results.csv", index=False)

    balanced_countries = balanced_outcome_countries(target)
    balanced_target = target[target["geo"].isin(balanced_countries)].copy()
    balanced_sample = model_sample(balanced_target)
    balanced_rows = []
    if not balanced_sample.empty and balanced_sample["geo"].nunique() >= 3:
        balanced_fit = fit_fe(balanced_sample)
        balanced_pop_fit = fit_fe(balanced_sample, weights=balanced_sample[POP_WEIGHT].to_numpy())
        balanced_rows.extend(
            [
                sensitivity_row(
                    "Balanced-outcome",
                    "Unweighted",
                    "Available covariate-complete",
                    "balanced-outcome restriction",
                    balanced_fit,
                    balanced_sample,
                ),
                sensitivity_row(
                    "Balanced-outcome",
                    "Year-normalized population",
                    "Available covariate-complete",
                    "balanced-outcome weighted restriction",
                    balanced_pop_fit,
                    balanced_sample,
                ),
            ]
        )
    pd.DataFrame(
        {
            "geo": balanced_countries,
            "balanced_outcome_panel": True,
        }
    ).to_csv(OUTPUTS / "balanced_outcome_countries.csv", index=False)
    write_estimand_framework_table(target, complete_sample, balanced_sample)

    existing_mi = pd.read_csv(OUTPUTS / "multiple_imputation_pooled_results.csv").iloc[0]
    existing_row = {
        "specification": "Earlier MI sensitivity",
        "term": "poverty_or_social_exclusion_pc",
        "coef": float(existing_mi["pooled_coef"]),
        "se": float(existing_mi["pooled_se"]),
        "p_value": float(existing_mi["p_value"]),
        "nobs": float(existing_mi["mean_nobs"]),
        "countries": float(existing_mi["mean_countries"]),
    }

    variants = imputation_variant_summary(target)
    mnar = mnar_sensitivity_summary(target, m=30)
    donor_diagnostics = write_pmm_donor_diagnostics(target)
    write_mi_diagnostics(target, variants)
    improved_poverty = variants[variants["variant"].eq("baseline_pmm")].iloc[0]
    tipping = mnar_tipping_point_analysis(target, complete_fit.params["poverty_or_social_exclusion_pc"], m=30)
    poverty_summary = write_poverty_robustness_outputs(target, complete_sample, improved_poverty)
    sensitivity_ladder = write_main_sensitivity_ladder(
        target,
        complete_sample,
        complete_fit,
        pop_fit,
        balanced_sample,
        ipw_fit,
        improved_poverty,
        mnar,
        poverty_summary,
    )
    improved_row = {
        "specification": "PMM MI full target",
        "term": "poverty_or_social_exclusion_pc",
        "coef": float(improved_poverty["coef"]),
        "se": float(improved_poverty["se"]),
        "p_value": float(improved_poverty["p_value"]),
        "ci_low": float(improved_poverty["coef"] - 1.96 * improved_poverty["se"]),
        "ci_high": float(improved_poverty["coef"] + 1.96 * improved_poverty["se"]),
        "nobs": float(improved_poverty["mean_nobs"]),
        "countries": float(improved_poverty["mean_countries"]),
    }

    comparison = pd.DataFrame([cc_row, pop_row, existing_row, ipw_row, improved_row])
    comparison.to_csv(OUTPUTS / "missingness_robustness_results.csv", index=False)
    write_missingness_table(comparison)

    target_rows = [
        sensitivity_row(
            "Selected complete-case",
            "Unweighted",
            "Complete-case",
            "selected complete-case result",
            complete_fit,
            complete_sample,
        ),
        sensitivity_row(
            "Selected complete-case",
            "Unweighted",
            "Complete-case",
            "EU-27 complete-case result",
            fit_fe(model_sample(target[target["geo"].isin(EU27)].copy())),
            model_sample(target[target["geo"].isin(EU27)].copy()),
            universe="EU-27",
        ),
        sensitivity_row(
            "Selected complete-case",
            "Year-normalized population",
            "Complete-case",
            "population-weighted selected result",
            pop_fit,
            complete_sample,
        ),
        *balanced_rows,
        mi_sensitivity_row(improved_poverty),
    ]
    write_target_sensitivity_table(pd.DataFrame(target_rows))
    print("MISSINGNESS ROBUSTNESS COMPLETE")
    print(f"Target rows: {len(target)}")
    print(f"Complete-case rows: {int(target['included_complete_case'].sum())}")
    print(f"Country universe rows: {len(country_universe)}")
    print(f"Universe sensitivity rows: {len(universe_sensitivity)}")
    print(f"MNAR sensitivity rows: {len(mnar)}")
    print(f"MNAR tipping rows: {len(tipping)}")
    print(f"PMM donor diagnostic rows: {len(donor_diagnostics)}")
    print(f"Inference diagnostic rows: {len(inference_comparison)}")
    print(f"Main sensitivity ladder rows: {len(sensitivity_ladder)}")
    print(f"IPW effective sample size: {effective_sample_size(complete['ipw_truncated']):.2f}")


if __name__ == "__main__":
    main()
