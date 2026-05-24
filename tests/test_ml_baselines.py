from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import run_step5_ml_analysis as ml
from run_step5_ml_analysis import FEATURES, FORECAST_SOURCE_FEATURES, OUTCOME, evaluate_naive_baselines, model_specs


def test_naive_baselines_include_previous_year_prediction(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(ml, "OUTPUTS", tmp_path)
    monkeypatch.setattr(ml, "TABLES", tmp_path)
    train = pd.DataFrame(
        {
            "geo": ["A", "A", "B", "B"],
            "year": [2018, 2019, 2018, 2019],
            OUTCOME: [1.0, 1.5, 3.0, 3.5],
            "lag1_unmet_need_pc": [0.8, 1.0, 2.8, 3.0],
        }
    )
    for col in [c for c in FEATURES if c != "lag1_unmet_need_pc"]:
        train[col] = 1.0
    test = pd.DataFrame(
        {
            "geo": ["A", "B"],
            "year": [2020, 2020],
            OUTCOME: [2.0, 4.0],
            "lag1_unmet_need_pc": [1.5, 3.5],
        }
    )
    for col in [c for c in FEATURES if c != "lag1_unmet_need_pc"]:
        test[col] = 1.0

    out = evaluate_naive_baselines(train, test)

    assert "Previous-year outcome" in set(out["model"])
    assert out["test_mae"].notna().all()


def test_prediction_features_are_lagged_only() -> None:
    assert FEATURES[0] == "lag1_unmet_need_pc"
    assert all(feature.startswith("lag1_") for feature in FEATURES)
    for source_feature in FORECAST_SOURCE_FEATURES:
        assert source_feature not in FEATURES
        assert f"lag1_{source_feature}" in FEATURES


def test_ml_specs_exclude_demoted_models() -> None:
    specs = model_specs()
    assert "MLP" not in specs
    assert "Gradient Boosting" not in specs
    assert "OLS" not in specs
    assert {"Ridge", "Lasso", "Elastic Net", "Random Forest"}.issubset(specs)
