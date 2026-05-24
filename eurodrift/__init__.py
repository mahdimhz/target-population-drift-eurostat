"""Import shim for the local ``src/eurodrift`` package.

This keeps ``python -m eurodrift`` usable from a fresh checkout before the
project is installed as a package.
"""

from __future__ import annotations

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
_SRC_PACKAGE = _SRC / "eurodrift"
if _SRC.exists() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))
if _SRC_PACKAGE.exists() and str(_SRC_PACKAGE) not in __path__:
    __path__.append(str(_SRC_PACKAGE))

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
    "estimand_ladder",
    "generate_report",
    "included_excluded_balance",
    "ipw_diagnostic",
    "load_eurostat_panel",
    "mnar_delta_sensitivity",
    "model_sample_with_covars",
    "pmm_imputation_sensitivity",
    "population_weighted_trend",
    "simulate_missingness",
    "standardized_mean_difference",
    "year_normalized_population_weights",
]
