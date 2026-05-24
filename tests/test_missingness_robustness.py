from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd

import run_missingness_robustness as mr
from run_missingness_robustness import effective_sample_size, format_p_value, rubin_components, rubin_pool


def test_effective_sample_size_reflects_weight_concentration() -> None:
    equal = effective_sample_size([1.0, 1.0, 1.0, 1.0])
    concentrated = effective_sample_size([1.0, 1.0, 1.0, 9.0])

    assert equal == 4.0
    assert concentrated < equal
    assert round(concentrated, 3) == 1.714


def test_rubin_pool_combines_estimates_and_between_variance() -> None:
    pooled = rubin_pool([0.10, 0.20, 0.30], [0.05, 0.05, 0.05])

    assert math.isclose(pooled["estimate"], 0.20, rel_tol=1e-9)
    assert pooled["se"] > 0.05
    assert 0.0 < pooled["p_value"] < 1.0


def test_rubin_components_reports_fraction_missing_information() -> None:
    pooled = rubin_components([0.10, 0.20, 0.30], [0.05, 0.05, 0.05])

    assert math.isclose(pooled["estimate"], 0.20, rel_tol=1e-9)
    assert pooled["between_variance"] > 0
    assert 0.0 < pooled["fraction_missing_information"] < 1.0


def test_format_p_value_never_reports_zero() -> None:
    assert format_p_value(0.0) == "<0.001"
    assert format_p_value(0.0004) == "<0.001"
    assert format_p_value(0.01234) == "0.012"


def test_country_universe_category_defines_core_groups() -> None:
    assert mr.country_universe_category("AT") == "EU-27"
    assert mr.country_universe_category("NO") == "EEA country"
    assert mr.country_universe_category("CH") == "Switzerland"
    assert mr.country_universe_category("UK") == "UK"
    assert mr.country_universe_category("AL") == "Candidate/potential candidate"
    assert mr.country_universe_category("ZZ") == "Other Eurostat-available national unit"


def test_write_country_universe_table_reports_sample_inclusion(tmp_path, monkeypatch) -> None:
    outputs = tmp_path / "outputs"
    tables = tmp_path / "tables"
    processed = tmp_path / "processed"
    outputs.mkdir()
    tables.mkdir()
    processed.mkdir()
    monkeypatch.setattr(mr, "OUTPUTS", outputs)
    monkeypatch.setattr(mr, "TABLES", tables)
    monkeypatch.setattr(mr, "DATA_PROCESSED", processed)

    target = pd.DataFrame(
        {
            "geo": ["AT", "AT", "NO", "AL"],
            "year": [2020, 2021, 2020, 2020],
            "unmet_need_pc": [1.0, 1.2, 2.0, 3.0],
        }
    )
    complete = pd.DataFrame({"geo": ["AT", "NO"], "year": [2020, 2020]})
    pd.DataFrame({"geo": ["AT"], "year": [2020]}).to_csv(processed / "modeling_dataset_5a_with_splits.csv", index=False)

    out = mr.write_country_universe_table(target, complete)

    assert set(out["geo"]) == {"AT", "NO", "AL"}
    assert out.loc[out["geo"].eq("AT"), "universe_category"].iloc[0] == "EU-27"
    assert out.loc[out["geo"].eq("NO"), "universe_category"].iloc[0] == "EEA country"
    assert out.loc[out["geo"].eq("AL"), "in_complete_case_fe"].iloc[0] == "no"
    assert (outputs / "country_universe.csv").stat().st_size > 0
    assert (outputs / "country_universe_summary.csv").stat().st_size > 0
    assert (tables / "country_universe.tex").stat().st_size > 0


def test_imputation_matrix_excludes_raw_gdp_to_avoid_log_raw_contradiction() -> None:
    base = pd.DataFrame(
        {
            "geo": ["AT", "AT", "BE"],
            "year": [2020, 2021, 2020],
            "unmet_need_pc": [1.0, 1.1, 2.0],
            "log_gdp_per_capita": [10.0, None, 10.2],
            "gdp_per_capita_eur": [22000.0, None, 27000.0],
            "unemployment_rate_pc": [5.0, 5.5, 6.0],
            "poverty_or_social_exclusion_pc": [20.0, 21.0, 22.0],
            "government_health_expenditure_gdp_pc": [6.0, 6.2, 6.4],
            "compulsory_health_financing_gdp_pc": [5.0, 5.2, 5.4],
        }
    )

    matrix = mr.imputation_matrix(base, include_outcome=True, country_structure="group", year_effects=True)

    assert "log_gdp_per_capita" in matrix.columns
    assert "gdp_per_capita_eur" not in matrix.columns


