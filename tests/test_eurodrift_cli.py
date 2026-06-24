from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def test_eurodrift_import_from_project_root_exposes_required_api() -> None:
    command = [
        sys.executable,
        "-c",
        (
            "import eurodrift; "
            "required=['load_eurostat_panel','define_estimand','coverage_audit','attrition_waterfall',"
            "'included_excluded_balance','population_weighted_trend','estimand_ladder','ipw_diagnostic',"
            "'pmm_imputation_sensitivity','mnar_delta_sensitivity','simulate_missingness','classify_drift','generate_report',"
            "'target_population_drift_index','conclusion_stability_index','standardized_coefficient']; "
            "missing=[name for name in required if not hasattr(eurodrift,name)]; "
            "assert not missing, missing"
        ),
    ]
    subprocess.run(command, cwd=ROOT, check=True)


def test_eurodrift_report_cli_generates_expected_file() -> None:
    output = ROOT / "outputs" / "eurodrift_report_hlth_silc_08.csv"
    if output.exists():
        output.unlink()
    subprocess.run(
        [sys.executable, "-m", "eurodrift", "report", "--indicator", "hlth_silc_08"],
        cwd=ROOT,
        check=True,
    )
    assert output.exists()
    report = pd.read_csv(output)
    assert report.loc[0, "indicator"] == "hlth_silc_08"
    assert int(report.loc[0, "observed_rows"]) > 0


def test_simulation_primary_config_exists() -> None:
    config = (ROOT / "configs" / "simulation_primary.yml").read_text(encoding="utf-8")
    assert "replicates: 100" in config
    assert "smoke_replicates: 20" in config
    assert "seed: 42" in config
