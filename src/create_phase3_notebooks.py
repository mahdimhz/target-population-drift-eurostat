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


def baseline_cells() -> list:
    return [
        nbf.v4.new_markdown_cell(
            "# Baseline models\n\n"
            "This section estimates baseline association models using the complete-case national panel."
        ),
        nbf.v4.new_markdown_cell("## Setup and data"),
        nbf.v4.new_code_cell(
            "from pathlib import Path\n\n"
            "import matplotlib.pyplot as plt\n"
            "import numpy as np\n"
            "import pandas as pd\n"
            "import seaborn as sns\n"
            "import statsmodels.api as sm\n"
            "import statsmodels.formula.api as smf\n\n"
            "sns.set_theme(style='whitegrid')\n\n"
            "PROJECT_ROOT = Path.cwd().parent if Path.cwd().name == 'notebooks' else Path.cwd()\n"
            "OUTPUTS_DIR = PROJECT_ROOT / 'outputs'\n"
            "FIGURES_DIR = OUTPUTS_DIR / 'figures'\n"
            "FIGURES_DIR.mkdir(parents=True, exist_ok=True)\n\n"
            "panel = pd.read_csv(PROJECT_ROOT / 'data' / 'processed' / 'panel_skeleton.csv')\n"
            "controls = [\n"
            "    'gdp_per_capita_eur',\n"
            "    'unemployment_rate_pc',\n"
            "    'poverty_or_social_exclusion_pc',\n"
            "    'government_health_expenditure_gdp_pc',\n"
            "    'compulsory_health_financing_gdp_pc',\n"
            "]\n"
            "panel['country'] = panel['geo']\n"
            "panel['year'] = panel['year'].astype(int)\n\n"
            "# prepare complete-case panel for baseline model\n"
            "model_data = panel[['country', 'year', 'unmet_need_pc'] + controls].dropna().copy()\n"
            "model_data['log_gdp_per_capita'] = np.log(model_data['gdp_per_capita_eur'])\n"
            "pd.DataFrame({\n"
            "    'complete_case_rows': [len(model_data)],\n"
            "    'countries': [model_data['country'].nunique()],\n"
            "    'years': [model_data['year'].nunique()],\n"
            "    'first_year': [model_data['year'].min()],\n"
            "    'last_year': [model_data['year'].max()],\n"
            "})"
        ),
        nbf.v4.new_code_cell("model_data.head()"),
        nbf.v4.new_markdown_cell("## Transformations and descriptive checks"),
        nbf.v4.new_code_cell(
            "standardize_columns = [\n"
            "    'log_gdp_per_capita',\n"
            "    'unemployment_rate_pc',\n"
            "    'poverty_or_social_exclusion_pc',\n"
            "    'government_health_expenditure_gdp_pc',\n"
            "    'compulsory_health_financing_gdp_pc',\n"
            "]\n"
            "for column in standardize_columns:\n"
            "    model_data[f'std_{column}'] = (model_data[column] - model_data[column].mean()) / model_data[column].std(ddof=0)\n\n"
            "corr_vars = ['unmet_need_pc'] + standardize_columns\n"
            "model_corr = model_data[corr_vars].corr(method='pearson')\n"
            "fig, ax = plt.subplots(figsize=(8, 6))\n"
            "sns.heatmap(model_corr, annot=True, fmt='.2f', cmap='vlag', center=0, square=True, linewidths=0.4, ax=ax)\n"
            "ax.set_title('Complete-case correlations')\n"
            "fig.tight_layout()\n"
            "fig.savefig(FIGURES_DIR / 'model_correlations_heatmap.png', dpi=180)\n"
            "plt.show()\n"
            "model_corr"
        ),
        nbf.v4.new_markdown_cell("## Baseline pooled model"),
        nbf.v4.new_code_cell(
            "main_terms = [\n"
            "    'log_gdp_per_capita',\n"
            "    'unemployment_rate_pc',\n"
            "    'poverty_or_social_exclusion_pc',\n"
            "    'government_health_expenditure_gdp_pc',\n"
            "    'compulsory_health_financing_gdp_pc',\n"
            "]\n"
            "formula = 'unmet_need_pc ~ ' + ' + '.join(main_terms) + ' + C(year)'\n"
            "pooled_model = smf.ols(formula=formula, data=model_data)\n"
            "pooled_result = pooled_model.fit(cov_type='cluster', cov_kwds={'groups': model_data['country']})\n"
            "pooled_result.summary()"
        ),
        nbf.v4.new_code_cell(
            "def tidy_result(result, keep_terms=None):\n"
            "    table = pd.DataFrame({\n"
            "        'variable': result.params.index,\n"
            "        'estimate': result.params.values,\n"
            "        'standard_error': result.bse.values,\n"
            "        't_stat': result.tvalues.values,\n"
            "        'p_value': result.pvalues.values,\n"
            "    })\n"
            "    if keep_terms is not None:\n"
            "        table = table.loc[table['variable'].isin(keep_terms)].copy()\n"
            "    return table.round(4)\n\n"
            "pooled_table = tidy_result(pooled_result)\n"
            "pooled_table.to_csv(OUTPUTS_DIR / 'table_pooled_baseline.csv', index=False)\n"
            "pooled_table"
        ),
        nbf.v4.new_code_cell(
            "def direction_text(value):\n"
            "    if value > 0:\n"
            "        return 'positive'\n"
            "    if value < 0:\n"
            "        return 'negative'\n"
            "    return 'near zero'\n\n"
            "coef = pooled_result.params\n"
            "lines = [\n"
            "    '# Pooled baseline summary',\n"
            "    '',\n"
            "    f'The pooled baseline uses {int(pooled_result.nobs)} complete country-year rows from {model_data[\"country\"].nunique()} countries.',\n"
            "    f'The model includes year indicators and clustered standard errors by country. The R-squared is {pooled_result.rsquared:.3f}.',\n"
            "    '',\n"
            "    'Main coefficient patterns:',\n"
            "]\n"
            "for term in main_terms:\n"
            "    lines.append(f'- `{term}` has a {direction_text(coef[term])} association. The estimate is {coef[term]:.3f}.')\n"
            "lines.extend([\n"
            "    '',\n"
            "    'The coefficients describe aggregate associations in the complete-case Eurostat panel.',\n"
            "    'They should not be read as evidence about cause and result.',\n"
            "])\n"
            "(OUTPUTS_DIR / 'pooled_baseline_summary.md').write_text('\\n'.join(lines) + '\\n', encoding='utf-8')\n"
            "'\\n'.join(lines)"
        ),
        nbf.v4.new_markdown_cell("## Country and year indicator extension"),
        nbf.v4.new_code_cell(
            "country_counts = model_data.groupby('country')['year'].nunique()\n"
            "fe_feasible = (len(model_data) >= 150) and (model_data['country'].nunique() >= 20) and ((country_counts >= 8).mean() >= 0.75)\n"
            "pd.DataFrame({\n"
            "    'complete_case_rows': [len(model_data)],\n"
            "    'countries': [model_data['country'].nunique()],\n"
            "    'share_countries_with_at_least_8_years': [round(float((country_counts >= 8).mean()), 3)],\n"
            "    'indicator_extension_feasible': [fe_feasible],\n"
            "})"
        ),
        nbf.v4.new_code_cell(
            "if fe_feasible:\n"
            "    indicator_formula = 'unmet_need_pc ~ ' + ' + '.join(main_terms) + ' + C(country) + C(year)'\n"
            "    indicator_model = smf.ols(formula=indicator_formula, data=model_data)\n"
            "    indicator_result = indicator_model.fit(cov_type='cluster', cov_kwds={'groups': model_data['country']})\n"
            "    fe_table = tidy_result(indicator_result, keep_terms=main_terms)\n"
            "    fe_table.to_csv(OUTPUTS_DIR / 'table_fe_baseline.csv', index=False)\n"
            "else:\n"
            "    indicator_result = None\n"
            "    fe_table = pd.DataFrame(columns=['variable', 'estimate', 'standard_error', 't_stat', 'p_value'])\n"
            "    fe_table.to_csv(OUTPUTS_DIR / 'table_fe_baseline.csv', index=False)\n"
            "fe_table"
        ),
        nbf.v4.new_code_cell(
            "if indicator_result is not None:\n"
            "    pooled_main = pooled_table.loc[pooled_table['variable'].isin(main_terms), ['variable', 'estimate']].rename(columns={'estimate': 'pooled_estimate'})\n"
            "    fe_main = fe_table[['variable', 'estimate']].rename(columns={'estimate': 'indicator_estimate'})\n"
            "    compare = pooled_main.merge(fe_main, on='variable', how='inner')\n"
            "    compare['change'] = compare['indicator_estimate'] - compare['pooled_estimate']\n"
            "    lines = [\n"
            "        '# Country and year indicator summary',\n"
            "        '',\n"
            "        f'The indicator extension uses {int(indicator_result.nobs)} complete country-year rows from {model_data[\"country\"].nunique()} countries.',\n"
            "        f'The model includes country and year indicators. The R-squared is {indicator_result.rsquared:.3f}.',\n"
            "        '',\n"
            "        'Control coefficient patterns compared with the pooled model:',\n"
            "    ]\n"
            "    for _, row in compare.iterrows():\n"
            "        lines.append(\n"
            "            f'- `{row[\"variable\"]}` changes from {row[\"pooled_estimate\"]:.3f} in the pooled model to {row[\"indicator_estimate\"]:.3f} in the indicator model.'\n"
            "        )\n"
            "    lines.extend([\n"
            "        '',\n"
            "        'The estimates remain descriptive associations in aggregate country-year data.',\n"
            "        'They should not be read as evidence about cause and result.',\n"
            "    ])\n"
            "else:\n"
            "    lines = [\n"
            "        '# Country and year indicator summary',\n"
            "        '',\n"
            "        'The complete-case panel is too thin for this extension under the feasibility rule used here.',\n"
            "        'The pooled model is the reported baseline for this phase.',\n"
            "    ]\n"
            "(OUTPUTS_DIR / 'fe_baseline_summary.md').write_text('\\n'.join(lines) + '\\n', encoding='utf-8')\n"
            "'\\n'.join(lines)"
        ),
    ]


