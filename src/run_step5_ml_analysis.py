from __future__ import annotations

import json
import math
import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.base import clone
from sklearn.compose import TransformedTargetRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.inspection import permutation_importance
from sklearn.linear_model import ElasticNet, Lasso, LinearRegression, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GridSearchCV, GroupKFold, TimeSeriesSplit, learning_curve
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

ROOT = Path(__file__).resolve().parents[1]
DATA_PROCESSED = ROOT / "data" / "processed"
OUTPUTS = ROOT / "outputs"
FIGURES = ROOT / "figures"
TABLES = ROOT / "tables"
ERROR_LOG = OUTPUTS / "analysis_errors.log"

for folder in [DATA_PROCESSED, OUTPUTS, FIGURES, TABLES]:
    folder.mkdir(parents=True, exist_ok=True)

RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)

OUTCOME = "unmet_need_pc"
CONTEMPORANEOUS_FEATURES = [
    "log_gdp_per_capita",
    "gdp_per_capita_eur",
    "gdp_per_capita_growth",
    "unemployment_rate_pc",
    "unemployment_rate_change",
    "long_term_unemployment_rate_pc",
    "poverty_or_social_exclusion_pc",
    "gini_income",
    "government_health_expenditure_gdp_pc",
    "compulsory_health_financing_gdp_pc",
    "oop_health_expenditure_share_pc",
    "physicians_per_100k",
    "physicians_per_100k_lag1",
    "hospital_beds_per_100k",
]
FORECAST_SOURCE_FEATURES = [
    "log_gdp_per_capita",
    "unemployment_rate_pc",
    "poverty_or_social_exclusion_pc",
    "government_health_expenditure_gdp_pc",
    "compulsory_health_financing_gdp_pc",
]
FEATURES = ["lag1_unmet_need_pc"] + [f"lag1_{feature}" for feature in FORECAST_SOURCE_FEATURES]


def log_error(message: str) -> None:
    with ERROR_LOG.open("a", encoding="utf-8") as f:
        f.write(message.rstrip() + "\n")


def write_latex(df: pd.DataFrame, path: Path, caption: str, label: str) -> None:
    path.write_text(
        df.to_latex(
            index=False,
            escape=True,
            caption=caption,
            label=label,
            float_format=lambda x: f"{x:.3f}",
            na_rep="",
        ),
        encoding="utf-8",
    )


def write_latex_fragment(df: pd.DataFrame, path: Path) -> None:
    column_format = "@{}" + "".join("l" if pd.api.types.is_object_dtype(df[col]) else "r" for col in df.columns) + "@{}"
    path.write_text(
        df.to_latex(
            index=False,
            escape=True,
            column_format=column_format,
            float_format=lambda x: f"{x:.3f}",
            na_rep="",
        ),
        encoding="utf-8",
    )


def safe_name(name: str) -> str:
    return name.lower().replace(" ", "_").replace("-", "_")


def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return math.sqrt(mean_squared_error(y_true, y_pred))


def make_time_split() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    source = pd.read_csv(DATA_PROCESSED / "panel_features_v2-3.csv").sort_values(["geo", "year"])
    missing = [v for v in FORECAST_SOURCE_FEATURES + [OUTCOME, "geo", "year"] if v not in source.columns]
    if missing:
        raise ValueError(f"Missing required ML source columns: {missing}")
    df = source[["geo", "year", OUTCOME] + FORECAST_SOURCE_FEATURES].copy()
    df["lag1_unmet_need_pc"] = df.groupby("geo")[OUTCOME].shift(1)
    for feature in FORECAST_SOURCE_FEATURES:
        df[f"lag1_{feature}"] = df.groupby("geo")[feature].shift(1)
    df = df.dropna(subset=FEATURES + [OUTCOME]).copy()
    df = df.sort_values(["year", "geo"]).reset_index(drop=True)

    existing_note = "Forecast split is built from lagged predictors in panel_features_v2-3.csv."

    df["time_split"] = np.where(df["year"].between(2016, 2020), "train", np.where(df["year"].between(2021, 2023), "test", "exclude"))
    split_df = df[df["time_split"].isin(["train", "test"])].copy()
    split_df.to_csv(DATA_PROCESSED / "modeling_dataset_time_split.csv", index=False)

    train = split_df[split_df["time_split"] == "train"].copy()
    test = split_df[split_df["time_split"] == "test"].copy()

    note = [
        "Created one-year-ahead prediction dataset using lagged predictors only.",
        existing_note,
        "",
        "Created time-based split for all Step 5 models.",
        f"Train: years 2016-2020, rows {len(train)}, countries {train['geo'].nunique()}",
        f"Test: years 2021-2023, rows {len(test)}, countries {test['geo'].nunique()}",
        "Saved: data/processed/modeling_dataset_time_split.csv",
    ]
    (OUTPUTS / "ml_split_confirmation.txt").write_text("\n".join(note) + "\n", encoding="utf-8")
    return split_df, train, test


