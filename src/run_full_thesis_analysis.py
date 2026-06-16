from __future__ import annotations

import json
import math
import warnings
from pathlib import Path
from collections.abc import Iterable

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
import seaborn as sns
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats
from scipy.stats import chi2
from sklearn.experimental import enable_iterative_imputer  # noqa: F401
from sklearn.impute import IterativeImputer
from statsmodels.nonparametric.smoothers_lowess import lowess
from statsmodels.stats.outliers_influence import variance_inflation_factor

from eurostat_api import dataset_to_tidy, download_json, eurostat_url, is_national_geo


warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
OUTPUTS = ROOT / "outputs"
FIGURES = ROOT / "figures"
TABLES = ROOT / "tables"

for folder in [DATA_RAW, DATA_PROCESSED, OUTPUTS, FIGURES, TABLES]:
    folder.mkdir(parents=True, exist_ok=True)

RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)

OUTCOME = "unmet_need_pc"
BASELINE_COVARS = [
    "log_gdp_per_capita",
    "unemployment_rate_pc",
    "poverty_or_social_exclusion_pc",
    "government_health_expenditure_gdp_pc",
    "compulsory_health_financing_gdp_pc",
]
DESCRIPTIVE_VARS = [
    "unmet_need_pc",
    "gdp_per_capita_eur",
    "log_gdp_per_capita",
    "unemployment_rate_pc",
    "long_term_unemployment_rate_pc",
    "poverty_or_social_exclusion_pc",
    "gini_income",
    "government_health_expenditure_gdp_pc",
    "compulsory_health_financing_gdp_pc",
    "oop_health_expenditure_share_pc",
    "physicians_per_100k",
    "hospital_beds_per_100k",
]
SCATTER_COVARS = [v for v in DESCRIPTIVE_VARS if v != OUTCOME]
POPULATION = "population_total"
POP_WEIGHT = "population_weight_year_norm"

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
MIN_FE_ROWS = 50
MIN_FE_COUNTRIES = 8
MIN_FE_YEARS = 3

ATTRITION_STEPS = [
    ("Outcome observed", [OUTCOME]),
    ("+ GDP", [OUTCOME, "log_gdp_per_capita"]),
    ("+ unemployment", [OUTCOME, "log_gdp_per_capita", "unemployment_rate_pc"]),
    (
        "+ poverty/social exclusion",
        [
            OUTCOME,
            "log_gdp_per_capita",
            "unemployment_rate_pc",
            "poverty_or_social_exclusion_pc",
        ],
    ),
    (
        "+ health expenditure",
        [
            OUTCOME,
            "log_gdp_per_capita",
            "unemployment_rate_pc",
            "poverty_or_social_exclusion_pc",
            "government_health_expenditure_gdp_pc",
        ],
    ),
    ("+ compulsory financing", [OUTCOME] + BASELINE_COVARS),
]

COVARIATE_BLOCKS = {
    "Outcome": [OUTCOME],
    "Macroeconomic": ["log_gdp_per_capita", "unemployment_rate_pc"],
    "Social vulnerability": ["poverty_or_social_exclusion_pc"],
    "Financing": [
        "government_health_expenditure_gdp_pc",
        "compulsory_health_financing_gdp_pc",
        "oop_health_expenditure_share_pc",
    ],
    "Capacity": ["physicians_per_100k", "hospital_beds_per_100k"],
    "Inequality/labour": ["gini_income", "long_term_unemployment_rate_pc"],
    "Population weights": [POPULATION, POP_WEIGHT],
}

VARIABLE_LABELS = {
    OUTCOME: "Unmet need",
    "gdp_per_capita_eur": "GDP/capita",
    "log_gdp_per_capita": "Log GDP/capita",
    "unemployment_rate_pc": "Unemployment",
    "poverty_or_social_exclusion_pc": "Poverty/social exclusion",
    "government_health_expenditure_gdp_pc": "Gov. health expenditure",
    "compulsory_health_financing_gdp_pc": "Compulsory financing",
    "oop_health_expenditure_share_pc": "OOP expenditure share",
    "physicians_per_100k": "Physicians",
    "hospital_beds_per_100k": "Hospital beds",
    "gini_income": "Gini",
    "long_term_unemployment_rate_pc": "Long-term unemployment",
    POPULATION: "Population",
    POP_WEIGHT: "Population weight",
}

MODEL_LADDER_SPECS = [
    (
        "A",
        "Poverty only",
        ["poverty_or_social_exclusion_pc"],
        "social-gradient test before macro or system adjustment",
    ),
    (
        "B",
        "Poverty + GDP + unemployment",
        ["poverty_or_social_exclusion_pc", "log_gdp_per_capita", "unemployment_rate_pc"],
        "adds macroeconomic context with relatively high coverage",
    ),
    (
        "C",
        "B + health financing",
        [
            "poverty_or_social_exclusion_pc",
            "log_gdp_per_capita",
            "unemployment_rate_pc",
            "government_health_expenditure_gdp_pc",
            "compulsory_health_financing_gdp_pc",
        ],
        "baseline financing-augmented specification",
    ),
    (
        "D",
        "C + capacity",
        [
            "poverty_or_social_exclusion_pc",
            "log_gdp_per_capita",
            "unemployment_rate_pc",
            "government_health_expenditure_gdp_pc",
            "compulsory_health_financing_gdp_pc",
            "physicians_per_100k",
            "hospital_beds_per_100k",
        ],
        "adds capacity proxies and tests sample-loss cost",
    ),
    (
        "E",
        "Full theory model",
        [
            "poverty_or_social_exclusion_pc",
            "log_gdp_per_capita",
            "unemployment_rate_pc",
            "government_health_expenditure_gdp_pc",
            "compulsory_health_financing_gdp_pc",
            "oop_health_expenditure_share_pc",
            "physicians_per_100k",
            "hospital_beds_per_100k",
            "gini_income",
            "long_term_unemployment_rate_pc",
        ],
        "broad conceptual model, highest covariate burden",
    ),
    (
        "F",
        "Reduced high-coverage model",
        [
            "poverty_or_social_exclusion_pc",
            "log_gdp_per_capita",
            "unemployment_rate_pc",
            "long_term_unemployment_rate_pc",
        ],
        "parsimonious macro-labour benchmark with higher coverage than system-expanded models",
    ),
]


def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def write_latex(df: pd.DataFrame, path: Path, caption: str, label: str | None = None) -> None:
    latex = df.to_latex(
        index=False,
        escape=True,
        caption=caption,
        label=label,
        float_format=lambda x: f"{x:.3f}",
        na_rep="",
    )
    path.write_text(latex, encoding="utf-8")


def format_p_value(p_value: float) -> str:
    if pd.isna(p_value):
        return ""
    if p_value < 0.001:
        return "<0.001"
    return f"{p_value:.3f}"


def country_group_label(geo: str) -> str:
    if geo in WEST_NORTH:
        return "West/North"
    if geo in EAST_SOUTH:
        return "East/South"
    return "Other"


def fmt_num(value: float, digits: int = 1) -> str:
    if pd.isna(value):
        return ""
    return f"{value:.{digits}f}"


