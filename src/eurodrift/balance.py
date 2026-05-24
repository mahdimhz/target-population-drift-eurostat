from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import pandas as pd


def standardized_mean_difference(included: pd.Series, excluded: pd.Series) -> float:
    included_values = pd.to_numeric(included, errors="coerce").dropna()
    excluded_values = pd.to_numeric(excluded, errors="coerce").dropna()
    if included_values.empty or excluded_values.empty:
        return np.nan
    pooled_var = (included_values.var(ddof=1) + excluded_values.var(ddof=1)) / 2
    if pd.isna(pooled_var) or pooled_var <= 0:
        return 0.0 if included_values.mean() == excluded_values.mean() else np.nan
    return float((included_values.mean() - excluded_values.mean()) / np.sqrt(pooled_var))


def included_excluded_balance(
    df: pd.DataFrame,
    included_mask: pd.Series,
    variables: Sequence[str],
) -> pd.DataFrame:
    included_mask = included_mask.reindex(df.index).fillna(False).astype(bool)
    rows: list[dict[str, object]] = []
    for variable in variables:
        if variable not in df.columns:
            rows.append(
                {
                    "variable": variable,
                    "included_n": 0,
                    "excluded_n": 0,
                    "included_mean": np.nan,
                    "excluded_mean": np.nan,
                    "smd": np.nan,
                    "status": "missing_column",
                }
            )
            continue
        included = pd.to_numeric(df.loc[included_mask, variable], errors="coerce")
        excluded = pd.to_numeric(df.loc[~included_mask, variable], errors="coerce")
        rows.append(
            {
                "variable": variable,
                "included_n": int(included.notna().sum()),
                "excluded_n": int(excluded.notna().sum()),
                "included_mean": float(included.mean()) if included.notna().any() else np.nan,
                "excluded_mean": float(excluded.mean()) if excluded.notna().any() else np.nan,
                "smd": standardized_mean_difference(included, excluded),
                "status": "estimated",
            }
        )
    return pd.DataFrame(rows)