def linear_pipeline(estimator) -> Pipeline:
    return Pipeline([("scale", StandardScaler()), ("model", estimator)])


def model_specs():
    specs = {
        "Ridge": {
            "family": "linear",
            "estimator": linear_pipeline(Ridge(random_state=RANDOM_SEED)),
            "grid": {"model__alpha": [0.01, 0.1, 1, 10, 100, 1000]},
        },
        "Lasso": {
            "family": "linear",
            "estimator": linear_pipeline(Lasso(random_state=RANDOM_SEED, max_iter=20000)),
            "grid": {"model__alpha": [0.001, 0.01, 0.1, 1, 10]},
        },
        "Elastic Net": {
            "family": "linear",
            "estimator": linear_pipeline(ElasticNet(random_state=RANDOM_SEED, max_iter=20000)),
            "grid": {"model__alpha": [0.01, 0.1, 1, 10], "model__l1_ratio": [0.2, 0.5, 0.8]},
        },
        "Random Forest": {
            "family": "tree",
            "estimator": RandomForestRegressor(random_state=RANDOM_SEED, n_jobs=-1),
            "grid": {
                "n_estimators": [100, 200, 500],
                "max_depth": [3, 5, None],
                "min_samples_leaf": [1, 3, 5],
            },
        },
    }
    try:
        from xgboost import XGBRegressor

        specs["XGBoost"] = {
            "family": "tree",
            "estimator": XGBRegressor(
                objective="reg:squarederror",
                random_state=RANDOM_SEED,
                n_jobs=1,
                verbosity=0,
            ),
            "grid": {
                "n_estimators": [100, 200, 500],
                "learning_rate": [0.01, 0.05, 0.1],
                "max_depth": [2, 3, 4],
            },
        }
    except Exception as exc:
        log_error(f"Step 5b XGBoost skipped: xgboost unavailable ({exc}).")
    return specs


def hyperparameter_grid_output() -> None:
    rows = []
    for name, spec in model_specs().items():
        grid = spec["grid"]
        if not grid:
            rows.append({"model": name, "parameter": "none", "values": "default estimator"})
        for parameter, values in grid.items():
            rows.append({"model": name, "parameter": parameter, "values": json.dumps(list(values))})
    out = pd.DataFrame(rows)
    out.to_csv(OUTPUTS / "ml_hyperparameter_grid.csv", index=False)
    write_latex_fragment(out, TABLES / "ml_hyperparameter_grid.tex")