def write_compact_latex(
    df: pd.DataFrame,
    path: Path,
    caption: str,
    label: str,
    align: str,
    note: str | None = None,
    placement: str = "htbp",
) -> None:
    body = df.copy()
    lines = [
        rf"\begin{{table}}[{placement}]",
        r"\centering",
        r"\small",
        f"\\caption{{{caption}}}",
        f"\\label{{{label}}}",
        f"\\begin{{tabular}}{{@{{}}{align}@{{}}}}",
        r"\toprule",
        " & ".join(body.columns) + r" \\",
        r"\midrule",
    ]
    for _, row in body.iterrows():
        lines.append(" & ".join(str(row[col]) for col in body.columns) + r" \\")
    lines.extend([r"\bottomrule", r"\end{tabular}"])
    if note:
        lines.extend(
            [
                "",
                r"\vspace{0.2em}",
                rf"\begin{{minipage}}{{0.92\textwidth}}\scriptsize {note}\end{{minipage}}",
            ]
        )
    lines.extend([r"\end{table}", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def clean_name(name: str) -> str:
    return (
        name.replace("C(year)[T.", "year_")
        .replace("C(geo)[T.", "country_")
        .replace("]", "")
        .replace(")", "")
    )


def result_to_frame(result, model_name: str) -> pd.DataFrame:
    names = result.model.exog_names
    params = np.asarray(result.params)
    bse = np.asarray(result.bse)
    tvals = np.asarray(result.tvalues)
    pvals = np.asarray(result.pvalues)
    ci = np.asarray(result.conf_int())
    return pd.DataFrame(
        {
            "model": model_name,
            "term": [clean_name(n) for n in names],
            "coef": params,
            "se": bse,
            "statistic": tvals,
            "p_value": pvals,
            "ci_low": ci[:, 0],
            "ci_high": ci[:, 1],
            "nobs": int(result.nobs),
            "r2": getattr(result, "rsquared", np.nan),
        }
    )


def model_sample(df: pd.DataFrame, covars: list[str]) -> pd.DataFrame:
    cols = ["geo", "year", OUTCOME] + covars
    return df[cols].dropna(subset=[OUTCOME] + covars).copy()


def ols_cluster(formula: str, df: pd.DataFrame):
    return smf.ols(formula, data=df).fit(
        cov_type="cluster", cov_kwds={"groups": df["geo"], "use_correction": True}
    )


def fit_pooled(df: pd.DataFrame, covars: list[str]):
    formula = f"{OUTCOME} ~ {' + '.join(covars)} + C(year)"
    return ols_cluster(formula, df)


def fit_fe(df: pd.DataFrame, covars: list[str]):
    formula = f"{OUTCOME} ~ {' + '.join(covars)} + C(geo) + C(year)"
    return ols_cluster(formula, df)


def safe_term(result, term: str) -> tuple[float, float, float]:
    names = result.model.exog_names
    if term not in names:
        return np.nan, np.nan, np.nan
    idx = names.index(term)
    return (
        float(np.asarray(result.params)[idx]),
        float(np.asarray(result.bse)[idx]),
        float(np.asarray(result.pvalues)[idx]),
    )


def summary_for_term(label: str, result, term: str, n_countries: int | None = None) -> dict[str, float | str | int]:
    coef, se, p_value = safe_term(result, term)
    return {
        "specification": label,
        "term": term,
        "coef": coef,
        "se": se,
        "p_value": p_value,
        "ci_low": coef - 1.96 * se if pd.notna(coef) and pd.notna(se) else np.nan,
        "ci_high": coef + 1.96 * se if pd.notna(coef) and pd.notna(se) else np.nan,
        "nobs": int(result.nobs),
        "countries": n_countries if n_countries is not None else np.nan,
    }


def fetch_citizenship_data() -> pd.DataFrame:
    params = {
        "unit": "PC",
        "age": "Y_GE16",
        "sex": "T",
        "reason": "TOOEFW",
    }
    citizen_map = {
        "NAT": "NAT",
        "EU27_2020_FOR": "EU_FOR",
        "NEU27_2020_FOR": "NEU_FOR",
    }
    url = eurostat_url("hlth_silc_32", params)
    raw_path = DATA_RAW / "hlth_silc_32_unmet_need_by_citizenship.json"
    notes_path = OUTPUTS / "hlth_silc_32_extraction_notes.txt"
    report_path = OUTPUTS / "citizenship_data_report.txt"

    response = requests.get(url, timeout=120)
    response.raise_for_status()
    data = response.json()
    raw_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    tidy = dataset_to_tidy(data)
    expected_dims = {"unit", "citizen", "age", "sex", "reason", "geo", "time"}
    dims = set(tidy.columns) if not tidy.empty else set(data.get("id", []))
    notes = [
        f"Request URL: {url}",
        f"Dimensions found: {', '.join(data.get('id', []))}",
        f"Expected dimensions present: {expected_dims.issubset(dims)}",
        "Citizenship mapping used: NAT=NAT, EU_FOR=EU27_2020_FOR, NEU_FOR=NEU27_2020_FOR.",
    ]
    if not expected_dims.issubset(dims):
        notes.append("API structure differs from expected; extraction used available JSON-stat dimensions.")

    if tidy.empty:
        out = pd.DataFrame(columns=["country", "year", "citizen_group", "unmet_need_pc"])
    else:
        out = tidy.copy()
        if "geo" in out.columns:
            out = out[out["geo"].map(is_national_geo)].copy()
        for column, wanted in [
            ("unit", ["PC"]),
            ("age", ["Y_GE16"]),
            ("sex", ["T"]),
            ("reason", ["TOOEFW"]),
        ]:
            if column in out.columns:
                out = out[out[column].isin(wanted)].copy()
        if "citizen" in out.columns:
            out = out[out["citizen"].isin(citizen_map)].copy()
            out["citizen"] = out["citizen"].map(citizen_map)
        out["year"] = pd.to_numeric(out["time"], errors="coerce").astype("Int64")
        out["unmet_need_pc"] = pd.to_numeric(out["value"], errors="coerce")
        out = out.dropna(subset=["year", "unmet_need_pc"])
        out = out.rename(columns={"geo": "country", "citizen": "citizen_group"})
        out = out[["country", "year", "citizen_group", "unmet_need_pc"]]
        out["year"] = out["year"].astype(int)
        out = out.sort_values(["country", "year", "citizen_group"]).reset_index(drop=True)

    out.to_csv(DATA_PROCESSED / "citizenship_unmet_need.csv", index=False)

    combos = len(out)
    year_range = "NA"
    complete_group_countries: list[str] = []
    sparse_countries: list[str] = []
    if not out.empty:
        year_range = f"{int(out['year'].min())}-{int(out['year'].max())}"
        wide = out.pivot_table(
            index=["country", "year"],
            columns="citizen_group",
            values="unmet_need_pc",
            aggfunc="mean",
        )
        complete_group_countries = sorted(wide.dropna(subset=["NAT", "EU_FOR", "NEU_FOR"]).index.get_level_values(0).unique())
        years_by_country = out.groupby("country")["year"].nunique()
        sparse_countries = sorted(years_by_country[years_by_country < 3].index.tolist())

    report = [
        f"Available country-year-citizenship combinations: {combos}",
        f"Year range: {year_range}",
        "Countries with at least one year containing all three citizenship groups: "
        + (", ".join(complete_group_countries) if complete_group_countries else "None"),
        "Countries with fewer than 3 years of data: " + (", ".join(sparse_countries) if sparse_countries else "None"),
    ]
    notes_path.write_text("\n".join(notes + [""] + report), encoding="utf-8")
    report_path.write_text("\n".join(report), encoding="utf-8")
    print("\n".join(report))
    return out


def fetch_population_data(years: Iterable[int]) -> pd.DataFrame:
    params = {
        "freq": "A",
        "unit": "NR",
        "age": "TOTAL",
        "sex": "T",
    }
    raw_path = DATA_RAW / "demo_pjan_population_total.json"
    data = download_json("demo_pjan", params, raw_path)
    tidy = dataset_to_tidy(data)
    if tidy.empty:
        raise ValueError("Eurostat demo_pjan returned no population rows.")

    pop = tidy.copy()
    pop = pop[pop["geo"].map(is_national_geo)].copy()
    pop["year"] = pd.to_numeric(pop["time"], errors="coerce")
    pop[POPULATION] = pd.to_numeric(pop["value"], errors="coerce")
    pop = pop[pop["year"].isin(list(years))].dropna(subset=["year", POPULATION])
    pop["year"] = pop["year"].astype(int)
    pop = pop[["geo", "year", POPULATION, "status"]].sort_values(["geo", "year"]).reset_index(drop=True)
    pop.to_csv(DATA_PROCESSED / "feature_population_total.csv", index=False)

    notes = [
        "Eurostat population extraction for target-population sensitivity.",
        "Dataset: demo_pjan.",
        "Filter: freq=A, unit=NR, age=TOTAL, sex=T.",
        f"Rows saved: {len(pop)}.",
        f"Years requested: {min(years)}-{max(years)}.",
    ]
    (OUTPUTS / "population_extraction_notes.txt").write_text("\n".join(notes) + "\n", encoding="utf-8")
    return pop


def add_population_weights(panel: pd.DataFrame) -> pd.DataFrame:
    panel = panel.drop(columns=[POPULATION, "population_status", POP_WEIGHT], errors="ignore").copy()
    pop = fetch_population_data(sorted(panel["year"].dropna().astype(int).unique()))
    panel = panel.merge(
        pop.rename(columns={"status": "population_status"}),
        on=["geo", "year"],
        how="left",
    )
    year_totals = panel.groupby("year")[POPULATION].transform("sum")
    panel[POP_WEIGHT] = panel[POPULATION] / year_totals
    panel.to_csv(DATA_PROCESSED / "panel_features_v2-3.csv", index=False)
    return panel


def population_weighted_trend(panel: pd.DataFrame) -> None:
    temp = panel.dropna(subset=[OUTCOME, POP_WEIGHT]).copy()
    rows = []
    for year, g in temp.groupby("year"):
        rows.append(
            {
                "year": int(year),
                "unweighted_mean": float(g[OUTCOME].mean()),
                "population_weighted_mean": float(np.average(g[OUTCOME], weights=g[POP_WEIGHT])),
                "countries": int(g["geo"].nunique()),
                "population_covered": float(g[POPULATION].sum()),
            }
        )
    out = pd.DataFrame(rows).sort_values("year")
    out.to_csv(OUTPUTS / "population_weighted_trend.csv", index=False)

    plt.figure(figsize=(9, 5))
    plt.plot(out["year"], out["unweighted_mean"], marker="o", linewidth=1.8, label="Unweighted country mean", color="#0072B2")
    plt.plot(out["year"], out["population_weighted_mean"], marker="s", linewidth=1.8, label="Year-normalized population-weighted mean", color="#D55E00")
    plt.axvline(2015, color="#333333", linestyle="--", linewidth=1.0, label="2015 methodology change")
    plt.xlabel("Year")
    plt.ylabel("Unmet medical need (%)")
    plt.legend(frameon=False)
    plt.grid(axis="y", alpha=0.25)
    plt.tight_layout()
    plt.savefig(FIGURES / "population_weighted_trend.pdf", dpi=300)
    plt.close()


def estimand_drift_diagnostic(outcome: pd.DataFrame, panel: pd.DataFrame, model: pd.DataFrame) -> None:
    outcome_year = (
        outcome.dropna(subset=[OUTCOME])
        .groupby("year")
        .agg(unweighted_mean=(OUTCOME, "mean"), outcome_countries=("geo", "nunique"))
        .reset_index()
    )
    weighted = (
        panel.dropna(subset=[OUTCOME, POP_WEIGHT])
        .groupby("year")
        .apply(
            lambda g: pd.Series(
                {
                    "population_weighted_mean": float(np.average(g[OUTCOME], weights=g[POP_WEIGHT])),
                    "population_weighted_countries": int(g["geo"].nunique()),
                }
            )
        )
        .reset_index()
    )
    complete_year = (
        model.groupby("year")
        .agg(complete_case_countries=("geo", "nunique"), complete_case_rows=("geo", "size"))
        .reset_index()
    )
    diag = outcome_year.merge(weighted, on="year", how="outer").merge(complete_year, on="year", how="outer")
    diag = diag.sort_values("year")
    diag.to_csv(OUTPUTS / "descriptive_estimand_drift_diagnostic.csv", index=False)

    fig, axes = plt.subplots(2, 2, figsize=(11, 7), sharex=True)
    ax = axes[0, 0]
    ax.plot(diag["year"], diag["unweighted_mean"], marker="o", linewidth=1.8, color="#0072B2")
    ax.set_title("Unweighted outcome-observed mean")
    ax.set_ylabel("Unmet need (%)")

    ax = axes[0, 1]
    ax.plot(diag["year"], diag["population_weighted_mean"], marker="s", linewidth=1.8, color="#D55E00")
    ax.set_title("Population-weighted mean")
    ax.set_ylabel("Unmet need (%)")

    ax = axes[1, 0]
    ax.bar(diag["year"], diag["outcome_countries"], color="#009E73")
    ax.set_title("Outcome-observed countries")
    ax.set_ylabel("Countries")
    ax.set_xlabel("Year")

    ax = axes[1, 1]
    ax.bar(diag["year"], diag["complete_case_countries"], color="#CC79A7")
    ax.set_title("Complete-case countries")
    ax.set_ylabel("Countries")
    ax.set_xlabel("Year")

    for ax in axes.ravel():
        ax.axvline(2015, color="#333333", linestyle="--", linewidth=0.9)
        ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIGURES / "descriptive_estimand_drift_diagnostic.pdf", dpi=300)
    plt.close(fig)


def descriptive_statistics(panel: pd.DataFrame) -> None:
    stats_df = panel[DESCRIPTIVE_VARS].agg(["count", "mean", "std", "min", "median", "max"]).T
    q = panel[DESCRIPTIVE_VARS].quantile([0.25, 0.75]).T.rename(columns={0.25: "p25", 0.75: "p75"})
    stats_df = stats_df.join(q)
    stats_df = stats_df.rename(columns={"count": "N"})
    stats_df = stats_df[["N", "mean", "std", "min", "p25", "median", "p75", "max"]]
    stats_df["N"] = stats_df["N"].astype(int)
    stats_df.reset_index(names="variable").to_csv(OUTPUTS / "table_descriptive_statistics.csv", index=False)
    write_latex(
        stats_df.reset_index(names="variable"),
        TABLES / "descriptive_statistics.tex",
        "Descriptive statistics for outcome and covariates, full enriched panel",
        "tab:descriptive_statistics",
    )


def correlation_matrix(panel: pd.DataFrame) -> None:
    corr = panel[DESCRIPTIVE_VARS].corr(method="pearson")
    corr.to_csv(OUTPUTS / "panel_correlations_full.csv")
    plt.figure(figsize=(12, 10))
    sns.heatmap(
        corr,
        cmap="vlag",
        vmin=-1,
        vmax=1,
        center=0,
        annot=True,
        fmt=".2f",
        linewidths=0.4,
        cbar_kws={"label": "Pearson r"},
    )
    plt.xticks(rotation=45, ha="right")
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.savefig(FIGURES / "panel_correlations_heatmap.pdf", dpi=300)
    plt.close()


def outcome_trend(outcome: pd.DataFrame) -> None:
    trend = outcome.groupby("year", as_index=False)[OUTCOME].mean()
    plt.figure(figsize=(9, 5))
    plt.axvspan(2008, 2013, color="#d55e00", alpha=0.12, label="Great Recession")
    plt.axvspan(2020, 2022, color="#0072b2", alpha=0.12, label="COVID")
    plt.axvline(2015, color="#333333", linestyle="--", linewidth=1.2, label="2015 methodology change")
    plt.plot(trend["year"], trend[OUTCOME], marker="o", color="#009e73", linewidth=2)
    plt.xlabel("Year")
    plt.ylabel("Unmet medical need (%)")
    plt.title("Unweighted mean unmet medical need across countries")
    plt.legend(frameon=False)
    plt.grid(axis="y", alpha=0.25)
    plt.tight_layout()
    plt.savefig(FIGURES / "descriptive_eu_trend.pdf", dpi=300)
    plt.close()


def country_rankings(outcome: pd.DataFrame) -> None:
    latest = outcome.dropna(subset=[OUTCOME]).sort_values("year").groupby("geo", as_index=False).tail(1)
    latest = latest.sort_values(OUTCOME, ascending=True)
    mean_latest = latest[OUTCOME].mean()
    plt.figure(figsize=(8, max(6, 0.22 * len(latest))))
    colors = ["#0072b2" if v <= mean_latest else "#d55e00" for v in latest[OUTCOME]]
    plt.barh(latest["geo"], latest[OUTCOME], color=colors)
    plt.axvline(mean_latest, color="#000000", linestyle="--", linewidth=1.1, label="Unweighted country mean")
    plt.xlabel("Latest available unmet medical need (%)")
    plt.ylabel("Country")
    plt.legend(frameon=False)
    plt.tight_layout()
    plt.savefig(FIGURES / "descriptive_country_rankings.pdf", dpi=300)
    plt.close()


def country_year_heatmap(outcome: pd.DataFrame) -> None:
    matrix = outcome.pivot_table(index="geo", columns="year", values=OUTCOME, aggfunc="mean")
    matrix = matrix.sort_index()
    cmap = sns.color_palette("mako", as_cmap=True)
    cmap.set_bad("#d9d9d9")
    plt.figure(figsize=(12, max(7, 0.23 * len(matrix))))
    sns.heatmap(matrix, cmap=cmap, linewidths=0.1, linecolor="white", cbar_kws={"label": "Unmet medical need (%)"})
    plt.xlabel("Year")
    plt.ylabel("Country")
    plt.tight_layout()
    plt.savefig(FIGURES / "descriptive_country_year_heatmap.pdf", dpi=300)
    plt.close()


def scatter_plots(panel: pd.DataFrame) -> None:
    for var in SCATTER_COVARS:
        sample = panel[["geo", "year", OUTCOME, var]].dropna().sort_values("year").groupby("geo", as_index=False).tail(1)
        if sample.shape[0] < 5:
            continue
        plt.figure(figsize=(6.5, 4.8))
        plt.scatter(sample[var], sample[OUTCOME], color="#0072b2", alpha=0.75, edgecolor="white", linewidth=0.4)
        try:
            smooth = lowess(sample[OUTCOME], sample[var], frac=0.65, return_sorted=True)
            plt.plot(smooth[:, 0], smooth[:, 1], color="#d55e00", linewidth=2)
        except Exception:
            pass
        plt.xlabel(var)
        plt.ylabel("Unmet medical need (%)")
        plt.grid(alpha=0.2)
        plt.tight_layout()
        plt.savefig(FIGURES / f"scatter_unmet_vs_{var}.pdf", dpi=300)
        plt.close()


def distribution_plots(panel: pd.DataFrame) -> None:
    ncols = 3
    nrows = math.ceil(len(DESCRIPTIVE_VARS) / ncols)
    fig, axes = plt.subplots(nrows, ncols, figsize=(14, 3.2 * nrows))
    axes = axes.ravel()
    for ax, var in zip(axes, DESCRIPTIVE_VARS):
        s = panel[var].dropna()
        sns.histplot(s, kde=True, ax=ax, color="#0072b2", edgecolor="white")
        ax.set_title(var, fontsize=9)
        ax.set_xlabel("")
        ax.grid(axis="y", alpha=0.2)
    for ax in axes[len(DESCRIPTIVE_VARS) :]:
        ax.axis("off")
    plt.tight_layout()
    plt.savefig(FIGURES / "panel_variable_distributions.pdf", dpi=300)
    plt.close()


def missingness(panel: pd.DataFrame) -> None:
    rows = []
    for var in DESCRIPTIVE_VARS:
        rows.append(
            {
                "variable": var,
                "observed": int(panel[var].notna().sum()),
                "missing": int(panel[var].isna().sum()),
                "missing_pct": float(panel[var].isna().mean() * 100),
            }
        )
    pd.DataFrame(rows).to_csv(OUTPUTS / "missingness_by_variable.csv", index=False)

    blocks = {
        "outcome": ("Outcome", ["unmet_need_pc"]),
        "socioeconomic": (
            "Socioeconomic",
            [
            "gdp_per_capita_eur",
            "log_gdp_per_capita",
            "unemployment_rate_pc",
            "long_term_unemployment_rate_pc",
            "poverty_or_social_exclusion_pc",
            "gini_income",
            ],
        ),
        "financing": (
            "Health financing",
            [
            "government_health_expenditure_gdp_pc",
            "compulsory_health_financing_gdp_pc",
            "oop_health_expenditure_share_pc",
            ],
        ),
        "capacity": (
            "Health-system capacity",
            [
            "physicians_per_100k",
            "hospital_beds_per_100k",
            ],
        ),
        "population": ("Population weights", [POPULATION, POP_WEIGHT]),
    }
    countries = sorted(panel["geo"].unique())
    years = sorted(panel["year"].unique())
    fig, axes = plt.subplots(len(blocks), 1, figsize=(12, 10), sharex=True)
    cmap = sns.color_palette("crest", as_cmap=True)
    for ax, (_, (name, vars_)) in zip(axes, blocks.items()):
        vars_ = [v for v in vars_ if v in panel.columns]
        temp = panel.set_index(["geo", "year"])[vars_].notna().mean(axis=1)
        matrix = temp.unstack("year").reindex(index=countries, columns=years)
        sns.heatmap(matrix, ax=ax, cmap=cmap, vmin=0, vmax=1, cbar=True, cbar_kws={"label": "Observed share"})
        ax.set_title(name)
        ax.set_ylabel("Country")
    axes[-1].set_xlabel("Year")
    plt.tight_layout()
    plt.savefig(FIGURES / "missingness_heatmap.pdf", dpi=300)
    plt.close()

    for key, (name, vars_) in blocks.items():
        vars_ = [v for v in vars_ if v in panel.columns]
        if not vars_:
            continue
        temp = panel.set_index(["geo", "year"])[vars_].notna().mean(axis=1)
        matrix = temp.unstack("year").reindex(index=countries, columns=years)
        plt.figure(figsize=(12, max(6, 0.22 * len(countries))))
        sns.heatmap(matrix, cmap=cmap, vmin=0, vmax=1, linewidths=0.08, linecolor="white", cbar_kws={"label": "Observed share"})
        plt.title(f"Missingness coverage: {name}")
        plt.xlabel("Year")
        plt.ylabel("Country")
        plt.tight_layout()
        plt.savefig(FIGURES / f"missingness_heatmap_{key}.pdf", dpi=300)
        plt.close()


def included_excluded(panel: pd.DataFrame, model: pd.DataFrame) -> None:
    keys = set(zip(model["geo"], model["year"]))
    comp = panel.copy()
    comp["included_regression"] = [key in keys for key in zip(comp["geo"], comp["year"])]
    vars_ = [OUTCOME, "gdp_per_capita_eur", "unemployment_rate_pc", "poverty_or_social_exclusion_pc"]
    rows = []
    for var in vars_:
        inc = comp.loc[comp["included_regression"], var].dropna()
        exc = comp.loc[~comp["included_regression"], var].dropna()
        t_stat, p_val = stats.ttest_ind(inc, exc, equal_var=False, nan_policy="omit")
        rows.append(
            {
                "variable": var,
                "included_n": len(inc),
                "included_mean": inc.mean(),
                "excluded_n": len(exc),
                "excluded_mean": exc.mean(),
                "difference": inc.mean() - exc.mean(),
                "t_stat": t_stat,
                "p_value": p_val,
            }
        )
    out = pd.DataFrame(rows)
    out.to_csv(OUTPUTS / "included_vs_excluded_comparison.csv", index=False)
    display = out.copy()
    variable_labels = {
        "unmet_need_pc": "Unmet need",
        "gdp_per_capita_eur": "GDP/cap.",
        "unemployment_rate_pc": "Unemp.",
        "poverty_or_social_exclusion_pc": "Poverty",
    }
    display["Variable"] = display["variable"].map(variable_labels).fillna(display["variable"].str.replace("_", r"\_", regex=False))
    display["Included N"] = display["included_n"].astype(int).astype(str)
    display["Included mean"] = display["included_mean"].map(lambda x: f"{x:.2f}")
    display["Excluded N"] = display["excluded_n"].astype(int).astype(str)
    display["Excluded mean"] = display["excluded_mean"].map(lambda x: f"{x:.2f}")
    display["Difference"] = display["difference"].map(lambda x: f"{x:.2f}")
    display["p-value"] = display["p_value"].map(format_p_value)
    compact = display[["Variable", "Included N", "Included mean", "Excluded N", "Excluded mean", "Difference", "p-value"]]
    lines = [
        r"\begingroup",
        r"\small",
        r"\begin{tabular}{@{}lrrrrrr@{}}",
        r"\toprule",
        r"Variable & Inc. \(N\) & Inc. mean & Exc. \(N\) & Exc. mean & Diff. & p-value \\",
        r"\midrule",
    ]
    for _, row in compact.iterrows():
        lines.append(
            f"{row['Variable']} & {row['Included N']} & {row['Included mean']} & {row['Excluded N']} & {row['Excluded mean']} & {row['Difference']} & {row['p-value']} \\\\"
        )
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}",
            "",
            r"\vspace{0.2em}",
            r"\begin{minipage}{0.92\textwidth}\scriptsize Notes: Welch tests compare rows included in the baseline complete-case regression with outcome-observed rows excluded because at least one baseline covariate is missing. The table is descriptive and is used as a selection diagnostic. \textit{Source:} Author's calculations from the merged Eurostat panel; exact \(N\) varies because excluded rows can also be missing the variable being compared.\end{minipage}",
            r"\endgroup",
        ]
    )
    (TABLES / "missingness_comparison.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


def attrition_and_drift_outputs(panel: pd.DataFrame) -> None:
    target = panel.dropna(subset=[OUTCOME]).copy()
    target["country_group"] = target["geo"].map(country_group_label)
    target_n = len(target)
    target_countries = target["geo"].nunique()
    target_years = target["year"].nunique()

    rows = []
    previous_n: int | None = None
    for step, cols in ATTRITION_STEPS:
        available_cols = [c for c in cols if c in target.columns]
        mask = target[available_cols].notna().all(axis=1)
        step_df = target.loc[mask]
        n_rows = len(step_df)
        rows.append(
            {
                "step": step,
                "required_variables": "; ".join(VARIABLE_LABELS.get(c, c) for c in available_cols),
                "rows": n_rows,
                "countries": step_df["geo"].nunique(),
                "years": step_df["year"].nunique(),
                "rows_lost_from_previous": 0 if previous_n is None else previous_n - n_rows,
                "retained_pct_of_outcome": 100 * n_rows / target_n if target_n else np.nan,
            }
        )
        previous_n = n_rows
    attrition = pd.DataFrame(rows)
    attrition.to_csv(OUTPUTS / "complete_case_attrition_waterfall.csv", index=False)

    display = attrition.copy()
    display["Step"] = display["step"]
    display["Rows"] = display["rows"].astype(int).astype(str)
    display["Countries"] = display["countries"].astype(int).astype(str)
    display["Years"] = display["years"].astype(int).astype(str)
    display["Rows lost"] = display["rows_lost_from_previous"].astype(int).astype(str)
    display["Retained pct"] = display["retained_pct_of_outcome"].map(lambda x: fmt_num(x, 1))
    write_compact_latex(
        display[["Step", "Rows", "Countries", "Years", "Rows lost", "Retained pct"]],
        TABLES / "complete_case_attrition_waterfall.tex",
        "Sequential attrition from the outcome-observed monitoring panel to the baseline complete-case FE sample.",
        "tab:complete_case_attrition_waterfall",
        "lrrrrr",
        r"\textit{Source:} Author's calculations from the merged Eurostat panel. Percentages use the 608 outcome-observed rows as the reference target.",
        "H",
    )

    fig, ax = plt.subplots(figsize=(9.5, 5.2))
    colors = ["#0072B2"] + ["#56B4E9"] * (len(attrition) - 2) + ["#D55E00"]
    ax.bar(range(len(attrition)), attrition["rows"], color=colors, edgecolor="white", linewidth=0.8)
    for i, row in attrition.iterrows():
        lost = int(row["rows_lost_from_previous"])
        label = f"{int(row['rows'])}"
        if i > 0:
            label += f"\n-{lost}"
        ax.text(i, row["rows"] + max(attrition["rows"]) * 0.025, label, ha="center", va="bottom", fontsize=8)
    ax.set_xticks(range(len(attrition)))
    ax.set_xticklabels(attrition["step"], rotation=25, ha="right")
    ax.set_ylabel("Country-years retained")
    ax.set_ylim(0, max(attrition["rows"]) * 1.16)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIGURES / "complete_case_attrition_waterfall.pdf", dpi=300)
    plt.close(fig)

    complete_mask = target[[OUTCOME] + BASELINE_COVARS].notna().all(axis=1)
    complete = target.loc[complete_mask].copy()
    baseline_n = len(complete)

    country_rows = []
    for geo, group in target.groupby("geo"):
        cc_rows = int(complete.loc[complete["geo"] == geo].shape[0])
        outcome_rows = int(group.shape[0])
        country_rows.append(
            {
                "geo": geo,
                "country_group": country_group_label(geo),
                "outcome_rows": outcome_rows,
                "complete_case_rows": cc_rows,
                "rows_lost": outcome_rows - cc_rows,
                "retained_pct": 100 * cc_rows / outcome_rows if outcome_rows else np.nan,
                "first_year": int(group["year"].min()),
                "last_year": int(group["year"].max()),
            }
        )
    by_country = pd.DataFrame(country_rows).sort_values(["retained_pct", "geo"])
    by_country.to_csv(OUTPUTS / "attrition_by_country.csv", index=False)

    country_display = by_country.head(14).copy()
    country_display["Country"] = country_display["geo"]
    country_display["Outcome rows"] = country_display["outcome_rows"].astype(int).astype(str)
    country_display["CC rows"] = country_display["complete_case_rows"].astype(int).astype(str)
    country_display["Rows lost"] = country_display["rows_lost"].astype(int).astype(str)
    country_display["Retained pct"] = country_display["retained_pct"].map(lambda x: fmt_num(x, 1))
    write_compact_latex(
        country_display[["Country", "Outcome rows", "CC rows", "Rows lost", "Retained pct"]],
        TABLES / "attrition_by_country_top_loss.tex",
        "Countries with the lowest retention from the outcome-observed target to the complete-case FE sample.",
        "tab:attrition_by_country_top_loss",
        "lrrrr",
        r"\textit{Source:} Author's calculations from the merged Eurostat panel. The table reports the lowest country-level retention rates without assigning substantive regional labels.",
        "H",
    )

    by_year = (
        target.assign(complete_case=complete_mask)
        .groupby("year")
        .agg(outcome_rows=(OUTCOME, "size"), complete_case_rows=("complete_case", "sum"), countries=("geo", "nunique"))
        .reset_index()
    )
    by_year["rows_lost"] = by_year["outcome_rows"] - by_year["complete_case_rows"]
    by_year["retained_pct"] = 100 * by_year["complete_case_rows"] / by_year["outcome_rows"]
    by_year.to_csv(OUTPUTS / "attrition_by_year.csv", index=False)

    year_display = by_year.copy()
    year_display["Year"] = year_display["year"].astype(int).astype(str)
    year_display["Outcome rows"] = year_display["outcome_rows"].astype(int).astype(str)
    year_display["CC rows"] = year_display["complete_case_rows"].astype(int).astype(str)
    year_display["Rows lost"] = year_display["rows_lost"].astype(int).astype(str)
    year_display["Retained pct"] = year_display["retained_pct"].map(lambda x: fmt_num(x, 1))
    write_compact_latex(
        year_display[["Year", "Outcome rows", "CC rows", "Rows lost", "Retained pct"]],
        TABLES / "attrition_by_year.tex",
        "Year-level retention from outcome-observed rows to baseline complete-case FE rows.",
        "tab:attrition_by_year",
        "lrrrr",
    )

    by_group = (
        target.assign(complete_case=complete_mask)
        .groupby("country_group")
        .agg(
            outcome_rows=(OUTCOME, "size"),
            complete_case_rows=("complete_case", "sum"),
            countries=("geo", "nunique"),
        )
        .reset_index()
    )
    by_group["rows_lost"] = by_group["outcome_rows"] - by_group["complete_case_rows"]
    by_group["retained_pct"] = 100 * by_group["complete_case_rows"] / by_group["outcome_rows"]
    by_group.to_csv(OUTPUTS / "attrition_by_country_group.csv", index=False)

    group_display = by_group.copy()
    group_display["Group"] = group_display["country_group"]
    group_display["Outcome rows"] = group_display["outcome_rows"].astype(int).astype(str)
    group_display["CC rows"] = group_display["complete_case_rows"].astype(int).astype(str)
    group_display["Countries"] = group_display["countries"].astype(int).astype(str)
    group_display["Rows lost"] = group_display["rows_lost"].astype(int).astype(str)
    group_display["Retained pct"] = group_display["retained_pct"].map(lambda x: fmt_num(x, 1))
    write_compact_latex(
        group_display[["Group", "Outcome rows", "CC rows", "Countries", "Rows lost", "Retained pct"]],
        TABLES / "attrition_by_country_group.tex",
        "Attrition from outcome-observed rows to complete-case FE rows by country group.",
        "tab:attrition_by_country_group",
        "lrrrrr",
    )

    block_rows = []
    for block, vars_ in COVARIATE_BLOCKS.items():
        available = [v for v in vars_ if v in target.columns]
        cols = sorted(set([OUTCOME] + available))
        block_df = target.dropna(subset=cols)
        block_rows.append(
            {
                "block": block,
                "variables": ", ".join(VARIABLE_LABELS.get(v, v) for v in available),
                "complete_rows": len(block_df),
                "countries": block_df["geo"].nunique(),
                "years": block_df["year"].nunique(),
                "retained_pct": 100 * len(block_df) / target_n if target_n else np.nan,
            }
        )
    by_block = pd.DataFrame(block_rows)
    by_block.to_csv(OUTPUTS / "attrition_by_covariate_block.csv", index=False)
    block_display = by_block.copy()
    block_display["Block"] = block_display["block"]
    block_display["Rows"] = block_display["complete_rows"].astype(int).astype(str)
    block_display["Countries"] = block_display["countries"].astype(int).astype(str)
    block_display["Years"] = block_display["years"].astype(int).astype(str)
    block_display["Retained pct"] = block_display["retained_pct"].map(lambda x: fmt_num(x, 1))
    write_compact_latex(
        block_display[["Block", "Rows", "Countries", "Years", "Retained pct"]],
        TABLES / "attrition_by_covariate_block.tex",
        "Outcome-observed rows retained when requiring complete coverage by covariate block.",
        "tab:attrition_by_covariate_block",
        "lrrrr",
        r"\textit{Source:} Author's calculations from the merged Eurostat panel. Each row applies one covariate-block completeness requirement to the outcome-observed target; blocks are not cumulative.",
        "H",
    )

    recovery_rows = []
    for omitted in BASELINE_COVARS:
        required = [OUTCOME] + [v for v in BASELINE_COVARS if v != omitted]
        recovered = target.dropna(subset=required)
        recovery_rows.append(
            {
                "omitted_variable": omitted,
                "rows": len(recovered),
                "countries": recovered["geo"].nunique(),
                "years": recovered["year"].nunique(),
                "rows_recovered": len(recovered) - baseline_n,
            }
        )
    recovery = pd.DataFrame(recovery_rows).sort_values("rows_recovered", ascending=False)
    recovery.to_csv(OUTPUTS / "leave_one_variable_out_sample_recovery.csv", index=False)
    recovery_display = recovery.copy()
    recovery_display["Omitted covariate"] = recovery_display["omitted_variable"].map(VARIABLE_LABELS)
    recovery_display["Rows"] = recovery_display["rows"].astype(int).astype(str)
    recovery_display["Countries"] = recovery_display["countries"].astype(int).astype(str)
    recovery_display["Years"] = recovery_display["years"].astype(int).astype(str)
    recovery_display["Rows recovered"] = recovery_display["rows_recovered"].astype(int).astype(str)
    write_compact_latex(
        recovery_display[["Omitted covariate", "Rows", "Countries", "Years", "Rows recovered"]],
        TABLES / "leave_one_variable_out_sample_recovery.tex",
        "Sample recovery when each baseline covariate is omitted from the complete-case requirement.",
        "tab:leave_one_variable_out_sample_recovery",
        "lrrrr",
        r"\textit{Source:} Author's calculations from the baseline covariate set. Rows recovered are measured relative to the 282-row complete-case sample.",
        "H",
    )

    smd_vars = [
        OUTCOME,
        "gdp_per_capita_eur",
        "unemployment_rate_pc",
        "poverty_or_social_exclusion_pc",
        "government_health_expenditure_gdp_pc",
        "compulsory_health_financing_gdp_pc",
    ]
    smd_rows = []
    for var in smd_vars:
        inc = target.loc[complete_mask, var].dropna()
        exc = target.loc[~complete_mask, var].dropna()
        pooled_sd = math.sqrt(((inc.std(ddof=1) ** 2) + (exc.std(ddof=1) ** 2)) / 2) if len(inc) > 1 and len(exc) > 1 else np.nan
        smd = (inc.mean() - exc.mean()) / pooled_sd if pooled_sd and not pd.isna(pooled_sd) else np.nan
        smd_rows.append(
            {
                "variable": var,
                "included_n": len(inc),
                "included_mean": inc.mean(),
                "excluded_n": len(exc),
                "excluded_mean": exc.mean(),
                "smd": smd,
            }
        )
    smd_out = pd.DataFrame(smd_rows)
    smd_out.to_csv(OUTPUTS / "included_vs_excluded_smd.csv", index=False)
    smd_display = smd_out.copy()
    smd_display["Variable"] = smd_display["variable"].map(VARIABLE_LABELS)
    smd_display["Included N"] = smd_display["included_n"].astype(int).astype(str)
    smd_display["Included mean"] = smd_display["included_mean"].map(lambda x: fmt_num(x, 2))
    smd_display["Excluded N"] = smd_display["excluded_n"].astype(int).astype(str)
    smd_display["Excluded mean"] = smd_display["excluded_mean"].map(lambda x: fmt_num(x, 2))
    smd_display["SMD"] = smd_display["smd"].map(lambda x: fmt_num(x, 2))
    write_compact_latex(
        smd_display[["Variable", "Included N", "Included mean", "Excluded N", "Excluded mean", "SMD"]],
        TABLES / "included_vs_excluded_smd.tex",
        "Standardized mean differences between complete-case rows and excluded outcome-observed rows.",
        "tab:included_vs_excluded_smd",
        "lrrrrr",
        r"\textit{Source:} Author's calculations from the 608 outcome-observed \texttt{hlth\_silc\_08} rows. SMDs compare the 282 complete cases with rows excluded by missing baseline covariates.",
        "H",
    )

    summary = {
        "outcome_observed_rows": target_n,
        "outcome_observed_countries": target_countries,
        "outcome_observed_years": target_years,
        "baseline_complete_case_rows": baseline_n,
        "baseline_complete_case_countries": complete["geo"].nunique(),
        "baseline_complete_case_years": complete["year"].nunique(),
    }
    (OUTPUTS / "attrition_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")


