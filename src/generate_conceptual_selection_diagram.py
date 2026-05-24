from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "figures"
FIGURES.mkdir(parents=True, exist_ok=True)


def box(ax, xy, width, height, text, facecolor="#f8f8f8", edgecolor="#4c4c4c"):
    patch = FancyBboxPatch(
        xy,
        width,
        height,
        boxstyle="round,pad=0.018,rounding_size=0.025",
        linewidth=1.1,
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
        fontsize=8.5,
        linespacing=1.15,
    )


def arrow(ax, start, end, color="#565656", style="-|>"):
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle=style,
            mutation_scale=11,
            linewidth=1.0,
            color=color,
            shrinkA=4,
            shrinkB=4,
        )
    )


def main() -> None:
    fig, ax = plt.subplots(figsize=(9.2, 5.6))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    box(ax, (0.05, 0.70), 0.23, 0.15, "Social vulnerability\npoverty, unemployment,\ninequality", "#edf4fb")
    box(ax, (0.05, 0.44), 0.23, 0.15, "Macroeconomic\ncontext\nGDP, labour market", "#edf4fb")
    box(ax, (0.05, 0.18), 0.23, 0.15, "Health-system\nproxies\nfinancing, OOP,\nphysicians, beds", "#edf4fb")

    box(ax, (0.38, 0.64), 0.24, 0.17, "Observed aggregate\nunmet medical care need\nhlth_silc_08", "#f5f1e8")
    box(ax, (0.38, 0.34), 0.24, 0.17, "Missing covariate\navailability\ncountry-year coverage", "#fff2f0")
    box(ax, (0.38, 0.08), 0.24, 0.15, "Country and year\nstructure\ninstitutions, shocks,\nmeasurement periods", "#f4f4f4")

    box(ax, (0.72, 0.52), 0.22, 0.16, "Complete-case\ninclusion\nselected analytical panel", "#fff2f0")
    box(ax, (0.72, 0.25), 0.22, 0.17, "Estimated coefficient\nchanges with target,\nweights, selection,\nand imputation", "#edf8f0")

    for y in [0.775, 0.515, 0.255]:
        arrow(ax, (0.28, y), (0.38, 0.715 if y > 0.6 else 0.425 if y > 0.35 else 0.17))
    arrow(ax, (0.50, 0.64), (0.50, 0.51))
    arrow(ax, (0.62, 0.425), (0.72, 0.60))
    arrow(ax, (0.62, 0.17), (0.72, 0.60))
    arrow(ax, (0.83, 0.52), (0.83, 0.42))
    arrow(ax, (0.50, 0.64), (0.72, 0.34))

    ax.text(
        0.5,
        0.95,
        "Conceptual selection and estimand diagram for aggregate Eurostat monitoring",
        ha="center",
        va="center",
        fontsize=11,
        fontweight="bold",
    )
    ax.text(
        0.5,
        0.015,
        "The diagram organizes non-causal assumptions: missing covariate availability changes the analysis population, so the coefficient is an estimand-dependent summary.",
        ha="center",
        va="center",
        fontsize=8.2,
    )
    fig.tight_layout()
    fig.savefig(FIGURES / "conceptual_selection_estimand_diagram.pdf", dpi=300)


if __name__ == "__main__":
    main()
