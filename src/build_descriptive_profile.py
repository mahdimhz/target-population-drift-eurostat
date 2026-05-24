from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


def save_year_summary(outcome: pd.DataFrame) -> pd.DataFrame:
    summary = (
        outcome.groupby("year")
        .agg(
            countries=("geo", "nunique"),
            mean_unmet_need_pc=("unmet_need_pc", "mean"),
            median_unmet_need_pc=("unmet_need_pc", "median"),
            min_unmet_need_pc=("unmet_need_pc", "min"),
            p25_unmet_need_pc=("unmet_need_pc", lambda values: values.quantile(0.25)),
            p75_unmet_need_pc=("unmet_need_pc", lambda values: values.quantile(0.75)),
            max_unmet_need_pc=("unmet_need_pc", "max"),
        )
        .reset_index()
        .round(3)
    )
    summary.to_csv(OUTPUTS_DIR / "primary_year_summary.csv", index=False)
    return summary


def save_country_summary(outcome: pd.DataFrame) -> pd.DataFrame:
    summary = (
        outcome.groupby("geo")
        .agg(
            first_year=("year", "min"),
            last_year=("year", "max"),
            observed_years=("year", "nunique"),
            mean_unmet_need_pc=("unmet_need_pc", "mean"),
            median_unmet_need_pc=("unmet_need_pc", "median"),
            min_unmet_need_pc=("unmet_need_pc", "min"),
            max_unmet_need_pc=("unmet_need_pc", "max"),
        )
        .reset_index()
        .round(3)
        .sort_values(["mean_unmet_need_pc", "geo"], ascending=[False, True])
    )
    summary.to_csv(OUTPUTS_DIR / "primary_country_summary.csv", index=False)
    return summary


def save_latest_ranking(outcome: pd.DataFrame) -> pd.DataFrame:
    latest_rows = outcome.sort_values(["geo", "year"]).groupby("geo", as_index=False).tail(1)
    latest_rows = latest_rows[["geo", "year", "unmet_need_pc"]].sort_values(
        ["unmet_need_pc", "geo"],
        ascending=[False, True],
    )
    latest_rows.to_csv(OUTPUTS_DIR / "primary_latest_available_ranking.csv", index=False)
    return latest_rows


def save_primary_figures(outcome: pd.DataFrame, year_summary: pd.DataFrame, latest: pd.DataFrame) -> None:
    sns.set_theme(style="whitegrid")

    plt.figure(figsize=(10, 5.5))
    plt.plot(year_summary["year"], year_summary["mean_unmet_need_pc"], marker="o", label="Mean")
    plt.plot(year_summary["year"], year_summary["median_unmet_need_pc"], marker="o", label="Median")
    plt.fill_between(
        year_summary["year"],
        year_summary["p25_unmet_need_pc"],
        year_summary["p75_unmet_need_pc"],
        color="#8bb6d9",
        alpha=0.25,
        label="Middle half of countries",
    )
    plt.xlabel("Year")
    plt.ylabel("Unmet medical needs (%)")
    plt.title("Primary outcome across observed countries")
    plt.legend(frameon=False)
    plt.tight_layout()
    plt.savefig(OUTPUTS_DIR / "primary_year_trend.png", dpi=180)
    plt.close()

    plot_latest = latest.sort_values("unmet_need_pc", ascending=True)
    plt.figure(figsize=(8, max(7, 0.23 * len(plot_latest))))
    plt.barh(plot_latest["geo"], plot_latest["unmet_need_pc"], color="#2364aa")
    plt.xlabel("Unmet medical needs (%)")
    plt.ylabel("Country code")
    plt.title("Latest available primary outcome by country")
    plt.tight_layout()
    plt.savefig(OUTPUTS_DIR / "primary_latest_available_ranking.png", dpi=180)
    plt.close()

    dense_countries = (
        outcome.groupby("geo")["year"]
        .nunique()
        .loc[lambda values: values >= 16]
        .index
        .tolist()
    )
    dense = outcome[outcome["geo"].isin(dense_countries)].copy()
    plt.figure(figsize=(11, 6.5))
    sns.lineplot(
        data=dense,
        x="year",
        y="unmet_need_pc",
        hue="geo",
        legend=False,
        linewidth=1,
        alpha=0.55,
    )
    plt.xlabel("Year")
    plt.ylabel("Unmet medical needs (%)")
    plt.title("Country paths with at least 16 observed years")
    plt.tight_layout()
    plt.savefig(OUTPUTS_DIR / "primary_country_paths_dense.png", dpi=180)
    plt.close()


