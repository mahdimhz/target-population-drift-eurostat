from __future__ import annotations

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    processed_dir = PROJECT_ROOT / "data" / "processed"
    outputs_dir = PROJECT_ROOT / "outputs"

    outcome = pd.read_csv(processed_dir / "country_year_outcome.csv")
    controls = pd.read_csv(processed_dir / "verified_control_candidates.csv")
    feasibility = pd.read_csv(outputs_dir / "control_feasibility.csv")

    approved_columns = feasibility.loc[
        feasibility["merge_approved"].eq("yes"),
        "variable_name",
    ].tolist()

    keep_columns = ["geo", "year"] + approved_columns
    controls = controls[[column for column in keep_columns if column in controls.columns]]

    panel = outcome.merge(controls, on=["geo", "year"], how="left")
    panel = panel.sort_values(["geo", "year"]).reset_index(drop=True)
    panel.to_csv(processed_dir / "panel_skeleton.csv", index=False)

    print(f"saved {processed_dir / 'panel_skeleton.csv'}")
    print(f"rows: {len(panel)}")
    print(f"control columns: {', '.join(approved_columns) if approved_columns else 'none'}")


if __name__ == "__main__":
    main()
