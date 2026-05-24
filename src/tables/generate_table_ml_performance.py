from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / "outputs" / "table_all_models_performance.csv"
OUTPUT = ROOT / "tables" / "ml_model_performance.tex"
TUNING_FILES = {
    "Gradient Boosting": ROOT / "outputs" / "gradient_boosting_validation_tuning.csv",
    "Random Forest": ROOT / "outputs" / "random_forest_validation_tuning.csv",
    "Ridge": ROOT / "outputs" / "ridge_validation_tuning.csv",
    "Lasso": ROOT / "outputs" / "lasso_validation_tuning.csv",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def fmt(value: str) -> str:
    if value == "":
        return "--"
    return f"{float(value):.3f}"


def best_validation_mae() -> dict[str, str]:
    best: dict[str, str] = {}
    for model, path in TUNING_FILES.items():
        if not path.exists():
            continue
        rows = read_csv(path)
        if not rows or "mae_valid" not in rows[0]:
            continue
        best[model] = min(rows, key=lambda row: float(row["mae_valid"]))["mae_valid"]
    return best


def main() -> None:
    rows = read_csv(INPUT)
    rows = sorted(rows, key=lambda row: float(row["mae_test"]))
    validation_mae = best_validation_mae()

    lines = [
        r"\begin{tabular}{llrrrr}",
        r"\toprule",
        r"Family & Model & Valid. MAE & Test MAE & Test RMSE & Test $R^2$ \\",
        r"\midrule",
    ]
    for row in rows:
        lines.append(
            f"{row['model_family']} & {row['model_name']} & "
            f"{fmt(validation_mae.get(row['model_name'], ''))} & "
            f"{fmt(row['mae_test'])} & {fmt(row['rmse_test'])} & {fmt(row['r2_test'])} \\\\"
        )
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}",
            r"",
            r"\vspace{0.2em}",
            r"\begin{minipage}{0.92\textwidth}",
            r"\scriptsize Notes: Models are ranked by test-set MAE. The tuning files contain held-out validation MAE rather than fold-level cross-validation means and standard deviations. Validation MAE is therefore reported where available from the tuning grid; OLS and MLP do not have comparable tuning-grid MAE entries. Test metrics are computed on the same 2021--2023 held-out test split.",
            r"\end{minipage}",
        ]
    )
    OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