def save_robustness_outputs(outcome: pd.DataFrame, outcome_08b: pd.DataFrame) -> pd.DataFrame:
    comparison = outcome.merge(outcome_08b, on=["geo", "year"], how="inner", suffixes=("_08", "_08b"))
    comparison["difference_08b_minus_08"] = comparison["unmet_need_08b_pc"] - comparison["unmet_need_pc"]
    comparison = comparison[
        ["geo", "year", "unmet_need_pc", "unmet_need_08b_pc", "difference_08b_minus_08"]
    ].sort_values(["geo", "year"])
    comparison.to_csv(OUTPUTS_DIR / "primary_vs_08b_common_cells.csv", index=False)

    summary = (
        comparison.groupby("year")
        .agg(
            countries=("geo", "nunique"),
            mean_primary_pc=("unmet_need_pc", "mean"),
            mean_08b_pc=("unmet_need_08b_pc", "mean"),
            mean_difference_08b_minus_08=("difference_08b_minus_08", "mean"),
            median_difference_08b_minus_08=("difference_08b_minus_08", "median"),
        )
        .reset_index()
        .round(3)
    )
    summary.to_csv(OUTPUTS_DIR / "primary_vs_08b_year_summary.csv", index=False)

    plt.figure(figsize=(7, 5.5))
    sns.scatterplot(
        data=comparison,
        x="unmet_need_pc",
        y="unmet_need_08b_pc",
        hue="year",
        palette="viridis",
        s=42,
    )
    axis_max = max(comparison["unmet_need_pc"].max(), comparison["unmet_need_08b_pc"].max())
    plt.plot([0, axis_max], [0, axis_max], color="#444444", linewidth=1, linestyle=":")
    plt.xlabel("Primary outcome (%)")
    plt.ylabel("08b robustness outcome (%)")
    plt.title("Common country-year cells, 2021-2025")
    plt.tight_layout()
    plt.savefig(OUTPUTS_DIR / "primary_vs_08b_scatter.png", dpi=180)
    plt.close()

    return comparison


def write_summary(
    outcome: pd.DataFrame,
    year_summary: pd.DataFrame,
    country_summary: pd.DataFrame,
    latest: pd.DataFrame,
    comparison: pd.DataFrame,
) -> None:
    observed_cells = len(outcome)
    countries = outcome["geo"].nunique()
    first_year = int(outcome["year"].min())
    last_year = int(outcome["year"].max())
    highest_latest = latest.head(5)["geo"].tolist()
    lowest_latest = latest.tail(5).sort_values("unmet_need_pc")["geo"].tolist()
    peak_year = year_summary.sort_values("mean_unmet_need_pc", ascending=False).iloc[0]
    lower_mean = country_summary.tail(5).sort_values("mean_unmet_need_pc")["geo"].tolist()
    higher_mean = country_summary.head(5)["geo"].tolist()

    summary = f"""# Descriptive profile summary

Date accessed: 2026-05-14

This section describes the observed national country-year data from Eurostat table `hlth_silc_08`.

The primary outcome file contains {observed_cells} observed country-year cells for {countries} national country codes from {first_year} to {last_year}. EU and euro-area aggregate codes are not included.

The year with the highest observed cross-country mean is {int(peak_year['year'])}, with a mean of {peak_year['mean_unmet_need_pc']:.2f} percent. This comparison uses the countries observed in each year, so it should be read together with the missingness tables.

The five countries with the highest mean observed values are: {", ".join(higher_mean)}. The five countries with the lowest mean observed values are: {", ".join(lower_mean)}.

The five highest latest available country values are: {", ".join(highest_latest)}. The five lowest latest available country values are: {", ".join(lowest_latest)}.

The robustness comparison uses {len(comparison)} common country-year cells where both `hlth_silc_08` and `hlth_silc_08b` are observed from 2021 to 2025. These indicators have different denominator definitions, so the table is a descriptive comparison only.

Files produced in this step include `outputs/primary_year_summary.csv`, `outputs/primary_country_summary.csv`, `outputs/primary_latest_available_ranking.csv`, `outputs/primary_year_trend.png`, `outputs/primary_latest_available_ranking.png`, `outputs/primary_country_paths_dense.png`, `outputs/primary_vs_08b_common_cells.csv`, `outputs/primary_vs_08b_year_summary.csv`, and `outputs/primary_vs_08b_scatter.png`.
"""
    (OUTPUTS_DIR / "descriptive_profile_summary.md").write_text(summary, encoding="utf-8")


def main() -> None:
    outcome = pd.read_csv(PROCESSED_DIR / "country_year_outcome.csv")
    outcome_08b = pd.read_csv(PROCESSED_DIR / "country_year_outcome_08b.csv")

    year_summary = save_year_summary(outcome)
    country_summary = save_country_summary(outcome)
    latest = save_latest_ranking(outcome)
    save_primary_figures(outcome, year_summary, latest)
    comparison = save_robustness_outputs(outcome, outcome_08b)
    write_summary(outcome, year_summary, country_summary, latest, comparison)

    print(f"saved {OUTPUTS_DIR / 'descriptive_profile_summary.md'}")
    print(f"primary rows: {len(outcome)}")
    print(f"08b common rows: {len(comparison)}")


if __name__ == "__main__":
    main()
