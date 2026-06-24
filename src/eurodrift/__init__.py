"""Reusable utilities for the target-population drift audit protocol."""

from .balance import included_excluded_balance, standardized_mean_difference
from .audit import (
    estimand_ladder,
    ipw_diagnostic,
    mnar_delta_sensitivity,
    pmm_imputation_sensitivity,
    population_weighted_trend,
)
from .classification import classify_drift, classify_feasibility
from .coverage import attrition_waterfall, coverage_audit
from .drift import (
    average_absolute_smd,
    conclusion_stability_index,
    directional_agreement,
    jensen_shannon_divergence,
    standardized_coefficient,
    support_loss,
    target_population_drift_index,
    total_variation_distance,
)
from .estimands import EstimandDefinition, define_estimand, model_sample_with_covars
from .io import load_eurostat_panel
from .report import generate_report
from .simulation import simulate_missingness
from .targets import country_group, country_universe_category
from .weights import balanced_outcome_countries, year_normalized_population_weights

__all__ = [
    "EstimandDefinition",
    "attrition_waterfall",
    "balanced_outcome_countries",
    "classify_drift",
    "classify_feasibility",
    "country_group",
    "country_universe_category",
    "coverage_audit",
    "define_estimand",
    "average_absolute_smd",
    "conclusion_stability_index",
    "directional_agreement",
    "estimand_ladder",
    "generate_report",
    "included_excluded_balance",
    "ipw_diagnostic",
    "jensen_shannon_divergence",
    "load_eurostat_panel",
    "mnar_delta_sensitivity",
    "model_sample_with_covars",
    "pmm_imputation_sensitivity",
    "population_weighted_trend",
    "simulate_missingness",
    "standardized_mean_difference",
    "standardized_coefficient",
    "support_loss",
    "target_population_drift_index",
    "total_variation_distance",
    "year_normalized_population_weights",
]
