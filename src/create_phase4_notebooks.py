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


def feature_feasibility_cells() -> list:
    return [
        nbf.v4.new_markdown_cell(
            "# Feature feasibility audit\n\n"
            "This section checks additional national Eurostat features before they are merged into the panel."
        ),
        nbf.v4.new_code_cell(
            "from pathlib import Path\n"
            "import json\n"
            "import sys\n\n"
            "import pandas as pd\n"
            "import requests\n\n"
            "PROJECT_ROOT = Path.cwd().parent if Path.cwd().name == 'notebooks' else Path.cwd()\n"
            "sys.path.insert(0, str(PROJECT_ROOT / 'src'))\n"
            "from eurostat_api import build_country_year_table, download_json, eurostat_url, is_national_geo\n\n"
            "OUTPUTS_DIR = PROJECT_ROOT / 'outputs'\n"
            "RAW_DIR = PROJECT_ROOT / 'data' / 'raw'\n"
            "PROCESSED_DIR = PROJECT_ROOT / 'data' / 'processed'\n"
            "YEARS = range(2008, 2026)\n"
            "outcome = pd.read_csv(PROCESSED_DIR / 'panel_skeleton.csv')\n"
            "outcome_pairs = set(zip(outcome['geo'], outcome['year']))\n"
            "outcome.shape"
        ),
        nbf.v4.new_code_cell(
            "candidates = [\n"
            "    {\n"
            "        'dataset_code': 'hlth_rs_prs2',\n"
            "        'short_title': 'Physicians per 100 000 inhabitants',\n"
            "        'variable_name': 'physicians_per_100k',\n"
            "        'params': {'unit': 'P_HTHAB', 'wstatus': 'PRACT', 'med_spec': 'PHYS'},\n"
            "        'filter': 'unit=P_HTHAB, wstatus=PRACT, med_spec=PHYS',\n"
            "    },\n"
            "    {\n"
            "        'dataset_code': 'hlth_rs_bds1',\n"
            "        'short_title': 'Hospital beds per 100 000 inhabitants',\n"
            "        'variable_name': 'hospital_beds_per_100k',\n"
            "        'params': {'unit': 'P_HTHAB', 'facility': 'HBEDT', 'hlthcare': 'TOTAL'},\n"
            "        'filter': 'unit=P_HTHAB, facility=HBEDT, hlthcare=TOTAL',\n"
            "    },\n"
            "    {\n"
            "        'dataset_code': 'hlth_sha11_hf',\n"
            "        'short_title': 'Out-of-pocket health expenditure share',\n"
            "        'variable_name': 'oop_health_expenditure_share_pc',\n"
            "        'params': {'unit': 'PC_CHE', 'icha11_hf': 'HF3'},\n"
            "        'filter': 'unit=PC_CHE, icha11_hf=HF3',\n"
            "    },\n"
            "    {\n"
            "        'dataset_code': 'ilc_di12',\n"
            "        'short_title': 'Gini coefficient of income inequality',\n"
            "        'variable_name': 'gini_income',\n"
            "        'params': {'age': 'TOTAL', 'statinfo': 'GINI_HND'},\n"
            "        'filter': 'age=TOTAL, statinfo=GINI_HND',\n"
            "    },\n"
            "    {\n"
            "        'dataset_code': 'une_ltu_a',\n"
            "        'short_title': 'Long-term unemployment rate',\n"
            "        'variable_name': 'long_term_unemployment_rate_pc',\n"
            "        'params': {'indic_em': 'LTU', 'age': 'Y15-74', 'sex': 'T', 'unit': 'PC_ACT'},\n"
            "        'filter': 'indic_em=LTU, age=Y15-74, sex=T, unit=PC_ACT',\n"
            "    },\n"
            "]\n"
            "candidates"
        ),
        nbf.v4.new_code_cell(
            "def category_label(data, dim_id, code):\n"
            "    labels = data.get('dimension', {}).get(dim_id, {}).get('category', {}).get('label', {})\n"
            "    return labels.get(code, code)\n\n"
            "def endpoint_available(dataset_code):\n"
            "    url = f'https://ec.europa.eu/eurostat/api/dissemination/sdmx/3.0/structure/dataflow/ESTAT/{dataset_code}/1.0?compress=false'\n"
            "    response = requests.get(url, timeout=45)\n"
            "    return 'yes' if response.ok else 'no'\n\n"
            "rows = []\n"
            "metadata_rows = []\n"
            "for candidate in candidates:\n"
            "    params = dict(candidate['params'])\n"
            "    params['time'] = [str(year) for year in YEARS]\n"
            "    raw_path = RAW_DIR / f\"feature_{candidate['dataset_code']}_{candidate['variable_name']}.json\"\n"
            "    data = download_json(candidate['dataset_code'], params, raw_path)\n"
            "    tidy = build_country_year_table(data, candidate['variable_name'], YEARS)\n"
            "    tidy = tidy[['geo', 'year', candidate['variable_name']]]\n"
            "    tidy.to_csv(PROCESSED_DIR / f\"feature_{candidate['variable_name']}.csv\", index=False)\n\n"
            "    national_codes = sorted(code for code in tidy['geo'].dropna().unique() if is_national_geo(str(code)))\n"
            "    years_available = sorted(int(year) for year in tidy['year'].dropna().unique())\n"
            "    feature_pairs = set(zip(tidy['geo'], tidy['year']))\n"
            "    overlap_pairs = feature_pairs.intersection(outcome_pairs)\n"
            "    unit_code = str(candidate['params'].get('unit', ''))\n"
            "    unit_label = category_label(data, 'unit', unit_code) if unit_code else category_label(data, 'statinfo', str(candidate['params'].get('statinfo', '')))\n"
            "    official_title = data.get('label', candidate['short_title'])\n"
            "    years_text = f\"{min(years_available)}-{max(years_available)}\" if years_available else 'none'\n"
            "    geography = 'national country codes' if national_codes else 'not verified'\n"
            "    overlap = 'yes' if overlap_pairs else 'no'\n"
            "    missing_cells = len(outcome_pairs) - len(overlap_pairs)\n"
            "    rows.append({\n"
            "        'dataset_code': candidate['dataset_code'],\n"
            "        'short_title': candidate['short_title'],\n"
            "        'official_title': official_title,\n"
            "        'variable_name': candidate['variable_name'],\n"
            "        'filter': candidate['filter'],\n"
            "        'unit': unit_label,\n"
            "        'geography_level': geography,\n"
            "        'years_available': years_text,\n"
            "        'countries_available': len(national_codes),\n"
            "        'overlaps_with_outcome': overlap,\n"
            "        'non_missing_country_years': len(tidy),\n"
            "        'overlap_country_years': len(overlap_pairs),\n"
            "        'missingness_notes': f'{len(overlap_pairs)} observed outcome cells match this exact filter; {missing_cells} outcome cells would be missing after a left merge.',\n"
            "        'dataflow_endpoint_available': endpoint_available(candidate['dataset_code']),\n"
            "        'merge_approved': 'yes' if overlap == 'yes' and len(overlap_pairs) >= 250 else 'no',\n"
            "    })\n"
            "    metadata_rows.append({\n"
            "        'dataset_code': candidate['dataset_code'],\n"
            "        'variable_name': candidate['variable_name'],\n"
            "        'api_url': eurostat_url(candidate['dataset_code'], params),\n"
            "        'raw_file': str(raw_path.relative_to(PROJECT_ROOT)),\n"
            "    })\n\n"
            "feasibility = pd.DataFrame(rows)\n"
            "feasibility.to_csv(OUTPUTS_DIR / 'control_feasibility_extended.csv', index=False)\n"
            "(OUTPUTS_DIR / 'feature_api_requests.json').write_text(json.dumps(metadata_rows, indent=2), encoding='utf-8')\n"
            "feasibility"
        ),
        nbf.v4.new_code_cell(
            "approved = feasibility.loc[feasibility['merge_approved'].eq('yes'), 'variable_name'].tolist()\n"
            "summary = (\n"
            "    '# Extended control feasibility summary\\n\\n'\n"
            "    f'The audit checked {len(feasibility)} additional national Eurostat features. '\n"
            "    f'{len(approved)} features passed the overlap rule and are approved for the Phase 4 panel: '\n"
            "    + (', '.join(approved) if approved else 'none')\n"
            "    + '.\\n\\nThe table records exact filters, units, national coverage, year coverage, and overlap with the observed outcome panel. '\n"
            "    'Features that do not meet the overlap rule are left out of the merged feature panel.\\n\\n'\n"
            "    + feasibility.to_markdown(index=False)\n"
            "    + '\\n'\n"
            ")\n"
            "(OUTPUTS_DIR / 'control_feasibility_extended.md').write_text(summary, encoding='utf-8')\n"
            "approved"
        ),
    ]


