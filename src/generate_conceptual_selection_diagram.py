from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "figures"
FIGURES.mkdir(parents=True, exist_ok=True)


def box(ax, xy, width, height, text, facecolor="#f8f8f8", edgecolor="#303030"):
    patch = FancyBboxPatch(
        xy,
        width,
        height,
        boxstyle="round,pad=0.018,rounding_size=0.025",
        linewidth=1.8,
        edgecolor=edgecolor,
        facecolor=facecolor,
    )
    ax.add_patch(patch)
    ax.text(
        xy[0] + width / 2,
        xy[1] + height / 2,
        text,
        ha="center",
        va="center",
        fontsize=9.2,
        linespacing=1.15,
    )


def arrow(ax, start, end, color="#303030", style="-|>"):
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle=style,
            mutation_scale=11,
            linewidth=1.5,
            color=color,
            shrinkA=4,
            shrinkB=4,
        )
    )


def main() -> None:
    fig, ax = plt.subplots(figsize=(10.2, 5.2))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    box(ax, (0.04, 0.70), 0.25, 0.15, "Social vulnerability\npoverty, unemployment,\ninequality", "#dbeafe")
    box(ax, (0.04, 0.44), 0.25, 0.15, "Macroeconomic\ncontext\nGDP, labour market", "#dbeafe")
    box(ax, (0.04, 0.18), 0.25, 0.15, "Health-system\nproxies\nfinancing, OOP,\nphysicians, beds", "#dbeafe")

    box(ax, (0.37, 0.64), 0.26, 0.17, "Observed aggregate\nunmet medical care need\nhlth_silc_08", "#fef3c7")
    box(ax, (0.37, 0.34), 0.26, 0.17, "Missing covariate\navailability\ncountry-year coverage", "#fee2e2")
    box(ax, (0.37, 0.08), 0.26, 0.15, "Country and year\nstructure\ninstitutions, shocks,\nmeasurement periods", "#e5e7eb")

    box(ax, (0.72, 0.52), 0.23, 0.16, "Complete-case\ninclusion\nselected analytical panel", "#fee2e2")
    box(ax, (0.72, 0.25), 0.23, 0.17, "Estimated coefficient\nchanges with target,\nweights, selection,\nand imputation", "#dcfce7")

    for y in [0.775, 0.515, 0.255]:
        arrow(ax, (0.29, y), (0.37, 0.715 if y > 0.6 else 0.425 if y > 0.35 else 0.17))
    arrow(ax, (0.50, 0.64), (0.50, 0.51))
    arrow(ax, (0.63, 0.425), (0.72, 0.60))
    arrow(ax, (0.63, 0.17), (0.72, 0.60))
    arrow(ax, (0.83, 0.52), (0.83, 0.42))
    arrow(ax, (0.50, 0.64), (0.72, 0.34))

    fig.tight_layout(pad=0.2)
    fig.savefig(
        FIGURES / "conceptual_selection_estimand_diagram.pdf",
        dpi=300,
        bbox_inches="tight",
        pad_inches=0.03,
    )


if __name__ == "__main__":
    main()