def test_delta_shift_applies_only_to_originally_missing_values() -> None:
    base = pd.DataFrame(
        {
            "poverty_or_social_exclusion_pc": [20.0, None],
            "unemployment_rate_pc": [5.0, None],
            "log_gdp_per_capita": [10.0, None],
            "gdp_per_capita_eur": [math.exp(10.0), None],
        }
    )
    completed = pd.DataFrame(
        {
            "poverty_or_social_exclusion_pc": [20.0, 21.0],
            "unemployment_rate_pc": [5.0, 6.0],
            "log_gdp_per_capita": [10.0, 10.5],
            "gdp_per_capita_eur": [math.exp(10.0), math.exp(10.5)],
        }
    )

    shifted = mr.apply_delta_shift(
        completed,
        base,
        {
            "poverty_or_social_exclusion_pc": 5.0,
            "unemployment_rate_pc": 2.0,
            "gdp_per_capita_eur": -0.10,
        },
    )

    assert shifted.loc[0, "poverty_or_social_exclusion_pc"] == completed.loc[0, "poverty_or_social_exclusion_pc"]
    assert shifted.loc[1, "poverty_or_social_exclusion_pc"] == 26.0
    assert shifted.loc[0, "unemployment_rate_pc"] == completed.loc[0, "unemployment_rate_pc"]
    assert shifted.loc[1, "unemployment_rate_pc"] == 8.0
    assert shifted.loc[0, "log_gdp_per_capita"] == completed.loc[0, "log_gdp_per_capita"]
    assert shifted.loc[1, "log_gdp_per_capita"] < completed.loc[1, "log_gdp_per_capita"]


def test_write_mi_diagnostics_outputs_required_files(tmp_path, monkeypatch) -> None:
    outputs = tmp_path / "outputs"
    tables = tmp_path / "tables"
    figures = tmp_path / "figures"
    outputs.mkdir()
    tables.mkdir()
    figures.mkdir()
    monkeypatch.setattr(mr, "OUTPUTS", outputs)
    monkeypatch.setattr(mr, "TABLES", tables)
    monkeypatch.setattr(mr, "FIGURES", figures)

    target = pd.DataFrame(
        {
            "geo": ["A", "A", "B", "B"],
            "year": [2014, 2015, 2014, 2015],
            "poverty_or_social_exclusion_pc": [20.0, None, 25.0, None],
            "unemployment_rate_pc": [7.0, 8.0, None, 10.0],
        }
    )
    pd.DataFrame(
        [
            {
                "variant": "baseline",
                "variable": "poverty_or_social_exclusion_pc",
                "observed_n": 2,
                "imputed_n": 2,
                "observed_mean": 22.5,
                "imputed_mean": 24.0,
                "observed_p05": 20.25,
                "imputed_p05": 23.1,
                "observed_p95": 24.75,
                "imputed_p95": 24.9,
            },
            {
                "variant": "baseline",
                "variable": "unemployment_rate_pc",
                "observed_n": 3,
                "imputed_n": 1,
                "observed_mean": 8.33,
                "imputed_mean": 9.0,
                "observed_p05": 7.1,
                "imputed_p05": 9.0,
                "observed_p95": 9.8,
                "imputed_p95": 9.0,
            },
        ]
    ).to_csv(outputs / "mi_observed_vs_imputed_baseline.csv", index=False)
    pd.DataFrame(
        [
            {
                "variant": "baseline",
                "variable": "poverty_or_social_exclusion_pc",
                "lower_bound": 0.0,
                "upper_bound": 60.0,
                "imputed_n": 2,
                "imputed_min": 23.0,
                "imputed_max": 25.0,
                "outside_bounds": 0,
            },
            {
                "variant": "baseline",
                "variable": "unemployment_rate_pc",
                "lower_bound": 0.0,
                "upper_bound": 40.0,
                "imputed_n": 1,
                "imputed_min": 9.0,
                "imputed_max": 9.0,
                "outside_bounds": 0,
            },
        ]
    ).to_csv(outputs / "mi_plausibility_checks_baseline.csv", index=False)
    pd.DataFrame(
        {
            "imputation": [1, 2, 3],
            "variant": ["baseline", "baseline", "baseline"],
            "term": ["poverty_or_social_exclusion_pc"] * 3,
            "coef": [0.10, 0.20, 0.30],
            "se": [0.05, 0.05, 0.05],
            "p_value": [0.1, 0.05, 0.01],
            "nobs": [4, 4, 4],
            "countries": [2, 2, 2],
        }
    ).to_csv(outputs / "improved_mi_fe_results_baseline.csv", index=False)

    variants = pd.DataFrame({"variant": ["baseline"], "imputations": [3]})
    mr.write_mi_diagnostics(target, variants)

    diagnostics = pd.read_csv(outputs / "mi_diagnostics_summary.csv")
    fmi = pd.read_csv(outputs / "mi_fmi_poverty.csv")
    coef_dist = pd.read_csv(outputs / "mi_coefficient_distribution.csv")

    assert {"variable", "missing_pct", "outside_bounds"}.issubset(diagnostics.columns)
    assert diagnostics["outside_bounds"].sum() == 0
    assert 0.0 < fmi.loc[0, "fraction_missing_information"] < 1.0
    assert len(coef_dist) == 3
    assert (tables / "mi_diagnostics_summary.tex").stat().st_size > 0
    assert (figures / "mi_coefficient_distribution.pdf").stat().st_size > 0


