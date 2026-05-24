from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def test_multi_outcome_weights_sum_to_one_within_year_outcome_universe() -> None:
    weights = pd.read_csv(ROOT / "outputs" / "multi_outcome_year_normalized_weights.csv")
    observed = weights.dropna(subset=["population_weight_year_norm"]).copy()
    sums = (
        observed.groupby(["indicator_id", "universe", "year"])["population_weight_year_norm"]
        .sum()
        .reset_index(name="weight_sum")
    )
    assert not sums.empty
    assert ((sums["weight_sum"] - 1.0).abs() < 1e-10).all()


def test_monitoring_benchmark_outputs_exist_and_are_nonempty() -> None:
    required = [
        ROOT / "outputs" / "multi_outcome_monitoring_trends.csv",
        ROOT / "outputs" / "multi_outcome_coverage_table.csv",
        ROOT / "outputs" / "multi_outcome_monitoring_dependence_summary.csv",
        ROOT / "tables" / "multi_outcome_coverage_table.tex",
        ROOT / "tables" / "multi_outcome_monitoring_dependence_summary.tex",
        ROOT / "figures" / "multi_outcome_monitoring_benchmark.pdf",
    ]
    missing = [path.as_posix() for path in required if not path.exists() or path.stat().st_size == 0]
    assert not missing


def test_monitoring_trends_include_full_and_eu27_universes() -> None:
    trends = pd.read_csv(ROOT / "outputs" / "multi_outcome_monitoring_trends.csv")
    assert {"Full Eurostat-available", "EU-27"}.issubset(set(trends["universe"]))
    primary = trends[trends["indicator_id"] == "medical_population_combined"]
    assert primary["year"].min() == 2008
    assert primary["year"].max() == 2025


def test_monitoring_benchmark_preserves_primary_608_rows() -> None:
    coverage = pd.read_csv(ROOT / "outputs" / "multi_outcome_coverage_table.csv")
    primary = coverage.loc[coverage["indicator_id"] == "medical_population_combined"].iloc[0]
    assert int(primary["observed_rows"]) == 608
    assert int(primary["country_count"]) == 37
