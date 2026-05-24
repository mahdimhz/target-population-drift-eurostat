# Thesis Roadmap

Date accessed: 2026-05-14

This roadmap is built from the verified scoping audit. It assumes the safest core is Eurostat aggregate data, not microdata.

## Recommended Title Options

| Option | Title | Use if | Evidence |
|---|---|---|---|
| 1 | **Unmet Medical Care Needs in Europe: A Eurostat EU-SILC Aggregate Panel Analysis** | Advisor accepts a national European panel. | Safest dataset is `hlth_silc_08`: https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/hlth_silc_08?lang=en&unit=PC&quantile=TOTAL&reason=TOOEFW&age=Y_GE16&sex=T |
| 2 | **Inequalities in Self-Reported Unmet Medical Needs Across European Countries** | Thesis should emphasize inequality but remain national-level. | Eurostat Statistics Explained uses EU-SILC unmet-needs data: https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Unmet_health_care_needs_statistics |
| 3 | **Regional Patterns in Unmet Medical Care Needs in Europe: A Conservative Eurostat Feasibility-Based Analysis** | Advisor requires regional framing and accepts a latest-year cross-section. | Regional panel not verified; regional cross-section is safer: https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/hlth_silc_08_r?lang=en&unit=PC&reason=TOOEFW |

Recommended default title: **Unmet Medical Care Needs in Europe: A Eurostat EU-SILC Aggregate Panel Analysis**.

## Main Research Question

How have self-reported unmet needs for medical examination due to financial reasons, distance, or waiting lists varied across European countries over time, and what verified aggregate country-level factors are associated with those differences?

Evidence for outcome: https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/hlth_silc_08?lang=en&unit=PC&quantile=TOTAL&reason=TOOEFW&age=Y_GE16&sex=T

## Subquestions

1. What are the levels and trends in self-reported unmet medical needs across European countries?
2. Which countries show persistently high or low unmet-need rates under the verified `hlth_silc_08` indicator?
3. How sensitive are descriptive conclusions to the denominator change in `hlth_silc_08b` for 2021-2025?
4. Which verified Eurostat country-level covariates are associated with unmet medical needs after matching geography and years?
5. If regional analysis remains required, what does the latest verified regional cross-section show after valid NUTS2 filtering?

## Chapter Structure

| Chapter | Content | Guardrail |
|---|---|---|
| 1. Introduction | Motivation, research question, scope, contribution, and explicit non-causal framing. | Do not promise NUTS2 panel or microdata unless later verified. |
| 2. Data and Indicator Definitions | Eurostat EU-SILC source, `hlth_silc_08` outcome, denominator, years, geography, missingness, and `08` vs `08b` distinction. | Cite Eurostat metadata and API URLs next to every definition. |
| 3. Descriptive Evidence | Time trends, cross-country dispersion, country rankings, missingness tables, and denominator sensitivity for `08b`. | Report flags and missing data before interpretation. |
| 4. Econometric Association Analysis | Baseline pooled associations and optional fixed-effects extension if panel completeness and controls permit. | Use “association,” not “effect.” |
| 5. Robustness and Extensions | `hlth_silc_08b` short-period comparison; optional regional cross-section; optional predictive appendix only if sample size permits. | Keep EHIS and ISTAT separate unless separately audited. |
| 6. Discussion and Conclusion | What the aggregate evidence can and cannot say; limitations; data caveats; future work. | Declare non-causal design and denominator/methodology limitations. |

## Recommended Timeline

| Stage | Duration | Output | Dependency |
|---|---:|---|---|
| 1. Final data extraction audit | 1 week | Reproducible extraction script, raw downloaded data, missingness report for `hlth_silc_08`. | Eurostat API docs: https://ec.europa.eu/eurostat/web/user-guides/data-browser/api-data-access/api-getting-started |
| 2. Control-variable feasibility audit | 1 week | Candidate controls table with dataset codes, definitions, years, geographies, and missingness. | No controls selected yet; must be verified before modeling. |
| 3. Descriptive analysis | 1 week | Figures and tables for outcome levels, trends, dispersion, and missing data. | Completed extraction audit. |
| 4. Baseline association models | 1 week | Pooled model and carefully documented fixed-effects candidate if feasible. | Verified controls and complete enough panel. |
| 5. Robustness checks | 1 week | `hlth_silc_08b` 2021-2025 denominator comparison and sensitivity tables. | `08b` extraction: https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/hlth_silc_08b?lang=en&unit=PC&rskpovth=TOTAL&reason=TXP_TFAR_WLIST&age=Y_GE16&sex=T |
| 6. Optional extension decision | 3-5 days | Go/no-go note for regional cross-section, ML appendix, or ISTAT appendix. | Additional feasibility checks. |
| 7. Writing and revision | 2-3 weeks | Full thesis draft, advisor feedback revision, final reproducibility package. | Stable results and locked scope. |

## Recommended Order Of Work

1. Freeze the primary outcome as `hlth_silc_08` with the standard filter unless the professor rejects national scope.
2. Write a reproducible Eurostat extraction script and save raw API responses.
3. Create a country-year missingness matrix for the outcome before choosing models.
4. Audit candidate controls from Eurostat one by one; record dataset code, definition, unit, geography, years, and missingness.
5. Build the analysis dataset only after outcome and controls pass the same geography/year checks.
6. Produce descriptive tables and figures before econometric models.
7. Estimate pooled associations using only verified controls.
8. Add fixed effects only if the final panel has enough repeated observations and within-country variation.
9. Run denominator robustness using `hlth_silc_08b` for 2021-2025, keeping it separate from `hlth_silc_08`.
10. Decide whether to include a regional cross-section or ML appendix only after the core results are stable.

## Scope Decisions To Preserve

| Decision | Default | Reason |
|---|---|---|
| Primary source | Eurostat | User requirement and verified Phase 2-4 evidence. |
| Primary outcome | `hlth_silc_08`, `reason=TOOEFW`, `age=Y_GE16`, `sex=T`, `quantile=TOTAL`, `unit=PC` | Safest verified national aggregate outcome. |
| Default geography | National/country-level Europe | Regional panel feasibility not verified. |
| Default years | 2008-2025 as returned by the standard API filter, subject to final non-missing country-year audit | Time categories verified for `hlth_silc_08`; completeness still must be checked. |
| Microdata | Do not pursue as default | Restricted access risk. Evidence: https://ec.europa.eu/eurostat/cache/metadata/en/hlth_silc_01_esms.htm |
| ISTAT | Do not include in core thesis | Compatibility not verified. |
| Causal claims | Avoid | No identification design verified. |

## Professor Confirmation Needed

1. Is a national European panel acceptable, or must the thesis be explicitly NUTS2 regional?
2. Is the preferred outcome the all-population unmet-need prevalence (`hlth_silc_08`) or the persons-with-need access-failure measure (`hlth_silc_08b`)?
3. Should predictive ML be excluded entirely, kept as an appendix, or treated as a secondary exploratory chapter?
4. Should Italy/ISTAT be excluded unless a separate compatibility audit passes?
