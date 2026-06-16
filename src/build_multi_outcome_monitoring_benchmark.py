from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


ROOT = Path(__file__).resolve().parents[1]
DATA_PROCESSED = ROOT / "data" / "processed"
OUTPUTS = ROOT / "outputs"
FIGURES = ROOT / "figures"
TABLES = ROOT / "tables"

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

LABELS = {
    "medical_population_combined": "Medical, population denominator",
    "medical_need_combined": "Medical, need denominator",
    "dental_population_combined": "Dental, population denominator",
    "dental_need_combined": "Dental, need denominator",
    "medical_population_cost": "Medical, cost",
    "medical_population_waiting": "Medical, waiting",
    "medical_population_distance": "Medical, distance",
}


def _latex_escape(value: object) -> str:
    text = "" if pd.isna(value) else str(value)
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def _write_latex_table(
    df: pd.DataFrame,
    columns: list[str],
    headers: list[str],
    path: Path,
    colspec: str,
) -> None:
    lines = [
        rf"\begin{{tabular}}{{{colspec}}}",
        r"\toprule",
        " & ".join(headers) + r" \\",
        r"\midrule",
    ]
    for _, row in df[columns].iterrows():
        values = [_latex_escape(row[column]) for column in columns]
        lines.append(" & ".join(values) + r" \\")
    lines.extend([r"\bottomrule", r"\end{tabular}", ""])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def load_monitoring_panel() -> pd.DataFrame:
    panel = pd.read_csv(DATA_PROCESSED / "multi_outcome_unmet_care.csv")
    population = pd.read_csv(DATA_PROCESSED / "feature_population_total.csv")
    panel = panel.merge(population[["geo", "year", "population_total"]], on=["geo", "year"], how="left")
    panel["universe"] = "Full Eurostat-available"
    eu_panel = panel[panel["geo"].isin(EU27)].copy()
    eu_panel["universe"] = "EU-27"
    return pd.concat([panel, eu_panel], ignore_index=True)


def add_year_normalized_weights(panel: pd.DataFrame) -> pd.DataFrame:
    panel = panel.copy()
    group_cols = ["indicator_id", "universe", "year"]
    denominators = panel.groupby(group_cols)["population_total"].transform("sum")
    panel["population_weight_year_norm"] = panel["population_total"] / denominators
    panel.loc[panel["population_total"].isna() | (denominators <= 0), "population_weight_year_norm"] = pd.NA
    return panel


def save_weight_file(panel: pd.DataFrame) -> pd.DataFrame:
    weights = panel[
        [
            "indicator_id",
            "universe",
            "geo",
            "year",
            "population_total",
            "population_weight_year_norm",
        ]
    ].copy()
    weights.to_csv(OUTPUTS / "multi_outcome_year_normalized_weights.csv", index=False)
    return weights


def build_trends(panel: pd.DataFrame) -> pd.DataFrame:
    records: list[dict[str, object]] = []
    for keys, group in panel.groupby(["indicator_id", "dataset_code", "care_type", "barrier_type", "denominator", "universe", "year"]):
        indicator_id, dataset_code, care_type, barrier_type, denominator, universe, year = keys
        weighted_group = group.dropna(subset=["population_weight_year_norm", "value_pc"])
        weighted_mean = (
            (weighted_group["value_pc"] * weighted_group["population_weight_year_norm"]).sum()
            if not weighted_group.empty
            else pd.NA
        )
        records.append(
            {
                "indicator_id": indicator_id,
                "indicator_label": LABELS.get(indicator_id, indicator_id),
                "dataset_code": dataset_code,
                "care_type": care_type,
                "barrier_type": barrier_type,
                "denominator": denominator,
                "universe": universe,
                "year": int(year),
                "countries": int(group["geo"].nunique()),
                "unweighted_mean_pc": round(float(group["value_pc"].mean()), 3),
                "population_weighted_mean_pc": round(float(weighted_mean), 3) if pd.notna(weighted_mean) else pd.NA,
                "population_weighted_countries": int(weighted_group["geo"].nunique()),
            }
        )
    trends = pd.DataFrame(records).sort_values(["indicator_id", "universe", "year"])
    trends.to_csv(OUTPUTS / "multi_outcome_monitoring_trends.csv", index=False)
    return trends


