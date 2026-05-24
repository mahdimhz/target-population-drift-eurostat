from __future__ import annotations

from pathlib import Path

import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.outliers_influence import variance_inflation_factor


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "processed" / "panel_features_v2-3.csv"
TABLE_DIR = ROOT / "tables"

OUTCOME = "unmet_need_pc"
BASELINE = [
    "log_gdp_per_capita",
    "unemployment_rate_pc",
    "poverty_or_social_exclusion_pc",
    "government_health_expenditure_gdp_pc",
    "compulsory_health_financing_gdp_pc",
]

LABELS = {
    "log_gdp_per_capita": "Log GDP per capita",
    "unemployment_rate_pc": "Unemployment rate",
    "poverty_or_social_exclusion_pc": "Poverty or social exclusion",
    "government_health_expenditure_gdp_pc": "Government health expenditure",
    "compulsory_health_financing_gdp_pc": "Compulsory health financing",
}


def fmt(value: float | None, digits: int = 3) -> str:
    if value is None or pd.isna(value):
        return "--"
    return f"{value:.{digits}f}"


def clustered_model(df: pd.DataFrame, covariates: list[str]):
    formula = f"{OUTCOME} ~ {' + '.join(covariates)} + C(year)"
    return smf.ols(formula, data=df).fit(cov_type="cluster", cov_kwds={"groups": df["geo"]})


def write_vif_table(df: pd.DataFrame) -> None:
    complete = df.dropna(subset=[OUTCOME] + BASELINE).copy()
    x = sm.add_constant(complete[BASELINE])
    rows = []
    for i, column in enumerate(x.columns):
        if column == "const":
            continue
        rows.append((LABELS[column], variance_inflation_factor(x.values, i)))

    lines = [
        r"\begin{tabular}{@{}lr@{}}",
        r"\toprule",
        r"Covariate & VIF \\",
        r"\midrule",
    ]
    for label, vif in rows:
        lines.append(f"{label} & {vif:.2f} \\\\")
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}",
            r"\par\vspace{0.3em}",
            r"\begin{minipage}{0.86\textwidth}",
            r"\footnotesize Notes: VIF is the variance inflation factor calculated for the five baseline covariates in the complete-case pooled regression sample. Values above 10 are commonly treated as indicating serious multicollinearity.",
            r"\end{minipage}",
        ]
    )
    (TABLE_DIR / "regression_vif_diagnostics.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_reduced_model_table(df: pd.DataFrame) -> None:
    specs = [
        ("Model A", ["log_gdp_per_capita", "unemployment_rate_pc"]),
        ("Model B", ["log_gdp_per_capita", "unemployment_rate_pc", "poverty_or_social_exclusion_pc"]),
        ("Model C", BASELINE),
    ]
    results = []
    for name, covariates in specs:
        sample = df.dropna(subset=[OUTCOME] + covariates).copy()
        model = clustered_model(sample, covariates)
        results.append((name, covariates, sample, model))

    rows = [
        ("Poverty or social exclusion", "poverty_or_social_exclusion_pc"),
        ("Log GDP per capita", "log_gdp_per_capita"),
        ("Unemployment rate", "unemployment_rate_pc"),
    ]
    lines = [
        r"\begin{tabular}{@{}lccc@{}}",
        r"\toprule",
        r" & Model A & Model B & Model C \\",
        r"\midrule",
    ]
    for label, variable in rows:
        vals = []
        for _, covariates, _, model in results:
            if variable in covariates:
                vals.append(f"{fmt(model.params[variable])}")
            else:
                vals.append("--")
        lines.append(f"{label} & {' & '.join(vals)} \\\\")
        ses = []
        for _, covariates, _, model in results:
            if variable in covariates:
                ses.append(f"({fmt(model.bse[variable])})")
            else:
                ses.append("--")
        lines.append(f" & {' & '.join(ses)} \\\\")
    lines.append(r"\midrule")
    lines.append(
        "Observations & "
        + " & ".join(str(len(sample)) for _, _, sample, _ in results)
        + r" \\"
    )
    lines.append(
        "Countries & "
        + " & ".join(str(sample["geo"].nunique()) for _, _, sample, _ in results)
        + r" \\"
    )
    lines.append(
        r"\(R^2\) & "
        + " & ".join(fmt(model.rsquared) for _, _, _, model in results)
        + r" \\"
    )
    lines.append(
        "Included covariates & GDP, unemp. & Model A + poverty & Full baseline \\\\"
    )
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}",
            r"\par\vspace{0.3em}",
            r"\begin{minipage}{0.96\textwidth}",
            r"\footnotesize Notes: Pooled OLS models include year indicators and country-clustered standard errors. Standard errors are shown in parentheses. No star thresholds are used because the table is a covariate-set sensitivity check.",
            r"\end{minipage}",
        ]
    )
    (TABLE_DIR / "reduced_covariate_sensitivity.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    df = pd.read_csv(DATA)
    write_vif_table(df)
    write_reduced_model_table(df)


if __name__ == "__main__":
    main()
