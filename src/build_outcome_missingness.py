from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from eurostat_api import availability_matrix


PROJECT_ROOT = Path(__file__).resolve().parents[1]
YEARS = range(2008, 2026)


def missing_year_text(observed_years: set[int]) -> str:
    missing = [str(year) for year in YEARS if year not in observed_years]
    return ", ".join(missing) if missing else "none"


def main() -> None:
    data_path = PROJECT_ROOT / "data" / "processed" / "country_year_outcome.csv"
    matrix_path = PROJECT_ROOT / "outputs" / "outcome_availability_matrix.csv"
    country_path = PROJECT_ROOT / "outputs" / "outcome_country_coverage.csv"
    heatmap_path = PROJECT_ROOT / "outputs" / "outcome_missingness_heatmap.png"
    summary_path = PROJECT_ROOT / "outputs" / "outcome_missingness_summary.md"

    df = pd.read_csv(data_path)
    matrix_long = availability_matrix(df, YEARS, "unmet_need_pc")
    matrix_wide = matrix_long.pivot(index="geo", columns="year", values="observed").sort_index()

    coverage = (
        matrix_long.groupby("geo", as_index=False)
        .agg(non_missing_years=("observed", "sum"))
        .sort_values(["non_missing_years", "geo"], ascending=[True, True])
    )
    first_last = (
        df.groupby("geo")
        .agg(first_year=("year", "min"), last_year=("year", "max"))
        .reset_index()
    )
    observed_sets = df.groupby("geo")["year"].apply(lambda values: set(values.astype(int))).to_dict()
    coverage["missing_years"] = coverage["geo"].map(lambda geo: missing_year_text(observed_sets.get(geo, set())))
    coverage = coverage.merge(first_last, on="geo", how="left")
    coverage = coverage[["geo", "non_missing_years", "first_year", "last_year", "missing_years"]]

    matrix_wide.to_csv(matrix_path)
    coverage.to_csv(country_path, index=False)

    plt.figure(figsize=(12, 8))
    sns.heatmap(
        matrix_wide,
        cmap=sns.color_palette(["#f0f0f0", "#2364aa"]),
        cbar=False,
        linewidths=0.15,
        linecolor="white",
    )
    plt.xlabel("Year")
    plt.ylabel("Country code")
    plt.title("Observed country-year cells for hlth_silc_08")
    plt.tight_layout()
    plt.savefig(heatmap_path, dpi=180)
    plt.close()

    countries = coverage["geo"].nunique()
    total_years = len(list(YEARS))
    sparse = coverage[coverage["non_missing_years"] <= 10]["geo"].tolist()
    mostly_complete = coverage[coverage["non_missing_years"] >= 16]["geo"].tolist()
    observed_cells = int(matrix_long["observed"].sum())
    total_cells = int(len(matrix_long))

    sparse_text = ", ".join(sparse) if sparse else "none"
    complete_text = ", ".join(mostly_complete) if mostly_complete else "none"
    summary = f"""# Outcome missingness summary

Date accessed: 2026-05-14

This section describes the country-year availability of the primary outcome from Eurostat table `hlth_silc_08`.

The tidy outcome file contains {observed_cells} observed country-year cells. The availability grid covers {countries} national country codes and {total_years} calendar years from 2008 to 2025. EU and euro-area aggregate codes are not included in the processed outcome file.

Countries with ten or fewer observed years are: {sparse_text}.

Countries with at least sixteen observed years are: {complete_text}.

The files `outputs/outcome_availability_matrix.csv`, `outputs/outcome_country_coverage.csv`, and `outputs/outcome_missingness_heatmap.png` give the detailed availability record.

This is a descriptive availability check. It is not an inference exercise.
"""
    summary_path.write_text(summary, encoding="utf-8")

    print(f"saved {matrix_path}")
    print(f"saved {country_path}")
    print(f"saved {heatmap_path}")
    print(f"saved {summary_path}")


if __name__ == "__main__":
    main()