def build_coverage_table(panel: pd.DataFrame) -> pd.DataFrame:
    full = panel[panel["universe"] == "Full Eurostat-available"].copy()
    coverage = (
        full.groupby(["indicator_id", "dataset_code", "care_type", "barrier_type", "denominator"], as_index=False)
        .agg(
            country_count=("geo", "nunique"),
            year_min=("year", "min"),
            year_max=("year", "max"),
            observed_rows=("value_pc", "size"),
            population_weight_rows=("population_total", lambda values: int(values.notna().sum())),
        )
        .sort_values(["care_type", "denominator", "barrier_type"])
    )
    coverage["indicator_label"] = coverage["indicator_id"].map(LABELS).fillna(coverage["indicator_id"])
    coverage = coverage[
        [
            "indicator_id",
            "indicator_label",
            "dataset_code",
            "care_type",
            "barrier_type",
            "denominator",
            "year_min",
            "year_max",
            "country_count",
            "observed_rows",
            "population_weight_rows",
        ]
    ]
    coverage.to_csv(OUTPUTS / "multi_outcome_coverage_table.csv", index=False)

    display = coverage.copy()
    display["years"] = display["year_min"].astype(str) + "--" + display["year_max"].astype(str)
    _write_latex_table(
        display,
        [
            "indicator_label",
            "dataset_code",
            "denominator",
            "country_count",
            "observed_rows",
            "population_weight_rows",
            "years",
        ],
        ["Indicator", "Dataset", "Denom.", "Countries", "Rows", "Pop. rows", "Years"],
        TABLES / "multi_outcome_coverage_table.tex",
        r"p{0.28\linewidth}p{0.13\linewidth}p{0.12\linewidth}rrrr",
    )
    return coverage


def build_monitoring_dependence_summary(trends: pd.DataFrame) -> pd.DataFrame:
    latest = trends.sort_values("year").groupby(["indicator_id", "universe"], as_index=False).tail(1)

    def latest_value(indicator_id: str, universe: str, column: str) -> float | None:
        row = latest[(latest["indicator_id"] == indicator_id) & (latest["universe"] == universe)]
        if row.empty or pd.isna(row[column].iloc[0]):
            return None
        return float(row[column].iloc[0])

    records = []
    primary_full = latest_value("medical_population_combined", "Full Eurostat-available", "unweighted_mean_pc")
    primary_weighted = latest_value("medical_population_combined", "Full Eurostat-available", "population_weighted_mean_pc")
    primary_eu = latest_value("medical_population_combined", "EU-27", "unweighted_mean_pc")
    medical_need = latest_value("medical_need_combined", "Full Eurostat-available", "unweighted_mean_pc")
    dental_population = latest_value("dental_population_combined", "Full Eurostat-available", "unweighted_mean_pc")
    cost = latest_value("medical_population_cost", "Full Eurostat-available", "unweighted_mean_pc")
    waiting = latest_value("medical_population_waiting", "Full Eurostat-available", "unweighted_mean_pc")
    distance = latest_value("medical_population_distance", "Full Eurostat-available", "unweighted_mean_pc")

    records.append(
        {
            "comparison": "Unweighted versus resident-weighted primary indicator",
            "latest_year": 2025,
            "first_value_pc": primary_full,
            "second_value_pc": primary_weighted,
            "difference_pc": None if primary_full is None or primary_weighted is None else primary_weighted - primary_full,
            "interpretation": "Population weighting changes the monitoring estimand from average country to average resident.",
        }
    )
    records.append(
        {
            "comparison": "Full Eurostat-available versus EU-27 primary indicator",
            "latest_year": 2025,
            "first_value_pc": primary_full,
            "second_value_pc": primary_eu,
            "difference_pc": None if primary_full is None or primary_eu is None else primary_eu - primary_full,
            "interpretation": "Country-universe restriction changes the set of national units being summarized.",
        }
    )
    records.append(
        {
            "comparison": "Medical population denominator versus medical need denominator",
            "latest_year": 2025,
            "first_value_pc": primary_full,
            "second_value_pc": medical_need,
            "difference_pc": None if primary_full is None or medical_need is None else medical_need - primary_full,
            "interpretation": "Need-denominator indicators answer a narrower question than population-denominator indicators.",
        }
    )
    records.append(
        {
            "comparison": "Medical versus dental population-denominator combined barriers",
            "latest_year": 2025,
            "first_value_pc": primary_full,
            "second_value_pc": dental_population,
            "difference_pc": None if primary_full is None or dental_population is None else dental_population - primary_full,
            "interpretation": "Care type changes the service domain and should not be treated as the same outcome.",
        }
    )
    records.append(
        {
            "comparison": "Medical barrier range: cost, waiting, distance",
            "latest_year": 2025,
            "first_value_pc": min(v for v in [cost, waiting, distance] if v is not None),
            "second_value_pc": max(v for v in [cost, waiting, distance] if v is not None),
            "difference_pc": max(v for v in [cost, waiting, distance] if v is not None)
            - min(v for v in [cost, waiting, distance] if v is not None),
            "interpretation": "Barrier-specific indicators separate affordability, waiting-time, and distance mechanisms.",
        }
    )
    summary = pd.DataFrame(records)
    numeric_cols = ["first_value_pc", "second_value_pc", "difference_pc"]
    summary[numeric_cols] = summary[numeric_cols].round(3)
    summary.to_csv(OUTPUTS / "multi_outcome_monitoring_dependence_summary.csv", index=False)

    _write_latex_table(
        summary,
        ["comparison", "latest_year", "first_value_pc", "second_value_pc", "difference_pc", "interpretation"],
        ["Comparison", "Year", "A", "B", "Diff.", "Interpretation"],
        TABLES / "multi_outcome_monitoring_dependence_summary.tex",
        r"p{0.32\linewidth}rrrrp{0.32\linewidth}",
    )
    return summary


