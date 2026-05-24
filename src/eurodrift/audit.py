from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from .coverage import attrition_waterfall
from .weights import year_normalized_population_weights


ROOT = Path(__file__).resolve().parents[2]


def population_weighted_trend(
    df: pd.DataFrame,
    outcome_col: str,
    population_col: str = "population_total",
    year_col: str = "year",
) -> pd.DataFrame:
    weighted = year_normalized_population_weights(df, population_col=population_col, group_cols=(year_col,))
    rows = []
    for year, group in weighted.groupby(year_col):
        observed = group.dropna(subset=[outcome_col])
        weighted_observed = observed.dropna(subset=["population_weight_year_norm"])
        rows.append(
            {
                "year": int(year),
                "countries": int(observed["geo"].nunique()) if "geo" in observed.columns else int(len(observed)),
                "unweighted_mean": float(observed[outcome_col].mean()) if not observed.empty else np.nan,
                "population_weighted_mean": float(
                    (weighted_observed[outcome_col] * weighted_observed["population_weight_year_norm"]).sum()
                )
                if not weighted_observed.empty
                else np.nan,
            }
        )
    return pd.DataFrame(rows)


def estimand_ladder(df: pd.DataFrame, outcome_col: str, covariates: list[str]) -> pd.DataFrame:
    steps = [("Outcome observed", [outcome_col])]
    steps.extend((f"+ {covar}", [outcome_col, *covariates[: i + 1]]) for i, covar in enumerate(covariates))
    return attrition_waterfall(df, steps)


def ipw_diagnostic(df: pd.DataFrame, inclusion_col: str) -> pd.DataFrame:
    if inclusion_col not in df.columns:
        raise KeyError(f"Missing inclusion column: {inclusion_col}")
    included = df[inclusion_col].astype(bool)
    return pd.DataFrame(
        [
            {
                "rows": int(len(df)),
                "included_rows": int(included.sum()),
                "excluded_rows": int((~included).sum()),
                "inclusion_rate": float(included.mean()) if len(df) else np.nan,
            }
        ]
    )


def pmm_imputation_sensitivity() -> pd.DataFrame:
    path = ROOT / "outputs" / "mi_variant_summary.csv"
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


def mnar_delta_sensitivity() -> pd.DataFrame:
    path = ROOT / "outputs" / "mnar_sensitivity_results.csv"
    return pd.read_csv(path) if path.exists() else pd.DataFrame()