def test_pmm_donor_diagnostics_reports_small_donor_pools() -> None:
    matrix = pd.DataFrame(
        {
            "x": [1.0, 2.0, None, None],
            "y": [1.0, 2.0, 3.0, None],
            "z": [1.0, 2.0, 3.0, 4.0],
        }
    )

    diagnostics = mr.pmm_donor_diagnostics(matrix, k_pmm=3)

    x = diagnostics[diagnostics["matrix_column"].eq("x")].iloc[0]
    y = diagnostics[diagnostics["matrix_column"].eq("y")].iloc[0]

    assert x["effective_donor_pool"] == 2
    assert x["donor_warning"] == "yes"
    assert y["effective_donor_pool"] == 3
    assert y["donor_warning"] == "no"
    assert "z" not in set(diagnostics["matrix_column"])


def test_mnar_tipping_point_outputs_grid_and_table(tmp_path, monkeypatch) -> None:
    outputs = tmp_path / "outputs"
    tables = tmp_path / "tables"
    figures = tmp_path / "figures"
    outputs.mkdir()
    tables.mkdir()
    figures.mkdir()
    monkeypatch.setattr(mr, "OUTPUTS", outputs)
    monkeypatch.setattr(mr, "TABLES", tables)
    monkeypatch.setattr(mr, "FIGURES", figures)

    rows = []
    for country_idx, geo in enumerate(["A", "B", "C", "D", "E", "F"]):
        for year in range(2015, 2021):
            poverty = 18.0 + country_idx + 0.25 * (year - 2015)
            rows.append(
                {
                    "geo": geo,
                    "year": year,
                    "unmet_need_pc": 1.0 + 0.10 * poverty + 0.1 * country_idx,
                    "log_gdp_per_capita": 10.0 + 0.02 * country_idx,
                    "gdp_per_capita_eur": math.exp(10.0 + 0.02 * country_idx),
                    "unemployment_rate_pc": 5.0 + 0.1 * country_idx,
                    "poverty_or_social_exclusion_pc": poverty if not (geo in {"E", "F"} and year >= 2018) else None,
                    "government_health_expenditure_gdp_pc": 5.0 + 0.05 * country_idx,
                    "compulsory_health_financing_gdp_pc": 4.0 + 0.05 * country_idx,
                }
            )
    target = pd.DataFrame(rows)

    out = mr.mnar_tipping_point_analysis(target, complete_case_coef=0.15, m=2, deltas=[0, 5])

    assert set(out["poverty_shift_pp"]) == {0.0, 5.0}
    assert (outputs / "mnar_tipping_point_results.csv").stat().st_size > 0
    assert (outputs / "mnar_tipping_point_fe_results.csv").stat().st_size > 0
    assert (tables / "mnar_tipping_point_results.tex").stat().st_size > 0
    assert (figures / "mnar_tipping_point_curve.pdf").stat().st_size > 0


def test_fe_feasibility_guard_rejects_tiny_samples() -> None:
    tiny = pd.DataFrame(
        {
            "geo": ["A", "A", "B"],
            "year": [2020, 2021, 2020],
            "unmet_need_pc": [1.0, 2.0, 3.0],
        }
    )

    feasible, reason = mr.feasible_fe_sample(tiny)

    assert not feasible
    assert reason.startswith("infeasible:")


