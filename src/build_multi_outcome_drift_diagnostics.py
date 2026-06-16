from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from eurodrift.balance import included_excluded_balance
from eurodrift.coverage import attrition_waterfall
from eurodrift.targets import country_group


ROOT = Path(__file__).resolve().parents[1]
DATA_PROCESSED = ROOT / "data" / "processed"
OUTPUTS = ROOT / "outputs"
FIGURES = ROOT / "figures"
TABLES = ROOT / "tables"

OUTCOME_VALUE = "outcome_value_pc"
BASELINE_COVARS = [
    "log_gdp_per_capita",
    "unemployment_rate_pc",
    "poverty_or_social_exclusion_pc",
    "government_health_expenditure_gdp_pc",
    "compulsory_health_financing_gdp_pc",
]
CAPACITY_COVARS = ["physicians_per_100k", "hospital_beds_per_100k"]
SMD_VARS = [
    OUTCOME_VALUE,
    "log_gdp_per_capita",
    "unemployment_rate_pc",
    "poverty_or_social_exclusion_pc",
    "government_health_expenditure_gdp_pc",
    "compulsory_health_financing_gdp_pc",
    "physicians_per_100k",
    "hospital_beds_per_100k",
]

STEP_SPECS = [
    ("Outcome observed", [OUTCOME_VALUE]),
    ("+ population weight", [OUTCOME_VALUE, "population_weight_year_norm"]),
    ("+ GDP", [OUTCOME_VALUE, "log_gdp_per_capita"]),
    ("+ unemployment", [OUTCOME_VALUE, "log_gdp_per_capita", "unemployment_rate_pc"]),
    (
        "+ poverty/social exclusion",
        [
            OUTCOME_VALUE,
            "log_gdp_per_capita",
            "unemployment_rate_pc",
            "poverty_or_social_exclusion_pc",
        ],
    ),
    (
        "Baseline complete case",
        [OUTCOME_VALUE] + BASELINE_COVARS,
    ),
    (
        "+ capacity sensitivity",
        [OUTCOME_VALUE] + BASELINE_COVARS + CAPACITY_COVARS,
    ),
]