def cv_train_models(train: pd.DataFrame, test: pd.DataFrame):
    x_train = train[FEATURES]
    y_train = train[OUTCOME]
    x_test = test[FEATURES]
    y_test = test[OUTCOME]
    cv = TimeSeriesSplit(n_splits=5)

    rows = []
    fitted = {}
    for name, spec in model_specs().items():
        try:
            estimator = spec["estimator"]
            grid = spec["grid"]
            if grid:
                search = GridSearchCV(
                    estimator,
                    grid,
                    scoring="neg_mean_absolute_error",
                    cv=cv,
                    n_jobs=-1 if name != "XGBoost" else 1,
                    refit=True,
                    error_score="raise",
                )
                search.fit(x_train, y_train)
                best = search.best_estimator_
                best_params = search.best_params_
                scores = -search.cv_results_["mean_test_score"][search.best_index_]
                split_scores = [
                    -search.cv_results_[f"split{i}_test_score"][search.best_index_]
                    for i in range(cv.get_n_splits())
                ]
                cv_mean = float(scores)
                cv_std = float(np.std(split_scores, ddof=1))
            else:
                split_scores = []
                for tr_idx, val_idx in cv.split(x_train):
                    fold_model = clone(estimator)
                    fold_model.fit(x_train.iloc[tr_idx], y_train.iloc[tr_idx])
                    pred = fold_model.predict(x_train.iloc[val_idx])
                    split_scores.append(mean_absolute_error(y_train.iloc[val_idx], pred))
                best = clone(estimator).fit(x_train, y_train)
                best_params = {}
                cv_mean = float(np.mean(split_scores))
                cv_std = float(np.std(split_scores, ddof=1))

            pred = best.predict(x_test)
            rows.append(
                {
                    "model": name,
                    "family": spec["family"],
                    "best_params": json.dumps(best_params, sort_keys=True),
                    "cv_mae_mean": cv_mean,
                    "cv_mae_std": cv_std,
                    "test_mae": mean_absolute_error(y_test, pred),
                    "test_rmse": rmse(y_test.to_numpy(), pred),
                    "test_r2": r2_score(y_test, pred),
                }
            )
            fitted[name] = best
        except Exception as exc:
            log_error(f"Step 5b {name} failed: {exc}")

    perf = pd.DataFrame(rows).sort_values("test_mae").reset_index(drop=True)
    perf.to_csv(OUTPUTS / "ml_performance_full.csv", index=False)
    table = perf[["model", "family", "cv_mae_mean", "cv_mae_std", "test_mae", "test_rmse", "test_r2"]].rename(
        columns={
            "model": "Model",
            "family": "Family",
            "cv_mae_mean": "CV MAE",
            "cv_mae_std": "CV SD",
            "test_mae": "Test MAE",
            "test_rmse": "RMSE",
            "test_r2": "R2",
        }
    )
    write_latex_fragment(table, TABLES / "ml_model_performance_full.tex")
    return perf, fitted


def evaluate_naive_baselines(train: pd.DataFrame, test: pd.DataFrame) -> pd.DataFrame:
    train = train.sort_values(["geo", "year"]).copy()
    test = test.sort_values(["geo", "year"]).copy()
    global_mean = float(train[OUTCOME].mean())
    latest_by_country = train.sort_values("year").groupby("geo")[OUTCOME].last()
    country_mean = train.groupby("geo")[OUTCOME].mean()
    rolling_by_country = train.sort_values("year").groupby("geo").tail(3).groupby("geo")[OUTCOME].mean()
    year_mean = train.groupby("year")[OUTCOME].mean()
    last_train_year_mean = float(year_mean.sort_index().iloc[-1])

    rows = []
    predictions: dict[str, np.ndarray] = {}
    predictions["Previous-year outcome"] = test["lag1_unmet_need_pc"].fillna(global_mean).to_numpy()
    predictions["Last observed country value"] = test["geo"].map(latest_by_country).fillna(global_mean).to_numpy()
    predictions["Country mean"] = test["geo"].map(country_mean).fillna(global_mean).to_numpy()
    predictions["Rolling country mean"] = test["geo"].map(rolling_by_country).fillna(global_mean).to_numpy()
    predictions["Global mean"] = np.repeat(global_mean, len(test))
    predictions["Last training-year mean"] = np.repeat(last_train_year_mean, len(test))

    ar_model = LinearRegression().fit(train[["lag1_unmet_need_pc"]], train[OUTCOME])
    predictions["AR(1) linear"] = ar_model.predict(test[["lag1_unmet_need_pc"]])
    ridge_lag = linear_pipeline(Ridge(alpha=1.0, random_state=RANDOM_SEED)).fit(train[FEATURES], train[OUTCOME])
    predictions["Ridge with lagged predictors"] = ridge_lag.predict(test[FEATURES])

    for name, pred in predictions.items():
        rows.append(
            {
                "model": name,
                "family": "naive/statistical baseline",
                "test_mae": mean_absolute_error(test[OUTCOME], pred),
                "test_rmse": rmse(test[OUTCOME].to_numpy(), pred),
                "test_r2": r2_score(test[OUTCOME], pred),
                "n_test": len(test),
            }
        )
    out = pd.DataFrame(rows).sort_values("test_mae")
    out.to_csv(OUTPUTS / "ml_naive_baselines.csv", index=False)
    table = out.copy()
    table["Model"] = table["model"]
    table["MAE"] = table["test_mae"].map(lambda x: f"{x:.3f}")
    table["RMSE"] = table["test_rmse"].map(lambda x: f"{x:.3f}")
    table["R2"] = table["test_r2"].map(lambda x: f"{x:.3f}")
    write_latex_fragment(table[["Model", "MAE", "RMSE", "R2"]], TABLES / "ml_naive_baselines.tex")
    return out