def country_coverage(panel: pd.DataFrame, model: pd.DataFrame, ml: pd.DataFrame) -> None:
    reg_countries = set(model["geo"].unique())
    ml_countries = set(ml["geo"].unique())
    rows = []
    for country, g in panel.groupby("geo"):
        baseline_missing = [v for v in BASELINE_COVARS if g[v].notna().sum() == 0]
        overlap = g.dropna(subset=[OUTCOME] + BASELINE_COVARS)
        cause = ""
        if country not in reg_countries:
            cause = ", ".join(baseline_missing) if baseline_missing else "No complete overlap across baseline covariates"
        rows.append(
            {
                "country": country,
                "descriptive_rows": len(g),
                "in_regression_sample": "yes" if country in reg_countries else "no",
                "in_ml_sample": "yes" if country in ml_countries else "no",
                "complete_baseline_rows": len(overlap),
                "exclusion_driver": cause,
            }
        )
    out = pd.DataFrame(rows).sort_values("country")
    out.to_csv(OUTPUTS / "country_coverage_table.csv", index=False)
    write_latex(out, TABLES / "country_coverage.tex", "Country coverage across descriptive, regression, and ML samples", "tab:country_coverage")


def citizenship_descriptives(cit: pd.DataFrame) -> None:
    if cit.empty:
        return
    order = ["NAT", "EU_FOR", "NEU_FOR"]
    means = cit.groupby("citizen_group", as_index=False)[OUTCOME].mean()
    means["citizen_group"] = pd.Categorical(means["citizen_group"], categories=order, ordered=True)
    means = means.sort_values("citizen_group")
    plt.figure(figsize=(6, 4))
    sns.barplot(data=means, x="citizen_group", y=OUTCOME, palette=["#0072b2", "#009e73", "#d55e00"])
    plt.xlabel("Citizenship group")
    plt.ylabel("Mean unmet medical need (%)")
    plt.tight_layout()
    plt.savefig(FIGURES / "citizenship_unmet_need_comparison.pdf", dpi=300)
    plt.close()

    trend = cit.groupby(["year", "citizen_group"], as_index=False)[OUTCOME].mean()
    plt.figure(figsize=(8, 4.8))
    sns.lineplot(data=trend, x="year", y=OUTCOME, hue="citizen_group", hue_order=order, marker="o", palette=["#0072b2", "#009e73", "#d55e00"])
    plt.xlabel("Year")
    plt.ylabel("Unweighted mean unmet medical need (%)")
    plt.tight_layout()
    plt.savefig(FIGURES / "citizenship_unmet_need_trend.pdf", dpi=300)
    plt.close()

    latest = cit.sort_values("year").groupby(["country", "citizen_group"], as_index=False).tail(1)
    matrix = latest.pivot_table(index="country", columns="citizen_group", values=OUTCOME, aggfunc="mean").reindex(columns=order)
    cmap = sns.color_palette("mako", as_cmap=True)
    cmap.set_bad("#d9d9d9")
    plt.figure(figsize=(5.5, max(6, 0.22 * len(matrix))))
    sns.heatmap(matrix.sort_index(), cmap=cmap, linewidths=0.2, cbar_kws={"label": "Unmet medical need (%)"})
    plt.xlabel("Citizenship group")
    plt.ylabel("Country")
    plt.tight_layout()
    plt.savefig(FIGURES / "citizenship_unmet_need_heatmap.pdf", dpi=300)
    plt.close()

    wide = latest.pivot_table(index="country", columns="citizen_group", values=OUTCOME, aggfunc="mean")
    wide["gap_neu_for_minus_nat"] = wide.get("NEU_FOR") - wide.get("NAT")
    gap = wide.reset_index()[["country", "NAT", "NEU_FOR", "gap_neu_for_minus_nat"]].sort_values("gap_neu_for_minus_nat", ascending=False)
    gap.to_csv(OUTPUTS / "citizenship_gap_by_country.csv", index=False)
    write_latex(gap.head(10), TABLES / "citizenship_gap_table.tex", "Top 10 citizenship gaps in unmet medical need, non-EU foreign citizens minus nationals", "tab:citizenship_gap")