LABELS = {
    "medical_population_combined": "Medical population",
    "medical_need_combined": "Medical need",
    "dental_population_combined": "Dental population",
    "dental_need_combined": "Dental need",
    "medical_population_cost": "Medical cost",
    "medical_population_waiting": "Medical waiting",
    "medical_population_distance": "Medical distance",
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


def _write_tabular(df: pd.DataFrame, columns: list[str], headers: list[str], path: Path, colspec: str) -> None:
    lines = [rf"\begin{{tabular}}{{{colspec}}}", r"\toprule", " & ".join(headers) + r" \\", r"\midrule"]
    for _, row in df[columns].iterrows():
        lines.append(" & ".join(_latex_escape(row[column]) for column in columns) + r" \\")
    lines.extend([r"\bottomrule", r"\end{tabular}", ""])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def load_multi_outcome_panel() -> pd.DataFrame:
    outcomes = pd.read_csv(DATA_PROCESSED / "multi_outcome_unmet_care.csv")
    features = pd.read_csv(DATA_PROCESSED / "panel_features_v2-3.csv").drop(columns=["unmet_need_pc", "status"], errors="ignore")
    panel = outcomes.rename(columns={"value_pc": OUTCOME_VALUE}).merge(features, on=["geo", "year"], how="left")
    panel["country_group"] = panel["geo"].map(country_group)
    panel["indicator_label"] = panel["indicator_id"].map(LABELS).fillna(panel["indicator_id"])
    return panel


def build_attrition_outputs(panel: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    step_rows = []
    for indicator_id, group in panel.groupby("indicator_id", sort=True):
        waterfall = attrition_waterfall(group, STEP_SPECS)
        waterfall.insert(0, "indicator_id", indicator_id)
        waterfall.insert(1, "indicator_label", LABELS.get(indicator_id, indicator_id))
        step_rows.append(waterfall)
        wide = {"indicator_id": indicator_id, "indicator_label": LABELS.get(indicator_id, indicator_id)}
        for _, row in waterfall.iterrows():
            step_key = str(row["step"]).lower().replace("+ ", "").replace(" ", "_").replace("/", "_")
            wide[f"{step_key}_rows"] = int(row["rows"])
            wide[f"{step_key}_countries"] = int(row["countries"])
            wide[f"{step_key}_years"] = int(row["years"])
        rows.append(wide)
    long = pd.concat(step_rows, ignore_index=True)
    matrix = pd.DataFrame(rows).sort_values("indicator_id")
    long.to_csv(OUTPUTS / "multi_outcome_attrition_long.csv", index=False)
    matrix.to_csv(OUTPUTS / "multi_outcome_attrition_matrix.csv", index=False)
    return long, matrix


def build_country_group_retention(panel: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (indicator_id, country_group_label), group in panel.groupby(["indicator_id", "country_group"], sort=True):
        complete = group[[OUTCOME_VALUE] + BASELINE_COVARS].notna().all(axis=1)
        rows.append(
            {
                "indicator_id": indicator_id,
                "indicator_label": LABELS.get(indicator_id, indicator_id),
                "country_group": country_group_label,
                "outcome_rows": int(len(group)),
                "complete_case_rows": int(complete.sum()),
                "countries_observed": int(group["geo"].nunique()),
                "countries_complete_case": int(group.loc[complete, "geo"].nunique()),
                "row_retention_pct": round(float(100 * complete.mean()), 1) if len(group) else 0.0,
            }
        )
    out = pd.DataFrame(rows)
    out.to_csv(OUTPUTS / "multi_outcome_country_group_retention.csv", index=False)
    return out


def build_included_excluded_smds(panel: pd.DataFrame) -> pd.DataFrame:
    frames = []
    for indicator_id, group in panel.groupby("indicator_id", sort=True):
        complete = group[[OUTCOME_VALUE] + BASELINE_COVARS].notna().all(axis=1)
        balance = included_excluded_balance(group, complete, SMD_VARS)
        balance.insert(0, "indicator_id", indicator_id)
        balance.insert(1, "indicator_label", LABELS.get(indicator_id, indicator_id))
        balance["complete_case_rows"] = int(complete.sum())
        balance["excluded_rows"] = int((~complete).sum())
        frames.append(balance)
    out = pd.concat(frames, ignore_index=True)
    out.to_csv(OUTPUTS / "multi_outcome_included_excluded_smd.csv", index=False)
    return out


def write_tables(matrix: pd.DataFrame, retention: pd.DataFrame, smd: pd.DataFrame) -> None:
    display = matrix[
        [
            "indicator_label",
            "outcome_observed_rows",
            "population_weight_rows",
            "gdp_rows",
            "unemployment_rows",
            "poverty_social_exclusion_rows",
            "baseline_complete_case_rows",
            "capacity_sensitivity_rows",
        ]
    ].copy()
    _write_tabular(
        display,
        display.columns.tolist(),
        ["Indicator", "Outcome", "Pop.", "GDP", "Unemp.", "Poverty", "Baseline CC", "Capacity"],
        TABLES / "multi_outcome_attrition_matrix.tex",
        r"p{0.24\linewidth}rrrrrrr",
    )

    primary = pd.read_csv(OUTPUTS / "multi_outcome_attrition_long.csv")
    primary = primary[primary["indicator_id"].eq("medical_population_combined")].copy()
    _write_tabular(
        primary,
        ["step", "rows", "countries", "years", "rows_lost_from_previous", "retained_pct_of_start"],
        ["Step", "Rows", "Countries", "Years", "Lost", "Retained pct"],
        TABLES / "multi_outcome_primary_attrition_waterfall.tex",
        r"p{0.30\linewidth}rrrrr",
    )

    top_smd = (
        smd.dropna(subset=["smd"])
        .assign(abs_smd=lambda df: df["smd"].abs())
        .sort_values(["indicator_id", "abs_smd"], ascending=[True, False])
        .groupby("indicator_id", as_index=False)
        .head(2)
        .copy()
    )
    for column in ["included_mean", "excluded_mean", "smd"]:
        top_smd[column] = top_smd[column].round(3)
    _write_tabular(
        top_smd,
        ["indicator_label", "variable", "included_n", "excluded_n", "included_mean", "excluded_mean", "smd"],
        ["Indicator", "Variable", "In N", "Excl. N", "In mean", "Excl. mean", "SMD"],
        TABLES / "multi_outcome_included_excluded_smd_top.tex",
        r"p{0.20\linewidth}p{0.21\linewidth}rrrrr",
    )

    retention_display = retention.copy()
    _write_tabular(
        retention_display,
        [
            "indicator_label",
            "country_group",
            "outcome_rows",
            "complete_case_rows",
            "countries_observed",
            "countries_complete_case",
            "row_retention_pct",
        ],
        ["Indicator", "Group", "Outcome rows", "CC rows", "Countries", "CC countries", "Ret. pct"],
        TABLES / "multi_outcome_country_group_retention.tex",
        r"p{0.20\linewidth}p{0.18\linewidth}rrrrr",
    )


def save_retention_heatmap(long: pd.DataFrame) -> None:
    heat = long.pivot(index="indicator_label", columns="step", values="retained_pct_of_start")
    ordered_cols = [step for step, _ in STEP_SPECS if step in heat.columns]
    heat = heat[ordered_cols].sort_index()
    plt.figure(figsize=(10.5, 4.8))
    sns.heatmap(heat, annot=True, fmt=".1f", cmap="Blues", cbar_kws={"label": "Retained % of outcome rows"})
    plt.xlabel("Sequential requirement")
    plt.ylabel("Indicator")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    FIGURES.mkdir(parents=True, exist_ok=True)
    plt.savefig(FIGURES / "multi_outcome_retention_heatmap.pdf")
    plt.savefig(FIGURES / "multi_outcome_retention_heatmap.png", dpi=180)
    plt.close()


def save_primary_waterfall(long: pd.DataFrame) -> None:
    primary = long[long["indicator_id"].eq("medical_population_combined")].copy()
    fig, ax = plt.subplots(figsize=(9.8, 5.0))
    colors = ["#0072B2"] + ["#56B4E9"] * (len(primary) - 2) + ["#D55E00"]
    ax.bar(range(len(primary)), primary["rows"], color=colors, edgecolor="white", linewidth=0.8)
    for i, row in primary.reset_index(drop=True).iterrows():
        lost = int(row["rows_lost_from_previous"])
        label = f"{int(row['rows'])}"
        if i > 0:
            label += f"\n-{lost}"
        ax.text(i, row["rows"] + primary["rows"].max() * 0.025, label, ha="center", va="bottom", fontsize=8)
    ax.set_xticks(range(len(primary)))
    ax.set_xticklabels(primary["step"], rotation=25, ha="right")
    ax.set_ylabel("Country-years retained")
    ax.set_ylim(0, primary["rows"].max() * 1.16)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIGURES / "multi_outcome_primary_attrition_waterfall.pdf")
    plt.close(fig)


def main() -> None:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    TABLES.mkdir(parents=True, exist_ok=True)

    panel = load_multi_outcome_panel()
    long, matrix = build_attrition_outputs(panel)
    retention = build_country_group_retention(panel)
    smd = build_included_excluded_smds(panel)
    write_tables(matrix, retention, smd)
    save_retention_heatmap(long)
    save_primary_waterfall(long)

    primary = matrix[matrix["indicator_id"].eq("medical_population_combined")].iloc[0]
    print(f"saved {OUTPUTS / 'multi_outcome_attrition_matrix.csv'}")
    print(f"saved {FIGURES / 'multi_outcome_retention_heatmap.pdf'}")
    print(
        "primary drift: "
        f"{int(primary['outcome_observed_rows'])} outcome rows -> "
        f"{int(primary['baseline_complete_case_rows'])} baseline complete-case rows"
    )


if __name__ == "__main__":
    main()