def benchmark_decision(perf: pd.DataFrame, baselines: pd.DataFrame) -> None:
    best_flexible = perf[perf["family"].isin(["tree"])].sort_values("test_mae").head(1)
    best_baseline = baselines.sort_values("test_mae").head(1)
    if best_flexible.empty or best_baseline.empty:
        decision = "ML chapter demotion decision unavailable because a comparison table is missing."
    else:
        flex = best_flexible.iloc[0]
        base = best_baseline.iloc[0]
        improvement = float(base["test_mae"] - flex["test_mae"])
        if improvement > 0.10:
            verdict = "retain as cautious predictive extension"
        else:
            verdict = "demote to negative-result benchmark section"
        decision = (
            f"Best flexible model: {flex['model']} MAE {flex['test_mae']:.3f}\n"
            f"Best naive/statistical baseline: {base['model']} MAE {base['test_mae']:.3f}\n"
            f"MAE improvement: {improvement:.3f}\n"
            f"Decision rule: flexible models must improve MAE by more than 0.10 percentage points.\n"
            f"Recommended interpretation: {verdict}.\n"
        )
    (OUTPUTS / "ml_benchmark_decision.txt").write_text(decision, encoding="utf-8")


def bootstrap_test_mae(test: pd.DataFrame, fitted: dict[str, object], n_boot: int = 1000) -> pd.DataFrame:
    rng = np.random.default_rng(RANDOM_SEED)
    y = test[OUTCOME].to_numpy()
    rows = []
    for name, model in fitted.items():
        pred = model.predict(test[FEATURES])
        abs_err = np.abs(y - pred)
        boot = []
        for _ in range(n_boot):
            idx = rng.integers(0, len(abs_err), len(abs_err))
            boot.append(float(abs_err[idx].mean()))
        rows.append(
            {
                "model": name,
                "test_mae": float(abs_err.mean()),
                "mae_ci_low": float(np.quantile(boot, 0.025)),
                "mae_ci_high": float(np.quantile(boot, 0.975)),
                "bootstrap_replicates": n_boot,
            }
        )
    out = pd.DataFrame(rows).sort_values("test_mae")
    out.to_csv(OUTPUTS / "ml_test_mae_bootstrap_ci.csv", index=False)
    table = out.rename(
        columns={
            "model": "Model",
            "test_mae": "MAE",
            "mae_ci_low": "2.5\\%",
            "mae_ci_high": "97.5\\%",
        }
    )[["Model", "MAE", "2.5\\%", "97.5\\%"]]
    write_latex_fragment(table, TABLES / "ml_test_mae_bootstrap_ci.tex")
    return out