def save_trend_figure(trends: pd.DataFrame) -> None:
    sns.set_theme(style="whitegrid")
    fig, axes = plt.subplots(2, 2, figsize=(13.5, 8.8), sharex=False)

    full = trends[trends["universe"] == "Full Eurostat-available"].copy()
    eu = trends[trends["universe"] == "EU-27"].copy()

    ax = axes[0, 0]
    subset = full[full["indicator_id"].isin(["medical_population_combined", "dental_population_combined"])]
    sns.lineplot(data=subset, x="year", y="unweighted_mean_pc", hue="indicator_label", marker="o", ax=ax)
    ax.set_title("A. Medical versus dental, population denominator")
    ax.set_ylabel("Unweighted mean (%)")
    ax.set_xlabel("")
    ax.legend(title="", fontsize=8)

    ax = axes[0, 1]
    subset = full[
        full["indicator_id"].isin(
            [
                "medical_population_combined",
                "medical_need_combined",
                "dental_population_combined",
                "dental_need_combined",
            ]
        )
    ]
    sns.lineplot(data=subset, x="year", y="unweighted_mean_pc", hue="indicator_label", marker="o", ax=ax)
    ax.set_title("B. Population versus need denominator")
    ax.set_ylabel("Unweighted mean (%)")
    ax.set_xlabel("")
    ax.legend(title="", fontsize=7)

    ax = axes[1, 0]
    subset = full[
        full["indicator_id"].isin(
            [
                "medical_population_combined",
                "medical_population_cost",
                "medical_population_waiting",
                "medical_population_distance",
            ]
        )
    ]
    sns.lineplot(data=subset, x="year", y="unweighted_mean_pc", hue="indicator_label", marker="o", ax=ax)
    ax.set_title("C. Medical barrier-specific indicators")
    ax.set_ylabel("Unweighted mean (%)")
    ax.set_xlabel("Year")
    ax.legend(title="", fontsize=7)

    ax = axes[1, 1]
    primary_full = full[full["indicator_id"] == "medical_population_combined"].copy()
    primary_eu = eu[eu["indicator_id"] == "medical_population_combined"].copy()
    ax.plot(primary_full["year"], primary_full["unweighted_mean_pc"], marker="o", label="Full, unweighted")
    ax.plot(primary_full["year"], primary_full["population_weighted_mean_pc"], marker="o", label="Full, weighted")
    ax.plot(primary_eu["year"], primary_eu["unweighted_mean_pc"], marker="o", label="EU-27, unweighted")
    ax.plot(primary_eu["year"], primary_eu["population_weighted_mean_pc"], marker="o", label="EU-27, weighted")
    ax.set_title("D. Primary indicator by universe and weighting")
    ax.set_ylabel("Mean (%)")
    ax.set_xlabel("Year")
    ax.legend(title="", fontsize=7)

    for ax in axes.flat:
        ax.grid(True, alpha=0.25)

    fig.tight_layout()
    FIGURES.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURES / "multi_outcome_monitoring_benchmark.pdf")
    fig.savefig(FIGURES / "multi_outcome_monitoring_benchmark.png", dpi=180)
    plt.close(fig)


def main() -> None:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    TABLES.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)

    panel = add_year_normalized_weights(load_monitoring_panel())
    save_weight_file(panel)
    trends = build_trends(panel)
    build_coverage_table(panel)
    build_monitoring_dependence_summary(trends)
    save_trend_figure(trends)

    print(f"saved {OUTPUTS / 'multi_outcome_monitoring_trends.csv'}")
    print(f"saved {OUTPUTS / 'multi_outcome_coverage_table.csv'}")
    print(f"saved {OUTPUTS / 'multi_outcome_monitoring_dependence_summary.csv'}")
    print(f"saved {FIGURES / 'multi_outcome_monitoring_benchmark.pdf'}")


if __name__ == "__main__":
    main()
