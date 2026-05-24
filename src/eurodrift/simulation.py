from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import pandas as pd


def simulate_missingness(
    df: pd.DataFrame,
    variables: Sequence[str],
    mechanism: str,
    missing_fraction: float,
    seed: int = 42,
    group_col: str = "geo",
    year_col: str = "year",
) -> pd.DataFrame:
    """Apply simple reproducible missingness mechanisms for smoke tests and simulations."""
    rng = np.random.default_rng(seed)
    out = df.copy()
    variables = [variable for variable in variables if variable in out.columns]
    if not variables:
        return out

    if mechanism == "mcar":
        mask = rng.random(len(out)) < missing_fraction
    elif mechanism == "early_year":
        cutoff = out[year_col].quantile(missing_fraction)
        mask = out[year_col] <= cutoff
    elif mechanism == "country_group":
        countries = sorted(out[group_col].dropna().unique())
        n_drop = max(1, int(round(len(countries) * missing_fraction)))
        selected = set(rng.choice(countries, size=n_drop, replace=False))
        mask = out[group_col].isin(selected)
    else:
        raise ValueError(f"Unknown missingness mechanism: {mechanism}")

    out.loc[mask, variables] = pd.NA
    return out
