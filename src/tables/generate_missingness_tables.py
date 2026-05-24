from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
TABLES = ROOT / "tables"
PANEL = ROOT / "data" / "processed" / "panel_features_v2-3.csv"
ML = ROOT / "data" / "processed" / "modeling_dataset_5a.csv"

OUTCOME = "unmet_need_pc"
REGRESSION_COVARIATES = [
    "log_gdp_per_capita",
    "unemployment_rate_pc",
    "poverty_or_social_exclusion_pc",
    "government_health_expenditure_gdp_pc",
    "compulsory_health_financing_gdp_pc",
]
ML_FEATURES = [
    "gdp_per_capita_eur",
    "unemployment_rate_pc",
    "poverty_or_social_exclusion_pc",
    "government_health_expenditure_gdp_pc",
    "compulsory_health_financing_gdp_pc",
    "physicians_per_100k",
    "hospital_beds_per_100k",
    "oop_health_expenditure_share_pc",
    "gini_income",
    "long_term_unemployment_rate_pc",
    "log_gdp_per_capita",
    "physicians_per_100k_lag1",
    "gdp_per_capita_growth",
    "unemployment_rate_change",
]

SHORT_LABELS = {
    "log_gdp_per_capita": "log GDP",
    "gdp_per_capita_eur": "GDP",
    "unemployment_rate_pc": "unemployment",
    "poverty_or_social_exclusion_pc": "poverty",
    "government_health_expenditure_gdp_pc": "gov. health exp.",
    "compulsory_health_financing_gdp_pc": "comp. financing",
    "physicians_per_100k": "physicians",
    "physicians_per_100k_lag1": "lag physicians",
    "hospital_beds_per_100k": "beds",
    "oop_health_expenditure_share_pc": "OOP spending",
    "gini_income": "Gini",
    "long_term_unemployment_rate_pc": "long-term unemp.",
    "gdp_per_capita_growth": "GDP growth",
    "unemployment_rate_change": "unemp. change",
}


def yes_no(value: bool) -> str:
    return "Yes" if value else "No"


def format_float(value: float) -> str:
    return f"{value:,.2f}"


def driver_for_country(rows: pd.DataFrame, in_regression: bool, in_ml: bool) -> str:
    if in_regression and in_ml:
        return "Included"
    if in_regression and not in_ml:
        zero_ml = [c for c in ML_FEATURES if rows[c].notna().sum() == 0]
        if "physicians_per_100k" in zero_ml:
            return "ML: physicians"
        return "ML: " + ", ".join(SHORT_LABELS[c] for c in zero_ml[:2])

    zero_reg = [c for c in REGRESSION_COVARIATES if rows[c].notna().sum() == 0]
    if zero_reg:
        return "Reg.: " + ", ".join(SHORT_LABELS[c] for c in zero_reg[:3])
    return "Reg.: no complete covariate row"


def write_country_coverage(panel: pd.DataFrame, ml: pd.DataFrame) -> None:
    reg = panel.dropna(subset=[OUTCOME] + REGRESSION_COVARIATES)
    reg_countries = set(reg["geo"])
    ml_countries = set(ml["geo"])

    lines = [
        r"\begin{tabular}{@{}lrrll@{}}",
        r"\toprule",
        r"Country & Years & Reg. & ML & Main exclusion driver \\",
        r"\midrule",
    ]
    for geo in sorted(panel["geo"].unique()):
        rows = panel[panel["geo"] == geo]
        in_reg = geo in reg_countries
        in_ml = geo in ml_countries
        lines.append(
            f"{geo} & {rows[OUTCOME].notna().sum()} & {yes_no(in_reg)} & {yes_no(in_ml)} & "
            f"{driver_for_country(rows, in_reg, in_ml)} \\\\"
        )
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}",
            r"\par\vspace{0.3em}",
            r"\begin{minipage}{0.96\textwidth}",
            r"\footnotesize Notes: Years counts observed primary-outcome years in the 2008--2025 descriptive panel. Reg. flags countries with at least one complete row in the baseline regression sample. ML flags countries included in the complete-case machine-learning sample. Exclusion drivers summarise the main missing covariates preventing inclusion.",
            r"\end{minipage}",
        ]
    )
    (TABLES / "country_coverage.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_missingness_comparison(panel: pd.DataFrame) -> None:
    reg = panel.dropna(subset=[OUTCOME] + REGRESSION_COVARIATES)
    included_index = set(reg.index)
    panel = panel.copy()
    panel["sample_group"] = panel.index.map(lambda idx: "Included" if idx in included_index else "Excluded")

    rows = []
    for group in ["Included", "Excluded"]:
        data = panel[panel["sample_group"] == group]
        rows.append(
            {
                "group": group,
                "rows": len(data),
                "countries": data["geo"].nunique(),
                "unmet": data[OUTCOME].mean(),
                "gdp": data["gdp_per_capita_eur"].mean(),
                "unemployment": data["unemployment_rate_pc"].mean(),
            }
        )

    lines = [
        r"\begin{tabular}{@{}lrrrrr@{}}",
        r"\toprule",
        r"Sample group & Rows & Countries & Mean outcome & Mean GDP pc & Mean unemployment \\",
        r"\midrule",
    ]
    for row in rows:
        lines.append(
            f"{row['group']} & {row['rows']} & {row['countries']} & "
            f"{format_float(row['unmet'])} & {format_float(row['gdp'])} & {format_float(row['unemployment'])} \\\\"
        )
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}",
            r"\par\vspace{0.3em}",
            r"\begin{minipage}{0.96\textwidth}",
        r"\footnotesize Notes: The outcome is unmet medical care need. Included rows are complete for the baseline regression variables. Excluded rows are observed in the descriptive outcome panel but are not complete for the baseline regression. GDP per capita and unemployment means are calculated over available non-missing values within each group.",
            r"\end{minipage}",
        ]
    )
    (TABLES / "missingness_comparison.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    panel = pd.read_csv(PANEL)
    ml = pd.read_csv(ML)
    write_country_coverage(panel, ml)
    write_missingness_comparison(panel)


if __name__ == "__main__":
    main()
