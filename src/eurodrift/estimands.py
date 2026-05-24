from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Sequence

import pandas as pd


@dataclass(frozen=True)
class EstimandDefinition:
    label: str
    target_population: str
    row_rule: str
    weighting: str
    missing_data_assumption: str
    interpretation: str


def define_estimand(
    label: str,
    target_population: str,
    row_rule: str,
    weighting: str,
    missing_data_assumption: str,
    interpretation: str,
) -> EstimandDefinition:
    return EstimandDefinition(
        label=label,
        target_population=target_population,
        row_rule=row_rule,
        weighting=weighting,
        missing_data_assumption=missing_data_assumption,
        interpretation=interpretation,
    )


def model_sample_with_covars(
    df: pd.DataFrame,
    outcome: str,
    covariates: Sequence[str],
    require_weight: bool = False,
    weight_col: str = "population_weight_year_norm",
) -> pd.DataFrame:
    columns = ["geo", "year", outcome, *covariates]
    if require_weight:
        columns.append(weight_col)
    existing = [column for column in columns if column in df.columns]
    required = [outcome, *covariates]
    if require_weight:
        required.append(weight_col)
    missing_required = [column for column in required if column not in df.columns]
    if missing_required:
        return pd.DataFrame(columns=columns)
    return df[existing].dropna(subset=required).copy()