def test_write_poverty_robustness_outputs_records_infeasible_splits(tmp_path, monkeypatch) -> None:
    outputs = tmp_path / "outputs"
    tables = tmp_path / "tables"
    figures = tmp_path / "figures"
    outputs.mkdir()
    tables.mkdir()
    figures.mkdir()
    monkeypatch.setattr(mr, "OUTPUTS", outputs)
    monkeypatch.setattr(mr, "TABLES", tables)
    monkeypatch.setattr(mr, "FIGURES", figures)
    monkeypatch.setattr(mr, "MIN_FE_ROWS", 10)
    monkeypatch.setattr(mr, "MIN_FE_COUNTRIES", 3)
    monkeypatch.setattr(mr, "MIN_FE_YEARS", 3)

    rows = []
    for country_idx, geo in enumerate(["A", "B", "C", "D"]):
        for year in range(2015, 2021):
            rows.append(
                {
                    "geo": geo,
                    "year": year,
                    "unmet_need_pc": float(country_idx + year - 2010),
                    "log_gdp_per_capita": 10.0 + country_idx * 0.1,
                    "unemployment_rate_pc": 6.0 + country_idx,
                    "poverty_or_social_exclusion_pc": 20.0 + country_idx + (year - 2015) * 0.2,
                    "government_health_expenditure_gdp_pc": 5.0 + country_idx * 0.1,
                    "compulsory_health_financing_gdp_pc": 4.0 + country_idx * 0.1,
                    "population_weight_year_norm": 0.25,
                }
            )
    target = pd.DataFrame(rows)
    improved_poverty = pd.Series(
        {
            "coef": -0.01,
            "se": 0.02,
            "p_value": 0.6,
            "mean_nobs": len(target),
            "mean_countries": target["geo"].nunique(),
        }
    )

    summary = mr.write_poverty_robustness_outputs(target, target, improved_poverty)

    assert (outputs / "poverty_robustness_summary.csv").stat().st_size > 0
    assert (outputs / "leave_one_country_out_poverty.csv").stat().st_size > 0
    assert (outputs / "measurement_break_2015_poverty.csv").stat().st_size > 0
    assert (tables / "poverty_robustness_summary.tex").stat().st_size > 0
    assert {"Baseline complete-case FE", "MI full target"}.issubset(set(summary["specification"]))
    assert any(summary["status"].astype(str).str.startswith("infeasible:"))


def test_write_fe_inference_outputs_reports_bootstrap_and_fit_stats(tmp_path, monkeypatch) -> None:
    outputs = tmp_path / "outputs"
    tables = tmp_path / "tables"
    outputs.mkdir()
    tables.mkdir()
    monkeypatch.setattr(mr, "OUTPUTS", outputs)
    monkeypatch.setattr(mr, "TABLES", tables)

    rows = []
    for country_idx, geo in enumerate(["A", "B", "C", "D", "E", "F"]):
        for year in range(2015, 2022):
            poverty = 15.0 + country_idx + 0.3 * (year - 2015)
            rows.append(
                {
                    "geo": geo,
                    "year": year,
                    "unmet_need_pc": 1.0 + 0.12 * poverty + country_idx * 0.1,
                    "log_gdp_per_capita": 10.0 + country_idx * 0.05,
                    "unemployment_rate_pc": 5.0 + 0.2 * country_idx,
                    "poverty_or_social_exclusion_pc": poverty,
                    "government_health_expenditure_gdp_pc": 5.0 + 0.1 * country_idx,
                    "compulsory_health_financing_gdp_pc": 4.0 + 0.1 * country_idx,
                }
            )
    sample = pd.DataFrame(rows)
    result = mr.fit_fe(sample)

    monkeypatch.setattr(
        mr,
        "wild_cluster_bootstrap",
        lambda df, term="poverty_or_social_exclusion_pc", reps=499, seed=mr.RANDOM_SEED: {
            "term": term,
            "bootstrap_reps_requested": reps,
            "bootstrap_reps_used": 11,
            "wild_cluster_p_value": 0.2,
            "wild_cluster_ci_low": -0.1,
            "wild_cluster_ci_high": 0.3,
        },
    )
    monkeypatch.setattr(mr, "driscoll_kraay_result", lambda df, maxlags=1: mr.fit_fe(df))

    out = mr.write_fe_inference_outputs(sample, result)

    assert out.loc[0, "bootstrap_reps_used"] == 11
    assert out.loc[0, "wild_cluster_p_value"] == 0.2
    assert (outputs / "fe_inference_comparison.csv").stat().st_size > 0
    assert (outputs / "fe_fit_diagnostics.csv").stat().st_size > 0
    assert (tables / "fe_inference_comparison.tex").stat().st_size > 0
    assert (tables / "fe_fit_diagnostics.tex").stat().st_size > 0