def run_descriptive(panel: pd.DataFrame, outcome: pd.DataFrame, model: pd.DataFrame, ml: pd.DataFrame, cit: pd.DataFrame) -> None:
    descriptive_statistics(panel)
    correlation_matrix(panel)
    outcome_trend(outcome)
    population_weighted_trend(panel)
    estimand_drift_diagnostic(outcome, panel, model)
    country_rankings(outcome)
    country_year_heatmap(outcome)
    scatter_plots(panel)
    distribution_plots(panel)
    missingness(panel)
    attrition_and_drift_outputs(panel)
    included_excluded(panel, model)
    country_coverage(panel, model, ml)
    citizenship_descriptives(cit)


def within_r2(df: pd.DataFrame) -> float:
    resid = {}
    for var in [OUTCOME] + BASELINE_COVARS:
        res = smf.ols(f"{var} ~ C(geo) + C(year)", data=df).fit()
        resid[var] = res.resid
    y = resid[OUTCOME]
    x = pd.DataFrame({v: resid[v] for v in BASELINE_COVARS})
    fit = sm.OLS(y, x).fit()
    return float(fit.rsquared)


def regression_core(panel: pd.DataFrame, model: pd.DataFrame) -> dict[str, pd.DataFrame]:
    outputs: dict[str, pd.DataFrame] = {}

    pooled = fit_pooled(model, BASELINE_COVARS)
    result_to_frame(pooled, "pooled_year_clustered").to_csv(OUTPUTS / "regression_pooled_full.csv", index=False)

    fe = fit_fe(model, BASELINE_COVARS)
    result_to_frame(fe, "two_way_fe_clustered").to_csv(OUTPUTS / "regression_fe_full.csv", index=False)

    wr2 = within_r2(model)
    (OUTPUTS / "regression_within_r2.txt").write_text(f"Within R2: {wr2:.6f}\nN: {len(model)}\nCountries: {model['geo'].nunique()}\n", encoding="utf-8")

    outputs["baseline_fe"] = pd.DataFrame([summary_for_term("Baseline two-way FE", fe, "poverty_or_social_exclusion_pc", model["geo"].nunique())])
    return outputs


