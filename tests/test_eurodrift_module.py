from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from eurodrift.balance import included_excluded_balance, standardized_mean_difference
from eurodrift.classification import FeasibilityThresholds, classify_drift, classify_feasibility
from eurodrift.coverage import attrition_waterfall, coverage_audit
from eurodrift.estimands import define_estimand, model_sample_with_covars
from eurodrift.simulation import simulate_missingness
from eurodrift.targets import country_group, country_universe_category
from eurodrift.weights import balanced_outcome_countries, year_normalized_population_weights


def test_eurodrift_country_categories_match_thesis_groups() -> None:
    assert country_universe_category("AT") == "EU-27"
    assert country_universe_category("NO") == "EEA country"
    assert country_universe_category("CH") == "Switzerland"
    assert country_universe_category("UK") == "UK"
    assert country_universe_category("AL") == "Candidate/potential candidate"
    assert country_group("AT") == "Western/Northern"
    assert country_group("RO") == "Eastern/Southern"


def test_eurodrift_year_normalized_weights_and_balanced_outcome() -> None:
    df = pd.DataFrame(
        {
            "geo": ["A", "B", "A", "B"],
            "year": [2020, 2020, 2021, 2021],
            "outcome": [1.0, 2.0, 1.5, 2.5],
            "population_total": [10.0, 30.0, 20.0, 20.0],
        }
    )
    weighted = year_normalized_population_weights(df)
    sums = weighted.groupby("year")["population_weight_year_norm"].sum()
    assert ((sums - 1.0).abs() < 1e-12).all()
    assert weighted.loc[(weighted["geo"] == "B") & (weighted["year"] == 2020), "population_weight_year_norm"].iloc[0] == 0.75
    assert balanced_outcome_countries(weighted, "outcome") == ["A", "B"]


def test_eurodrift_attrition_and_coverage_audit() -> None:
    df = pd.DataFrame(
        {
            "geo": ["A", "A", "B"],
            "year": [2020, 2021, 2020],
            "y": [1.0, 1.2, 2.0],
            "x1": [1.0, None, 3.0],
            "x2": [1.0, 2.0, None],
        }
    )
    attrition = attrition_waterfall(df, [("Outcome", ["y"]), ("+ x1", ["y", "x1"]), ("+ x2", ["y", "x1", "x2"])])
    assert attrition["rows"].tolist() == [3, 2, 1]
    assert attrition["rows_lost_from_previous"].tolist() == [0, 1, 1]

    coverage = coverage_audit(df, ["y", "x1", "missing_col"])
    assert coverage.loc[coverage["variable"].eq("y"), "observed_rows"].iloc[0] == 3
    assert coverage.loc[coverage["variable"].eq("missing_col"), "status"].iloc[0] == "missing_column"


def test_eurodrift_balance_reports_smds() -> None:
    df = pd.DataFrame({"x": [1.0, 2.0, 5.0, 6.0], "z": [10.0, 10.0, 10.0, 10.0]})
    included = pd.Series([True, True, False, False])
    assert standardized_mean_difference(df.loc[included, "z"], df.loc[~included, "z"]) == 0.0
    balance = included_excluded_balance(df, included, ["x", "z"])
    assert balance.loc[balance["variable"].eq("x"), "smd"].iloc[0] < 0
    assert balance.loc[balance["variable"].eq("z"), "smd"].iloc[0] == 0.0


def test_eurodrift_estimand_and_model_sample_helpers() -> None:
    estimand = define_estimand(
        "Complete-case FE",
        "Covariate-complete country-years",
        "Drop rows with missing baseline covariates",
        "None",
        "Complete-case assumption",
        "Selected analytical panel",
    )
    assert estimand.label == "Complete-case FE"

    df = pd.DataFrame(
        {
            "geo": ["A", "B"],
            "year": [2020, 2020],
            "y": [1.0, 2.0],
            "x": [3.0, None],
            "population_weight_year_norm": [0.4, 0.6],
        }
    )
    sample = model_sample_with_covars(df, "y", ["x"], require_weight=True)
    assert len(sample) == 1
    assert sample["geo"].iloc[0] == "A"


def test_eurodrift_feasibility_and_classification_labels() -> None:
    small = pd.DataFrame({"geo": ["A", "B"], "year": [2020, 2020], "y": [1.0, 2.0]})
    ok, reason = classify_feasibility(small, FeasibilityThresholds(min_rows=3, min_countries=2, min_years=1))
    assert not ok
    assert reason == "infeasible: fewer than 3 rows"

    stable = classify_drift(
        {
            "complete_case": 0.10,
            "population_weighted": 0.11,
            "balanced": 0.09,
            "ipw": 0.10,
            "mi": 0.08,
        },
        poverty_iqr=10.0,
        outcome_sd=10.0,
    )
    assert stable == "stable"

    missingness_dependent = classify_drift(
        {
            "complete_case": 0.50,
            "population_weighted": 0.51,
            "balanced": 0.50,
            "ipw": 0.49,
            "mi": -0.05,
        },
        poverty_iqr=10.0,
        outcome_sd=5.0,
    )
    assert missingness_dependent == "missingness-dependent"


def test_eurodrift_simulation_reproducible_under_seed() -> None:
    df = pd.DataFrame(
        {
            "geo": ["A", "B", "C", "D"],
            "year": [2020, 2020, 2021, 2021],
            "x": [1.0, 2.0, 3.0, 4.0],
        }
    )
    first = simulate_missingness(df, ["x"], "mcar", 0.5, seed=42)
    second = simulate_missingness(df, ["x"], "mcar", 0.5, seed=42)
    pd.testing.assert_frame_equal(first, second)


def test_eurodrift_report_can_write_csv(tmp_path: Path) -> None:
    from eurodrift.report import generate_report

    df = pd.DataFrame({"geo": ["A"], "year": [2020], "x": [1.0]})
    path = generate_report(df, ["x"], tmp_path / "report.csv")
    assert path.exists()
    assert pd.read_csv(path)["variable"].iloc[0] == "x"
