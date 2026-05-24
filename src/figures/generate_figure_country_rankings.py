from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "outputs" / "primary_latest_available_ranking.csv"
OUT = ROOT / "figures" / "descriptive_country_rankings_latest.pdf"


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(DATA).sort_values("unmet_need_pc", ascending=True)

    sns.set_theme(style="white", context="paper", font_scale=1.0)
    palette = sns.color_palette("colorblind", n_colors=3)
    colors = [
        palette[2] if value >= df["unmet_need_pc"].quantile(0.75)
        else palette[0] if value <= df["unmet_need_pc"].quantile(0.25)
        else "0.62"
        for value in df["unmet_need_pc"]
    ]

    fig, ax = plt.subplots(figsize=(7.2, 8.4), dpi=300)
    ax.barh(df["geo"], df["unmet_need_pc"], color=colors, edgecolor="white", linewidth=0.4)

    for y, (_, row) in enumerate(df.iterrows()):
        ax.text(
            row["unmet_need_pc"] + 0.12,
            y,
            f"{row['unmet_need_pc']:.1f}",
            va="center",
            fontsize=7.5,
            color="0.25",
        )

    ax.set_xlabel("Unmet medical care need (%)")
    ax.set_ylabel("Country code")
    ax.set_title("Latest available national values")
    ax.set_xlim(0, max(df["unmet_need_pc"]) + 1.4)
    ax.text(
        0,
        -1.3,
        "Values use each country's latest observed year in the processed 2008--2025 panel.",
        fontsize=8,
        color="0.35",
    )
    sns.despine(ax=ax, left=True)
    fig.tight_layout()
    fig.savefig(OUT, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
