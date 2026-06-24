from __future__ import annotations

import platform
from pathlib import Path

import matplotlib
import pandas
import seaborn
import sklearn
import statsmodels


ROOT = Path(__file__).resolve().parents[2]
TABLES = ROOT / "tables"
OUTPUTS = ROOT / "outputs"


EUROSTAT_ROWS = [
    ("demo\\_pjan", "Population weights", "freq=A; unit=NR; age=TOTAL; sex=T; years 2008--2025", "2026-05-21"),
    ("nama\\_10\\_pc", "GDP per capita", "unit=CP\\_EUR\\_HAB; na\\_item=B1GQ; years 2008--2025", "2026-05-14"),
    ("une\\_rt\\_a", "Unemployment rate", "unit=PC\\_ACT; sex=T; age=Y15-74; years 2008--2025", "2026-05-14"),
    ("ilc\\_peps01n", "Poverty or social exclusion", "unit=PC; sex=T; age=TOTAL; years 2008--2025", "2026-05-14"),
    ("gov\\_10a\\_exp", "Government health expenditure", "unit=PC\\_GDP; sector=S13; cofog99=GF07; na\\_item=TE; years 2008--2025", "2026-05-14"),
    ("hlth\\_sha11\\_hf", "Compulsory health financing", "unit=PC\\_GDP; icha11\\_hf=HF1; years 2008--2025", "2026-05-14"),
    ("hlth\\_sha11\\_hf", "Out-of-pocket spending", "unit=PC\\_CHE; icha11\\_hf=HF3; years 2008--2025", "2026-05-14"),
    ("hlth\\_rs\\_prs2", "Physicians per 100,000", "unit=P\\_HTHAB; wstatus=PRACT; med\\_spec=PHYS; years 2008--2025", "2026-05-14"),
    ("hlth\\_rs\\_bds1", "Hospital beds per 100,000", "unit=P\\_HTHAB; facility=HBEDT; hlthcare=TOTAL; years 2008--2025", "2026-05-14"),
    ("ilc\\_di12", "Gini coefficient", "age=TOTAL; statinfo=GINI\\_HND; years 2008--2025", "2026-05-14"),
    ("une\\_ltu\\_a", "Long-term unemployment", "indic\\_em=LTU; age=Y15-74; sex=T; unit=PC\\_ACT; years 2008--2025", "2026-05-14"),
]


def latex_escape(text: object) -> str:
    value = "" if pandas.isna(text) else str(text)
    replacements = {
        "\\": r"\textbackslash{}",
        "_": r"\_",
        "%": r"\%",
        "&": r"\&",
        "#": r"\#",
    }
    for old, new in replacements.items():
        value = value.replace(old, new)
    return value


def registry_source_rows() -> list[tuple[str, str, str, str]]:
    registry_path = OUTPUTS / "multi_outcome_indicator_registry.csv"
    if not registry_path.exists():
        return []
    registry = pandas.read_csv(registry_path)
    wanted = {
        "medical_population_combined": "Medical population denominator",
        "medical_need_combined": "Medical need denominator",
        "dental_population_combined": "Dental population denominator",
        "dental_need_combined": "Dental need denominator",
    }
    rows: list[tuple[str, str, str, str]] = []
    for indicator_id, use in wanted.items():
        match = registry[registry["indicator_id"].eq(indicator_id)]
        if match.empty:
            continue
        row = match.iloc[0]
        filter_parts = [
            f"unit={row['unit']}",
            "quantile=TOTAL" if row["denominator"] == "population" else "rskpovth=TOTAL",
            f"reason={row['reason_code']}",
            f"age={row['age']}",
            f"sex={row['sex']}",
            f"years {int(row['year_min'])}--{int(row['year_max'])}",
        ]
        rows.append(
            (
                latex_escape(row["dataset_code"]),
                use,
                latex_escape("; ".join(filter_parts)),
                latex_escape(row["extraction_date"]),
            )
        )
    return rows


def write_eurostat_table() -> None:
    rows = registry_source_rows() + EUROSTAT_ROWS
    lines = [
        r"\resizebox{\textwidth}{!}{%",
        r"\begin{tabular}{@{}>{\raggedright\arraybackslash}p{0.15\textwidth}>{\raggedright\arraybackslash}p{0.23\textwidth}>{\raggedright\arraybackslash}p{0.45\textwidth}r@{}}",
        r"\toprule",
        r"Code & Use & Filters & Accessed \\",
        r"\midrule",
    ]
    for code, use, filters, accessed in rows:
        lines.append(f"\\texttt{{{code}}} & {latex_escape(use)} & {filters} & {accessed} \\\\")
    lines.extend([r"\bottomrule", r"\end{tabular}%", r"}"])
    (TABLES / "eurostat_sources_appendix.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_software_table() -> None:
    rows = [
        ("Python", platform.python_version()),
        ("pandas", pandas.__version__),
        ("scikit-learn", sklearn.__version__),
        ("statsmodels", statsmodels.__version__),
        ("matplotlib", matplotlib.__version__),
        ("seaborn", seaborn.__version__),
    ]
    lines = [
        r"\begin{tabular}{@{}ll@{}}",
        r"\toprule",
        r"Software & Version \\",
        r"\midrule",
    ]
    for package, version in rows:
        lines.append(f"{package} & {version} \\\\")
    lines.extend([r"\bottomrule", r"\end{tabular}"])
    (TABLES / "software_versions.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    write_eurostat_table()
    write_software_table()


if __name__ == "__main__":
    main()
