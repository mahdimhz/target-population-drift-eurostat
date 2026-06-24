from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class DriftWeights:
    row: float = 1.0
    country: float = 1.0
    year: float = 1.0
    weight: float = 1.0
    balance: float = 1.0


def support_loss(analytical_count: int, reference_count: int) -> float:
    if reference_count <= 0:
        return np.nan
    return float(1.0 - analytical_count / reference_count)


def jensen_shannon_divergence(reference: pd.Series, analytical: pd.Series) -> float:
    """Bounded Jensen-Shannon divergence using log base 2."""
    ref = pd.to_numeric(reference, errors="coerce").fillna(0.0).astype(float)
    ana = pd.to_numeric(analytical, errors="coerce").fillna(0.0).astype(float)
    ref_sum = ref.sum()
    ana_sum = ana.sum()
    if ref_sum <= 0 or ana_sum <= 0:
        return np.nan
    p = (ref / ref_sum).to_numpy(dtype=float)
    q = (ana / ana_sum).to_numpy(dtype=float)
    m = 0.5 * (p + q)

    def _kl(values: np.ndarray, base: np.ndarray) -> float:
        mask = values > 0
        return float(np.sum(values[mask] * np.log2(values[mask] / base[mask])))

    return float(0.5 * _kl(p, m) + 0.5 * _kl(q, m))


def total_variation_distance(reference: pd.Series, analytical: pd.Series) -> float:
    ref = pd.to_numeric(reference, errors="coerce").fillna(0.0).astype(float)
    ana = pd.to_numeric(analytical, errors="coerce").fillna(0.0).astype(float)
    ref_sum = ref.sum()
    ana_sum = ana.sum()
    if ref_sum <= 0 or ana_sum <= 0:
        return np.nan
    p = ref / ref_sum
    q = ana / ana_sum
    return float(0.5 * (p - q).abs().sum())


def average_absolute_smd(reference: pd.DataFrame, analytical: pd.DataFrame, variables: Iterable[str]) -> float:
    values: list[float] = []
    for variable in variables:
        if variable not in reference.columns or variable not in analytical.columns:
            continue
        ref_values = pd.to_numeric(reference[variable], errors="coerce").dropna()
        ana_values = pd.to_numeric(analytical[variable], errors="coerce").dropna()
        if ref_values.empty or ana_values.empty:
            continue
        ref_sd = ref_values.std(ddof=1)
        if pd.isna(ref_sd) or ref_sd <= 0:
            continue
        values.append(abs(float((ana_values.mean() - ref_values.mean()) / ref_sd)))
    return float(np.mean(values)) if values else np.nan


def target_population_drift_index(components: Mapping[str, float], weights: DriftWeights = DriftWeights()) -> float:
    weight_map = {
        "Delta_row": weights.row,
        "Delta_country": weights.country,
        "Delta_year": weights.year,
        "Delta_weight": weights.weight,
        "Delta_balance": weights.balance,
    }
    numerator = 0.0
    denominator = 0.0
    for key, value in components.items():
        if key not in weight_map or pd.isna(value):
            continue
        numerator += float(value) * weight_map[key]
        denominator += weight_map[key]
    return float(numerator / denominator) if denominator > 0 else np.nan


def standardized_coefficient(coef: float, x_iqr: float, y_iqr: float) -> float:
    if pd.isna(coef) or pd.isna(x_iqr) or pd.isna(y_iqr) or y_iqr == 0:
        return np.nan
    return float(coef) * float(x_iqr) / float(y_iqr)


def conclusion_stability_index(theta_values: Iterable[float], delta: float = 0.10) -> tuple[float, float]:
    values = pd.Series(list(theta_values), dtype="float64").dropna()
    if values.empty or delta <= 0:
        return np.nan, np.nan
    theta_iqr = float(values.quantile(0.75) - values.quantile(0.25))
    csi = float(1.0 - min(1.0, theta_iqr / delta))
    return theta_iqr, csi


def directional_agreement(theta_values: Iterable[float], reference_sign: int | None = None) -> float:
    values = pd.Series(list(theta_values), dtype="float64").dropna()
    values = values[values.ne(0)]
    if values.empty:
        return np.nan
    if reference_sign is None:
        median = float(values.median())
        if median == 0:
            return np.nan
        reference_sign = 1 if median > 0 else -1
    signs = values.map(lambda value: 1 if value > 0 else -1)
    return float(signs.eq(reference_sign).mean())
