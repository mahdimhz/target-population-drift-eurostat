from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / "outputs" / "tree_feature_importance.csv"
OUTPUT = ROOT / "figures" / "ml_tree_feature_importance.pdf"


LABELS = {
    "physicians_per_100k": "Physicians per 100,000",
    "gini_income": "Gini coefficient",
    "poverty_or_social_exclusion_pc": "Poverty or social exclusion",
    "long_term_unemployment_rate_pc": "Long-term unemployment",
    "hospital_beds_per_100k": "Hospital beds per 100,000",
    "unemployment_rate_pc": "Unemployment rate",
    "compulsory_health_financing_gdp_pc": "Compulsory health financing",
    "gdp_per_capita_eur": "GDP per capita",
    "physicians_per_100k_lag1": "Physicians per 100,000, lag 1",
    "oop_health_expenditure_share_pc": "Out-of-pocket spending share",
    "government_health_expenditure_gdp_pc": "Government health expenditure",
    "gdp_per_capita_growth": "GDP per capita growth",
    "unemployment_rate_change": "Unemployment-rate change",
    "log_gdp_per_capita": "Log GDP per capita",
}


def main() -> None:
    df = pd.read_csv(INPUT)
    df["label"] = df["feature"].map(LABELS).fillna(df["feature"])
    df = df.sort_values("importance", ascending=True)

    sns.set_theme(style="white", context="paper", font_scale=1.0)
    palette = sns.color_palette("colorblind", n_colors=1)

    fig, ax = plt.subplots(figsize=(7.2, 5.6))
    ax.barh(df["label"], df["importance"], color=palette[0])
    ax.set_xlabel("Feature importance")
    ax.set_ylabel("")
    ax.set_title("Tree-model feature importance")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x", color="#dddddd", linewidth=0.6)
    ax.set_axisbelow(True)

    fig.tight_layout()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT, dpi=300, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