def paired_tree_mae_differences(test: pd.DataFrame, fitted: dict[str, object], n_boot: int = 1000) -> pd.DataFrame:
    rng = np.random.default_rng(RANDOM_SEED + 1)
    names = [name for name in ["Random Forest", "XGBoost"] if name in fitted]
    if len(names) < 2:
        out = pd.DataFrame(
            [
                {
                    "comparison": "not available",
                    "mean_mae_difference": np.nan,
                    "ci_low": np.nan,
                    "ci_high": np.nan,
                    "interpretation": "requires both Random Forest and XGBoost",
                }
            ]
        )
        out.to_csv(OUTPUTS / "ml_paired_tree_mae_differences.csv", index=False)
        table = out.rename(
            columns={
                "comparison": "Comparison",
                "mean_mae_difference": "Mean diff.",
                "ci_low": "2.5\\%",
                "ci_high": "97.5\\%",
            }
        )[["Comparison", "Mean diff.", "2.5\\%", "97.5\\%"]]
        write_latex_fragment(table, TABLES / "ml_paired_tree_mae_differences.tex")
        return out
    errors = {name: np.abs(test[OUTCOME].to_numpy() - fitted[name].predict(test[FEATURES])) for name in names}
    rows = []
    for i, left in enumerate(names):
        for right in names[i + 1 :]:
            diff = errors[left] - errors[right]
            boot = []
            for _ in range(n_boot):
                idx = rng.integers(0, len(diff), len(diff))
                boot.append(float(diff[idx].mean()))
            rows.append(
                {
                    "comparison": f"{left} minus {right}",
                    "mean_mae_difference": float(diff.mean()),
                    "ci_low": float(np.quantile(boot, 0.025)),
                    "ci_high": float(np.quantile(boot, 0.975)),
                    "interpretation": "negative favors left model; positive favors right model",
                }
            )
    out = pd.DataFrame(rows)
    out.to_csv(OUTPUTS / "ml_paired_tree_mae_differences.csv", index=False)
    table = out.copy()
    table["comparison"] = table["comparison"].str.replace("Random Forest", "RF", regex=False)
    table["comparison"] = table["comparison"].str.replace("XGBoost", "XGB", regex=False)
    table = table.rename(
        columns={
            "comparison": "Comparison",
            "mean_mae_difference": "Mean diff.",
            "ci_low": "2.5\\%",
            "ci_high": "97.5\\%",
        }
    )[["Comparison", "Mean diff.", "2.5\\%", "97.5\\%"]]
    write_latex_fragment(table, TABLES / "ml_paired_tree_mae_differences.tex")
    return out


def country_holdout_evaluation(split_df: pd.DataFrame, fitted: dict[str, object]) -> pd.DataFrame:
    eval_df = split_df.dropna(subset=FEATURES + [OUTCOME, "geo"]).copy()
    countries = eval_df["geo"].nunique()
    if countries < 3:
        raise ValueError("Country-holdout evaluation requires at least three countries.")
    splitter = GroupKFold(n_splits=min(5, countries))
    model_names = [name for name in ["Ridge", "Lasso", "Elastic Net", "Random Forest", "XGBoost"] if name in fitted]
    rows = []
    for model_name in model_names:
        base_model = fitted[model_name]
        for fold, (train_idx, test_idx) in enumerate(splitter.split(eval_df[FEATURES], eval_df[OUTCOME], groups=eval_df["geo"]), start=1):
            train_fold = eval_df.iloc[train_idx]
            test_fold = eval_df.iloc[test_idx]
            model = clone(base_model)
            model.fit(train_fold[FEATURES], train_fold[OUTCOME])
            pred = model.predict(test_fold[FEATURES])
            rows.append(
                {
                    "model": model_name,
                    "fold": fold,
                    "heldout_countries": ",".join(sorted(test_fold["geo"].unique())),
                    "mae": mean_absolute_error(test_fold[OUTCOME], pred),
                    "rmse": rmse(test_fold[OUTCOME].to_numpy(), pred),
                    "n_train": len(train_fold),
                    "n_test": len(test_fold),
                    "countries_test": test_fold["geo"].nunique(),
                }
            )
    fold_out = pd.DataFrame(rows)
    fold_out.to_csv(OUTPUTS / "ml_country_holdout_fold_results.csv", index=False)
    summary = (
        fold_out.groupby("model", as_index=False)
        .agg(mean_mae=("mae", "mean"), sd_mae=("mae", "std"), mean_rmse=("rmse", "mean"), folds=("fold", "count"))
        .sort_values("mean_mae")
    )
    summary.to_csv(OUTPUTS / "ml_country_holdout_summary.csv", index=False)
    write_latex_fragment(summary, TABLES / "ml_country_holdout_summary.tex")
    return summary


def set_random_state(estimator, seed: int):
    estimator = clone(estimator)
    params = estimator.get_params()
    if "random_state" in params:
        estimator.set_params(random_state=seed)
    for key in params:
        if key.endswith("__random_state"):
            estimator.set_params(**{key: seed})
    return estimator