def panel_features_cells() -> list:
    return [
        nbf.v4.new_markdown_cell(
            "# Build panel features v2\n\n"
            "This section merges approved national features and creates simple lag and change variables."
        ),
        nbf.v4.new_code_cell(
            "from pathlib import Path\n\n"
            "import numpy as np\n"
            "import pandas as pd\n\n"
            "PROJECT_ROOT = Path.cwd().parent if Path.cwd().name == 'notebooks' else Path.cwd()\n"
            "OUTPUTS_DIR = PROJECT_ROOT / 'outputs'\n"
            "PROCESSED_DIR = PROJECT_ROOT / 'data' / 'processed'\n\n"
            "base = pd.read_csv(PROCESSED_DIR / 'panel_skeleton.csv')\n"
            "feasibility = pd.read_csv(OUTPUTS_DIR / 'control_feasibility_extended.csv')\n"
            "approved_new = feasibility.loc[feasibility['merge_approved'].eq('yes'), 'variable_name'].tolist()\n"
            "panel = base.copy()\n"
            "panel.shape, approved_new"
        ),
        nbf.v4.new_code_cell(
            "# merge approved national features by country and year\n"
            "for variable in approved_new:\n"
            "    feature = pd.read_csv(PROCESSED_DIR / f'feature_{variable}.csv')\n"
            "    panel = panel.merge(feature, on=['geo', 'year'], how='left')\n\n"
            "panel = panel.sort_values(['geo', 'year']).reset_index(drop=True)\n"
            "panel.head()"
        ),
        nbf.v4.new_code_cell(
            "existing_controls = [\n"
            "    'gdp_per_capita_eur',\n"
            "    'unemployment_rate_pc',\n"
            "    'poverty_or_social_exclusion_pc',\n"
            "    'government_health_expenditure_gdp_pc',\n"
            "    'compulsory_health_financing_gdp_pc',\n"
            "]\n"
            "panel['log_gdp_per_capita'] = np.log(panel['gdp_per_capita_eur'])\n"
            "if 'oop_health_expenditure_share_pc' in panel.columns:\n"
            "    panel['log_oop_health_expenditure_share'] = np.log1p(panel['oop_health_expenditure_share_pc'])\n\n"
            "lag_sources = [\n"
            "    'gdp_per_capita_eur',\n"
            "    'unemployment_rate_pc',\n"
            "    'poverty_or_social_exclusion_pc',\n"
            "]\n"
            "health_lag_candidates = [\n"
            "    'physicians_per_100k',\n"
            "    'hospital_beds_per_100k',\n"
            "    'oop_health_expenditure_share_pc',\n"
            "]\n"
            "selected_health_feature = next((column for column in health_lag_candidates if column in panel.columns), None)\n"
            "if selected_health_feature is not None:\n"
            "    lag_sources.append(selected_health_feature)\n\n"
            "for column in lag_sources:\n"
            "    panel[f'{column}_lag1'] = panel.groupby('geo')[column].shift(1)\n\n"
            "panel['gdp_per_capita_growth'] = (panel['gdp_per_capita_eur'] - panel['gdp_per_capita_eur_lag1']) / panel['gdp_per_capita_eur_lag1']\n"
            "panel['unemployment_rate_change'] = panel['unemployment_rate_pc'] - panel['unemployment_rate_pc_lag1']\n"
            "selected_health_feature"
        ),
        nbf.v4.new_code_cell(
            "feature_columns = existing_controls + approved_new + [\n"
            "    'log_gdp_per_capita',\n"
            "    'gdp_per_capita_eur_lag1',\n"
            "    'unemployment_rate_pc_lag1',\n"
            "    'poverty_or_social_exclusion_pc_lag1',\n"
            "    'gdp_per_capita_growth',\n"
            "    'unemployment_rate_change',\n"
            "]\n"
            "if selected_health_feature is not None:\n"
            "    feature_columns.append(f'{selected_health_feature}_lag1')\n"
            "if 'log_oop_health_expenditure_share' in panel.columns:\n"
            "    feature_columns.append('log_oop_health_expenditure_share')\n\n"
            "feature_columns = [column for column in feature_columns if column in panel.columns]\n"
            "X_for_later_ml = panel[feature_columns].copy()\n"
            "X_standardized = (X_for_later_ml - X_for_later_ml.mean()) / X_for_later_ml.std(ddof=0)\n"
            "panel.to_csv(PROCESSED_DIR / 'panel_features_v2.csv', index=False)\n"
            "pd.DataFrame({'feature': feature_columns, 'non_missing_rows': [int(panel[column].notna().sum()) for column in feature_columns]})"
        ),
        nbf.v4.new_code_cell(
            "new_missing = panel[approved_new].isna().sum().sort_values(ascending=False) if approved_new else pd.Series(dtype='int64')\n"
            "engineered = [column for column in feature_columns if column not in existing_controls and column not in approved_new]\n"
            "summary = (\n"
            "    '# Feature engineering summary\\n\\n'\n"
            "    f'The extended panel keeps {len(panel)} observed country-year rows from the Phase 1 panel. '\n"
            "    f'{len(approved_new)} new Eurostat feature datasets were merged.\\n\\n'\n"
            "    f'The feature view contains {len(feature_columns)} columns: {len(existing_controls)} original controls, '\n"
            "    f'{len(approved_new)} new variables, and {len(engineered)} transformed, lag, or change variables.\\n\\n'\n"
            "    'Main missingness introduced by new features:\\n'\n"
            ")\n"
            "if len(new_missing) == 0:\n"
            "    summary += '- No approved new features were merged.\\n'\n"
            "else:\n"
            "    for variable, count in new_missing.items():\n"
            "        summary += f'- `{variable}` has {int(count)} missing rows after the left merge.\\n'\n"
            "summary += '\\nLag variables are missing for the first observed year within each country. No values were carried forward.\\n'\n"
            "(OUTPUTS_DIR / 'feature_engineering_summary.md').write_text(summary, encoding='utf-8')\n"
            "summary"
        ),
    ]


