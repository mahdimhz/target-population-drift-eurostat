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


def eda_notebook_cells() -> list:
    return [
        nbf.v4.new_markdown_cell(
            "# EDA for outcome and controls\n\n"
            "This section describes the observed panel and simple descriptive patterns."
        ),
        nbf.v4.new_markdown_cell("## Setup"),
        nbf.v4.new_code_cell(
            "from pathlib import Path\n\n"
            "import matplotlib.pyplot as plt\n"
            "import numpy as np\n"
            "import pandas as pd\n"
            "import seaborn as sns\n\n"
            "sns.set_theme(style='whitegrid')\n\n"
            "PROJECT_ROOT = Path.cwd().parent if Path.cwd().name == 'notebooks' else Path.cwd()\n"
            "DATA_PATH = PROJECT_ROOT / 'data' / 'processed' / 'panel_skeleton.csv'\n"
            "CONTROL_PATH = PROJECT_ROOT / 'outputs' / 'control_feasibility-4.csv'\n"
            "FIGURES_DIR = PROJECT_ROOT / 'outputs' / 'figures'\n"
            "FIGURES_DIR.mkdir(parents=True, exist_ok=True)\n\n"
            "panel = pd.read_csv(DATA_PATH)\n"
            "control_feasibility = pd.read_csv(CONTROL_PATH)\n"
            "approved_controls = control_feasibility.loc[\n"
            "    control_feasibility['merge_approved'].eq('yes'),\n"
            "    'variable_name',\n"
            "].tolist()\n"
            "approved_controls"
        ),
        nbf.v4.new_code_cell(
            "panel.head()"
        ),
        nbf.v4.new_code_cell(
            "panel.dtypes"
        ),
        nbf.v4.new_code_cell(
            "pd.DataFrame({\n"
            "    'rows': [len(panel)],\n"
            "    'countries': [panel['geo'].nunique()],\n"
            "    'years': [panel['year'].nunique()],\n"
            "    'first_year': [panel['year'].min()],\n"
            "    'last_year': [panel['year'].max()],\n"
            "})"
        ),
        nbf.v4.new_markdown_cell("## Outcome over time"),
        nbf.v4.new_code_cell(
            "highlight_countries = ['IT', 'DE', 'BG', 'SE']\n"
            "fig, ax = plt.subplots(figsize=(11, 6))\n\n"
            "# draw all country paths in the background\n"
            "for geo, group in panel.sort_values('year').groupby('geo'):\n"
            "    ax.plot(group['year'], group['unmet_need_pc'], color='0.78', linewidth=0.9, alpha=0.8)\n\n"
            "colors = {'IT': '#1b9e77', 'DE': '#d95f02', 'BG': '#7570b3', 'SE': '#e7298a'}\n"
            "for geo in highlight_countries:\n"
            "    group = panel.loc[panel['geo'].eq(geo)].sort_values('year')\n"
            "    if group.empty:\n"
            "        continue\n"
            "    ax.plot(group['year'], group['unmet_need_pc'], marker='o', linewidth=2.0, label=geo, color=colors[geo])\n\n"
            "ax.set_xlabel('Year')\n"
            "ax.set_ylabel('Unmet medical needs (%)')\n"
            "ax.set_title('Unmet medical needs by country')\n"
            "ax.legend(title='Example countries', frameon=False)\n"
            "fig.tight_layout()\n"
            "fig.savefig(FIGURES_DIR / 'unmet_need_trends_all_countries.png', dpi=180)\n"
            "plt.show()"
        ),
        nbf.v4.new_markdown_cell("## Cross-section patterns"),
        nbf.v4.new_code_cell(
            "coverage_by_year = panel.groupby('year')['geo'].nunique().sort_index()\n"
            "recent_year = int(coverage_by_year[coverage_by_year >= 20].index.max())\n"
            "recent = panel.loc[panel['year'].eq(recent_year)].copy()\n"
            "pd.DataFrame({'selected_year': [recent_year], 'countries': [recent['geo'].nunique()]})"
        ),
        nbf.v4.new_code_cell(
            "axis_labels = {\n"
            "    'gdp_per_capita_eur': 'GDP per capita (euro)',\n"
            "    'unemployment_rate_pc': 'Unemployment rate (%)',\n"
            "    'poverty_or_social_exclusion_pc': 'At risk of poverty or social exclusion (%)',\n"
            "    'government_health_expenditure_gdp_pc': 'Government health expenditure (% of GDP)',\n"
            "    'compulsory_health_financing_gdp_pc': 'Compulsory health financing (% of GDP)',\n"
            "}\n\n"
            "scatter_outputs = []\n"
            "for control in approved_controls:\n"
            "    plot_data = recent[['geo', 'unmet_need_pc', control]].dropna()\n"
            "    fig, ax = plt.subplots(figsize=(6.5, 4.8))\n"
            "    if len(plot_data) >= 3:\n"
            "        sns.regplot(\n"
            "            data=plot_data,\n"
            "            x=control,\n"
            "            y='unmet_need_pc',\n"
            "            ci=None,\n"
            "            scatter_kws={'s': 38, 'alpha': 0.85},\n"
            "            line_kws={'color': '#444444', 'linewidth': 1.2},\n"
            "            ax=ax,\n"
            "        )\n"
            "    else:\n"
            "        sns.scatterplot(data=plot_data, x=control, y='unmet_need_pc', s=38, ax=ax)\n"
            "    for _, row in plot_data.iterrows():\n"
            "        ax.text(row[control], row['unmet_need_pc'], row['geo'], fontsize=7, alpha=0.75)\n"
            "    ax.set_xlabel(axis_labels[control])\n"
            "    ax.set_ylabel('Unmet medical needs (%)')\n"
            "    ax.set_title(f'{recent_year}: unmet needs and {axis_labels[control].lower()}')\n"
            "    fig.tight_layout()\n"
            "    output_path = FIGURES_DIR / f'unmet_need_vs_{control}_{recent_year}.png'\n"
            "    fig.savefig(output_path, dpi=180)\n"
            "    scatter_outputs.append(str(output_path.relative_to(PROJECT_ROOT)))\n"
            "    plt.show()\n\n"
            "scatter_outputs"
        ),
        nbf.v4.new_markdown_cell("## Correlations and distributions"),
        nbf.v4.new_code_cell(
            "correlation_vars = ['unmet_need_pc'] + approved_controls\n"
            "complete_rows = panel[correlation_vars].dropna()\n"
            "correlations = complete_rows.corr(method='pearson')\n"
            "correlations.to_csv(PROJECT_ROOT / 'outputs' / 'panel_correlations.csv')\n"
            "pd.DataFrame({'complete_rows': [len(complete_rows)]})"
        ),
        nbf.v4.new_code_cell(
            "fig, ax = plt.subplots(figsize=(8, 6))\n"
            "sns.heatmap(\n"
            "    correlations,\n"
            "    annot=True,\n"
            "    fmt='.2f',\n"
            "    cmap='vlag',\n"
            "    center=0,\n"
            "    square=True,\n"
            "    linewidths=0.4,\n"
            "    ax=ax,\n"
            ")\n"
            "ax.set_title('Pairwise Pearson correlations')\n"
            "fig.tight_layout()\n"
            "fig.savefig(FIGURES_DIR / 'panel_correlations_heatmap.png', dpi=180)\n"
            "plt.show()"
        ),
        nbf.v4.new_code_cell(
            "distribution_vars = correlation_vars\n"
            "n_cols = 2\n"
            "n_rows = int(np.ceil(len(distribution_vars) / n_cols))\n"
            "fig, axes = plt.subplots(n_rows, n_cols, figsize=(10, 3.2 * n_rows))\n"
            "axes = axes.flatten()\n"
            "for ax, column in zip(axes, distribution_vars):\n"
            "    sns.histplot(panel[column].dropna(), bins=18, kde=True, ax=ax, color='#4c78a8')\n"
            "    ax.set_xlabel(axis_labels.get(column, 'Unmet medical needs (%)'))\n"
            "    ax.set_ylabel('Count')\n"
            "for ax in axes[len(distribution_vars):]:\n"
            "    ax.set_visible(False)\n"
            "fig.tight_layout()\n"
            "fig.savefig(FIGURES_DIR / 'panel_variable_distributions.png', dpi=180)\n"
            "plt.show()"
        ),
    ]


