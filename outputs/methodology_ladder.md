# Methodology Ladder

Date accessed: 2026-05-14

This Phase 5 file proposes methodology options only after the Phase 2-4 evidence audit. It does not make causal claims and does not select final controls.

## Evidence Base

| Evidence point | Status | Source |
|---|---|---|
| Safest core dataset is `hlth_silc_08` for national Eurostat aggregate analysis. | VERIFIED | https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/hlth_silc_08?lang=en&unit=PC&quantile=TOTAL&reason=TOOEFW&age=Y_GE16&sex=T |
| `hlth_silc_08` standard filter returned time categories 2008-2025. | VERIFIED for the standard filter only | https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/hlth_silc_08?lang=en&unit=PC&quantile=TOTAL&reason=TOOEFW&age=Y_GE16&sex=T |
| `hlth_silc_08b` and `hlth_silc_08b_r` use a persons-with-need denominator and returned 2021-2025 under standard filters. | VERIFIED for the standard filters only | https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/hlth_silc_08b?lang=en&unit=PC&rskpovth=TOTAL&reason=TXP_TFAR_WLIST&age=Y_GE16&sex=T ; https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/hlth_silc_08b_r?lang=en&unit=PC&reason=TXP_TFAR_WLIST |
| NUTS2 panel feasibility is not verified. | VERIFIED constraint | https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/hlth_silc_08_r?lang=en&unit=PC&reason=TOOEFW |
| EU-SILC and EHIS unmet-needs indicators are not interchangeable. | VERIFIED | https://ec.europa.eu/eurostat/cache/metadata/en/hlth_det_esms.htm |
| Restricted EU-SILC microdata access is not a safe default for this thesis. | VERIFIED | https://ec.europa.eu/eurostat/cache/metadata/en/hlth_silc_01_esms.htm |

## Layered Methodology

| Layer | Objective | Data requirement | Minimal assumptions | Likely risks | Type | Thesis location | Recommendation |
|---|---|---|---|---|---|---|---|
| Layer 0 — descriptive/statistical profile | Describe levels, trends, country dispersion, and missingness for unmet medical needs. | `hlth_silc_08`, standard filter `unit=PC&quantile=TOTAL&reason=TOOEFW&age=Y_GE16&sex=T`; final extraction must show non-missing country-year cells. | Published Eurostat aggregates are comparable enough for descriptive reporting after declared breaks and flags. | Missingness, country composition changes, methodology change around 2015. | Descriptive, not causal. | Core thesis. | Recommended. |
| Layer 1 — baseline econometric model | Estimate associations between unmet medical needs and verified country-level covariates. | Layer 0 outcome plus Eurostat controls verified to match geography, years, and definitions. | Conditional associations are interpretable as descriptive relationships only. | Omitted variables, reverse causality, small country panel, control mismatch. | Explanatory econometrics, non-causal. | Core only after controls audit. | Recommended with strict language. |
| Layer 2 — panel extension | Add country and year fixed effects if country-year panel completeness supports it. | Repeated country-year observations for outcome and controls; enough within-country variation. | Unit fixed effects absorb time-invariant country differences; year fixed effects absorb common shocks. | Overfitting with small panels, weak within variation, serial correlation, unbalancedness. | Explanatory econometrics, non-causal unless identification is separately justified. | Core or robustness, depending on completeness. | Optional. |
| Layer 3 — robustness checks | Test whether findings change under safer alternative definitions and samples. | `hlth_silc_08b` for 2021-2025; alternative reason categories if documented; exclusion of flagged or sparse countries. | Robustness checks are sensitivity exercises, not proof of causality. | Denominator changes between `08` and `08b`; short period for `08b`; interpretation drift. | Explanatory sensitivity. | Core robustness or appendix. | Recommended for denominator transparency. |
| Layer 4 — predictive ML extension | Predict unmet-need levels using verified aggregate predictors and compare out-of-sample error to simple baselines. | Enough country-year or regional observations after missingness checks; train/test split or cross-validation documented. | Predictive performance is evaluated out of sample; prediction does not imply explanation or causality. | Too few observations, leakage across years, overfitting, unstable feature importance. | Predictive, not explanatory. | Appendix only unless advisor explicitly wants ML. | Optional and risky. |
| Layer 5 — optional spatial or Italy-focused extension | Add a regional cross-section or Italy descriptive appendix if regional/ISTAT feasibility is separately verified. | For regional: latest-year `hlth_silc_08_r` or `hlth_silc_08b_r` with valid NUTS2 filter and missingness table. For ISTAT: verified comparable definition, years, geography, and access. | Extension remains separate from the national Eurostat core unless definitions are proven compatible. | Mixed NUTS levels, incomplete regions, ISTAT comparability failure, scope creep. | Descriptive or exploratory. | Appendix or separate chapter only. | Risky unless additional audit passes. |