def ml_cells() -> list:
    return [
        nbf.v4.new_markdown_cell(
            "# ML benchmark\n\n"
            "This section compares simple prediction benchmarks for the aggregate panel."
        ),
        nbf.v4.new_markdown_cell("## Setup and data"),
        nbf.v4.new_code_cell(
            "from pathlib import Path\n\n"
            "import numpy as np\n"
            "import pandas as pd\n"
            "import torch\n"
            "from sklearn.ensemble import GradientBoostingRegressor\n"
            "from sklearn.linear_model import LinearRegression\n"
            "from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score\n"
            "from sklearn.pipeline import Pipeline\n"
            "from sklearn.preprocessing import StandardScaler\n"
            "from torch import nn\n\n"
            "PROJECT_ROOT = Path.cwd().parent if Path.cwd().name == 'notebooks' else Path.cwd()\n"
            "OUTPUTS_DIR = PROJECT_ROOT / 'outputs'\n"
            "panel = pd.read_csv(PROJECT_ROOT / 'data' / 'processed' / 'panel_skeleton.csv')\n"
            "controls = [\n"
            "    'gdp_per_capita_eur',\n"
            "    'unemployment_rate_pc',\n"
            "    'poverty_or_social_exclusion_pc',\n"
            "    'government_health_expenditure_gdp_pc',\n"
            "    'compulsory_health_financing_gdp_pc',\n"
            "]\n"
            "data = panel[['geo', 'year', 'unmet_need_pc'] + controls].dropna().copy()\n"
            "data['log_gdp_per_capita'] = np.log(data['gdp_per_capita_eur'])\n"
            "features = [\n"
            "    'log_gdp_per_capita',\n"
            "    'unemployment_rate_pc',\n"
            "    'poverty_or_social_exclusion_pc',\n"
            "    'government_health_expenditure_gdp_pc',\n"
            "    'compulsory_health_financing_gdp_pc',\n"
            "]\n"
            "data[['geo', 'year', 'unmet_need_pc'] + features].head()"
        ),
        nbf.v4.new_markdown_cell("## Train and test split"),
        nbf.v4.new_markdown_cell(
            "The split uses time order. Rows from 2015 to 2019 are used for training. Rows from 2020 to 2024 are held out for testing."
        ),
        nbf.v4.new_code_cell(
            "train = data.loc[data['year'] <= 2019].copy()\n"
            "test = data.loc[data['year'] >= 2020].copy()\n"
            "X_train = train[features]\n"
            "y_train = train['unmet_need_pc']\n"
            "X_test = test[features]\n"
            "y_test = test['unmet_need_pc']\n"
            "pd.DataFrame({\n"
            "    'train_rows': [len(train)],\n"
            "    'test_rows': [len(test)],\n"
            "    'train_years': [f\"{train['year'].min()}-{train['year'].max()}\"],\n"
            "    'test_years': [f\"{test['year'].min()}-{test['year'].max()}\"],\n"
            "})"
        ),
        nbf.v4.new_markdown_cell("## Baseline predictive models"),
        nbf.v4.new_code_cell(
            "def metrics(name, y_true, y_pred):\n"
            "    return {\n"
            "        'model': name,\n"
            "        'mae': mean_absolute_error(y_true, y_pred),\n"
            "        'rmse': np.sqrt(mean_squared_error(y_true, y_pred)),\n"
            "        'r_squared': r2_score(y_true, y_pred),\n"
            "    }\n\n"
            "performance = []\n\n"
            "linear_model = Pipeline([\n"
            "    ('scale', StandardScaler()),\n"
            "    ('model', LinearRegression()),\n"
            "])\n"
            "linear_model.fit(X_train, y_train)\n"
            "linear_pred = linear_model.predict(X_test)\n"
            "performance.append(metrics('Linear', y_test, linear_pred))\n\n"
            "tree_model = GradientBoostingRegressor(\n"
            "    n_estimators=150,\n"
            "    learning_rate=0.04,\n"
            "    max_depth=2,\n"
            "    random_state=42,\n"
            ")\n"
            "tree_model.fit(X_train, y_train)\n"
            "tree_pred = tree_model.predict(X_test)\n"
            "performance.append(metrics('Tree', y_test, tree_pred))\n\n"
            "pd.DataFrame(performance).round(3)"
        ),
        nbf.v4.new_markdown_cell("## Small MLP model"),
        nbf.v4.new_code_cell(
            "torch.manual_seed(42)\n"
            "np.random.seed(42)\n\n"
            "# fit scaling on training rows only\n"
            "scaler = StandardScaler()\n"
            "X_train_scaled = scaler.fit_transform(X_train).astype('float32')\n"
            "X_test_scaled = scaler.transform(X_test).astype('float32')\n"
            "y_train_array = y_train.to_numpy(dtype='float32').reshape(-1, 1)\n"
            "y_test_array = y_test.to_numpy(dtype='float32').reshape(-1, 1)\n\n"
            "validation_mask = train['year'].eq(2019).to_numpy()\n"
            "X_inner = torch.tensor(X_train_scaled[~validation_mask])\n"
            "y_inner = torch.tensor(y_train_array[~validation_mask])\n"
            "X_valid = torch.tensor(X_train_scaled[validation_mask])\n"
            "y_valid = torch.tensor(y_train_array[validation_mask])\n"
            "X_test_tensor = torch.tensor(X_test_scaled)\n\n"
            "mlp = nn.Sequential(\n"
            "    nn.Linear(len(features), 16),\n"
            "    nn.ReLU(),\n"
            "    nn.Linear(16, 8),\n"
            "    nn.ReLU(),\n"
            "    nn.Linear(8, 1),\n"
            ")\n"
            "loss_fn = nn.MSELoss()\n"
            "optimizer = torch.optim.Adam(mlp.parameters(), lr=0.01, weight_decay=1e-4)\n\n"
            "best_state = None\n"
            "best_valid = float('inf')\n"
            "patience = 30\n"
            "wait = 0\n"
            "for epoch in range(500):\n"
            "    mlp.train()\n"
            "    optimizer.zero_grad()\n"
            "    train_loss = loss_fn(mlp(X_inner), y_inner)\n"
            "    train_loss.backward()\n"
            "    optimizer.step()\n\n"
            "    mlp.eval()\n"
            "    with torch.no_grad():\n"
            "        valid_loss = loss_fn(mlp(X_valid), y_valid).item()\n"
            "    if valid_loss < best_valid - 1e-5:\n"
            "        best_valid = valid_loss\n"
            "        best_state = {key: value.detach().clone() for key, value in mlp.state_dict().items()}\n"
            "        wait = 0\n"
            "    else:\n"
            "        wait += 1\n"
            "    if wait >= patience:\n"
            "        break\n\n"
            "if best_state is not None:\n"
            "    mlp.load_state_dict(best_state)\n"
            "mlp.eval()\n"
            "with torch.no_grad():\n"
            "    mlp_pred = mlp(X_test_tensor).numpy().ravel()\n"
            "performance.append(metrics('MLP', y_test, mlp_pred))\n\n"
            "performance_table = pd.DataFrame(performance).round(4)\n"
            "performance_table.to_csv(OUTPUTS_DIR / 'table_ml_performance.csv', index=False)\n"
            "pd.DataFrame({'epochs_used': [epoch + 1], 'validation_rmse': [np.sqrt(best_valid)]})"
        ),
        nbf.v4.new_code_cell(
            "performance_table"
        ),
        nbf.v4.new_markdown_cell("## Brief ML summary"),
        nbf.v4.new_code_cell(
            "best_mae = performance_table.sort_values('mae').iloc[0]\n"
            "best_rmse = performance_table.sort_values('rmse').iloc[0]\n"
            "linear_row = performance_table.loc[performance_table['model'].eq('Linear')].iloc[0]\n"
            "mae_gain = linear_row['mae'] - best_mae['mae']\n"
            "rmse_gain = linear_row['rmse'] - best_rmse['rmse']\n"
            "summary = f'''# ML benchmark summary\n\n"
            "The benchmark uses {len(train)} training rows from 2015-2019 and {len(test)} test rows from 2020-2024.\n\n"
            "The lowest test MAE is from the {best_mae['model']} model, with MAE {best_mae['mae']:.3f}. The lowest test RMSE is from the {best_rmse['model']} model, with RMSE {best_rmse['rmse']:.3f}.\n\n"
            "Compared with the linear baseline, the best MAE is lower by {mae_gain:.3f} percentage points and the best RMSE is lower by {rmse_gain:.3f} percentage points.\n\n"
            "These results describe predictive performance on aggregate Eurostat data. They do not support claims about cause and result or policy change.\n"
            "'''\n"
            "(OUTPUTS_DIR / 'ml_benchmark_summary.md').write_text(summary, encoding='utf-8')\n"
            "summary"
        ),
    ]


def main() -> None:
    write_notebook(PROJECT_ROOT / "notebooks" / "05_baseline_models.ipynb", baseline_cells())
    write_notebook(PROJECT_ROOT / "notebooks" / "06_ml_benchmark.ipynb", ml_cells())
    print("saved notebooks/05_baseline_models.ipynb")
    print("saved notebooks/06_ml_benchmark.ipynb")


if __name__ == "__main__":
    main()
