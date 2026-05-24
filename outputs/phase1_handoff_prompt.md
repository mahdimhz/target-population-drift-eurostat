# Phase 1 Handoff Prompt

You are the next agent starting Phase 1 of the actual Master's thesis build for Mahdi Mohammadzadeh.

Use only the verified scoping choices from `outputs/final_scoping_report.md`. Do not re-decide the thesis scope unless new official evidence appears and is documented with URLs.

## Locked Scope

- Thesis direction: unmet medical care needs in Europe using Eurostat EU-SILC aggregate data.
- Primary dataset: `hlth_silc_08`.
- Primary outcome filter: `unit=PC`, `quantile=TOTAL`, `reason=TOOEFW`, `age=Y_GE16`, `sex=T`.
- Primary extraction years: 2008-2025, then restrict to verified non-missing country-year cells.
- Primary geography: national/country-level Europe.
- Exclude EU/EA aggregate codes from econometric models; they may be retained only as descriptive benchmarks.
- Robustness dataset: `hlth_silc_08b`.
- Robustness filter: `unit=PC`, `rskpovth=TOTAL`, `reason=TXP_TFAR_WLIST`, `age=Y_GE16`, `sex=T`.
- Robustness extraction years: 2021-2025, then restrict to verified non-missing country-year cells.

## Prohibited Unless New Evidence Is Produced

- Do not use a NUTS2 regional panel as the core design.
- Do not claim NUTS2 balanced panel feasibility.
- Do not merge EU-SILC and EHIS.
- Do not include ISTAT in the core thesis.
- Do not use microdata as the core thesis data source.
- Do not add substantive controls until each candidate control has verified Eurostat dataset code, definition, unit, geography, years, and missingness.
- Do not use causal language.
- Do not report coefficients as effects or impacts.

## First Tasks

1. Build a reproducible Eurostat extraction script for `hlth_silc_08` using the locked filter.
2. Save raw API responses and processed tidy data.
3. Produce a country-year missingness matrix for the primary outcome.
4. Identify and remove EU/EA aggregate codes from the econometric analysis dataset.
5. Create a status-flag and missing-data report before any modeling.
6. Create a separate control-variable feasibility audit before selecting covariates.
7. Only after the outcome and controls are verified, construct the analysis dataset.

## Methodology Guardrails

- Start with descriptive statistics, plots, and missingness tables.
- Use pooled association models only after verified controls exist.
- Add country and year fixed effects only if the final panel supports them.
- Use `hlth_silc_08b` only as denominator robustness for 2021-2025.
- Treat predictive ML as appendix-only and optional.
- Keep all claims descriptive or associational unless a later formal identification strategy is independently justified.

## Required Citations To Preserve

- Eurostat Statistics Explained, unmet health care needs: https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Unmet_health_care_needs_statistics
- Eurostat EU-SILC health metadata: https://ec.europa.eu/eurostat/cache/metadata/en/hlth_silc_01_esms.htm
- `hlth_silc_08` API extraction URL: https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/hlth_silc_08?lang=en&unit=PC&quantile=TOTAL&reason=TOOEFW&age=Y_GE16&sex=T
- `hlth_silc_08b` API extraction URL: https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/hlth_silc_08b?lang=en&unit=PC&rskpovth=TOTAL&reason=TXP_TFAR_WLIST&age=Y_GE16&sex=T
- EHIS/EU-SILC distinction: https://ec.europa.eu/eurostat/cache/metadata/en/hlth_det_esms.htm

## Output Expected From Phase 1 Builder

- Reproducible data extraction code.
- Raw data archive or documented raw API response files.
- Tidy primary outcome dataset.
- Missingness and status-flag report.
- Control-variable feasibility table.
- Updated advisor-facing scope note if new evidence changes feasibility.