def expanding_window(split_df: pd.DataFrame, fitted: dict[str, object]) -> None:
    model_names = ["Ridge", "Lasso", "Elastic Net", "Random Forest", "XGBoost"]
    windows = [
        (2017, 2018),
        (2018, 2019),
        (2019, 2020),
        (2020, 2021),
        (2021, 2022),
        (2022, 2023),
    ]
    rows = []
    for model_name in model_names:
        if model_name not in fitted:
            log_error(f"Step 5d skipped {model_name}: model not fitted.")
            continue
        base_model = fitted[model_name]
        for train_end, test_year in windows:
            train = split_df[split_df["year"].between(2015, train_end)].copy()
            test = split_df[split_df["year"] == test_year].copy()
            if train.empty or test.empty:
                continue
            model = clone(base_model)
            model.fit(train[FEATURES], train[OUTCOME])
            pred = model.predict(test[FEATURES])
            rows.append(
                {
                    "model": model_name,
                    "train_start": 2015,
                    "train_end": train_end,
                    "test_year": test_year,
                    "mae": mean_absolute_error(test[OUTCOME], pred),
                    "n_train": len(train),
                    "n_test": len(test),
                }
            )
    out = pd.DataFrame(rows)
    out.to_csv(OUTPUTS / "ml_expanding_window_results.csv", index=False)

    plt.figure(figsize=(8, 4.8))
    sns.lineplot(data=out, x="test_year", y="mae", hue="model", marker="o", palette="colorblind")
    plt.xlabel("Test year")
    plt.ylabel("MAE")
    plt.grid(axis="y", alpha=0.25)
    plt.tight_layout()
    plt.savefig(FIGURES / "ml_expanding_window_validation.pdf", dpi=300)
    plt.close()


def get_feature_importance(model) -> np.ndarray:
    if hasattr(model, "feature_importances_"):
        return np.asarray(model.feature_importances_)
    if isinstance(model, Pipeline) and hasattr(model[-1], "feature_importances_"):
        return np.asarray(model[-1].feature_importances_)
    raise ValueError("Model has no impurity feature_importances_.")


def best_tree_model(perf: pd.DataFrame, fitted: dict[str, object]) -> tuple[str, object]:
    candidates = perf[perf["model"].isin(["Random Forest", "XGBoost"])].sort_values("test_mae")
    if candidates.empty:
        raise ValueError("No RF/XGBoost tree model available.")
    name = candidates.iloc[0]["model"]
    return str(name), fitted[str(name)]


