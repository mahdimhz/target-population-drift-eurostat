# Target-Population Drift and Conclusion Stability in Eurostat Unmet-Care Panels

This repository contains the reproducible code, data-processing pipeline, generated outputs, and LaTeX source for a Master's thesis on target-population drift in public Eurostat unmet-care panels.

The thesis develops a diagnostic drift-stability framework for public aggregate monitoring data. It combines a public-data estimand registry, the Target-Population Drift Index, the Conclusion Stability Index, rule-based failure classification, a multi-outcome Eurostat unmet-care application, and a semi-synthetic missingness simulation.

The work is aggregate and associational. It does not claim causal identification, individual-level effects, policy effects, a new estimator, or that multiple imputation corrects the data.

## Repository Structure

- `main.tex` - LaTeX entry point using the Luigi Vanvitelli thesis template.
- `abstract.tex`, `frontmatter/`, `chapters/`, `writing/` - thesis text, front matter, and bibliography.
- `src/` - analysis, data-processing, simulation, table, and figure scripts.
- `src/eurodrift/` and `eurodrift/` - reusable drift-audit utilities and command-line entry points.
- `configs/` - simulation and pipeline configuration files.
- `data/raw/` - raw Eurostat JSON downloads.
- `data/processed/` - processed country-year panel files.
- `outputs/` - generated analysis outputs, diagnostics, manifests, and reproducibility archive.
- `tables/` - generated LaTeX table fragments.
- `figures/` - generated PDF and PNG figures.
- `tests/` - pytest checks for data integrity, weights, registry validation, simulations, CLI behavior, and reproducibility outputs.
- `references/` - source-register material.
- `Latex-Luigi-Vanvitelli/`, `vanvfrontespizio.sty`, `Vanv-logo.pdf` - local thesis-template support files.

## Core Data Sources

The analysis uses public Eurostat aggregate tables. The main unmet-care and population sources are:

- `hlth_silc_08` - self-reported unmet medical examination or treatment need, population denominator.
- `hlth_silc_08b` - unmet medical need among persons reporting the same needs.
- `hlth_silc_09` - self-reported unmet dental examination or treatment need, population denominator.
- `hlth_silc_09b` - unmet dental need among persons reporting the same needs.
- `demo_pjan` - country-year population for year-normalized population weights.

The covariate panel also uses Eurostat macroeconomic, labour-market, poverty/social-exclusion, health-financing, inequality, and health-capacity tables, including `nama_10_pc`, `une_rt_a`, `ilc_peps01n`, `gov_10a_exp`, `hlth_sha11_hf`, `ilc_di12`, `une_ltu_a`, `hlth_rs_prs2`, and `hlth_rs_bds1`.

Exact filters, extraction dates, and source notes are documented in `references/source_register.csv`, `tables/eurostat_sources_appendix.tex`, and the generated manifests in `outputs/`.

## Reproducibility

Install dependencies with one of:

```powershell
python -m pip install -r requirements.txt
```

```powershell
conda env create -f environment.yml
conda activate unmet-care-thesis
```

Run the thesis pipeline from the repository root:

```powershell
python src/run_full_thesis_analysis.py
python src/generate_conceptual_selection_diagram.py
python src/run_missingness_robustness.py
python src/build_multi_outcome_indicator_registry.py
python src/build_multi_outcome_monitoring_benchmark.py
python src/build_multi_outcome_drift_diagnostics.py
python src/build_outcome_estimand_stability_matrix.py
python src/build_drift_stability_framework.py
python src/run_missingness_simulation.py --replicates 100 --imputations 2 --seed 42
python src/build_reporting_protocol_tables.py
python src/run_step5_ml_analysis.py
python src/run_step6_additional_analysis.py
python src/run_step7_master_summary.py
```

Compile the thesis with the available LaTeX toolchain:

```powershell
latexmk -pdf main.tex
```

or, if `latexmk` is unavailable:

```powershell
tectonic -X compile --outfmt pdf main.tex
```

Run tests with:

```powershell
python -m pytest tests -q
```

## Reusable Commands

The `eurodrift` command-line interface provides compact smoke checks:

```powershell
python -m eurodrift report --indicator hlth_silc_08
python -m eurodrift simulate --config configs/simulation_primary.yml --smoke
python -m eurodrift reproduce-thesis
```

These commands generate a compact indicator report, run a simulation smoke test, and rerun the thesis-specific report builders from the current local data files.

## Outputs

Important generated outputs include:

- `outputs/reproducibility_manifest.json` - package versions, command order, input/script hashes, output hashes, and modelling metadata.
- `outputs/output_manifest_hashes.csv` - SHA-256 hashes and file sizes for generated outputs.
- `outputs/processed_data_dictionary.csv` - processed-data column dictionary.
- `outputs/table_figure_generation_map.csv` - table/figure to script/input/chapter map.
- `outputs/reproducibility_archive.zip` - local reproducibility archive for submission.
- `tables/` - LaTeX-ready generated tables.
- `figures/` - generated figures used in the thesis.
- `main.pdf` - compiled thesis PDF.

## Thesis Status

This is a thesis repository under active revision. Administrative front matter, including the Declaration and Acknowledgements pages, may still be finalized before submission.

The GitHub remote for review is:

```text
https://github.com/mahdimhz/unmet-medical-care-needs-europe-thesis.git
```

The current feature branch is used for review before any merge to `main`. Do not push before confirming that tests pass, the PDF compiles, and the intended files are staged. No public repository is cited in the thesis unless the repository or archive is finalized and approved for citation.

## Limitations

The thesis uses public aggregate country-year data. The results should be interpreted as monitoring and sensitivity evidence, not as individual-level mechanisms or causal policy effects. Complete-case selection, population weighting, country-universe restriction, and missing-data assumptions change the estimand being reported. Multiple imputation and MNAR sensitivity analyses are treated as model-based sensitivity checks, not corrections that recover an unobserved true coefficient.

## Citation

Citation details will be added after final thesis submission or public archiving.
