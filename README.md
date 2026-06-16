# Target-Population Drift in Eurostat Unmet-Care Panels

Reproducible MSc thesis project by Mahdi Mohammadzadeh, MSc in Data Science, Universita degli Studi della Campania Luigi Vanvitelli, academic year 2025--2026.

## Thesis Identity

This thesis contributes a reproducible target-population drift audit protocol for public Eurostat aggregate unmet-care panels. It shows how denominator choice, country-universe restriction, population weighting, covariate completeness, missing-data assumptions, and validation design change the empirical interpretation of poverty-related unmet-care gradients. The contribution is methodological-applied: it improves how aggregate health-access monitoring results are reported and interpreted without claiming individual-level mechanisms or causal policy effects.

The central empirical audit tracks the movement from 608 primary outcome-observed country-years to 282 complete-case fixed-effects rows, extends the audit to multiple unmet-care indicators, and adds a semi-synthetic missingness simulation using a reference estimand.

## Repository Status

The GitHub remote used for this project is:

```powershell
https://github.com/mahdimhz/unmet-medical-care-needs-europe-thesis.git
```

No public repository is cited in the thesis unless the remote is populated and verified. The recommended final publishing sequence after the final validation step is:

```powershell
git add .
git commit -m "Reproducible thesis sensitivity audit"
git push -u origin main
```

Do not push before confirming that the full pipeline, tests, reproducibility archive, and PDF compile from a clean checkout. Public GitHub/OSF citation remains optional until supervisor approval.

## Folder Structure

- `chapters/` - LaTeX thesis chapter files.
- `frontmatter/` - declaration, acknowledgements, and front-matter components.
- `writing/` - bibliography and writing support files.
- `references/` - source register and supporting reference tables.
- `src/` - scripted data extraction, analysis, diagnostics, and reporting.
- `src/eurodrift/` - reusable target-population drift audit utilities and CLI.
- `configs/` - simulation and reproducibility configuration files.
- `tests/` - pytest checks for core reproducibility assumptions.
- `data/raw/` - raw Eurostat JSON downloads, ignored by git by default.
- `data/processed/` - processed country-year CSV files.
- `outputs/` - generated analysis results, diagnostics, manifests, and local archive.
- `tables/` - generated LaTeX table fragments.
- `figures/` - generated PDF figures.
- `Latex-Luigi-Vanvitelli/` and `vanvfrontespizio.sty` - local Luigi Vanvitelli thesis theme support.

## Environment

Install with `requirements.txt`:

```powershell
python -m pip install -r requirements.txt
```

Or create the optional conda environment:

```powershell
conda env create -f environment.yml
conda activate unmet-care-thesis
```

The exact package versions from each complete run are written to `outputs/reproducibility_manifest.json`. Scripted stochastic steps use seed `42` unless a script states otherwise.

## Reproduce the Analysis

Run from the project root:

```powershell
python src/run_full_thesis_analysis.py
python src/generate_conceptual_selection_diagram.py
python src/run_missingness_robustness.py
python src/build_multi_outcome_indicator_registry.py
python src/build_multi_outcome_monitoring_benchmark.py
python src/build_multi_outcome_drift_diagnostics.py
python src/build_outcome_estimand_stability_matrix.py
python src/run_missingness_simulation.py --replicates 100 --imputations 2 --seed 42
python src/build_reporting_protocol_tables.py
python src/run_step5_ml_analysis.py
python src/run_step6_additional_analysis.py
python src/run_step7_master_summary.py
```

Then compile the thesis:

```powershell
latexmk -pdf main.tex
```

If `latexmk` is unavailable, compile with Tectonic:

```powershell
tectonic -X compile --outfmt pdf main.tex
```

## Tests

Run the checks:

```powershell
python -m pytest tests -q
```

The tests check population weights, target counts, indicator registry validation, multi-outcome monitoring, drift diagnostics, coefficient classification, MI plausibility, raw/log GDP consistency, MNAR shifts, lagged prediction features, simulation reproducibility, generated output existence, CLI smoke behavior, and the reproducibility package.