## Explanatory Econometrics

Recommended starting point:

| Step | Safe specification boundary | Evidence |
|---|---|---|
| Descriptive panel table | Report country-year outcome availability before estimating anything. | Phase 3 verified time categories but not final complete country-year panel cells: https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/hlth_silc_08?lang=en&unit=PC&quantile=TOTAL&reason=TOOEFW&age=Y_GE16&sex=T |
| Pooled association model | Use only verified controls with same country-year coverage; call coefficients associations. | Controls were not audited in Phases 1-4, so no control should be added without a matching source audit. |
| Fixed-effects extension | Use only if enough within-country variation and panel completeness remain after control matching. | Fixed-effects panel methods are standard for panel data but do not by themselves identify causal effects; academic method reference: https://www.jstor.org/stable/j.ctvcm4j72 |
| Inference | Use conservative standard errors appropriate to the final data shape; document cluster count limits if clustering is used. | Cluster-robust inference depends on clustering structure and sample size; method reference: https://arxiv.org/abs/1710.02926 |

## Predictive Machine Learning

ML should be a secondary extension only.

| Rule | Safe implementation | Evidence |
|---|---|---|
| Prediction target | Predict `hlth_silc_08` levels or changes only after the final panel is assembled. | Outcome feasibility evidence: https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/hlth_silc_08?lang=en&unit=PC&quantile=TOTAL&reason=TOOEFW&age=Y_GE16&sex=T |
| Baseline comparison | Compare any ML model against simple baselines such as country mean, year mean, or linear model. | Statistical learning reference for prediction framing and validation: https://link.springer.com/book/10.1007/978-0-387-21606-5 |
| Validation | Use out-of-sample validation; avoid reporting in-sample fit as evidence of useful prediction. | Cross-validation reference: https://hastie.su.domains/ElemStatLearnII_figures/figures7.pdf |
| Interpretation | Treat feature importance as exploratory, not causal. | Prediction methods do not establish causal effects without identification design; econometric reference: https://www.jstor.org/stable/j.ctvcm4j72 |

## Causal Language To Avoid

Do not use:

- “effect of income on unmet healthcare needs”
- “impact of regional deprivation”
- “causes unmet needs”
- “policy effect”
- “determinants” unless carefully defined as correlates
- “inequality caused by”

Use instead:

- “association between”
- “correlates of”
- “patterns in”
- “differences across countries or regions”
- “predictive relationship”
- “descriptive inequality”

## Claims The Thesis Can Safely Make

| Safe claim | Condition | Evidence |
|---|---|---|
| Eurostat EU-SILC aggregate data can support a national descriptive panel on self-reported unmet medical needs. | Use `hlth_silc_08` and document final missingness. | https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/hlth_silc_08?lang=en&unit=PC&quantile=TOTAL&reason=TOOEFW&age=Y_GE16&sex=T |
| The thesis can compare all-population and persons-with-need denominators as a robustness or interpretation exercise. | Keep `hlth_silc_08` and `hlth_silc_08b` separate. | https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Unmet_health_care_needs_statistics ; https://ec.europa.eu/eurostat/api/dissemination/sdmx/3.0/structure/dataflow/ESTAT/hlth_silc_08b/1.0?compress=false |
| A regional cross-section may be feasible after NUTS2 filtering and missingness reporting. | Do not claim panel feasibility before a year-by-year NUTS2 audit. | https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/hlth_silc_08_r?lang=en&unit=PC&reason=TOOEFW |
| The thesis can make descriptive and associational claims. | No causal identification design has been verified. | Method reference: https://www.jstor.org/stable/j.ctvcm4j72 |

## Claims The Thesis Should NOT Make

| Unsafe claim | Why not | Evidence |
|---|---|---|
| “A balanced NUTS2 panel is available.” | Not verified; regional API responses include mixed geography-code levels. | https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/hlth_silc_08_r?lang=en&unit=PC&reason=TOOEFW |
| “EU-SILC and EHIS unmet needs are equivalent.” | Eurostat metadata states they differ in questions, denominator, age, sequence, concept, and context. | https://ec.europa.eu/eurostat/cache/metadata/en/hlth_det_esms.htm |
| “The model estimates causal effects.” | No exogenous variation, policy design, instrument, or quasi-experimental design has been verified. | https://www.jstor.org/stable/j.ctvcm4j72 |
| “ISTAT can be merged with Eurostat for Italy.” | ISTAT comparability has not been audited. | Phase 4 evidence summary: `outputs/thesis_design_feasibility.md` |
| “Microdata will be used.” | EU-SILC microdata access is restricted and not secured. | https://ec.europa.eu/eurostat/cache/metadata/en/hlth_silc_01_esms.htm |