def descriptive_tables_cells() -> list:
    return [
        nbf.v4.new_markdown_cell(
            "# Descriptive tables\n\n"
            "This section builds country and year summary tables from the observed panel."
        ),
        nbf.v4.new_markdown_cell("## Setup"),
        nbf.v4.new_code_cell(
            "from pathlib import Path\n\n"
            "import numpy as np\n"
            "import pandas as pd\n\n"
            "PROJECT_ROOT = Path.cwd().parent if Path.cwd().name == 'notebooks' else Path.cwd()\n"
            "PANEL_PATH = PROJECT_ROOT / 'data' / 'processed' / 'panel_skeleton.csv'\n"
            "OUTPUTS_DIR = PROJECT_ROOT / 'outputs'\n\n"
            "panel = pd.read_csv(PANEL_PATH)\n"
            "summary_counts = pd.DataFrame({\n"
            "    'country_year_cells': [len(panel)],\n"
            "    'countries': [panel['geo'].nunique()],\n"
            "    'years': [panel['year'].nunique()],\n"
            "    'first_year': [panel['year'].min()],\n"
            "    'last_year': [panel['year'].max()],\n"
            "})\n"
            "summary_counts"
        ),
        nbf.v4.new_markdown_cell("## Country-level summary table"),
        nbf.v4.new_code_cell(
            "country_summary = (\n"
            "    panel.groupby('geo', as_index=False)\n"
            "    .agg(\n"
            "        observed_years=('year', 'nunique'),\n"
            "        mean_unmet_need_pc=('unmet_need_pc', 'mean'),\n"
            "        min_unmet_need_pc=('unmet_need_pc', 'min'),\n"
            "        max_unmet_need_pc=('unmet_need_pc', 'max'),\n"
            "    )\n"
            "    .round(3)\n"
            "    .sort_values(['mean_unmet_need_pc', 'geo'], ascending=[False, True])\n"
            ")\n"
            "country_summary.to_csv(OUTPUTS_DIR / 'table_country_summary.csv', index=False)\n"
            "country_summary"
        ),
        nbf.v4.new_markdown_cell("## Year-level summary table"),
        nbf.v4.new_code_cell(
            "year_summary = (\n"
            "    panel.groupby('year', as_index=False)\n"
            "    .agg(\n"
            "        countries_observed=('geo', 'nunique'),\n"
            "        mean_unmet_need_pc=('unmet_need_pc', 'mean'),\n"
            "        median_unmet_need_pc=('unmet_need_pc', 'median'),\n"
            "        min_unmet_need_pc=('unmet_need_pc', 'min'),\n"
            "        max_unmet_need_pc=('unmet_need_pc', 'max'),\n"
            "    )\n"
            "    .round(3)\n"
            "    .sort_values('year')\n"
            ")\n"
            "year_summary.to_csv(OUTPUTS_DIR / 'table_year_summary.csv', index=False)\n"
            "year_summary"
        ),
        nbf.v4.new_markdown_cell("## Simple inequality measures"),
        nbf.v4.new_code_cell(
            "def iqr(values):\n"
            "    return values.quantile(0.75) - values.quantile(0.25)\n\n"
            "# compute cross-country spread by year\n"
            "year_inequality = (\n"
            "    panel.groupby('year')\n"
            "    .agg(\n"
            "        countries_observed=('geo', 'nunique'),\n"
            "        sd_unmet_need_pc=('unmet_need_pc', 'std'),\n"
            "        iqr_unmet_need_pc=('unmet_need_pc', iqr),\n"
            "    )\n"
            "    .reset_index()\n"
            ")\n"
            "year_inequality = year_inequality.loc[year_inequality['countries_observed'] >= 20]\n"
            "year_inequality = year_inequality.round(3).sort_values('year')\n"
            "year_inequality.to_csv(OUTPUTS_DIR / 'table_year_inequality.csv', index=False)\n"
            "year_inequality"
        ),
        nbf.v4.new_markdown_cell("## Short written summaries"),
        nbf.v4.new_code_cell(
            "first_year = int(panel['year'].min())\n"
            "last_year = int(panel['year'].max())\n"
            "country_count = int(panel['geo'].nunique())\n"
            "cell_count = int(len(panel))\n\n"
            "high_avg = country_summary.head(5)['geo'].tolist()\n"
            "low_avg = country_summary.tail(5).sort_values('mean_unmet_need_pc')['geo'].tolist()\n\n"
            "spread = year_inequality[['year', 'sd_unmet_need_pc']].dropna().copy()\n"
            "if len(spread) >= 2 and spread.iloc[-1]['sd_unmet_need_pc'] < spread.iloc[0]['sd_unmet_need_pc']:\n"
            "    spread_sentence = 'The cross-country standard deviation is lower at the end of the period than at the start of the measured period.'\n"
            "elif len(spread) >= 2 and spread.iloc[-1]['sd_unmet_need_pc'] > spread.iloc[0]['sd_unmet_need_pc']:\n"
            "    spread_sentence = 'The cross-country standard deviation is higher at the end of the period than at the start of the measured period.'\n"
            "else:\n"
            "    spread_sentence = 'The cross-country standard deviation shows little net change across the measured period.'\n\n"
            "corr_path = OUTPUTS_DIR / 'panel_correlations.csv'\n"
            "if corr_path.exists():\n"
            "    corr = pd.read_csv(corr_path, index_col=0)\n"
            "    poverty_corr = corr.loc['unmet_need_pc', 'poverty_or_social_exclusion_pc']\n"
            "    gdp_corr = corr.loc['unmet_need_pc', 'gdp_per_capita_eur']\n"
            "    association_sentence = (\n"
            "        f'Complete-case correlations show a correlation of {poverty_corr:.2f} with poverty or social exclusion '\n"
            "        f'and {gdp_corr:.2f} with GDP per capita.'\n"
            "    )\n"
            "else:\n"
            "    association_sentence = 'The correlation table was not available when this summary was written.'\n\n"
            "summary_text = f'''# EDA descriptive summary\n\n"
            "- The observed panel contains {cell_count} country-year cells for {country_count} national country codes from {first_year} to {last_year}.\n"
            "- Countries with high average unmet medical needs over their observed years include {', '.join(high_avg)}.\n"
            "- Countries with low average unmet medical needs over their observed years include {', '.join(low_avg)}.\n"
            "- {spread_sentence}\n"
            "- {association_sentence}\n"
            "- These points describe patterns in aggregate Eurostat data. They are not model results.\n"
            "'''\n\n"
            "(OUTPUTS_DIR / 'eda_descriptive_summary.md').write_text(summary_text, encoding='utf-8')\n"
            "summary_text"
        ),
    ]


def main() -> None:
    write_notebook(
        PROJECT_ROOT / "notebooks" / "03_eda_outcome_controls.ipynb",
        eda_notebook_cells(),
    )
    write_notebook(
        PROJECT_ROOT / "notebooks" / "04_descriptive_tables.ipynb",
        descriptive_tables_cells(),
    )
    print("saved notebooks/03_eda_outcome_controls.ipynb")
    print("saved notebooks/04_descriptive_tables.ipynb")


if __name__ == "__main__":
    main()