def feature_importance_outputs(best_name: str, best_model, train: pd.DataFrame, test: pd.DataFrame) -> None:
    impurity = get_feature_importance(best_model)
    imp_df = pd.DataFrame({"feature": FEATURES, "importance": impurity, "model_name": best_name}).sort_values("importance", ascending=False)
    imp_df.to_csv(OUTPUTS / "tree_feature_importance_final.csv", index=False)

    perm = permutation_importance(
        best_model,
        test[FEATURES],
        test[OUTCOME],
        n_repeats=30,
        random_state=RANDOM_SEED,
        scoring="neg_mean_absolute_error",
        n_jobs=-1,
    )
    perm_df = pd.DataFrame(
        {
            "feature": FEATURES,
            "mean_importance": perm.importances_mean,
            "std_importance": perm.importances_std,
        }
    ).sort_values("mean_importance", ascending=False)
    perm_df.to_csv(OUTPUTS / "permutation_importance_final.csv", index=False)

    compare = imp_df[["feature", "importance"]].merge(perm_df[["feature", "mean_importance"]], on="feature")
    top_features = compare.assign(score=compare["importance"].rank(ascending=False) + compare["mean_importance"].rank(ascending=False)).sort_values("score").head(10)["feature"]
    plot_df = compare[compare["feature"].isin(top_features)].melt(
        id_vars="feature",
        value_vars=["importance", "mean_importance"],
        var_name="importance_type",
        value_name="importance_value",
    )
    plot_df["importance_type"] = plot_df["importance_type"].map({"importance": "Impurity", "mean_importance": "Permutation"})
    plt.figure(figsize=(9, 5.2))
    sns.barplot(data=plot_df, y="feature", x="importance_value", hue="importance_type", palette="colorblind")
    plt.xlabel("Importance")
    plt.ylabel("")
    plt.title("Impurity-based vs permutation feature importance, best tree model, test set")
    plt.tight_layout()
    plt.savefig(FIGURES / "ml_importance_comparison.pdf", dpi=300)
    plt.close()

    stability_rows = []
    rankings = []
    for seed in range(20):
        model = set_random_state(best_model, seed)
        model.fit(train[FEATURES], train[OUTCOME])
        vals = get_feature_importance(model)
        order = pd.Series(vals, index=FEATURES).rank(ascending=False, method="min")
        rankings.append(order)
        for feature, value in zip(FEATURES, vals):
            stability_rows.append({"seed": seed, "feature": feature, "importance": value, "rank": int(order[feature])})
    stability_long = pd.DataFrame(stability_rows)
    stability = (
        stability_long.groupby("feature", as_index=False)
        .agg(mean_importance=("importance", "mean"), std_importance=("importance", "std"))
    )
    stability["cv_coefficient"] = stability["std_importance"] / stability["mean_importance"].replace(0, np.nan)
    stability = stability.sort_values("mean_importance", ascending=False)
    stability.to_csv(OUTPUTS / "ml_importance_stability.csv", index=False)

    monitored_feature = "lag1_poverty_or_social_exclusion_pc"
    top3_all = bool((stability_long[stability_long["feature"] == monitored_feature]["rank"] <= 3).all())
    top3_count = int((stability_long[stability_long["feature"] == monitored_feature]["rank"] <= 3).sum())
    note = (
        f"Best tree model: {best_name}\n"
        f"{monitored_feature} ranked top 3 in {top3_count}/20 runs.\n"
        f"Consistently top 3 across all 20 runs: {top3_all}\n"
    )
    (OUTPUTS / "ml_importance_stability_note.txt").write_text(note, encoding="utf-8")
    if not top3_all:
        (OUTPUTS / "ml_importance_caution.txt").write_text(
            f"{monitored_feature} was not consistently top 3 across all 20 runs; feature importance is model inspection only.\n",
            encoding="utf-8",
        )

    plt.figure(figsize=(8.5, 5.8))
    plot_stab = stability.head(14)
    plt.barh(plot_stab["feature"], plot_stab["mean_importance"], xerr=plot_stab["std_importance"], color="#0072B2", alpha=0.85)
    plt.gca().invert_yaxis()
    plt.xlabel("Mean impurity importance across 20 seeds")
    plt.ylabel("")
    plt.tight_layout()
    plt.savefig(FIGURES / "ml_importance_stability.pdf", dpi=300)
    plt.close()


def residual_outputs(best_name: str, best_model, ridge_model, test: pd.DataFrame) -> None:
    for model_name, model in [(best_name, best_model), ("Ridge", ridge_model)]:
        if model is None:
            log_error(f"Step 5j skipped residuals for {model_name}: model unavailable.")
            continue
        pred = model.predict(test[FEATURES])
        residual = test[OUTCOME].to_numpy() - pred
        out = pd.DataFrame(
            {
                "country": test["geo"].values,
                "year": test["year"].values,
                "actual": test[OUTCOME].values,
                "predicted": pred,
                "residual": residual,
            }
        )
        name = safe_name(model_name)
        out.to_csv(OUTPUTS / f"ml_test_residuals_{name}.csv", index=False)

        lo = min(out["actual"].min(), out["predicted"].min())
        hi = max(out["actual"].max(), out["predicted"].max())
        plt.figure(figsize=(5.5, 5.2))
        sns.scatterplot(data=out, x="actual", y="predicted", hue="year", palette="viridis", legend=False)
        plt.plot([lo, hi], [lo, hi], color="black", linestyle="--", linewidth=1)
        plt.xlabel("Actual unmet medical need (%)")
        plt.ylabel("Predicted unmet medical need (%)")
        plt.tight_layout()
        plt.savefig(FIGURES / f"ml_actual_vs_predicted_{name}.pdf", dpi=300)
        plt.close()

        plt.figure(figsize=(6.2, 4.6))
        sns.scatterplot(data=out, x="predicted", y="residual", hue="year", palette="viridis", legend=False)
        plt.axhline(0, color="black", linestyle="--", linewidth=1)
        plt.xlabel("Predicted unmet medical need (%)")
        plt.ylabel("Residual")
        plt.tight_layout()
        plt.savefig(FIGURES / f"ml_residuals_vs_predicted_{name}.pdf", dpi=300)
        plt.close()

        plt.figure(figsize=(9, 4.8))
        sns.boxplot(data=out, x="country", y="residual", color="#56B4E9")
        plt.axhline(0, color="black", linestyle="--", linewidth=1)
        plt.xlabel("Country")
        plt.ylabel("Residual")
        plt.xticks(rotation=90)
        plt.tight_layout()
        plt.savefig(FIGURES / f"ml_residuals_by_country_{name}.pdf", dpi=300)
        plt.close()


