from __future__ import annotations

from pathlib import Path

import nbformat as nbf


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def write_notebook(path: Path, cells: list) -> None:
    notebook = nbf.v4.new_notebook()
    notebook["cells"] = cells
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
    path.parent.mkdir(parents=True, exist_ok=True)
    nbf.write(notebook, path)


def outcome_missingness_notebook() -> list:
    return [
        nbf.v4.new_markdown_cell(
            "# Outcome missingness\n\n"
            "This section describes the data source and extraction steps for the primary outcome. "
            "The file loaded below is the tidy national country-year extract from Eurostat table `hlth_silc_08`."
        ),
        nbf.v4.new_code_cell(
            "from pathlib import Path\n\n"
            "import matplotlib.pyplot as plt\n"
            "import pandas as pd\n"
            "import seaborn as sns\n\n"
            "PROJECT_ROOT = Path.cwd().parent if Path.cwd().name == 'notebooks' else Path.cwd()\n"
            "YEARS = list(range(2008, 2026))\n"
            "data_path = PROJECT_ROOT / 'data' / 'processed' / 'country_year_outcome.csv'\n"
            "outputs_dir = PROJECT_ROOT / 'outputs'\n\n"
            "df = pd.read_csv(data_path)\n"
            "df.head()"
        ),
        nbf.v4.new_code_cell(
            "# build country-year table with one row per geo and time\n"
            "base = pd.MultiIndex.from_product(\n"
            "    [sorted(df['geo'].unique()), YEARS],\n"
            "    names=['geo', 'year'],\n"
            ").to_frame(index=False)\n"
            "observed = df[['geo', 'year', 'unmet_need_pc']].copy()\n"
            "observed['observed'] = observed['unmet_need_pc'].notna().astype(int)\n"
            "availability = base.merge(observed[['geo', 'year', 'observed']], on=['geo', 'year'], how='left')\n"
            "availability['observed'] = availability['observed'].fillna(0).astype(int)\n"
            "availability.head()"
        ),
        nbf.v4.new_code_cell(
            "country_coverage = (\n"
            "    availability.groupby('geo', as_index=False)['observed']\n"
            "    .sum()\n"
            "    .rename(columns={'observed': 'non_missing_years'})\n"
            "    .sort_values(['non_missing_years', 'geo'])\n"
            ")\n"
            "country_coverage"
        ),
        nbf.v4.new_code_cell(
            "matrix = availability.pivot(index='geo', columns='year', values='observed').sort_index()\n"
            "matrix.to_csv(outputs_dir / 'outcome_availability_matrix.csv')\n"
            "country_coverage.to_csv(outputs_dir / 'outcome_country_coverage_notebook.csv', index=False)\n"
            "matrix"
        ),
        nbf.v4.new_code_cell(
            "plt.figure(figsize=(12, 8))\n"
            "sns.heatmap(\n"
            "    matrix,\n"
            "    cmap=sns.color_palette(['#f0f0f0', '#2364aa']),\n"
            "    cbar=False,\n"
            "    linewidths=0.15,\n"
            "    linecolor='white',\n"
            ")\n"
            "plt.xlabel('Year')\n"
            "plt.ylabel('Country code')\n"
            "plt.title('Observed country-year cells for hlth_silc_08')\n"
            "plt.tight_layout()\n"
            "plt.savefig(outputs_dir / 'outcome_missingness_heatmap_notebook.png', dpi=180)\n"
            "plt.show()"
        ),
        nbf.v4.new_markdown_cell(
            "The table and heatmap describe observed and missing cells only. They do not report inference."
        ),
    ]


def control_feasibility_notebook() -> list:
    return [
        nbf.v4.new_markdown_cell(
            "# Control feasibility\n\n"
            "This section describes candidate Eurostat control variables. Each row uses an exact dataset code and filter."
        ),
        nbf.v4.new_code_cell(
            "from pathlib import Path\n\n"
            "import pandas as pd\n\n"
            "PROJECT_ROOT = Path.cwd().parent if Path.cwd().name == 'notebooks' else Path.cwd()\n"
            "feasibility_path = PROJECT_ROOT / 'outputs' / 'control_feasibility.csv'\n"
            "controls_path = PROJECT_ROOT / 'data' / 'processed' / 'verified_control_candidates.csv'\n\n"
            "feasibility = pd.read_csv(feasibility_path)\n"
            "controls = pd.read_csv(controls_path)\n"
            "feasibility"
        ),
        nbf.v4.new_code_cell(
            "# keep only columns approved by the feasibility audit\n"
            "approved = feasibility.loc[feasibility['merge_approved'].eq('yes'), 'variable_name'].tolist()\n"
            "approved"
        ),
        nbf.v4.new_code_cell(
            "missingness = controls[['geo', 'year'] + approved].copy()\n"
            "missingness = missingness.groupby('year')[approved].apply(lambda frame: frame.notna().sum()).reset_index()\n"
            "missingness"
        ),
        nbf.v4.new_code_cell(
            "feasibility.to_csv(PROJECT_ROOT / 'outputs' / 'control_feasibility_notebook.csv', index=False)\n"
            "feasibility.to_markdown(PROJECT_ROOT / 'outputs' / 'control_feasibility_notebook.md', index=False)\n"
            "missingness.to_csv(PROJECT_ROOT / 'outputs' / 'control_missingness_by_year.csv', index=False)"
        ),
        nbf.v4.new_markdown_cell(
            "The audit records source feasibility and missingness. It does not estimate any model."
        ),
    ]


def main() -> None:
    write_notebook(
        PROJECT_ROOT / "notebooks" / "01_outcome_missingness.ipynb",
        outcome_missingness_notebook(),
    )
    write_notebook(
        PROJECT_ROOT / "notebooks" / "02_control_feasibility.ipynb",
        control_feasibility_notebook(),
    )
    print("saved notebooks/01_outcome_missingness.ipynb")
    print("saved notebooks/02_control_feasibility.ipynb")


if __name__ == "__main__":
    main()