def test_wild_cluster_bootstrap_is_reproducible_with_fixed_seed() -> None:
    rows = []
    for country_idx, geo in enumerate(["A", "B", "C", "D", "E", "F", "G", "H"]):
        for year in range(2015, 2022):
            poverty = 18.0 + 0.7 * country_idx + 0.25 * (year - 2015)
            rows.append(
                {
                    "geo": geo,
                    "year": year,
                    "unmet_need_pc": 1.5 + 0.09 * poverty + 0.03 * country_idx + 0.01 * (year - 2015),
                    "log_gdp_per_capita": 10.0 + 0.03 * country_idx + 0.01 * (year - 2015),
                    "unemployment_rate_pc": 5.0 + 0.2 * country_idx + 0.03 * (year - 2015),
                    "poverty_or_social_exclusion_pc": poverty,
                    "government_health_expenditure_gdp_pc": 5.0 + 0.04 * country_idx,
                    "compulsory_health_financing_gdp_pc": 4.0 + 0.04 * country_idx,
                }
            )
    sample = pd.DataFrame(rows)

    first = mr.wild_cluster_bootstrap(sample, reps=31, seed=123)
    second = mr.wild_cluster_bootstrap(sample, reps=31, seed=123)

    assert first == second
    assert first["bootstrap_reps_requested"] == 31
    assert first["bootstrap_reps_used"] == 31
    assert 0.0 <= first["wild_cluster_p_value"] <= 1.0


def test_write_main_sensitivity_ladder_contains_core_estimands(tmp_path, monkeypatch) -> None:
    outputs = tmp_path / "outputs"
    tables = tmp_path / "tables"
    figures = tmp_path / "figures"
    outputs.mkdir()
    tables.mkdir()
    figures.mkdir()
    monkeypatch.setattr(mr, "OUTPUTS", outputs)
    monkeypatch.setattr(mr, "TABLES", tables)
    monkeypatch.setattr(mr, "FIGURES", figures)
    monkeypatch.setattr(mr, "MIN_FE_ROWS", 10)
    monkeypatch.setattr(mr, "MIN_FE_COUNTRIES", 3)
    monkeypatch.setattr(mr, "MIN_FE_YEARS", 3)

    rows = []
    for country_idx, geo in enumerate(["AT", "BE", "BG", "NO", "AL"]):
        for year in range(2015, 2021):
            poverty = 18.0 + country_idx * 0.8 + (year - 2015) * 0.4
            rows.append(
                {
                    "geo": geo,
                    "year": year,
                    "unmet_need_pc": 2.0 + 0.15 * poverty + 0.05 * country_idx,
                    "log_gdp_per_capita": 10.0 + country_idx * 0.04 + (year - 2015) * 0.01,
                    "unemployment_rate_pc": 6.0 + country_idx * 0.2 + (year - 2015) * 0.05,
                    "poverty_or_social_exclusion_pc": poverty,
                    "government_health_expenditure_gdp_pc": 5.0 + country_idx * 0.05,
                    "compulsory_health_financing_gdp_pc": 4.0 + country_idx * 0.05,
                    "population_weight_year_norm": 0.2,
                }
            )
    target = pd.DataFrame(rows)
    complete = mr.model_sample(target)
    complete_fit = mr.fit_fe(complete)
    pop_fit = mr.fit_fe(complete, weights=complete["population_weight_year_norm"].to_numpy())
    ipw_fit = complete_fit
    improved = pd.Series({"coef": 0.01, "se": 0.03, "p_value": 0.7, "mean_nobs": len(target), "mean_countries": target["geo"].nunique()})
    mnar = pd.DataFrame(
        [
            {"variant": "mnar_pessimistic_combo", "coef": 0.02, "se": 0.03, "p_value": 0.5, "mean_nobs": len(target), "mean_countries": target["geo"].nunique()},
            {"variant": "mnar_optimistic_combo", "coef": 0.00, "se": 0.03, "p_value": 0.9, "mean_nobs": len(target), "mean_countries": target["geo"].nunique()},
        ]
    )
    poverty_summary = mr.write_poverty_robustness_outputs(target, complete, improved)

    ladder = mr.write_main_sensitivity_ladder(target, complete, complete_fit, pop_fit, complete, ipw_fit, improved, mnar, poverty_summary)

    assert {"Pooled complete-case", "Country + year FE", "EU-27 FE", "IPW", "MAR MI", "MNAR pessimistic", "MNAR optimistic"}.issubset(set(ladder["step"]))
    assert any(ladder["status"].astype(str).str.startswith("infeasible:"))
    assert (outputs / "main_sensitivity_ladder.csv").stat().st_size > 0
    assert (tables / "main_sensitivity_ladder.tex").stat().st_size > 0
