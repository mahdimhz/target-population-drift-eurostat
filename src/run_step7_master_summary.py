from __future__ import annotations

import hashlib
import json
import platform
import re
import zipfile
import sys
from importlib import metadata
from pathlib import Path

import fitz
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = ROOT / "outputs"
FIGURES = ROOT / "figures"
TABLES = ROOT / "tables"
DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"

ERROR_LOG = OUTPUTS / "analysis_errors.log"
COMMAND_ORDER = [
    "rtk python src/run_full_thesis_analysis.py",
    "rtk python src/generate_conceptual_selection_diagram.py",
    "rtk python src/run_missingness_robustness.py",
    "rtk python src/run_step5_ml_analysis.py",
    "rtk python src/run_step6_additional_analysis.py",
    "rtk python src/run_step7_master_summary.py",
    "rtk latexmk -pdf main.tex",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def first_row(path: Path) -> dict:
    return pd.read_csv(path).iloc[0].to_dict() if path.exists() else {}


def csv_records(path: Path) -> list[dict]:
    return pd.read_csv(path).to_dict("records") if path.exists() else []


def extract_number(text: str, pattern: str) -> str:
    match = re.search(pattern, text)
    return match.group(1) if match else "NA"


def generated_files() -> tuple[list[Path], list[Path], list[Path]]:
    figures = sorted(FIGURES.glob("*.pdf"))
    tables = sorted(TABLES.glob("*.tex"))
    outputs = sorted([p for p in OUTPUTS.iterdir() if p.is_file()])
    return figures, tables, outputs


def latex_escape(value: object) -> str:
    text = str(value)
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def package_versions() -> dict[str, str]:
    packages = [
        "numpy",
        "pandas",
        "scipy",
        "statsmodels",
        "scikit-learn",
        "matplotlib",
        "seaborn",
        "requests",
        "PyMuPDF",
        "xgboost",
    ]
    out = {}
    for package in packages:
        try:
            out[package] = metadata.version(package)
        except metadata.PackageNotFoundError:
            out[package] = "not installed"
    return out


def processed_data_dictionary() -> None:
    records = []
    summary = []
    for path in sorted(DATA_PROCESSED.glob("*.csv")):
        try:
            df = pd.read_csv(path)
        except Exception as exc:
            records.append(
                {
                    "file": path.relative_to(ROOT).as_posix(),
                    "column": "READ_ERROR",
                    "dtype": "",
                    "non_missing": 0,
                    "missing": 0,
                    "missing_pct": "",
                    "example": str(exc),
                }
            )
            continue
        rel = path.relative_to(ROOT).as_posix()
        key_columns = [c for c in ["geo", "country", "year", "unmet_need_pc", "population_total"] if c in df.columns]
        summary.append(
            {
                "file": rel,
                "rows": int(len(df)),
                "columns": int(len(df.columns)),
                "key_columns": ", ".join(key_columns) if key_columns else ", ".join(df.columns[:4]),
            }
        )
        for col in df.columns:
            non_missing = int(df[col].notna().sum())
            missing = int(df[col].isna().sum())
            examples = df[col].dropna().astype(str).head(3).tolist()
            records.append(
                {
                    "file": rel,
                    "column": col,
                    "dtype": str(df[col].dtype),
                    "non_missing": non_missing,
                    "missing": missing,
                    "missing_pct": round(float(df[col].isna().mean() * 100), 2) if len(df) else 0.0,
                    "example": "; ".join(examples),
                }
            )
    pd.DataFrame(records).to_csv(OUTPUTS / "processed_data_dictionary.csv", index=False)
    summary_df = pd.DataFrame(summary)
    summary_df.to_csv(OUTPUTS / "processed_data_dictionary_summary.csv", index=False)

    def short_processed_file(value: str) -> str:
        name = Path(str(value)).name
        replacements = {
            "citizenship_unmet_need.csv": "citizenship.csv",
            "country_year_outcome.csv": "outcome.csv",
            "country_year_outcome_08b.csv": "outcome_08b.csv",
            "feature_gini_income.csv": "gini.csv",
            "feature_hospital_beds_per_100k.csv": "beds.csv",
            "feature_long_term_unemployment_rate_pc.csv": "lt_unemp.csv",
            "feature_oop_health_expenditure_share_pc.csv": "oop_share.csv",
            "feature_physicians_per_100k.csv": "physicians.csv",
            "feature_population_total.csv": "population.csv",
            "modeling_dataset_5a.csv": "ml_5a.csv",
            "modeling_dataset_5a_with_splits.csv": "ml_5a_splits.csv",
            "modeling_dataset_time_split.csv": "ml_time.csv",
            "panel_features_v2-3.csv": "panel.csv",
            "panel_skeleton.csv": "skeleton.csv",
            "verified_control_candidates.csv": "controls.csv",
        }
        if name.startswith("panel_features_v2-3_imputed_"):
            return "imp_" + name.removeprefix("panel_features_v2-3_imputed_")
        return replacements.get(name, name if len(name) <= 22 else name[:19] + "...")

    def short_keys(value: str) -> str:
        return (
            str(value)
            .replace("unmet_need_pc", "unmet")
            .replace("population_total", "pop")
            .replace("country", "ctry")
        )

    compact = summary_df.copy()
    compact["file"] = compact["file"].map(short_processed_file)
    compact["key_columns"] = compact["key_columns"].map(short_keys)
    lines = [
        r"\begingroup",
        r"\scriptsize",
        r"\begin{longtable}{@{}>{\raggedright\arraybackslash}p{0.31\textwidth}rr>{\raggedright\arraybackslash}p{0.33\textwidth}@{}}",
        r"\caption{Processed data dictionary summary}\label{tab:processed_data_dictionary_summary}\\",
        r"\toprule",
        r"File & Rows & Columns & Key columns \\",
        r"\midrule",
        r"\endfirsthead",
        r"\toprule",
        r"File & Rows & Columns & Key columns \\",
        r"\midrule",
        r"\endhead",
    ]
    for _, row in compact.iterrows():
        lines.append(
            f"{latex_escape(row['file'])} & {int(row['rows'])} & {int(row['columns'])} & {latex_escape(row['key_columns'])} \\\\"
        )
    lines.extend([r"\bottomrule", r"\end{longtable}", r"\endgroup"])
    (TABLES / "processed_data_dictionary_summary.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


def infer_source(output: Path) -> tuple[str, str]:
    name = output.name.lower()
    if "conceptual_selection" in name:
        return "src/generate_conceptual_selection_diagram.py", "chapter text and manually specified conceptual structure"
    if any(token in name for token in ["mi_", "mnar", "ipw", "poverty", "target_population", "main_sensitivity", "country_universe", "complete_case_selection", "fe_", "leave_one", "estimand_framework", "missingness_robustness"]):
        return "src/run_missingness_robustness.py", "data/processed/panel_features_v2-3.csv"
    if any(token in name for token in ["ml_", "xgboost", "random_forest", "lasso", "ridge"]):
        return "src/run_step5_ml_analysis.py", "data/processed/modeling_dataset_5a.csv"
    if any(token in name for token in ["citizenship", "08b", "convergence", "trend_with_bands", "trend_test"]):
        return "src/run_step6_additional_analysis.py", "data/processed/citizenship_unmet_need.csv; data/processed/country_year_outcome_08b.csv"
    if any(token in name for token in ["software_versions", "output_generation_map", "data_dictionary", "eurostat_sources"]):
        return "src/run_step7_master_summary.py", "generated project files"
    return "src/run_full_thesis_analysis.py", "data/processed/panel_features_v2-3.csv"


def find_chapter_for_output(output: Path) -> str:
    stem = output.stem
    patterns = [
        f"tables/{stem}",
        f"{{{stem}}}",
        f"{stem}",
    ]
    hits = []
    for chapter in sorted((ROOT / "chapters").glob("*.tex")) + [ROOT / "abstract.tex"]:
        text = read_text(chapter)
        if any(pattern in text for pattern in patterns):
            hits.append(chapter.relative_to(ROOT).as_posix())
    return "; ".join(hits) if hits else "appendix/reproducibility artifact"


def output_generation_map(figures: list[Path], tables: list[Path]) -> None:
    rows = []
    for output in sorted(tables + figures):
        script, input_file = infer_source(output)
        rows.append(
            {
                "chapter_or_use": find_chapter_for_output(output),
                "output_type": "table" if output.suffix == ".tex" else "figure",
                "output_file": output.relative_to(ROOT).as_posix(),
                "script": script,
                "input_file": input_file,
            }
        )
    df = pd.DataFrame(rows)
    df.to_csv(OUTPUTS / "table_figure_generation_map.csv", index=False)
    compact = df.copy()
    def clipped(value: str, limit: int) -> str:
        value = str(value)
        return value if len(value) <= limit else value[: max(0, limit - 3)] + "..."

    def short_use(value: str) -> str:
        value = str(value)
        if value == "appendix/reproducibility artifact":
            return "App."
        labels = {
            "introduction": "Ch. 1",
            "background_literature": "Ch. 2",
            "data_indicators": "Ch. 3",
            "descriptive_evidence": "Ch. 4",
            "modeling_strategy_results": "Ch. 5",
            "ml_extension": "Ch. 6",
            "discussion_conclusion": "Ch. 7",
            "appendix": "App.",
        }
        seen: list[str] = []
        for part in str(value).split("; "):
            label = labels.get(Path(part).stem, "Multi")
            if label not in seen:
                seen.append(label)
        return "; ".join(seen)

    def short_script(value: str) -> str:
        name = Path(str(value)).name
        labels = {
            "run_full_thesis_analysis.py": "full",
            "generate_conceptual_selection_diagram.py": "diagram",
            "run_missingness_robustness.py": "missing",
            "run_step5_ml_analysis.py": "ml",
            "run_step6_additional_analysis.py": "extra",
            "run_step7_master_summary.py": "summary",
        }
        return labels.get(name, clipped(name, 12))

    compact["chapter_or_use"] = compact["chapter_or_use"].map(short_use)
    compact["output_file"] = compact["output_file"].map(lambda x: clipped(Path(str(x)).name, 24))
    compact["script"] = compact["script"].map(short_script)

    def short_input(value: str) -> str:
        value = str(value)
        if "modeling_dataset_5a" in value:
            return "ML"
        if "citizenship_unmet_need" in value or "country_year_outcome_08b" in value:
            return "C/08b"
        if "generated project files" in value:
            return "Gen."
        if "conceptual" in value:
            return "Concept"
        return "Panel"

    compact["input_file"] = compact["input_file"].map(short_input)
    lines = [
        r"\begingroup",
        r"\tiny",
        r"\begin{longtable}{@{}p{0.11\textwidth}p{0.39\textwidth}p{0.13\textwidth}p{0.11\textwidth}@{}}",
        r"\caption{Table and figure generation map}\label{tab:output_generation_map}\\",
        r"\toprule",
        r"Use & Output & Script & Input \\",
        r"\midrule",
        r"\endfirsthead",
        r"\toprule",
        r"Use & Output & Script & Input \\",
        r"\midrule",
        r"\endhead",
    ]
    for _, row in compact.iterrows():
        lines.append(
            f"{latex_escape(row['chapter_or_use'])} & {latex_escape(row['output_file'])} & {latex_escape(row['script'])} & {latex_escape(row['input_file'])} \\\\"
        )
    lines.extend([r"\bottomrule", r"\end{longtable}", r"\endgroup"])
    (TABLES / "output_generation_map.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


def output_hash_manifest(figures: list[Path], tables: list[Path], outputs: list[Path]) -> list[dict]:
    excluded = {
        "reproducibility_archive.zip",
        "output_manifest_hashes.csv",
        "reproducibility_manifest.json",
    }
    paths = [p for p in sorted(figures + tables + outputs) if p.name not in excluded and p.is_file()]
    rows = [
        {
            "path": p.relative_to(ROOT).as_posix(),
            "bytes": int(p.stat().st_size),
            "sha256": sha256(p),
        }
        for p in paths
    ]
    pd.DataFrame(rows).to_csv(OUTPUTS / "output_manifest_hashes.csv", index=False)
    return rows


def raw_data_download_instructions() -> None:
    lines = [
        "# Raw Eurostat Download Instructions",
        "",
        "Run the pipeline from the project root. The first command downloads or refreshes the raw Eurostat JSON files used by the thesis:",
        "",
        "```powershell",
        "rtk python src/run_full_thesis_analysis.py",
        "```",
        "",
        "The extraction code calls the Eurostat dissemination API through `src/eurostat_api.py`. Dataset codes, filters, extraction notes, and source verification are documented in:",
        "",
        "- `references/source_register.csv`",
        "- `tables/eurostat_sources_appendix.tex`",
        "- `outputs/population_extraction_notes.txt`",
        "- `outputs/hlth_silc_08_api_url.txt`",
        "- `outputs/hlth_silc_08b_api_url.txt`",
        "- `outputs/hlth_silc_32_extraction_notes.txt`",
        "",
        "The main raw inputs are stored in `data/raw/`; processed country-year files are written to `data/processed/`. No external substantive covariates outside the Eurostat scope are required.",
    ]
    (OUTPUTS / "raw_data_download_instructions.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def reproducibility_manifest() -> None:
    hash_paths = (
        sorted((ROOT / "data" / "processed").glob("*.csv"))
        + sorted((ROOT / "data" / "raw").glob("*.json"))
        + sorted((ROOT / "src").glob("*.py"))
        + sorted((ROOT / "references").glob("*.csv"))
    )
    hyper_grid = csv_records(OUTPUTS / "ml_hyperparameter_grid.csv")
    output_hashes = csv_records(OUTPUTS / "output_manifest_hashes.csv")
    manifest = {
        "python": sys.version,
        "platform": platform.platform(),
        "random_seed": 42,
        "command_order": COMMAND_ORDER,
        "package_versions": package_versions(),
        "input_and_script_hashes": {p.relative_to(ROOT).as_posix(): sha256(p) for p in hash_paths if p.exists()},
        "output_hashes": output_hashes,
        "hyperparameter_grid": hyper_grid,
        "population_weighting": {
            "source": "Eurostat demo_pjan",
            "filter": "freq=A, unit=NR, age=TOTAL, sex=T",
            "weight": "country-year population normalized within year",
        },
    }
    (OUTPUTS / "reproducibility_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def create_reproducibility_archive() -> None:
    archive = OUTPUTS / "reproducibility_archive.zip"
    include_dirs = [
        "chapters",
        "frontmatter",
        "writing",
        "references",
        "src",
        "tests",
        "tables",
        "figures",
        "data/raw",
        "data/processed",
        "outputs",
    ]
    include_files = [
        "README.md",
        "requirements.txt",
        "main.tex",
        "abstract.tex",
        "latexmkrc",
        "vanvfrontespizio.sty",
        "Vanv-logo.pdf",
        "Vanv-logo.png",
    ]
    exclude_suffixes = {".aux", ".bbl", ".bcf", ".blg", ".log", ".out", ".run.xml", ".toc", ".lof", ".lot", ".xdv"}
    exclude_names = {"reproducibility_archive.zip", "thesis_overleaf_upload.zip"}
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for rel in include_files:
            path = ROOT / rel
            if path.exists():
                zf.write(path, path.relative_to(ROOT).as_posix())
        for rel_dir in include_dirs:
            directory = ROOT / rel_dir
            if not directory.exists():
                continue
            for path in sorted(directory.rglob("*")):
                if not path.is_file():
                    continue
                if path.name in exclude_names or path.suffix in exclude_suffixes:
                    continue
                zf.write(path, path.relative_to(ROOT).as_posix())


def figure_quality_report(figures: list[Path]) -> list[str]:
    lines = [
        "Figures quality report",
        "Checks: PDF opens, has at least one page, has extractable English text or a descriptive filename, and is not trivially blank by file size.",
        "",
    ]
    manual_review = []
    english_terms = [
        "year",
        "mean",
        "country",
        "feature",
        "importance",
        "unmet",
        "need",
        "predicted",
        "actual",
        "residual",
        "coefficient",
        "mae",
    ]
    for fig in figures:
        status = "OK"
        notes = []
        try:
            doc = fitz.open(fig)
            page_count = doc.page_count
            text = "\n".join(page.get_text("text") for page in doc)
            doc.close()
            size = fig.stat().st_size
            if page_count < 1:
                status = "REVIEW"
                notes.append("no pages")
            if size < 5_000:
                status = "REVIEW"
                notes.append(f"small file size ({size} bytes)")
            text_lower = text.lower()
            english_hit = any(term in text_lower for term in english_terms)
            if len(text.strip()) < 8:
                status = "REVIEW"
                notes.append("little/no extractable text")
            elif not english_hit:
                status = "REVIEW"
                notes.append("axis/title text not clearly detected as English")
        except Exception as exc:
            status = "REVIEW"
            notes.append(f"open/extract failed: {exc}")
        if status != "OK":
            manual_review.append(fig.name)
        lines.append(f"{fig.as_posix()} | {status} | {'; '.join(notes) if notes else 'caption-ready; nonblank PDF detected'}")
    lines.extend(["", "Figures needing manual review:", ", ".join(manual_review) if manual_review else "None"])
    (OUTPUTS / "figures_quality_report.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return manual_review


def table_quality_report(tables: list[Path]) -> list[str]:
    lines = [
        "Tables quality report",
        "Checks: booktabs markers, caption, label, and excessive decimal precision scan.",
        "",
    ]
    manual_review = []
    long_decimal_re = re.compile(r"[-+]?\d+\.\d{5,}")
    for table in tables:
        text = read_text(table)
        notes = []
        status = "OK"
        for marker in ["\\toprule", "\\midrule", "\\bottomrule"]:
            if marker not in text:
                status = "REVIEW"
                notes.append(f"missing {marker}")
        if "\\caption" not in text:
            status = "REVIEW"
            notes.append("missing caption")
        if "\\label" not in text:
            status = "REVIEW"
            notes.append("missing label")
        long_decimals = long_decimal_re.findall(text)
        if long_decimals:
            status = "REVIEW"
            notes.append(f"{len(long_decimals)} values with >4 decimals")
        if status != "OK":
            manual_review.append(table.name)
        lines.append(f"{table.as_posix()} | {status} | {'; '.join(notes) if notes else 'booktabs/caption/label present; rounded'}")
    lines.extend(["", "Tables needing manual review:", ", ".join(manual_review) if manual_review else "None"])
    (OUTPUTS / "tables_quality_report.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return manual_review


def poverty_specs_text() -> list[str]:
    lines = []
    target_path = OUTPUTS / "target_population_sensitivity_results.csv"
    if target_path.exists():
        target = pd.read_csv(target_path)
        lines.append("Target-population sensitivity table:")
        for _, row in target.iterrows():
            lines.append(
                f"- {row['target_population']} / {row['weighting']} / {row['missingness_handling']}: "
                f"coef {row['poverty_coef']:.4f}, 95% CI [{row['ci_low']:.4f}, {row['ci_high']:.4f}], "
                f"p {row['p_value']:.4f}, N {int(row['rows'])}"
            )
    path = OUTPUTS / "regression_robustness_summary.csv"
    if path.exists():
        df = pd.read_csv(path)
        lines.append("Robustness specifications:")
        for _, row in df.iterrows():
            lines.append(
                f"- {row['specification']}: coef {row['coef']:.4f}, SE {row['se']:.4f}, p {row['p_value']:.4f}, N {int(row['nobs'])}"
            )
    mi = first_row(OUTPUTS / "multiple_imputation_pooled_results.csv")
    if mi:
        lines.append(
            f"- Multiple imputation pooled: coef {mi['pooled_coef']:.4f}, SE {mi['pooled_se']:.4f}, p {mi['p_value']:.4f}"
        )
    return lines


def suspicious_results() -> list[str]:
    flags = []
    vif_path = OUTPUTS / "regression_vif.csv"
    if vif_path.exists():
        vif = pd.read_csv(vif_path)
        high = vif[vif["vif"] > 10]
        if not high.empty:
            flags.append("VIF > 10 detected: " + ", ".join(high["variable"].tolist()))
    robust_path = OUTPUTS / "regression_robustness_summary.csv"
    mi_path = OUTPUTS / "multiple_imputation_pooled_results.csv"
    if robust_path.exists() and mi_path.exists():
        robust = pd.read_csv(robust_path)
        baseline = robust.loc[robust["specification"].eq("Baseline two-way FE"), "coef"]
        mi = pd.read_csv(mi_path).iloc[0]
        if not baseline.empty and np.sign(float(baseline.iloc[0])) != np.sign(float(mi["pooled_coef"])):
            flags.append("Poverty/social-exclusion coefficient changes sign under multiple imputation.")
        elif not baseline.empty and abs(float(mi["pooled_coef"])) < 0.01 and abs(float(baseline.iloc[0])) > 0.05:
            flags.append("Multiple-imputation poverty coefficient is near zero while baseline FE is materially positive.")
    stability_note = read_text(OUTPUTS / "ml_importance_stability_note.txt")
    if "Consistently top 3 across all 20 runs: False" in stability_note:
        flags.append("Monitored lagged feature is not consistently top 3 in ML importance stability.")
    return flags or ["None"]


def master_summary(figures: list[Path], tables: list[Path], outputs: list[Path], fig_review: list[str], table_review: list[str]) -> None:
    within = read_text(OUTPUTS / "regression_within_r2.txt")
    icc = read_text(OUTPUTS / "regression_icc.txt")
    hausman = read_text(OUTPUTS / "hausman_test_result.txt")
    ml = first_row(OUTPUTS / "ml_performance_full.csv")
    ml_bootstrap = first_row(OUTPUTS / "ml_test_mae_bootstrap_ci.csv")
    ml_baseline = first_row(OUTPUTS / "ml_naive_baselines.csv")
    ml_decision = read_text(OUTPUTS / "ml_benchmark_decision.txt")
    country_holdout = first_row(OUTPUTS / "ml_country_holdout_summary.csv")
    stability_note = read_text(OUTPUTS / "ml_importance_stability_note.txt")
    gap_ttest = read_text(OUTPUTS / "citizenship_gap_ttest.txt")
    gap_clustered = first_row(OUTPUTS / "citizenship_gap_clustered.csv")
    missingness = csv_records(OUTPUTS / "missingness_robustness_results.csv")
    gap_reg = csv_records(OUTPUTS / "citizenship_gap_regression.csv")
    trend = read_text(OUTPUTS / "trend_test_results.txt")
    convergence = read_text(OUTPUTS / "convergence_beta_result.txt")
    sigma = pd.read_csv(OUTPUTS / "convergence_sigma.csv") if (OUTPUTS / "convergence_sigma.csv").exists() else pd.DataFrame()
    errors = read_text(ERROR_LOG).strip() or "No errors encountered."

    sigma_direction = "NA"
    if not sigma.empty:
        first_sd = sigma.sort_values("year").iloc[0]["sd_unmet_need_pc"]
        last_sd = sigma.sort_values("year").iloc[-1]["sd_unmet_need_pc"]
        sigma_direction = f"{'declined' if last_sd < first_sd else 'increased'} from {first_sd:.4f} to {last_sd:.4f}"

    gap_reg_lines = []
    for row in gap_reg:
        if row.get("term") != "Intercept":
            gap_reg_lines.append(f"- {row['term']}: coef {row['coef']:.4f}, p {row['p_value']:.4f}")

    lines = [
        "# Master Analysis Summary",
        "",
        "## Steps completed",
        "- Step 0: Duplicate cleanup.",
        "- Step 1: Eurostat hlth_silc_32 citizenship data extraction.",
        "- Step 2: Descriptive analysis.",
        "- Step 3: Regression and robustness analysis.",
        "- Step 4: Multiple-imputation sensitivity.",
        "- Step 4b: Missingness-aware IPW and improved multiple-imputation robustness.",
        "- Step 5: One-year-ahead prediction analysis with naive baselines.",
        "- Step 6: Additional trend, convergence, citizenship-gap, and heterogeneity analyses.",
        "- Step 7: Master summary and quality checks.",
        "",
        "## Key numeric results",
        f"- Within-R2 from FE model: {extract_number(within, r'Within R2: ([-0-9.]+)')}",
        f"- ICC from multilevel model: {extract_number(icc, r'ICC: ([-0-9.]+)')}",
        f"- Hausman test p-value: {extract_number(hausman, r'p-value: ([-0-9.]+)')}; conclusion: {extract_number(hausman, r'Conclusion: (.+)')}",
        "",
        "### Poverty/social-exclusion coefficient",
        *poverty_specs_text(),
        "",
        "### Missingness-aware poverty/social-exclusion comparison",
        *[
            f"- {row['specification']}: coef {float(row['coef']):.4f}, SE {float(row['se']):.4f}, p {float(row['p_value']):.4f}, N {int(round(float(row['nobs'])))}"
            for row in missingness
        ],
        "",
        "### ML",
        f"- Lowest point-MAE ML model: {ml.get('model', 'NA')}",
        f"- Test MAE: {float(ml.get('test_mae', np.nan)):.4f}" if ml else "- Test MAE: NA",
        f"- Test RMSE: {float(ml.get('test_rmse', np.nan)):.4f}" if ml else "- Test RMSE: NA",
        f"- Test R2: {float(ml.get('test_r2', np.nan)):.4f}" if ml else "- Test R2: NA",
        f"- Bootstrap MAE interval for lowest point-MAE model: {ml_bootstrap.get('model', 'NA')} {float(ml_bootstrap.get('mae_ci_low', np.nan)):.4f}-{float(ml_bootstrap.get('mae_ci_high', np.nan)):.4f}" if ml_bootstrap else "- Bootstrap MAE interval: NA",
        f"- Best naive/statistical baseline: {ml_baseline.get('model', 'NA')}; MAE {float(ml_baseline.get('test_mae', np.nan)):.4f}" if ml_baseline else "- Best naive/statistical baseline: NA",
        f"- Benchmark decision: {ml_decision.strip().replace(chr(10), ' | ')}" if ml_decision else "- Benchmark decision: NA",
        f"- Best country-holdout point model: {country_holdout.get('model', 'NA')}; mean MAE {float(country_holdout.get('mean_mae', np.nan)):.4f}" if country_holdout else "- Country-holdout summary: NA",
        f"- ML importance stability diagnostic: {stability_note.strip().replace(chr(10), ' | ')}",
        "",
        "### Citizenship gap",
        f"- Mean gap: {extract_number(gap_ttest, r'Mean gap: ([-0-9.]+)')}",
        f"- Intercept-only clustered two-sided p-value: {extract_number(gap_ttest, r'Intercept-only two-sided p-value: (.+)')}",
        f"- Year-adjusted clustered two-sided p-value: {extract_number(gap_ttest, r'Year-adjusted two-sided p-value: (.+)')}",
        f"- Clustered gap coefficient: {float(gap_clustered.get('coef', np.nan)):.4f}" if gap_clustered else "- Clustered gap coefficient: NA",
        *gap_reg_lines,
        "",
        "### Trend and convergence",
        f"- Trend test: {extract_number(trend, r'Conclusion: (.+)')}",
        f"- Kendall tau: {extract_number(trend, r'Kendall tau: ([-0-9.]+)')}; p-value: {extract_number(trend, r'p-value: ([-0-9.]+)')}",
        f"- Sigma-convergence direction: {sigma_direction}",
        f"- Beta-convergence: {extract_number(convergence, r'Conclusion: (.+)')}",
        f"- Beta coefficient: {extract_number(convergence, r'Initial-level coefficient: ([-0-9.]+)')}; p-value: {extract_number(convergence, r'p-value: ([-0-9.]+)')}",
        "",
        "## Figures generated",
        *[f"- {p.relative_to(ROOT).as_posix()}" for p in figures],
        "",
        "## LaTeX tables generated",
        *[f"- {p.relative_to(ROOT).as_posix()}" for p in tables],
        "",
        "## Other output files",
        *[f"- {p.relative_to(ROOT).as_posix()}" for p in outputs],
        "",
        "## Errors or skipped steps",
        errors,
        "",
        "## Suspicious results for review",
        *[f"- {flag}" for flag in suspicious_results()],
        "",
        "## Quality check manual-review lists",
        "- Figures: " + (", ".join(fig_review) if fig_review else "None"),
        "- Tables: " + (", ".join(table_review) if table_review else "None"),
    ]
    (OUTPUTS / "master_analysis_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    figures, tables, outputs = generated_files()
    processed_data_dictionary()
    figures, tables, outputs = generated_files()
    output_generation_map(figures, tables)
    raw_data_download_instructions()
    figures, tables, outputs = generated_files()
    output_hash_manifest(figures, tables, outputs)
    outputs = sorted([p for p in OUTPUTS.iterdir() if p.is_file()])
    reproducibility_manifest()
    outputs = sorted([p for p in OUTPUTS.iterdir() if p.is_file()])
    fig_review = figure_quality_report(figures)
    table_review = table_quality_report(tables)
    (OUTPUTS / "random_seed.txt").write_text("All stochastic analyses used random_state=42\n", encoding="utf-8")
    if not ERROR_LOG.exists() or ERROR_LOG.read_text(encoding="utf-8").strip() == "":
        ERROR_LOG.write_text("No errors encountered.\n", encoding="utf-8")
    master_summary(figures, tables, outputs, fig_review, table_review)
    create_reproducibility_archive()

    steps_completed = ["0", "1", "2", "3", "4", "5", "6", "7"]
    skipped = []
    errors = read_text(ERROR_LOG).strip()
    if errors and errors != "No errors encountered.":
        skipped.append("See outputs/analysis_errors.log")
    print("FULL ANALYSIS COMPLETE")
    print(f"Steps completed: {steps_completed}")
    print(f"Steps skipped: {skipped if skipped else 'None'}")
    print(f"Total figures generated: {len(figures)}")
    print(f"Total LaTeX tables generated: {len(tables)}")
    print("Master summary saved to: outputs/master_analysis_summary.md")
    print("Ready for thesis writing phase.")


if __name__ == "__main__":
    main()