def calibration_plot(best_name: str, best_model, ridge_model, test: pd.DataFrame) -> None:
    rows = []
    for model_name, model in [(best_name, best_model), ("Ridge", ridge_model)]:
        if model is None:
            continue
        temp = pd.DataFrame({"actual": test[OUTCOME].values, "predicted": model.predict(test[FEATURES])})
        try:
            temp["decile"] = pd.qcut(temp["predicted"], 10, labels=False, duplicates="drop") + 1
        except ValueError:
            temp["decile"] = pd.cut(temp["predicted"], 10, labels=False, duplicates="drop") + 1
        agg = temp.groupby("decile", as_index=False).agg(mean_actual=("actual", "mean"), mean_predicted=("predicted", "mean"))
        agg["model"] = model_name
        rows.append(agg)
    if not rows:
        return
    plot_df = pd.concat(rows, ignore_index=True)
    plt.figure(figsize=(6, 5.2))
    sns.lineplot(data=plot_df, x="mean_predicted", y="mean_actual", hue="model", marker="o", palette="colorblind")
    lo = min(plot_df["mean_predicted"].min(), plot_df["mean_actual"].min())
    hi = max(plot_df["mean_predicted"].max(), plot_df["mean_actual"].max())
    plt.plot([lo, hi], [lo, hi], color="black", linestyle="--", linewidth=1)
    plt.xlabel("Mean predicted by decile")
    plt.ylabel("Mean actual by decile")
    plt.tight_layout()
    plt.savefig(FIGURES / "ml_calibration_plot.pdf", dpi=300)
    plt.close()


def learning_curve_plot(best_model, train: pd.DataFrame) -> None:
    try:
        sizes, train_scores, cv_scores = learning_curve(
            best_model,
            train[FEATURES],
            train[OUTCOME],
            cv=TimeSeriesSplit(n_splits=5),
            scoring="neg_mean_absolute_error",
            train_sizes=np.linspace(0.25, 1.0, 6),
            n_jobs=-1,
        )
        plt.figure(figsize=(7, 4.8))
        plt.plot(sizes, -train_scores.mean(axis=1), marker="o", label="Train MAE")
        plt.plot(sizes, -cv_scores.mean(axis=1), marker="o", label="CV MAE")
        plt.fill_between(sizes, -cv_scores.mean(axis=1) - cv_scores.std(axis=1), -cv_scores.mean(axis=1) + cv_scores.std(axis=1), alpha=0.15)
        plt.xlabel("Training sample size")
        plt.ylabel("MAE")
        plt.legend(frameon=False)
        plt.grid(axis="y", alpha=0.25)
        plt.tight_layout()
        plt.savefig(FIGURES / "ml_learning_curves.pdf", dpi=300)
        plt.close()
    except Exception as exc:
        log_error(f"Step 5l learning curves failed: {exc}")


def main() -> None:
    ERROR_LOG.write_text("", encoding="utf-8")
    hyperparameter_grid_output()
    split_df, train, test = make_time_split()
    perf, fitted = cv_train_models(train, test)
    baselines = evaluate_naive_baselines(train, test)
    benchmark_decision(perf, baselines)
    bootstrap_test_mae(test, fitted)
    paired_tree_mae_differences(test, fitted)
    country_holdout_evaluation(split_df, fitted)
    expanding_window(split_df, fitted)
    best_name, best_model = best_tree_model(perf, fitted)
    feature_importance_outputs(best_name, best_model, train, test)
    residual_outputs(best_name, best_model, fitted.get("Ridge"), test)
    calibration_plot(best_name, best_model, fitted.get("Ridge"), test)
    learning_curve_plot(best_model, train)
    if ERROR_LOG.read_text(encoding="utf-8").strip() == "":
        ERROR_LOG.write_text("No errors encountered.\n", encoding="utf-8")
    print("STEP 5 COMPLETE")


if __name__ == "__main__":
    main()