def robustness_cells() -> list:
    return [
        nbf.v4.new_markdown_cell(
            "# hlth_silc_08b robustness check\n\n"
            "This section compares the primary outcome with the persons-with-need denominator indicator for 2021-2025."
        ),
        nbf.v4.new_code_cell(
            "from pathlib import Path\n"
            "import sys\n\n"
            "import matplotlib.pyplot as plt\n"
            "import numpy as np\n"
            "import pandas as pd\n"
            "import seaborn as sns\n"
            "import statsmodels.formula.api as smf\n\n"
            "PROJECT_ROOT = Path.cwd().parent if Path.cwd().name == 'notebooks' else Path.cwd()\n"
            "sys.path.insert(0, str(PROJECT_ROOT / 'src'))\n"
            "from eurostat_api import build_country_year_table, download_json, eurostat_url\n\n"
            "sns.set_theme(style='whitegrid')\n"
            "OUTPUTS_DIR = PROJECT_ROOT / 'outputs'\n"
            "FIGURES_DIR = OUTPUTS_DIR / 'figures'\n"
            "FIGURES_DIR.mkdir(parents=True, exist_ok=True)\n"
            "RAW_DIR = PROJECT_ROOT / 'data' / 'raw'\n"
            "PROCESSED_DIR = PROJECT_ROOT / 'data' / 'processed'\n"
            "YEARS_08B = range(2021, 2026)\n"
            "panel = pd.read_csv(PROCESSED_DIR / 'panel_skeleton.csv')\n"
            "panel.shape"
        ),
        nbf.v4.new_code_cell(
            "params_08b = {\n"
            "    'unit': 'PC',\n"
            "    'rskpovth': 'TOTAL',\n"
            "    'reason': 'TXP_TFAR_WLIST',\n"
            "    'age': 'Y_GE16',\n"
            "    'sex': 'T',\n"
            "    'time': [str(year) for year in YEARS_08B],\n"
            "}\n"
            "raw_path = RAW_DIR / 'hlth_silc_08b_unmet_need_2021_2025_phase4.json'\n"
            "data_08b = download_json('hlth_silc_08b', params_08b, raw_path)\n"
            "outcome_08b = build_country_year_table(data_08b, 'unmet_need_pc_08b', YEARS_08B)\n"
            "outcome_08b = outcome_08b[['geo', 'year', 'unmet_need_pc_08b', 'status']].rename(columns={'status': 'status_08b'})\n"
            "outcome_08b.to_csv(PROCESSED_DIR / 'country_year_outcome_08b.csv', index=False)\n"
            "(OUTPUTS_DIR / 'hlth_silc_08b_phase4_api_url.txt').write_text(eurostat_url('hlth_silc_08b', params_08b), encoding='utf-8')\n"
            "outcome_08b.head()"
        ),
        nbf.v4.new_code_cell(
            "primary_08 = panel.loc[panel['year'].between(2021, 2025), ['geo', 'year', 'unmet_need_pc']].rename(columns={'unmet_need_pc': 'unmet_need_pc_08'})\n"
            "comparison = primary_08.merge(outcome_08b[['geo', 'year', 'unmet_need_pc_08b']], on=['geo', 'year'], how='inner')\n"
            "comparison['difference_08b_minus_08'] = comparison['unmet_need_pc_08b'] - comparison['unmet_need_pc_08']\n"
            "comparison.to_csv(OUTPUTS_DIR / '08b_common_country_years.csv', index=False)\n"
            "country_avg = comparison.groupby('geo', as_index=False).agg(\n"
            "    unmet_need_pc_08=('unmet_need_pc_08', 'mean'),\n"
            "    unmet_need_pc_08b=('unmet_need_pc_08b', 'mean'),\n"
            "    difference_08b_minus_08=('difference_08b_minus_08', 'mean'),\n"
            ").sort_values('difference_08b_minus_08', ascending=False)\n"
            "country_avg.to_csv(OUTPUTS_DIR / '08b_country_average_comparison.csv', index=False)\n"
            "country_avg.head()"
        ),
        nbf.v4.new_code_cell(
            "fig, ax = plt.subplots(figsize=(6.5, 5.5))\n"
            "sns.scatterplot(data=country_avg, x='unmet_need_pc_08', y='unmet_need_pc_08b', s=45, ax=ax)\n"
            "axis_max = max(country_avg['unmet_need_pc_08'].max(), country_avg['unmet_need_pc_08b'].max())\n"
            "ax.plot([0, axis_max], [0, axis_max], color='0.35', linestyle=':', linewidth=1)\n"
            "for _, row in country_avg.iterrows():\n"
            "    ax.text(row['unmet_need_pc_08'], row['unmet_need_pc_08b'], row['geo'], fontsize=7, alpha=0.75)\n"
            "ax.set_xlabel('Primary outcome, average 2021-2025 (%)')\n"
            "ax.set_ylabel('08b outcome, average 2021-2025 (%)')\n"
            "ax.set_title('Primary and 08b outcome levels')\n"
            "fig.tight_layout()\n"
            "fig.savefig(FIGURES_DIR / '08b_vs_08_scatter.png', dpi=180)\n"
            "plt.show()"
        ),
        nbf.v4.new_code_cell(
            "plot_data = country_avg.sort_values('difference_08b_minus_08')\n"
            "fig, ax = plt.subplots(figsize=(8, max(6, 0.24 * len(plot_data))))\n"
            "ax.barh(plot_data['geo'], plot_data['difference_08b_minus_08'], color='#4c78a8')\n"
            "ax.axvline(0, color='0.25', linewidth=1)\n"
            "ax.set_xlabel('08b minus primary outcome (percentage points)')\n"
            "ax.set_ylabel('Country code')\n"
            "ax.set_title('Average denominator difference by country')\n"
            "fig.tight_layout()\n"
            "fig.savefig(FIGURES_DIR / '08b_minus_08_difference_by_country.png', dpi=180)\n"
            "plt.show()"
        ),
        nbf.v4.new_code_cell(
            "model_panel = panel.merge(outcome_08b[['geo', 'year', 'unmet_need_pc_08b']], on=['geo', 'year'], how='inner')\n"
            "model_panel = model_panel.rename(columns={'unmet_need_pc': 'unmet_need_pc_08'})\n"
            "model_panel['log_gdp_per_capita'] = np.log(model_panel['gdp_per_capita_eur'])\n"
            "model_vars = ['geo', 'year', 'unmet_need_pc_08', 'unmet_need_pc_08b', 'log_gdp_per_capita', 'unemployment_rate_pc', 'poverty_or_social_exclusion_pc']\n"
            "model_data = model_panel[model_vars].dropna().copy()\n"
            "formula_08 = 'unmet_need_pc_08 ~ log_gdp_per_capita + unemployment_rate_pc + poverty_or_social_exclusion_pc'\n"
            "formula_08b = 'unmet_need_pc_08b ~ log_gdp_per_capita + unemployment_rate_pc + poverty_or_social_exclusion_pc'\n"
            "result_08 = smf.ols(formula_08, data=model_data).fit(cov_type='HC1')\n"
            "result_08b = smf.ols(formula_08b, data=model_data).fit(cov_type='HC1')\n"
            "model_data.shape"
        ),
        nbf.v4.new_code_cell(
            "def tidy_result(result, outcome_name):\n"
            "    return pd.DataFrame({\n"
            "        'outcome': outcome_name,\n"
            "        'variable': result.params.index,\n"
            "        'estimate': result.params.values,\n"
            "        'standard_error': result.bse.values,\n"
            "        't_stat': result.tvalues.values,\n"
            "        'p_value': result.pvalues.values,\n"
            "    }).round(4)\n\n"
            "table_08 = tidy_result(result_08, 'unmet_need_pc_08')\n"
            "table_08b = tidy_result(result_08b, 'unmet_need_pc_08b')\n"
            "coef_table = pd.concat([table_08, table_08b], ignore_index=True)\n"
            "coef_table.to_csv(OUTPUTS_DIR / 'table_08b_robustness_models.csv', index=False)\n"
            "coef_table"
        ),
        nbf.v4.new_code_cell(
            "mean_08 = comparison['unmet_need_pc_08'].mean()\n"
            "mean_08b = comparison['unmet_need_pc_08b'].mean()\n"
            "mean_diff = comparison['difference_08b_minus_08'].mean()\n"
            "control_terms = ['log_gdp_per_capita', 'unemployment_rate_pc', 'poverty_or_social_exclusion_pc']\n"
            "same_sign = []\n"
            "for term in control_terms:\n"
            "    sign_08 = np.sign(result_08.params[term])\n"
            "    sign_08b = np.sign(result_08b.params[term])\n"
            "    same_sign.append(term if sign_08 == sign_08b else None)\n"
            "same_sign = [term for term in same_sign if term is not None]\n"
            "summary = (\n"
            "    '# 08b robustness summary\\n\\n'\n"
            "    f'The comparison uses {len(comparison)} overlapping country-year cells from 2021-2025. '\n"
            "    f'The primary outcome has an average level of {mean_08:.2f} percent, while the 08b outcome has an average level of {mean_08b:.2f} percent. '\n"
            "    f'The average 08b minus primary difference is {mean_diff:.2f} percentage points.\\n\\n'\n"
            "    f'The simple pooled models use {len(model_data)} complete rows. '\n"
            "    f'The same coefficient sign appears for {len(same_sign)} of the {len(control_terms)} shared controls: '\n"
            "    + (', '.join(same_sign) if same_sign else 'none')\n"
            "    + '.\\n\\nThis is a denominator robustness and interpretation check. It is not a new core model.\\n'\n"
            ")\n"
            "(OUTPUTS_DIR / '08b_robustness_summary.md').write_text(summary, encoding='utf-8')\n"
            "summary"
        ),
    ]


def main() -> None:
    write_notebook(PROJECT_ROOT / "notebooks" / "07_feature_feasibility.ipynb", feature_feasibility_cells())
    write_notebook(PROJECT_ROOT / "notebooks" / "08_build_panel_features_v2.ipynb", panel_features_cells())
    write_notebook(PROJECT_ROOT / "notebooks" / "09_08b_robustness.ipynb", robustness_cells())
    print("saved notebooks/07_feature_feasibility.ipynb")
    print("saved notebooks/08_build_panel_features_v2.ipynb")
    print("saved notebooks/09_08b_robustness.ipynb")


if __name__ == "__main__":
    main()