## Reusable CLI

The `eurodrift` module exposes a compact command-line interface for smoke checks and reuse:

```powershell
python -m eurodrift report --indicator hlth_silc_08
python -m eurodrift simulate --config configs/simulation_primary.yml --smoke
python -m eurodrift reproduce-thesis
```

The first command writes a compact indicator coverage report. The second command runs a 20-replicate simulation smoke test using seed 42. The third command reruns the thesis-specific audit builders and summary manifest from the current local data files.

## Raw Data Download Workflow

Raw Eurostat JSON files are produced by the extraction steps inside `src/run_full_thesis_analysis.py` and helper scripts using `src/eurostat_api.py`. Dataset codes, filters, extraction notes, and source verification are documented in:

- `references/source_register.csv`
- `tables/eurostat_sources_appendix.tex`
- `outputs/raw_data_download_instructions.md`
- `outputs/population_extraction_notes.txt`
- `outputs/hlth_silc_08_api_url.txt`
- `outputs/hlth_silc_08b_api_url.txt`
- `outputs/hlth_silc_32_extraction_notes.txt`

Eurostat tables used include `hlth_silc_08`, `hlth_silc_08b`, `hlth_silc_32`, `demo_pjan`, `nama_10_pc`, `une_rt_a`, `ilc_peps01n`, `gov_10a_exp`, `hlth_sha11_hf`, `ilc_di12`, `une_ltu_a`, `hlth_rs_prs2`, and `hlth_rs_bds1`.

## Main Reproducibility Outputs

- `outputs/reproducibility_manifest.json` - Python version, package versions, command order, input/script hashes, output hashes, and ML hyperparameter grids.
- `outputs/output_manifest_hashes.csv` - file sizes and SHA-256 hashes for generated tables, figures, and output files.
- `outputs/processed_data_dictionary.csv` - column-level dictionary for processed CSV files.
- `outputs/processed_data_dictionary_summary.csv` - file-level processed-data summary.
- `outputs/table_figure_generation_map.csv` - table/figure to script/input/chapter map.
- `outputs/raw_data_download_instructions.md` - raw Eurostat download instructions.
- `outputs/reproducibility_archive.zip` - local archive for submission.
- `outputs/master_analysis_summary.md` - compact summary of generated results and quality checks.

## Table and Figure Generation Map

- `src/run_full_thesis_analysis.py` builds the panel, descriptive diagnostics, baseline regression tables, population-weighted trend, model ladder, and source/register outputs.
- `src/generate_conceptual_selection_diagram.py` builds the conceptual selection and estimand diagram.
- `src/run_missingness_robustness.py` builds target-population sensitivity, IPW diagnostics, MI diagnostics, MNAR sensitivity, and poverty-robustness outputs.
- `src/build_multi_outcome_indicator_registry.py` builds the public-data estimand registry.
- `src/build_multi_outcome_monitoring_benchmark.py` builds the multi-outcome monitoring benchmark.
- `src/build_multi_outcome_drift_diagnostics.py` builds multi-outcome attrition and retention diagnostics.
- `src/build_outcome_estimand_stability_matrix.py` builds the outcome-by-estimand coefficient matrix and classifications.
- `src/run_missingness_simulation.py` builds the semi-synthetic missingness simulation.
- `src/build_reporting_protocol_tables.py` builds the reporting checklist, failure-mode table, and final classification table.
- `src/run_step5_ml_analysis.py` builds one-year-ahead prediction baselines, reduced benchmark model comparisons, and country-holdout outputs.
- `src/run_step6_additional_analysis.py` builds citizenship paired-gap and `hlth_silc_08b` denominator-check outputs.
- `src/run_step7_master_summary.py` builds the reproducibility manifest, data dictionary, command order, hashes, output map, and archive.

## License

No license assigned. All rights reserved. Copyright Mahdi Mohammadzadeh 2026.