def model_sample_with_covars(df: pd.DataFrame, covars: list[str], require_weight: bool = False) -> pd.DataFrame:
    extra = [POP_WEIGHT] if require_weight and POP_WEIGHT in df.columns else []
    cols = ["geo", "year", OUTCOME] + covars + extra
    subset = [OUTCOME] + covars + extra
    return df[cols].dropna(subset=subset).copy()


def feasible_regression_sample(df: pd.DataFrame) -> tuple[bool, str]:
    if len(df) < MIN_FE_ROWS:
        return False, f"infeasible: fewer than {MIN_FE_ROWS} observations"
    if df["geo"].nunique() < MIN_FE_COUNTRIES:
        return False, f"infeasible: fewer than {MIN_FE_COUNTRIES} countries"
    if df["year"].nunique() < MIN_FE_YEARS:
        return False, f"infeasible: fewer than {MIN_FE_YEARS} years"
    return True, "estimated"


def fit_fe_covars(df: pd.DataFrame, covars: list[str], weights: pd.Series | None = None):
    formula = f"{OUTCOME} ~ {' + '.join(covars)} + C(geo) + C(year)"
    if weights is None:
        return smf.ols(formula, data=df).fit(
            cov_type="cluster",
            cov_kwds={"groups": df["geo"], "use_correction": True},
        )
    return smf.wls(formula, data=df, weights=weights).fit(
        cov_type="cluster",
        cov_kwds={"groups": df["geo"], "use_correction": True},
    )


