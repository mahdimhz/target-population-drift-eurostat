from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import pandas as pd

from .coverage import coverage_audit


ROOT = Path(__file__).resolve().parents[2]


def _read_simple_config(path: Path) -> dict[str, int]:
    config: dict[str, int] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        config[key.strip()] = int(value.strip())
    return config


def report(indicator: str) -> Path:
    panel_path = ROOT / "data" / "processed" / "multi_outcome_unmet_care.csv"
    panel = pd.read_csv(panel_path)
    subset = panel[panel["dataset_code"].eq(indicator) | panel["indicator_id"].eq(indicator)].copy()
    if subset.empty:
        raise SystemExit(f"No rows found for indicator or dataset: {indicator}")
    out = coverage_audit(subset.rename(columns={"value_pc": "outcome_value_pc"}), ["outcome_value_pc"])
    out.insert(0, "indicator", indicator)
    output_path = ROOT / "outputs" / f"eurodrift_report_{indicator}.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(output_path, index=False)
    return output_path


def simulate(config_path: Path, smoke: bool) -> None:
    config = _read_simple_config(config_path)
    replicates = config["smoke_replicates"] if smoke else config["replicates"]
    prefix = "cli_smoke" if smoke else "cli"
    command = [
        sys.executable,
        str(ROOT / "src" / "run_missingness_simulation.py"),
        "--replicates",
        str(replicates),
        "--imputations",
        str(config.get("imputations", 2)),
        "--seed",
        str(config.get("seed", 42)),
        "--prefix",
        prefix,
    ]
    subprocess.run(command, cwd=ROOT, check=True)


def reproduce_thesis() -> None:
    commands = [
        [sys.executable, str(ROOT / "src" / "build_multi_outcome_indicator_registry.py")],
        [sys.executable, str(ROOT / "src" / "build_multi_outcome_monitoring_benchmark.py")],
        [sys.executable, str(ROOT / "src" / "build_multi_outcome_drift_diagnostics.py")],
        [sys.executable, str(ROOT / "src" / "build_outcome_estimand_stability_matrix.py")],
        [sys.executable, str(ROOT / "src" / "build_drift_stability_framework.py")],
        [sys.executable, str(ROOT / "src" / "build_reporting_protocol_tables.py")],
        [sys.executable, str(ROOT / "src" / "run_step7_master_summary.py")],
    ]
    for command in commands:
        subprocess.run(command, cwd=ROOT, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(prog="eurodrift")
    subparsers = parser.add_subparsers(dest="command", required=True)

    report_parser = subparsers.add_parser("report")
    report_parser.add_argument("--indicator", required=True)

    simulate_parser = subparsers.add_parser("simulate")
    simulate_parser.add_argument("--config", required=True)
    simulate_parser.add_argument("--smoke", action="store_true")

    subparsers.add_parser("reproduce-thesis")

    args = parser.parse_args()
    if args.command == "report":
        output = report(args.indicator)
        print(f"saved {output}")
    elif args.command == "simulate":
        simulate(Path(args.config), smoke=args.smoke)
    elif args.command == "reproduce-thesis":
        reproduce_thesis()
