from __future__ import annotations

from collections.abc import Sequence

import pandas as pd


def year_normalized_population_weights(
    df: pd.DataFrame,
    population_col: str = "population_total",
    group_cols: Sequence[str] = ("year",),
    weight_col: str = "population_weight_year_norm",
) -> pd.DataFrame:
    """Add weights that sum to one within each year-like group."""
    out = df.copy()
    denominators = out.groupby(list(group_cols))[population_col].transform("sum")
    out[weight_col] = out[population_col] / denominators
    out.loc[out[population_col].isna() | denominators.le(0), weight_col] = pd.NA
    return out


def balanced_outcome_countries(
    df: pd.DataFrame,
    outcome_col: str,
    weight_col: str = "population_weight_year_norm",
    country_col: str = "geo",
    year_col: str = "year",
) -> list[str]:
    """Countries with complete outcome coverage and valid weights for all observed years."""
    years = set(df[year_col].dropna().astype(int).unique())
    countries: list[str] = []
    for country, group in df.groupby(country_col):
        observed_years = set(group.loc[group[outcome_col].notna(), year_col].dropna().astype(int))
        has_valid_weights = weight_col in group.columns and group[weight_col].notna().all()
        if years.issubset(observed_years) and has_valid_weights:
            countries.append(str(country))
    return sorted(countries)
