from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "processed" / "country_year_outcome.csv"
OUT = ROOT / "figures" / "descriptive_country_year_heatmap.pdf"


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(DATA)
    order = (
        df.groupby("geo")["unmet_need_pc"]
        .mean()
        .sort_values(ascending=False)
        .index
        .tolist()
    )
    heat = df.pivot(index="geo", columns="year", values="unmet_need_pc").reindex(order)

    sns.set_theme(style="white", context="paper", font_scale=0.95)
    fig, ax = plt.subplots(figsize=(9.0, 8.4), dpi=300)
    sns.heatmap(
        heat,
        ax=ax,
        cmap="viridis",
        linewidths=0.15,
        linecolor="white",
        cbar_kws={"label": "Unmet medical care need (%)", "shrink": 0.72},
        mask=heat.isna(),
    )
    ax.set_xlabel("Year")
    ax.set_ylabel("Country code")
    ax.set_title("Country-year pattern of unmet medical care need")
    ax.tick_params(axis="x", rotation=45)
    ax.tick_params(axis="y", rotation=0)
    fig.tight_layout()
    fig.savefig(OUT, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
