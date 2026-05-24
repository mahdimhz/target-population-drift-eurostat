from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class FeasibilityThresholds:
    min_rows: int = 100
    min_countries: int = 15
    min_years: int = 5


def classify_feasibility(
    df: pd.DataFrame,
    thresholds: FeasibilityThresholds = FeasibilityThresholds(),
    country_col: str = "geo",
    year_col: str = "year",
) -> tuple[bool, str]:
    if len(df) < thresholds.min_rows:
        return False, f"infeasible: fewer than {thresholds.min_rows} rows"
    if country_col not in df.columns or df[country_col].nunique() < thresholds.min_countries:
        return False, f"infeasible: fewer than {thresholds.min_countries} countries"
    if year_col not in df.columns or df[year_col].nunique() < thresholds.min_years:
        return False, f"infeasible: fewer than {thresholds.min_years} years"
    return True, "feasible"


def _iqr_effect(coef: float, poverty_iqr: float) -> float:
    return float(coef) * float(poverty_iqr)


def classify_drift(
    estimates: dict[str, float | None],
    poverty_iqr: float,
    outcome_sd: float,
    mi_variant_effects: list[float] | None = None,
) -> str:
    """Deterministically classify drift using IQR-scale effect differences."""
    required = ["complete_case", "population_weighted", "balanced", "ipw"]
    available = {key: value for key, value in estimates.items() if value is not None and pd.notna(value)}
    if len([key for key in required if key in available]) < 2:
        return "non-identifiable"

    cc = available.get("complete_case")
    if cc is None:
        return "non-identifiable"
    cc_effect = _iqr_effect(cc, poverty_iqr)
    threshold_25 = 0.25 * outcome_sd
    threshold_50 = 0.50 * outcome_sd

    observed_effects = {
        key: _iqr_effect(value, poverty_iqr)
        for key, value in available.items()
        if key in {"population_weighted", "balanced", "ipw", "eu27"}
    }
    if any((value >= 0) != (cc >= 0) for key, value in available.items() if key in observed_effects):
        return "target-dependent"
    if any(abs(effect - cc_effect) > threshold_25 for effect in observed_effects.values()):
        return "target-dependent"

    mi = available.get("mi")
    if mi is not None:
        mi_effect = _iqr_effect(mi, poverty_iqr)
        if (mi >= 0) != (cc >= 0) or abs(mi_effect - cc_effect) > threshold_50:
            if mi_variant_effects:
                effects_range = max(mi_variant_effects) - min(mi_variant_effects)
                if effects_range > threshold_50:
                    return "imputation-model-dependent"
            return "missingness-dependent"

    if mi_variant_effects:
        effects_range = max(mi_variant_effects) - min(mi_variant_effects)
        signs = {effect >= 0 for effect in mi_variant_effects}
        if len(signs) > 1 or effects_range > threshold_50:
            return "imputation-model-dependent"

    return "stable"
