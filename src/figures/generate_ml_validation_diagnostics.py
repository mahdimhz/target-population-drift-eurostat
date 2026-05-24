from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.inspection import PartialDependenceDisplay, permutation_importance
from sklearn.metrics import mean_absolute_error


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "processed" / "modeling_dataset_5a_with_splits.csv"
FIGURES = ROOT / "figures"
OUTPUTS = ROOT / "outputs"

FEATURES = [
    "gdp_per_capita_eur",
    "unemployment_rate_pc",
    "poverty_or_social_exclusion_pc",
    "government_health_expenditure_gdp_pc",
    "compulsory_health_financing_gdp_pc",
    "physicians_per_100k",
    "hospital_beds_per_100k",
    "oop_health_expenditure_share_pc",
    "gini_income",
    "long_term_unemployment_rate_pc",
    "log_gdp_per_capita",
    "physicians_per_100k_lag1",
    "gdp_per_capita_growth",
    "unemployment_rate_change",
]

LABELS = {
    "gdp_per_capita_eur": "GDP per capita",
    "unemployment_rate_pc": "Unemployment",
    "poverty_or_social_exclusion_pc": "Poverty or social exclusion",
    "government_health_expenditure_gdp_pc": "Government health spending",
    "compulsory_health_financing_gdp_pc": "Compulsory financing",
    "physicians_per_100k": "Physicians per 100k",
    "hospital_beds_per_100k": "Hospital beds per 100k",
    "oop_health_expenditure_share_pc": "Out-of-pocket spending",
    "gini_income": "Gini",
    "long_term_unemployment_rate_pc": "Long-term unemployment",
    "log_gdp_per_capita": "Log GDP per capita",
    "physicians_per_100k_lag1": "Lagged physicians per 100k",
    "gdp_per_capita_growth": "GDP per capita growth",
    "unemployment_rate_change": "Unemployment change",
}

TUNING_FILES = [
    ("Gradient Boosting", OUTPUTS / "gradient_boosting_validation_tuning.csv"),
    ("Random Forest", OUTPUTS / "random_forest_validation_tuning.csv"),
    ("Ridge", OUTPUTS / "ridge_validation_tuning.csv"),
    ("Lasso", OUTPUTS / "lasso_validation_tuning.csv"),
]


def fit_gradient_boosting(df: pd.DataFrame) -> tuple[GradientBoostingRegressor, pd.DataFrame, pd.DataFrame]:
    train_valid = df[df["split"].isin(["train", "valid"])].copy()
    test = df[df["split"] == "test"].copy()
    model = GradientBoostingRegressor(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=2,
        random_state=42,
    )
    model.fit(train_valid[FEATURES], train_valid["unmet_need_pc"])
    return model, train_valid, test


def plot_permutation_vs_impurity(model: GradientBoostingRegressor, test: pd.DataFrame) -> pd.DataFrame:
    perm = permutation_importance(
        model,
        test[FEATURES],
        test["unmet_need_pc"],
        scoring="neg_mean_absolute_error",
        n_repeats=50,
        random_state=42,
    )
    diagnostics = pd.DataFrame(
        {
            "feature": FEATURES,
            "label": [LABELS[f] for f in FEATURES],
            "impurity_importance": model.feature_importances_,
            "permutation_mae_increase": perm.importances_mean,
            "permutation_mae_std": perm.importances_std,
        }
    ).sort_values("impurity_importance", ascending=False)
    diagnostics.to_csv(OUTPUTS / "ml_permutation_vs_impurity_importance.csv", index=False)

    top = diagnostics.head(10).iloc[::-1]
    sns.set_theme(style="white", context="paper", font_scale=1.0)
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 5.8), sharey=True)
    color = sns.color_palette("colorblind")[0]
    axes[0].barh(top["label"], top["impurity_importance"], color=color)
    axes[0].set_title("Impurity importance")
    axes[0].set_xlabel("Relative importance")
    axes[0].set_ylabel("")

    axes[1].barh(
        top["label"],
        top["permutation_mae_increase"],
        xerr=top["permutation_mae_std"],
        color=sns.color_palette("colorblind")[2],
        ecolor="0.25",
        capsize=2,
    )
    axes[1].axvline(0, color="0.35", linewidth=0.8)
    axes[1].set_title("Permutation importance")
    axes[1].set_xlabel("Increase in MAE when permuted")
    axes[1].set_ylabel("")
    for ax in axes:
        ax.grid(axis="x", color="0.9", linewidth=0.8)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIGURES / "ml_permutation_vs_impurity_importance.pdf", dpi=300, bbox_inches="tight")
    plt.close(fig)
    return diagnostics


def plot_poverty_pdp(model: GradientBoostingRegressor, train_valid: pd.DataFrame) -> None:
    sns.set_theme(style="white", context="paper", font_scale=1.0)
    fig, ax = plt.subplots(figsize=(6.8, 4.4))
    PartialDependenceDisplay.from_estimator(
        model,
        train_valid[FEATURES],
        ["poverty_or_social_exclusion_pc"],
        feature_names=FEATURES,
        ax=ax,
        line_kw={"color": sns.color_palette("colorblind")[1], "linewidth": 2},
    )
    ax.set_title("")
    ax.set_xlabel("Poverty or social exclusion (%)")
    ax.set_ylabel("Predicted unmet medical care need (%)")
    ax.grid(axis="y", color="0.9", linewidth=0.8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIGURES / "tree_pdp_poverty_or_social_exclusion_pc.pdf", dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_validation_tuning() -> None:
    sns.set_theme(style="white", context="paper", font_scale=1.0)
    fig, axes = plt.subplots(2, 2, figsize=(10, 7), sharey=False)
    axes = axes.flatten()
    palette = sns.color_palette("colorblind")
    for ax, (model_name, path), color in zip(axes, TUNING_FILES, palette):
        df = pd.read_csv(path).sort_values("mae_valid").reset_index(drop=True)
        ax.plot(range(1, len(df) + 1), df["mae_valid"], marker="o", linewidth=1.6, color=color)
        ax.set_title(model_name)
        ax.set_xlabel("Tuning candidate rank")
        ax.set_ylabel("Validation MAE")
        ax.grid(axis="y", color="0.9", linewidth=0.8)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIGURES / "ml_validation_tuning_mae.pdf", dpi=300, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    df = pd.read_csv(DATA)
    model, train_valid, test = fit_gradient_boosting(df)
    diagnostics = plot_permutation_vs_impurity(model, test)
    plot_poverty_pdp(model, train_valid)
    plot_validation_tuning()

    predictions = model.predict(test[FEATURES])
    print(f"Gradient Boosting test MAE from reproduced model: {mean_absolute_error(test['unmet_need_pc'], predictions):.3f}")
    print(diagnostics.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
