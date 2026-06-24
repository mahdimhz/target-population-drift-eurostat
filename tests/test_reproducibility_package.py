from __future__ import annotations

import json
import hashlib
import re
import subprocess
from collections import Counter
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def _manuscript_files() -> list[Path]:
    return (
        [ROOT / "main.tex", ROOT / "abstract.tex"]
        + sorted((ROOT / "frontmatter").glob("*.tex"))
        + sorted((ROOT / "chapters").glob("*.tex"))
    )


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
    assert "python src/run_full_thesis_analysis.py" in manifest["command_order"]
    assert "python src/run_step7_master_summary.py" in manifest["command_order"]
    assert "data/processed/panel_features_v2-3.csv" in manifest["input_and_script_hashes"]
    assert "src/run_missingness_robustness.py" in manifest["input_and_script_hashes"]
    assert len(manifest["output_hashes"]) > 10


def test_table_figure_generation_map_points_to_existing_outputs() -> None:
    generation_map = pd.read_csv(ROOT / "outputs" / "table_figure_generation_map.csv")
    assert {"output_file", "script", "input_file", "chapter_or_use"}.issubset(generation_map.columns)
    missing_outputs = [path for path in generation_map["output_file"] if not (ROOT / path).exists()]
    assert not missing_outputs


def test_reported_tables_and_figures_exist() -> None:
    text = "\n".join(path.read_text(encoding="utf-8") for path in _manuscript_files())

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


def test_manuscript_does_not_insert_the_same_table_fragment_twice() -> None:
    table_inputs: list[str] = []
    for path in (ROOT / "chapters").glob("*.tex"):
        table_inputs.extend(re.findall(r"\\input\{(tables/[^}]+)\}", path.read_text(encoding="utf-8")))

    duplicates = sorted(name for name, count in Counter(table_inputs).items() if count > 1)
    assert duplicates == []


def test_manuscript_uses_one_primary_attrition_waterfall() -> None:
    text = "\n".join(path.read_text(encoding="utf-8") for path in (ROOT / "chapters").glob("*.tex"))
    assert "multi_outcome_primary_attrition_waterfall" not in text
    assert text.count(r"\includegraphics[width=0.92\textwidth]{complete_case_attrition_waterfall}") == 1


def test_manuscript_references_no_byte_identical_figures() -> None:
    figure_names: set[str] = set()
    for path in (ROOT / "chapters").glob("*.tex"):
        figure_names.update(
            re.findall(
                r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}",
                path.read_text(encoding="utf-8"),
            )
        )

    hashes: dict[str, list[str]] = {}
    for name in sorted(figure_names):
        path = ROOT / "figures" / f"{name}.pdf"
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        hashes.setdefault(digest, []).append(path.name)

    duplicates = [sorted(names) for names in hashes.values() if len(names) > 1]
    assert duplicates == []


def test_all_latex_inputs_and_figures_exist() -> None:
    missing: list[str] = []
    for source in _manuscript_files():
        text = source.read_text(encoding="utf-8")
        for item in re.findall(r"\\input\{([^}]+)\}", text):
            path = ROOT / item
            if path.suffix == "":
                path = path.with_suffix(".tex")
            if not path.exists() or path.stat().st_size == 0:
                missing.append(f"{source.relative_to(ROOT)} -> {item}")
        for item in re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", text):
            candidates = [ROOT / item, source.parent / item, ROOT / "figures" / item]
            if Path(item).suffix == "":
                candidates = [
                    ROOT / "figures" / f"{item}.pdf",
                    ROOT / "figures" / f"{item}.png",
                    ROOT / "figures" / f"{item}.jpg",
                ]
            if not any(path.exists() and path.stat().st_size > 0 for path in candidates):
                missing.append(f"{source.relative_to(ROOT)} -> {item}")
    assert missing == []


def test_final_manuscript_contains_no_drafting_or_agent_artifacts() -> None:
    text = "\n".join(path.read_text(encoding="utf-8") for path in _manuscript_files())
    forbidden = [
        "SOURCE NEEDED",
        "TODO",
        "PLACEHOLDER",
        "upgraded thesis",
        "ChatGPT",
        "OpenAI",
        "rtk ",
        "p = 0.000",
        "MI reveals",
        "corrected truth",
    ]
    present = [term for term in forbidden if term.lower() in text.lower()]
    assert present == []


def test_github_publish_set_has_no_oversized_tracked_or_changed_files() -> None:
    size_limit = 50 * 1024 * 1024
    tracked = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True).splitlines()
    changed = [
        line[3:]
        for line in subprocess.check_output(["git", "status", "--porcelain=v1"], cwd=ROOT, text=True).splitlines()
        if line[:2].strip() and line[:2] != " D"
    ]
    paths = sorted(set(tracked + changed))
    oversized = []
    for item in paths:
        path = ROOT / item
        if path.is_file() and path.stat().st_size > size_limit:
            oversized.append(f"{item}: {path.stat().st_size / 1024 / 1024:.1f} MB")
    assert oversized == []


def test_source_appendix_contains_verified_dental_multi_outcome_rows() -> None:
    source_table = (ROOT / "tables" / "eurostat_sources_appendix.tex").read_text(encoding="utf-8")
    assert r"\texttt{hlth\_silc\_09}" in source_table
    assert r"\texttt{hlth\_silc\_09b}" in source_table
    assert "Dental population denominator" in source_table
    assert "Dental need denominator" in source_table
    assert "reason=TXP\\_TFAR\\_WLIST" in source_table
    assert "reason=TOOEFW" not in source_table
