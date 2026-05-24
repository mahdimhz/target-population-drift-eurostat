from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_MAIN = ROOT / "tables" / "regression_main_results.tex"
OUTPUT_ROBUSTNESS = ROOT / "tables" / "robustness_08b_results.tex"


LABELS = {
    "log_gdp_per_capita": "Log GDP per capita",
    "unemployment_rate_pc": "Unemployment rate",
    "poverty_or_social_exclusion_pc": "Poverty or social exclusion",
    "government_health_expenditure_gdp_pc": "Government health expenditure",
    "compulsory_health_financing_gdp_pc": "Compulsory health financing",
}


ROBUSTNESS_LABELS = {
    "log_gdp_per_capita": "Log GDP per capita",
    "unemployment_rate_pc": "Unemployment rate",
    "poverty_or_social_exclusion_pc": "Poverty or social exclusion",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def coefficient_cell(row: dict[str, str] | None) -> str:
    if row is None:
        return ""
    estimate = float(row["estimate"])
    se = float(row["standard_error"])
    return f"{estimate:.3f} ({se:.3f})"


def by_variable(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row["variable"]: row for row in rows}


def write_main_table() -> None:
    pooled = by_variable(read_csv(ROOT / "outputs" / "table_pooled_baseline.csv"))
    indicator = by_variable(read_csv(ROOT / "outputs" / "table_fe_baseline.csv"))

    lines = [
        r"\begin{tabular}{lcc}",
        r"\toprule",
        r"Variable & Pooled + year & Country + year \\",
        r"\midrule",
    ]
    for variable, label in LABELS.items():
        lines.append(
            f"{label} & {coefficient_cell(pooled.get(variable))} & "
            f"{coefficient_cell(indicator.get(variable))} \\\\"
        )
    lines.extend(
        [
            r"\midrule",
            r"Observations & 282 & 282 \\",
            r"Countries & 30 & 30 \\",
            r"Year indicators & Yes & Yes \\",
            r"Country indicators & No & Yes \\",
            r"$R^2$ & 0.221 & 0.895 \\",
            r"\bottomrule",
            r"\end{tabular}",
            r"",
            r"\vspace{0.2em}",
            r"\begin{minipage}{0.92\textwidth}",
            r"\scriptsize Notes: Cells report coefficient estimates with standard errors in parentheses. "
            r"Both the pooled model and the country-and-year fixed-effects model use country-clustered standard errors with finite-sample correction. "
            r"No star thresholds are used because the thesis emphasizes coefficient stability across estimands.",
            r"\end{minipage}",
        ]
    )
    OUTPUT_MAIN.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_robustness_table() -> None:
    rows = read_csv(ROOT / "outputs" / "table_08b_robustness_models.csv")
    grouped: dict[str, dict[str, dict[str, str]]] = {}
    for row in rows:
        grouped.setdefault(row["outcome"], {})[row["variable"]] = row

    lines = [
        r"\begin{tabular}{lcc}",
        r"\toprule",
        r"Variable & Primary outcome & Robustness outcome \\",
        r"\midrule",
    ]
    for variable, label in ROBUSTNESS_LABELS.items():
        lines.append(
            f"{label} & {coefficient_cell(grouped['unmet_need_pc_08'].get(variable))} & "
            f"{coefficient_cell(grouped['unmet_need_pc_08b'].get(variable))} \\\\"
        )
    lines.extend(
        [
            r"\midrule",
            r"Observations & 147 & 147 \\",
            r"Outcome table & \texttt{hlth\_silc\_08} & \texttt{hlth\_silc\_08b} \\",
            r"\bottomrule",
            r"\end{tabular}",
            r"",
            r"\vspace{0.2em}",
            r"\begin{minipage}{0.82\textwidth}",
            r"\scriptsize Notes: Cells report coefficient estimates with standard errors in parentheses. "
            r"The comparison is restricted to overlapping 2021--2025 country-year cells with complete values for the three shared controls. "
            r"No star thresholds are used because this is a denominator sensitivity check, not a main inferential model.",
            r"\end{minipage}",
        ]
    )
    OUTPUT_ROBUSTNESS.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    write_main_table()
    write_robustness_table()


if __name__ == "__main__":
    main()
