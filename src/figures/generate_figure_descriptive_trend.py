from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "outputs" / "primary_year_summary.csv"
OUT = ROOT / "figures" / "descriptive_trend_europe.pdf"


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(DATA).sort_values("year")

    sns.set_theme(style="white", context="paper", font_scale=1.1)
    palette = sns.color_palette("colorblind")

    fig, ax = plt.subplots(figsize=(7.2, 4.2), dpi=300)
    ax.fill_between(
        df["year"].to_numpy(),
        df["p25_unmet_need_pc"].to_numpy(),
        df["p75_unmet_need_pc"].to_numpy(),
        color=palette[0],
        alpha=0.16,
        linewidth=0,
        label="Interquartile range",
    )
    ax.plot(
        df["year"],
        df["mean_unmet_need_pc"],
        color=palette[0],
        linewidth=2.2,
        marker="o",
        markersize=3.8,
        label="Cross-country mean",
    )
    ax.plot(
        df["year"],
        df["median_unmet_need_pc"],
        color=palette[1],
        linewidth=1.8,
        marker="s",
        markersize=3.2,
        label="Cross-country median",
    )

    ax.axvspan(2008, 2013, color="0.85", alpha=0.25, linewidth=0)
    ax.axvspan(2020, 2021, color="0.75", alpha=0.18, linewidth=0)
    ax.text(2010.5, ax.get_ylim()[1] * 0.95, "Great Recession\ncontext", ha="center", va="top", fontsize=8, color="0.35")
    ax.text(2020.5, ax.get_ylim()[1] * 0.95, "COVID-19\ncontext", ha="center", va="top", fontsize=8, color="0.35")

    ax.set_xlabel("Year")
    ax.set_ylabel("Unmet medical care need (%)")
    ax.set_title("National unmet medical care need in Europe, 2008--2025")
    ax.set_xticks(df["year"])
    ax.tick_params(axis="x", rotation=45)
    ax.legend(frameon=False, loc="upper right")
    sns.despine(ax=ax)
    fig.tight_layout()
    fig.savefig(OUT, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
