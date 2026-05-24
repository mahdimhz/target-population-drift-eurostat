from __future__ import annotations

from pathlib import Path

import nbformat as nbf


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    notebook = nbf.v4.new_notebook()
    notebook["metadata"] = {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {
            "name": "python",
            "pygments_lexer": "ipython3",
        },
    }
    notebook["cells"] = [
        nbf.v4.new_markdown_cell(
            "# Descriptive profile\n\n"
            "This section describes the observed national country-year values for the primary Eurostat outcome."
        ),
        nbf.v4.new_code_cell(
            "from pathlib import Path\n\n"
            "import matplotlib.pyplot as plt\n"
            "import pandas as pd\n"
            "import seaborn as sns\n\n"
            "PROJECT_ROOT = Path.cwd().parent if Path.cwd().name == 'notebooks' else Path.cwd()\n"
            "outputs_dir = PROJECT_ROOT / 'outputs'\n"
            "processed_dir = PROJECT_ROOT / 'data' / 'processed'\n\n"
            "outcome = pd.read_csv(processed_dir / 'country_year_outcome.csv')\n"
            "outcome_08b = pd.read_csv(processed_dir / 'country_year_outcome_08b.csv')\n"
            "outcome.head()"
        ),
        nbf.v4.new_code_cell(
            "year_summary = pd.read_csv(outputs_dir / 'primary_year_summary.csv')\n"
            "country_summary = pd.read_csv(outputs_dir / 'primary_country_summary.csv')\n"
            "latest = pd.read_csv(outputs_dir / 'primary_latest_available_ranking.csv')\n"
            "year_summary"
        ),
        nbf.v4.new_code_cell(
            "country_summary.head(10)"
        ),
        nbf.v4.new_code_cell(
            "latest.head(10)"
        ),
        nbf.v4.new_code_cell(
            "sns.set_theme(style='whitegrid')\n"
            "plt.figure(figsize=(10, 5.5))\n"
            "plt.plot(year_summary['year'], year_summary['mean_unmet_need_pc'], marker='o', label='Mean')\n"
            "plt.plot(year_summary['year'], year_summary['median_unmet_need_pc'], marker='o', label='Median')\n"
            "plt.fill_between(\n"
            "    year_summary['year'],\n"
            "    year_summary['p25_unmet_need_pc'],\n"
            "    year_summary['p75_unmet_need_pc'],\n"
            "    color='#8bb6d9',\n"
            "    alpha=0.25,\n"
            "    label='Middle half of countries',\n"
            ")\n"
            "plt.xlabel('Year')\n"
            "plt.ylabel('Unmet medical needs (%)')\n"
            "plt.title('Primary outcome across observed countries')\n"
            "plt.legend(frameon=False)\n"
            "plt.tight_layout()\n"
            "plt.show()"
        ),
        nbf.v4.new_code_cell(
            "comparison = pd.read_csv(outputs_dir / 'primary_vs_08b_common_cells.csv')\n"
            "comparison_summary = pd.read_csv(outputs_dir / 'primary_vs_08b_year_summary.csv')\n"
            "comparison_summary"
        ),
        nbf.v4.new_code_cell(
            "plt.figure(figsize=(7, 5.5))\n"
            "sns.scatterplot(\n"
            "    data=comparison,\n"
            "    x='unmet_need_pc',\n"
            "    y='unmet_need_08b_pc',\n"
            "    hue='year',\n"
            "    palette='viridis',\n"
            "    s=42,\n"
            ")\n"
            "axis_max = max(comparison['unmet_need_pc'].max(), comparison['unmet_need_08b_pc'].max())\n"
            "plt.plot([0, axis_max], [0, axis_max], color='#444444', linewidth=1, linestyle=':')\n"
            "plt.xlabel('Primary outcome (%)')\n"
            "plt.ylabel('08b robustness outcome (%)')\n"
            "plt.title('Common country-year cells, 2021-2025')\n"
            "plt.tight_layout()\n"
            "plt.show()"
        ),
        nbf.v4.new_markdown_cell(
            "The tables and figures describe observed values only. The two outcome definitions are kept separate."
        ),
    ]

    path = PROJECT_ROOT / "notebooks" / "03_descriptive_profile.ipynb"
    nbf.write(notebook, path)
    print(f"saved {path}")


if __name__ == "__main__":
    main()
