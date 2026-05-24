from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "tables" / "variable_summary.tex"


DESCRIPTIONS = {
    "unmet_need_pc": "Primary outcome: unmet medical examination need due to cost, distance, or waiting list; persons aged 16+.",
    "unmet_need_pc_08b": "Robustness outcome: same access-barrier reasons, measured among persons having the same medical needs.",
    "gdp_per_capita_eur": "Macroeconomic level: current-price GDP per inhabitant.",
    "unemployment_rate_pc": "Labour-market condition: unemployment rate for ages 15--74.",
    "poverty_or_social_exclusion_pc": "Inequality and poverty: persons at risk of poverty or social exclusion.",
    "government_health_expenditure_gdp_pc": "Health-system financing: general government health expenditure as share of GDP.",
    "compulsory_health_financing_gdp_pc": "Health-system financing: compulsory financing schemes as share of GDP.",
    "physicians_per_100k": "Health-system capacity: practising physicians per 100,000 inhabitants.",
    "hospital_beds_per_100k": "Health-system capacity: total hospital beds per 100,000 inhabitants.",
    "oop_health_expenditure_share_pc": "Health-system financing: out-of-pocket spending as share of current health expenditure.",
    "gini_income": "Inequality: Gini coefficient of equivalised disposable income.",
    "long_term_unemployment_rate_pc": "Labour-market condition: long-term unemployment rate for ages 15--74.",
    "log_gdp_per_capita": "Engineered feature: natural log of GDP per inhabitant.",
    "gdp_per_capita_growth": "Engineered feature: annual within-country change in GDP per inhabitant.",
    "unemployment_rate_change": "Engineered feature: annual within-country change in unemployment rate.",
    "physicians_per_100k_lag1": "Engineered feature: one-year lag of practising physicians per 100,000 inhabitants.",
}


SOURCES = {
    "unmet_need_pc": "Eurostat \\texttt{hlth\\_silc\\_08}",
    "unmet_need_pc_08b": "Eurostat \\texttt{hlth\\_silc\\_08b}",
    "log_gdp_per_capita": "Derived: \\texttt{nama\\_10\\_pc}",
    "gdp_per_capita_growth": "Derived: \\texttt{nama\\_10\\_pc}",
    "unemployment_rate_change": "Derived: \\texttt{une\\_rt\\_a}",
    "physicians_per_100k_lag1": "Derived: \\texttt{hlth\\_rs\\_prs2}",
}


ORDER = [
    "unmet_need_pc",
    "unmet_need_pc_08b",
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
    "gdp_per_capita_growth",
    "unemployment_rate_change",
    "physicians_per_100k_lag1",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def latex_escape(value: str) -> str:
    replacements = {
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
    }
    escaped = value
    for old, new in replacements.items():
        escaped = escaped.replace(old, new)
    return escaped


def texttt(value: str) -> str:
    return "\\path{" + value + "}"


def panel_years() -> dict[str, str]:
    panel = read_csv(ROOT / "data" / "processed" / "panel_features_v2.csv")
    years: dict[str, str] = {}
    if not panel:
        return years
    for col in panel[0]:
        if col in {"geo", "year", "status"}:
            continue
        observed = sorted({int(row["year"]) for row in panel if row.get(col, "") not in {"", None}})
        if observed:
            years[col] = f"{observed[0]}--{observed[-1]}"
    return years


def build_metadata() -> dict[str, dict[str, str]]:
    metadata: dict[str, dict[str, str]] = {}
    for path in [
        ROOT / "outputs" / "control_feasibility.csv",
        ROOT / "outputs" / "control_feasibility_extended.csv",
    ]:
        for row in read_csv(path):
            var = row["variable_name"]
            metadata[var] = {
                "source": f"Eurostat {texttt(row['dataset_code'])}",
                "years": row["years_available"].replace("-", "--"),
            }
    metadata["unmet_need_pc"] = {
        "source": SOURCES["unmet_need_pc"],
        "years": "2008--2025",
    }
    metadata["unmet_need_pc_08b"] = {
        "source": SOURCES["unmet_need_pc_08b"],
        "years": "2021--2025",
    }
    years = panel_years()
    for var in ["log_gdp_per_capita", "gdp_per_capita_growth", "unemployment_rate_change", "physicians_per_100k_lag1"]:
        metadata[var] = {
            "source": SOURCES[var],
            "years": years.get(var, ""),
        }
    return metadata


def row_for(var: str, metadata: dict[str, dict[str, str]]) -> str:
    return (
        f"{texttt(var)} & "
        f"{latex_escape(DESCRIPTIONS[var])} & "
        f"{metadata[var]['source']} & "
        f"{metadata[var]['years']} \\\\"
    )


def main() -> None:
    metadata = build_metadata()
    lines = [
        r"\begingroup",
        r"\setlength{\tabcolsep}{4pt}",
        r"\begin{tabular}{@{}>{\raggedright\arraybackslash}p{0.22\textwidth}>{\raggedright\arraybackslash}p{0.38\textwidth}>{\raggedright\arraybackslash}p{0.23\textwidth}r@{}}",
        r"\toprule",
        r"Variable & Description & Source & Years \\",
        r"\midrule",
    ]
    lines.extend(row_for(var, metadata) for var in ORDER)
    lines.extend([r"\bottomrule", r"\end{tabular}", r"\endgroup"])
    OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