def balanced_outcome_country_list(panel: pd.DataFrame) -> list[str]:
    target = panel.dropna(subset=[OUTCOME]).copy()
    years = sorted(target["year"].dropna().astype(int).unique())
    keep: list[str] = []
    for geo, group in target.groupby("geo"):
        observed_years = set(group.loc[group[OUTCOME].notna() & group[POP_WEIGHT].notna(), "year"].astype(int))
        if set(years).issubset(observed_years):
            keep.append(str(geo))
    return sorted(keep)


def model_ladder_infeasible_row(
    model: str,
    label: str,
    row_set: str,
    universe: str,
    weighting: str,
    covars: list[str],
    sample: pd.DataFrame,
    status: str,
    interpretation: str,
) -> dict[str, float | str | int]:
    return {
        "model": model,
        "label": label,
        "row_set": row_set,
        "universe": universe,
        "weighting": weighting,
        "covariates": "; ".join(VARIABLE_LABELS.get(v, v) for v in covars),
        "rows": int(len(sample)),
        "countries": int(sample["geo"].nunique()) if "geo" in sample.columns and not sample.empty else 0,
        "years": int(sample["year"].nunique()) if "year" in sample.columns and not sample.empty else 0,
        "term": "poverty_or_social_exclusion_pc",
        "coef": np.nan,
        "ci_low": np.nan,
        "ci_high": np.nan,
        "p_value": np.nan,
        "status": status,
        "interpretation": interpretation,
    }


def model_ladder_row(
    model: str,
    label: str,
    data: pd.DataFrame,
    covars: list[str],
    interpretation: str,
    row_set: str = "Available covariate-complete rows",
    universe: str = "Full Eurostat-available",
    weighting: str = "Unweighted",
    use_weights: bool = False,
) -> dict[str, float | str | int]:
    sample = model_sample_with_covars(data, covars, require_weight=use_weights)
    feasible, status = feasible_regression_sample(sample)
    if not feasible:
        return model_ladder_infeasible_row(model, label, row_set, universe, weighting, covars, sample, status, interpretation)
    try:
        weights = sample[POP_WEIGHT] if use_weights else None
        result = fit_fe_covars(sample, covars, weights=weights)
        term = "poverty_or_social_exclusion_pc"
        if term not in result.params.index:
            return model_ladder_infeasible_row(model, label, row_set, universe, weighting, covars, sample, "infeasible: poverty term absent", interpretation)
        conf = result.conf_int().loc[term]
        return {
            "model": model,
            "label": label,
            "row_set": row_set,
            "universe": universe,
            "weighting": weighting,
            "covariates": "; ".join(VARIABLE_LABELS.get(v, v) for v in covars),
            "rows": int(result.nobs),
            "countries": int(sample["geo"].nunique()),
            "years": int(sample["year"].nunique()),
            "term": term,
            "coef": float(result.params[term]),
            "ci_low": float(conf.iloc[0]),
            "ci_high": float(conf.iloc[1]),
            "p_value": float(result.pvalues[term]),
            "status": "estimated",
            "interpretation": interpretation,
        }
    except Exception as exc:  # noqa: BLE001 - infeasible rows must be recorded rather than hidden.
        return model_ladder_infeasible_row(
            model,
            label,
            row_set,
            universe,
            weighting,
            covars,
            sample,
            f"infeasible: {type(exc).__name__}",
            interpretation,
        )


def write_model_ladder_table(out: pd.DataFrame) -> None:
    display = out.copy()
    display["Spec."] = display["model"] + ": " + display["label"]
    display["Rows"] = display["rows"].astype(int).astype(str)
    display["Countries"] = display["countries"].astype(int).astype(str)
    display["Years"] = display["years"].astype(int).astype(str)
    display["Coef. [95\\% CI]"] = display.apply(
        lambda r: (
            f"{r['coef']:.3f} [{r['ci_low']:.3f}, {r['ci_high']:.3f}]"
            if pd.notna(r["coef"]) and pd.notna(r["ci_low"]) and pd.notna(r["ci_high"])
            else "not estimated"
        ),
        axis=1,
    )
    display["p-value"] = display["p_value"].map(format_p_value)
    display["Target"] = display["universe"] + "; " + display["weighting"]
    display["Status"] = display["status"]
    lines = [
        r"\begingroup",
        r"\scriptsize",
        r"\begin{tabular}{@{}p{0.20\textwidth}p{0.23\textwidth}rrrp{0.20\textwidth}lp{0.20\textwidth}@{}}",
        r"\toprule",
        r"Spec. & Target/weighting & Rows & Countries & Years & Coef. [95\% CI] & p-value & Interpretation \\",
        r"\midrule",
    ]
    for _, row in display.iterrows():
        coef_text = row["Coef. [95\\% CI]"] if row["Status"] == "estimated" else row["Status"]
        lines.append(
            f"{row['Spec.']} & {row['Target']} & {row['Rows']} & {row['Countries']} & {row['Years']} & {coef_text} & {row['p-value']} & {row['interpretation']} \\\\"
        )
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}",
            "",
            r"\vspace{0.2em}",
            r"\begin{minipage}{0.94\textwidth}\scriptsize Notes: All rows use country-and-year fixed effects and country-clustered standard errors. Infeasible rows are retained in the table when the available row set has too few observations, countries, or years for stable FE estimation. Population weights are year-normalized country populations.\end{minipage}",
            r"\endgroup",
        ]
    )
    (TABLES / "model_ladder_results.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


def plot_model_ladder_forest(out: pd.DataFrame) -> None:
    plot_df = out[out["status"].eq("estimated") & out["coef"].notna()].copy()
    if plot_df.empty:
        return
    plot_df["plot_label"] = plot_df["model"] + ": " + plot_df["label"] + " (" + plot_df["universe"] + ", " + plot_df["weighting"] + ")"
    plot_df = plot_df.iloc[::-1].reset_index(drop=True)
    y = np.arange(len(plot_df))
    lower = plot_df["coef"] - plot_df["ci_low"]
    upper = plot_df["ci_high"] - plot_df["coef"]
    plt.figure(figsize=(10, max(5.5, 0.45 * len(plot_df))))
    plt.errorbar(
        plot_df["coef"],
        y,
        xerr=np.vstack([lower, upper]),
        fmt="o",
        color="#0072B2",
        ecolor="#555555",
        elinewidth=1.4,
        capsize=3,
    )
    plt.axvline(0, color="#000000", linestyle="--", linewidth=1)
    plt.yticks(y, plot_df["plot_label"], fontsize=8)
    plt.xlabel("Poverty/social-exclusion coefficient (95% CI)")
    plt.grid(axis="x", alpha=0.2)
    plt.tight_layout()
    plt.savefig(FIGURES / "model_ladder_coefficient_forest.pdf", dpi=300)
    plt.close()


def reduced_covariate_sensitivity(panel: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, float | str | int]] = []
    for model_id, label, covars, interpretation in MODEL_LADDER_SPECS:
        rows.append(model_ladder_row(model_id, label, panel, covars, interpretation))

    baseline_covars = MODEL_LADDER_SPECS[2][2]
    rows.append(
        model_ladder_row(
            "C-EU27",
            "EU-27 baseline",
            panel[panel["geo"].isin(EU27)].copy(),
            baseline_covars,
            "mandatory EU-27 universe comparison",
            universe="EU-27",
        )
    )
    rows.append(
        model_ladder_row(
            "C-PW",
            "Population-weighted baseline",
            panel,
            baseline_covars,
            "resident-weighted selected-panel version",
            weighting="Year-normalized population",
            use_weights=True,
        )
    )

    balanced_countries = balanced_outcome_country_list(panel)
    balanced_panel = panel[panel["geo"].isin(balanced_countries)].copy()
    rows.append(
        model_ladder_row(
            "C-BO",
            "Balanced-outcome baseline",
            balanced_panel,
            baseline_covars,
            "coverage-restricted outcome/population target",
            row_set="Balanced-outcome country set; covariate-complete rows",
            universe="Balanced outcome",
        )
    )
    rows.append(
        model_ladder_row(
            "C-BO-PW",
            "Balanced-outcome weighted",
            balanced_panel,
            baseline_covars,
            "resident-weighted balanced-outcome target",
            row_set="Balanced-outcome country set; covariate-complete rows",
            universe="Balanced outcome",
            weighting="Year-normalized population",
            use_weights=True,
        )
    )

    out = pd.DataFrame(rows)
    out.to_csv(OUTPUTS / "model_ladder_results.csv", index=False)
    out.to_csv(OUTPUTS / "regression_sensitivity_covariate_set.csv", index=False)
    write_model_ladder_table(out)
    plot_model_ladder_forest(out)

    feasibility = out[["model", "label", "rows", "countries", "years", "status"]].copy()
    feasibility.to_csv(OUTPUTS / "model_ladder_feasibility.csv", index=False)
    return out


