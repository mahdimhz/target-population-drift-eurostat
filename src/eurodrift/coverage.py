from __future__ import annotations

from collections.abc import Sequence

import pandas as pd


def attrition_waterfall(
    df: pd.DataFrame,
    steps: Sequence[tuple[str, Sequence[str]]],
    country_col: str = "geo",
    year_col: str = "year",
) -> pd.DataFrame:
    """Compute retained rows after each sequential complete-case requirement."""
    rows: list[dict[str, object]] = []
    base_n = len(df)
    previous_n: int | None = None
    for label, columns in steps:
        required = list(columns)
        available = [column for column in required if column in df.columns]
        if available:
            retained = df.loc[df[available].notna().all(axis=1)].copy()
        else:
            retained = df.iloc[0:0].copy()
        n_rows = len(retained)
        rows.append(
            {
                "step": label,
                "required_variables": "; ".join(available),
                "rows": n_rows,
                "countries": retained[country_col].nunique() if country_col in retained.columns else 0,
                "years": retained[year_col].nunique() if year_col in retained.columns else 0,
                "rows_lost_from_previous": 0 if previous_n is None else previous_n - n_rows,
                "retained_pct_of_start": 100 * n_rows / base_n if base_n else pd.NA,
            }
        )
        previous_n = n_rows
    return pd.DataFrame(rows)


def coverage_audit(
    df: pd.DataFrame,
    variables: Sequence[str],
    country_col: str = "geo",
    year_col: str = "year",
) -> pd.DataFrame:
    """Summarize row, country, and year coverage for each variable."""
    rows: list[dict[str, object]] = []
    for variable in variables:
        if variable not in df.columns:
            rows.append(
                {
                    "variable": variable,
                    "observed_rows": 0,
                    "missing_rows": len(df),
                    "missing_pct": 100.0 if len(df) else 0.0,
                    "countries": 0,
                    "year_min": "",
                    "year_max": "",
                    "status": "missing_column",
                }
            )
            continue
        observed = df.loc[df[variable].notna()]
        rows.append(
            {
                "variable": variable,
                "observed_rows": int(len(observed)),
                "missing_rows": int(df[variable].isna().sum()),
                "missing_pct": float(100 * df[variable].isna().mean()) if len(df) else 0.0,
                "countries": int(observed[country_col].nunique()) if country_col in observed.columns else 0,
                "year_min": int(observed[year_col].min()) if not observed.empty and year_col in observed.columns else "",
                "year_max": int(observed[year_col].max()) if not observed.empty and year_col in observed.columns else "",
                "status": "observed" if not observed.empty else "all_missing",
            }
        )
    return pd.DataFrame(rows)
