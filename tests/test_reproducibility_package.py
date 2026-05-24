from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def test_reproducibility_files_exist() -> None:
    required = [
        ROOT / "README.md",
        ROOT / "requirements.txt",
        ROOT / "environment.yml",
        ROOT / ".gitignore",
        ROOT / "outputs" / "reproducibility_manifest.json",
        ROOT / "outputs" / "output_manifest_hashes.csv",
        ROOT / "outputs" / "processed_data_dictionary.csv",
        ROOT / "outputs" / "processed_data_dictionary_summary.csv",
        ROOT / "outputs" / "table_figure_generation_map.csv",
        ROOT / "outputs" / "raw_data_download_instructions.md",
    ]
    missing = [path.as_posix() for path in required if not path.exists() or path.stat().st_size == 0]
    assert not missing


def test_manifest_contains_command_order_hashes_and_seed() -> None:
    manifest = json.loads((ROOT / "outputs" / "reproducibility_manifest.json").read_text(encoding="utf-8"))
    assert manifest["random_seed"] == 42
    assert "rtk python src/run_full_thesis_analysis.py" in manifest["command_order"]
    assert "rtk python src/run_step7_master_summary.py" in manifest["command_order"]
    assert "data/processed/panel_features_v2-3.csv" in manifest["input_and_script_hashes"]
    assert "src/run_missingness_robustness.py" in manifest["input_and_script_hashes"]
    assert len(manifest["output_hashes"]) > 10


def test_table_figure_generation_map_points_to_existing_outputs() -> None:
    generation_map = pd.read_csv(ROOT / "outputs" / "table_figure_generation_map.csv")
    assert {"output_file", "script", "input_file", "chapter_or_use"}.issubset(generation_map.columns)
    missing_outputs = [path for path in generation_map["output_file"] if not (ROOT / path).exists()]
    assert not missing_outputs


def test_reported_tables_and_figures_exist() -> None:
    manuscript_files = list((ROOT / "chapters").glob("*.tex")) + [ROOT / "abstract.tex", ROOT / "main.tex"]
    text = "\n".join(path.read_text(encoding="utf-8") for path in manuscript_files)

    expected_outputs = {
        "tables/ml_naive_baselines": "ml_naive_baselines",
        "tables/model_ladder_results": "model_ladder_results",
        "tables/target_population_sensitivity_results": "target_population_sensitivity_results",
        "figures/complete_case_attrition_waterfall": "complete_case_attrition_waterfall",
        "figures/model_ladder_coefficient_forest": "model_ladder_coefficient_forest",
        "figures/conceptual_selection_estimand_diagram": "conceptual_selection_estimand_diagram",
    }
    for stem, manuscript_token in expected_outputs.items():
        assert manuscript_token in text
        suffix = ".tex" if stem.startswith("tables/") else ".pdf"
        assert (ROOT / f"{stem}{suffix}").exists()


def test_readme_has_guarded_github_publish_instructions() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "https://github.com/mahdimhz/unmet-medical-care-needs-europe-thesis.git" in readme
    assert "Do not push before confirming" in readme
    assert "No public repository is cited" in readme