def influential_country_sensitivity(panel: pd.DataFrame, model: pd.DataFrame) -> pd.DataFrame:
    means = panel.groupby("geo")[OUTCOME].mean().sort_values(ascending=False)
    top3 = means.head(3).index.tolist()
    bottom3 = means.tail(3).index.tolist()
    specs = {
        "Drop top 3 high-unmet countries": top3,
        "Drop bottom 3 low-unmet countries": bottom3,
        "Drop top 3 and bottom 3": top3 + bottom3,
    }
    rows = []
    for label, drops in specs.items():
        df = model[~model["geo"].isin(drops)].copy()
        result = fit_fe(df, BASELINE_COVARS)
        row = summary_for_term(label, result, "poverty_or_social_exclusion_pc", df["geo"].nunique())
        row["dropped_countries"] = ", ".join(drops)
        rows.append(row)
    out = pd.DataFrame(rows)
    out.to_csv(OUTPUTS / "regression_sensitivity_influential.csv", index=False)
    write_latex(out, TABLES / "regression_sensitivity_influential.tex", "Influential-country sensitivity of the poverty association", "tab:regression_sensitivity_influential")
    return out


def lag_robustness(panel: pd.DataFrame) -> pd.DataFrame:
    temp = panel.sort_values(["geo", "year"]).copy()
    for lag in [1, 2]:
        for var in BASELINE_COVARS:
            temp[f"{var}_lag{lag}"] = temp.groupby("geo")[var].shift(lag)
    rows = []
    for lag in [1, 2]:
        covars = [f"{v}_lag{lag}" for v in BASELINE_COVARS]
        df = model_sample(temp, covars)
        rename = dict(zip(covars, BASELINE_COVARS))
        fit_df = df.rename(columns=rename)
        result = fit_fe(fit_df, BASELINE_COVARS)
        rows.append(summary_for_term(f"{lag}-year lagged covariates", result, "poverty_or_social_exclusion_pc", fit_df["geo"].nunique()))
    out = pd.DataFrame(rows)
    out.to_csv(OUTPUTS / "regression_lag_robustness.csv", index=False)
    write_latex(out, TABLES / "regression_lag_robustness.tex", "Lag-structure robustness of the poverty association", "tab:regression_lag_robustness")
    return out


def crisis_exclusion(model: pd.DataFrame) -> pd.DataFrame:
    specs = {
        "Exclude COVID 2020-2022": list(range(2020, 2023)),
        "Exclude 2015 measurement-change year": [2015],
        "Restrict 2016 onward": list(range(int(model["year"].min()), 2016)),
    }
    rows = []
    for label, years in specs.items():
        df = model[~model["year"].isin(years)].copy()
        result = fit_fe(df, BASELINE_COVARS)
        rows.append(summary_for_term(label, result, "poverty_or_social_exclusion_pc", df["geo"].nunique()))
    out = pd.DataFrame(rows)
    out.to_csv(OUTPUTS / "regression_crisis_exclusion.csv", index=False)
    write_latex(out, TABLES / "regression_crisis_exclusion.tex", "Crisis-period exclusion robustness of the poverty association", "tab:regression_crisis_exclusion")
    return out


