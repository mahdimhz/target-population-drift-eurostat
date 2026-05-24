from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Lasso, LinearRegression, Ridge
from sklearn.metrics import mean_absolute_error
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[2]
TABLES = ROOT / "tables"

FEATURES = [
    "gdp_per_capita_eur",
    "unemployment_rate_pc",
    "poverty_or_social_exclusion_pc",
    "government_health_expenditure_gdp_pc",
    "compulsory_health_financing_gdp_pc",
    "physicians_per_100k",
    "hospital_beds_per_100k",
    "oop_health_expenditure_share_pc",
    "gini_income",
    "long_term_unemployment_rate_pc",
    "log_gdp_per_capita",
    "physicians_per_100k_lag1",
    "gdp_per_capita_growth",
    "unemployment_rate_change",
]

REG_LABELS = {
    "Intercept": "Intercept",
    "log_gdp_per_capita": "Log GDP per capita",
    "unemployment_rate_pc": "Unemployment rate",
    "poverty_or_social_exclusion_pc": "Poverty or social exclusion",
    "government_health_expenditure_gdp_pc": "Government health expenditure",
    "compulsory_health_financing_gdp_pc": "Compulsory health financing",
}


def full_regression_label(variable: str) -> str:
    year_match = re.match(r"C\(year\)\[T\.(\d{4})\]", variable)
    if year_match:
        return f"Year {year_match.group(1)}"
    return REG_LABELS.get(variable, variable.replace("_", " "))


def write_full_pooled_regression() -> None:
    df = pd.read_csv(ROOT / "outputs" / "table_pooled_baseline.csv")
    lines = [
        r"\begin{tabular}{@{}lrrrr@{}}",
        r"\toprule",
        r"Variable & Estimate & Std. error & \(t\) & \(p\) \\",
        r"\midrule",
    ]
    for _, row in df.iterrows():
        lines.append(
            f"{full_regression_label(row['variable'])} & "
            f"{row['estimate']:.3f} & "
            f"{row['standard_error']:.3f} & {row['t_stat']:.3f} & {row['p_value']:.3f} \\\\"
        )
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}",
            r"\par\vspace{0.3em}",
            r"\begin{minipage}{0.96\textwidth}",
            r"\footnotesize Notes: This is the full pooled baseline specification corresponding to Table~\ref{tab:regression_main_results}, including all year-indicator coefficients. The omitted year is 2015. Standard errors are country-clustered; exact p-values are shown instead of significance stars.",
            r"\end{minipage}",
        ]
    )
    (TABLES / "appendix_full_pooled_regression.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


def models() -> dict[str, object]:
    return {
        "OLS": make_pipeline(StandardScaler(), LinearRegression()),
        "Ridge": make_pipeline(StandardScaler(), Ridge(alpha=100.0)),
        "Lasso": make_pipeline(StandardScaler(), Lasso(alpha=0.1, max_iter=10000)),
        "Random Forest": RandomForestRegressor(n_estimators=300, min_samples_leaf=3, random_state=42),
        "Gradient Boosting": GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, max_depth=2, random_state=42),
    }


def write_ml_time_fold_results() -> None:
    df = pd.read_csv(ROOT / "data" / "processed" / "modeling_dataset_5a_with_splits.csv")
    folds = [
        ("Fold 1", 2017, 2018),
        ("Fold 2", 2018, 2019),
        ("Fold 3", 2019, 2020),
    ]
    rows = []
    for model_name, model in models().items():
        fold_maes = []
        for fold_name, train_end, valid_year in folds:
            train = df[df["year"] <= train_end].copy()
            valid = df[df["year"] == valid_year].copy()
            fitted = model
            fitted.fit(train[FEATURES], train["unmet_need_pc"])
            pred = fitted.predict(valid[FEATURES])
            mae = mean_absolute_error(valid["unmet_need_pc"], pred)
            fold_maes.append(mae)
            rows.append(
                {
                    "model": model_name,
                    "fold": fold_name,
                    "valid_year": valid_year,
                    "mae": mae,
                }
            )
    raw = pd.DataFrame(rows)
    raw.to_csv(ROOT / "outputs" / "ml_time_aware_fold_results.csv", index=False)

    lines = [
        r"\begin{tabular}{@{}lrrrr@{}}",
        r"\toprule",
        r"Model & 2018 fold & 2019 fold & 2020 fold & Mean \(\pm\) SD \\",
        r"\midrule",
    ]
    for model_name in models().keys():
        vals = raw[raw["model"] == model_name].sort_values("valid_year")["mae"].to_numpy()
        lines.append(
            f"{model_name} & {vals[0]:.3f} & {vals[1]:.3f} & {vals[2]:.3f} & "
            f"{vals.mean():.3f} $\\pm$ {vals.std(ddof=1):.3f} \\\\"
        )
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}",
            r"\par\vspace{0.3em}",
            r"\begin{minipage}{0.96\textwidth}",
            r"\footnotesize Notes: Folds are time-aware expanding-window checks within the pre-test period. Fold 1 trains on 2015--2017 and validates on 2018; Fold 2 trains on 2015--2018 and validates on 2019; Fold 3 trains on 2015--2019 and validates on 2020. MAE is measured in percentage points of unmet medical care need.",
            r"\end{minipage}",
        ]
    )
    (TABLES / "ml_time_aware_fold_results.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    write_full_pooled_regression()
    write_ml_time_fold_results()


if __name__ == "__main__":
    main()