def country_group_stratification(panel: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for label, countries in [("Western/Northern Europe", WEST_NORTH), ("Eastern/Southern Europe", EAST_SOUTH)]:
        df = model_sample(panel[panel["geo"].isin(countries)].copy(), BASELINE_COVARS)
        result = fit_pooled(df, BASELINE_COVARS)
        for var in BASELINE_COVARS:
            coef, se, p_value = safe_term(result, var)
            rows.append(
                {
                    "group": label,
                    "term": var,
                    "coef": coef,
                    "se": se,
                    "p_value": p_value,
                    "nobs": int(result.nobs),
                    "countries": df["geo"].nunique(),
                    "r2": result.rsquared,
                }
            )
    out = pd.DataFrame(rows)
    out.to_csv(OUTPUTS / "regression_country_groups.csv", index=False)
    write_latex(out, TABLES / "regression_country_groups.tex", "Pooled regression estimates by country group", "tab:regression_country_groups")
    return out


def vif_table(model: pd.DataFrame) -> None:
    x = model[BASELINE_COVARS].dropna().copy()
    x = sm.add_constant(x)
    rows = []
    for i, col in enumerate(x.columns):
        if col == "const":
            continue
        rows.append({"variable": col, "vif": variance_inflation_factor(x.values, i)})
    out = pd.DataFrame(rows)
    out.to_csv(OUTPUTS / "regression_vif.csv", index=False)
    write_latex(out, TABLES / "regression_vif.tex", "Variance inflation factors for baseline covariates", "tab:regression_vif")


def hausman_test(model: pd.DataFrame) -> None:
    fe_nonrobust = smf.ols(
        f"{OUTCOME} ~ {' + '.join(BASELINE_COVARS)} + C(geo) + C(year)",
        data=model,
    ).fit()
    re = smf.mixedlm(
        f"{OUTCOME} ~ {' + '.join(BASELINE_COVARS)} + C(year)",
        data=model,
        groups=model["geo"],
    ).fit(reml=False, method="lbfgs", maxiter=500, disp=False)
    terms = BASELINE_COVARS
    b_fe = fe_nonrobust.params[terms].values
    b_re = re.params[terms].values
    v_fe = fe_nonrobust.cov_params().loc[terms, terms].values
    v_re = re.cov_params().loc[terms, terms].values
    diff = b_fe - b_re
    v_diff = v_fe - v_re
    inv = np.linalg.pinv(v_diff)
    stat = float(diff.T @ inv @ diff)
    df = len(terms)
    p_value = float(1 - chi2.cdf(max(stat, 0), df))
    conclusion = "FE preferred" if p_value < 0.05 else "RE plausible"
    text = [
        "Hausman test comparing country FE and random-intercept RE (same baseline covariates plus year indicators).",
        f"Statistic: {stat:.6f}",
        f"Degrees of freedom: {df}",
        f"p-value: {p_value:.6f}",
        f"Conclusion: {conclusion}",
    ]
    (OUTPUTS / "hausman_test_result.txt").write_text("\n".join(text) + "\n", encoding="utf-8")


def serial_correlation_check(model: pd.DataFrame) -> None:
    formula = f"{OUTCOME} ~ {' + '.join(BASELINE_COVARS)} + C(geo) + C(year)"
    base = smf.ols(formula, data=model).fit(cov_type="cluster", cov_kwds={"groups": model["geo"], "use_correction": True})
    dk = smf.ols(formula, data=model).fit(
        cov_type="hac-groupsum",
        cov_kwds={"time": model["year"].values, "maxlags": 1, "use_correction": "cluster"},
    )
    rows = []
    base_params = np.asarray(base.params)
    base_bse = np.asarray(base.bse)
    base_pvalues = np.asarray(base.pvalues)
    dk_params = np.asarray(dk.params)
    dk_bse = np.asarray(dk.bse)
    dk_pvalues = np.asarray(dk.pvalues)
    for var in BASELINE_COVARS:
        i_base = base.model.exog_names.index(var)
        i_dk = dk.model.exog_names.index(var)
        rows.append(
            {
                "term": var,
                "cluster_coef": float(base_params[i_base]),
                "cluster_se": float(base_bse[i_base]),
                "cluster_p_value": float(base_pvalues[i_base]),
                "driscoll_kraay_coef": float(dk_params[i_dk]),
                "driscoll_kraay_se": float(dk_bse[i_dk]),
                "driscoll_kraay_p_value": float(dk_pvalues[i_dk]),
            }
        )
    pd.DataFrame(rows).to_csv(OUTPUTS / "regression_serial_correlation_check.csv", index=False)


def multilevel_model(panel: pd.DataFrame) -> None:
    temp = panel.copy()
    temp["mean_log_gdp_per_capita"] = temp.groupby("geo")["log_gdp_per_capita"].transform("mean")
    temp["mean_government_health_expenditure_gdp_pc"] = temp.groupby("geo")["government_health_expenditure_gdp_pc"].transform("mean")
    temp["mean_oop_health_expenditure_share_pc"] = temp.groupby("geo")["oop_health_expenditure_share_pc"].transform("mean")
    covars = [
        "unemployment_rate_pc",
        "gdp_per_capita_growth",
        "unemployment_rate_change",
        "mean_log_gdp_per_capita",
        "mean_government_health_expenditure_gdp_pc",
        "mean_oop_health_expenditure_share_pc",
    ]
    df = temp[["geo", "year", OUTCOME] + covars].dropna().copy()
    formula = f"{OUTCOME} ~ {' + '.join(covars)}"
    result = smf.mixedlm(formula, data=df, groups=df["geo"]).fit(reml=False, method="lbfgs", maxiter=1000, disp=False)
    names = result.model.exog_names
    fixed = pd.DataFrame(
        {
            "term": names,
            "coef": result.fe_params.values,
            "se": result.bse_fe.values,
            "z_value": result.fe_params.values / result.bse_fe.values,
            "p_value": result.pvalues[names].values,
            "nobs": int(result.nobs),
            "countries": df["geo"].nunique(),
        }
    )
    rand_var = float(result.cov_re.iloc[0, 0]) if result.cov_re.size else np.nan
    resid_var = float(result.scale)
    icc = rand_var / (rand_var + resid_var) if pd.notna(rand_var) else np.nan
    fixed.loc[len(fixed)] = ["Random intercept variance", rand_var, np.nan, np.nan, np.nan, int(result.nobs), df["geo"].nunique()]
    fixed.loc[len(fixed)] = ["Residual variance", resid_var, np.nan, np.nan, np.nan, int(result.nobs), df["geo"].nunique()]
    fixed.to_csv(OUTPUTS / "regression_multilevel_results.csv", index=False)
    (OUTPUTS / "regression_icc.txt").write_text(
        f"Random intercept variance: {rand_var:.6f}\nResidual variance: {resid_var:.6f}\nICC: {icc:.6f}\nN: {int(result.nobs)}\nCountries: {df['geo'].nunique()}\n",
        encoding="utf-8",
    )
    write_latex(fixed, TABLES / "regression_multilevel.tex", "Multilevel random-intercept model for unmet medical need", "tab:regression_multilevel")


def robustness_summary(
    baseline: pd.DataFrame,
    lag: pd.DataFrame,
    crisis: pd.DataFrame,
    influential: pd.DataFrame,
    groups: pd.DataFrame,
) -> pd.DataFrame:
    rows = []
    rows.append(baseline.iloc[0].to_dict())
    rows.extend(lag.to_dict("records"))
    rows.extend(crisis.to_dict("records"))
    rows.extend(influential.to_dict("records"))
    for group in ["Western/Northern Europe", "Eastern/Southern Europe"]:
        row = groups[(groups["group"] == group) & (groups["term"] == "poverty_or_social_exclusion_pc")].iloc[0]
        rows.append(
            {
                "specification": f"Country group {group}",
                "term": "poverty_or_social_exclusion_pc",
                "coef": row["coef"],
                "se": row["se"],
                "p_value": row["p_value"],
                "ci_low": row["coef"] - 1.96 * row["se"],
                "ci_high": row["coef"] + 1.96 * row["se"],
                "nobs": row["nobs"],
                "countries": row["countries"],
            }
        )
    out = pd.DataFrame(rows)
    out.to_csv(OUTPUTS / "regression_robustness_summary.csv", index=False)
    write_latex(
        out,
        TABLES / "regression_robustness_summary.tex",
        "Stability of poverty and social exclusion association across alternative specifications",
        "tab:regression_robustness_summary",
    )
    return out


def forest_plot(summary: pd.DataFrame) -> None:
    plot_df = summary.dropna(subset=["coef", "se"]).copy()
    plot_df = plot_df.iloc[::-1].reset_index(drop=True)
    y = np.arange(len(plot_df))
    plt.figure(figsize=(9, max(5.5, 0.42 * len(plot_df))))
    plt.errorbar(
        plot_df["coef"],
        y,
        xerr=1.96 * plot_df["se"],
        fmt="o",
        color="#0072b2",
        ecolor="#555555",
        elinewidth=1.5,
        capsize=3,
    )
    plt.axvline(0, color="#000000", linestyle="--", linewidth=1)
    plt.yticks(y, plot_df["specification"])
    plt.xlabel("Coefficient on poverty/social exclusion (95% CI)")
    plt.tight_layout()
    plt.savefig(FIGURES / "regression_robustness_forest_plot.pdf", dpi=300)
    plt.close()


def multiple_imputation(panel: pd.DataFrame) -> None:
    impute_vars = [
        "poverty_or_social_exclusion_pc",
        "gini_income",
        "physicians_per_100k",
        "oop_health_expenditure_share_pc",
        "hospital_beds_per_100k",
        "long_term_unemployment_rate_pc",
    ]
    context_vars = [
        "year",
        "gdp_per_capita_eur",
        "log_gdp_per_capita",
        "unemployment_rate_pc",
        "government_health_expenditure_gdp_pc",
        "compulsory_health_financing_gdp_pc",
        "gdp_per_capita_growth",
        "unemployment_rate_change",
    ]
    numeric_vars = [v for v in dict.fromkeys(context_vars + impute_vars) if v in panel.columns]
    rows = []
    imputed_paths = []
    for i in range(10):
        df = panel.copy()
        imp = IterativeImputer(max_iter=10, random_state=RANDOM_SEED + i, sample_posterior=True)
        arr = imp.fit_transform(df[numeric_vars])
        filled = pd.DataFrame(arr, columns=numeric_vars, index=df.index)
        for var in impute_vars:
            df[var] = filled[var]
        fit_df = model_sample(df, BASELINE_COVARS)
        result = fit_fe(fit_df, BASELINE_COVARS)
        coef, se, p_value = safe_term(result, "poverty_or_social_exclusion_pc")
        rows.append(
            {
                "imputation": i + 1,
                "coef": coef,
                "se": se,
                "p_value": p_value,
                "nobs": int(result.nobs),
                "countries": fit_df["geo"].nunique(),
            }
        )
        path = DATA_PROCESSED / f"panel_features_v2-3_imputed_{i + 1}.csv"
        df.to_csv(path, index=False)
        imputed_paths.append(str(path.relative_to(ROOT)))

    estimates = pd.DataFrame(rows)
    estimates.to_csv(OUTPUTS / "multiple_imputation_fe_results.csv", index=False)
    m = len(estimates)
    q_bar = estimates["coef"].mean()
    u_bar = (estimates["se"] ** 2).mean()
    b = estimates["coef"].var(ddof=1)
    total_var = u_bar + (1 + 1 / m) * b
    pooled_se = math.sqrt(total_var)
    t_stat = q_bar / pooled_se if pooled_se > 0 else np.nan
    df_old = (m - 1) * (1 + u_bar / ((1 + 1 / m) * b)) ** 2 if b > 0 else np.inf
    p_value = 2 * (1 - stats.t.cdf(abs(t_stat), df_old)) if np.isfinite(df_old) else 2 * (1 - stats.norm.cdf(abs(t_stat)))
    pooled = pd.DataFrame(
        [
            {
                "term": "poverty_or_social_exclusion_pc",
                "pooled_coef": q_bar,
                "pooled_se": pooled_se,
                "t_stat": t_stat,
                "df": df_old,
                "p_value": p_value,
                "imputations": m,
                "mean_nobs": estimates["nobs"].mean(),
                "mean_countries": estimates["countries"].mean(),
            }
        ]
    )
    pooled.to_csv(OUTPUTS / "multiple_imputation_pooled_results.csv", index=False)
    write_latex(pooled, TABLES / "multiple_imputation_sensitivity.tex", "Multiple-imputation sensitivity for the poverty association", "tab:multiple_imputation_sensitivity")
    (OUTPUTS / "multiple_imputation_notes.txt").write_text(
        "MICE-style IterativeImputer used max_iter=10 and sample_posterior=True with random seeds 42-51.\n"
        "Outcome, country identifiers, and year identifiers were not overwritten.\n"
        "Saved imputed panels:\n" + "\n".join(imputed_paths) + "\n",
        encoding="utf-8",
    )


def run_regressions(panel: pd.DataFrame, model: pd.DataFrame) -> None:
    core = regression_core(panel, model)
    reduced_covariate_sensitivity(panel)
    influential = influential_country_sensitivity(panel, model)
    lag = lag_robustness(panel)
    crisis = crisis_exclusion(model)
    groups = country_group_stratification(panel)
    vif_table(model)
    hausman_test(model)
    serial_correlation_check(model)
    multilevel_model(panel)
    summary = robustness_summary(core["baseline_fe"], lag, crisis, influential, groups)
    forest_plot(summary)
    multiple_imputation(panel)


def main() -> None:
    panel = add_population_weights(read_csv(DATA_PROCESSED / "panel_features_v2-3.csv"))
    outcome = read_csv(DATA_PROCESSED / "country_year_outcome.csv")
    model_file = read_csv(DATA_PROCESSED / "modeling_dataset_5a.csv")
    regression_sample = model_sample(panel, BASELINE_COVARS)
    ml = read_csv(DATA_PROCESSED / "modeling_dataset_5a_with_splits.csv")
    (OUTPUTS / "regression_sample_note.txt").write_text(
        "Regression sample constructed from panel_features_v2-3.csv complete cases for outcome and the five baseline covariates.\n"
        f"Constructed regression sample: {len(regression_sample)} rows, {regression_sample['geo'].nunique()} countries.\n"
        f"modeling_dataset_5a.csv currently has {len(model_file)} rows, {model_file['geo'].nunique()} countries.\n",
        encoding="utf-8",
    )

    cit = fetch_citizenship_data()
    print("STEP 1 COMPLETE")

    run_descriptive(panel, outcome, regression_sample, ml, cit)
    print("STEP 2 COMPLETE")

    run_regressions(panel, regression_sample)
    print("STEP 3 COMPLETE")
    print("STEP 4 COMPLETE")


if __name__ == "__main__":
    main()
