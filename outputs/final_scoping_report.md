# Final Scoping Report

Date accessed: 2026-05-14  
Student: Mahdi Mohammadzadeh

This report closes the pre-Phase-1 scoping audit. It recommends a conservative thesis scope based only on verified official Eurostat evidence and clearly labeled secondary evidence.

## 1. Verified Thesis Direction

Recommended direction: **a reproducible Eurostat EU-SILC aggregate analysis of self-reported unmet medical care needs in Europe, using a national/country-level panel as the safest core design.**

Evidence: `hlth_silc_08` is a verified Eurostat dataflow and the standard Phase 3 API filter returned time categories 2008-2025. Source: https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/hlth_silc_08?lang=en&unit=PC&quantile=TOTAL&reason=TOOEFW&age=Y_GE16&sex=T

If the professor requires a regional thesis, the conservative alternative is **a latest-year regional cross-section**, not a regional panel, unless a new year-by-year NUTS2 completeness audit proves panel feasibility. Source: https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/hlth_silc_08_r?lang=en&unit=PC&reason=TOOEFW

## 2. Exact Recommended Data Source(s)

| Role | Source | Status | Evidence |
|---|---|---|---|
| Primary source | Eurostat EU-SILC aggregate table `hlth_silc_08` | Recommended | https://ec.europa.eu/eurostat/api/dissemination/sdmx/3.0/structure/dataflow/ESTAT/hlth_silc_08/1.0?compress=false |
| Denominator robustness source | Eurostat EU-SILC aggregate table `hlth_silc_08b` | Recommended as robustness only | https://ec.europa.eu/eurostat/api/dissemination/sdmx/3.0/structure/dataflow/ESTAT/hlth_silc_08b/1.0?compress=false |
| Regional fallback source | `hlth_silc_08_r` or `hlth_silc_08b_r` | Possible but risky | https://ec.europa.eu/eurostat/api/dissemination/sdmx/3.0/structure/dataflow/ESTAT/hlth_silc_08_r/1.0?compress=false ; https://ec.europa.eu/eurostat/api/dissemination/sdmx/3.0/structure/dataflow/ESTAT/hlth_silc_08b_r/1.0?compress=false |
| EHIS | Not a substitute for EU-SILC | Not recommended for merged analysis | https://ec.europa.eu/eurostat/cache/metadata/en/hlth_det_esms.htm |

## 3. Exact Recommended Outcome Variable(s)

Primary outcome:

| Item | Choice |
|---|---|
| Dataset | `hlth_silc_08` |
| Exact title | Self-reported unmet needs for medical examination by sex, age, main reason declared and income quintile |
| Filter | `unit=PC`, `quantile=TOTAL`, `reason=TOOEFW`, `age=Y_GE16`, `sex=T` |
| Interpretation | Percentage indicator for self-reported unmet needs for medical examination due to being too expensive, too far to travel, or waiting list among persons aged 16+ in private households. |
| Evidence | https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/hlth_silc_08?lang=en&unit=PC&quantile=TOTAL&reason=TOOEFW&age=Y_GE16&sex=T ; https://ec.europa.eu/eurostat/cache/metadata/en/hlth_silc_01_esms.htm |

Robustness outcome:

| Item | Choice |
|---|---|
| Dataset | `hlth_silc_08b` |
| Exact title | Self-reported unmet needs for medical examination due to financial reasons, long waiting list or distance by sex, age and risk of poverty threshold - % of the persons having the same needs |
| Filter | `unit=PC`, `rskpovth=TOTAL`, `reason=TXP_TFAR_WLIST`, `age=Y_GE16`, `sex=T` |
| Interpretation | Percentage of persons having the same medical needs who report unmet needs due to financial reasons, waiting list, or distance. |
| Evidence | https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/hlth_silc_08b?lang=en&unit=PC&rskpovth=TOTAL&reason=TXP_TFAR_WLIST&age=Y_GE16&sex=T |

## 4. Exact Recommended Geography

Core geography: **national/country-level Europe using Eurostat `geo` country codes from `hlth_silc_08`; exclude EU/EA aggregate codes from econometric models and use them only as descriptive benchmarks if needed.**

Reason: NUTS2 panel feasibility is not verified. Regional APIs returned mixed country-like and regional-looking geo codes. Evidence: https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/hlth_silc_08_r?lang=en&unit=PC&reason=TOOEFW

## 5. Exact Recommended Years

Primary extraction years: **2008-2025 as returned by the `hlth_silc_08` standard API filter**, subject to a final country-year non-missing audit before modeling.

Robustness extraction years: **2021-2025 for `hlth_silc_08b` under the standard filter**, subject to non-missing audit.

Evidence: https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/hlth_silc_08?lang=en&unit=PC&quantile=TOTAL&reason=TOOEFW&age=Y_GE16&sex=T ; https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/hlth_silc_08b?lang=en&unit=PC&rskpovth=TOTAL&reason=TXP_TFAR_WLIST&age=Y_GE16&sex=T

Do not claim a balanced panel until non-missing country-year cells are verified.

## 6. Exact Recommended Baseline Controls

No substantive baseline controls are verified yet.

Recommended safe baseline:

| Component | Include? | Reason |
|---|---|---|
| Country indicators or country fixed effects | Yes, after final panel construction confirms repeated country observations. | Captures stable country-level differences without inventing unverified covariates. |
| Year indicators or year fixed effects | Yes, after final panel construction confirms usable repeated years. | Captures common shocks and time patterns. |
| Substantive Eurostat covariates | Not yet. | Dataset codes, definitions, units, geography, and years were not audited in this scoping package. |

Before adding any substantive controls, the Phase 1 builder must create a control-variable feasibility table with official Eurostat dataset codes, definitions, units, years, geography, and missingness.

## 7. Whether ISTAT Should Be Included

Recommendation: **Do not include ISTAT in the core thesis.**

Reason: ISTAT has official health-service access material, but this audit did not verify a Eurostat-compatible ISTAT dataset, definition, geography, time structure, or reproducible extraction path. It may be considered only as a separate appendix after a dedicated ISTAT compatibility audit.

Evidence: `outputs/thesis_design_feasibility.md`

## 8. Whether Microdata Should Be Pursued

Recommendation: **Do not pursue microdata as the default thesis core.**

Reason: Eurostat metadata states that direct access to anonymised EU-SILC microdata is through research contracts and individuals cannot be granted direct access.

Evidence: https://ec.europa.eu/eurostat/cache/metadata/en/hlth_silc_01_esms.htm

## 9. Recommended Econometric Core

Recommended sequence:

1. Descriptive country-year panel profile for `hlth_silc_08`.
2. Missingness and status-flag audit before modeling.
3. Pooled association model only after verified controls are added.
4. Country and year fixed-effects extension only if the final panel has enough repeated observations and within-country variation.
5. `hlth_silc_08b` denominator robustness for 2021-2025.

All econometric language must be non-causal unless a later identification design is justified with new evidence.

## 10. Recommended ML Role

Recommendation: **ML is optional and appendix-only.**

Allowed role: prediction benchmark after the final analysis dataset is built, using out-of-sample validation and comparison to simple baselines.

Not allowed: using ML feature importance as causal evidence.

## 11. Key Limitations To Declare From Day 1

- The primary design uses aggregate published Eurostat indicators, not individual microdata.
- The safest design is national/country-level, not NUTS2 regional.
- Regional panel feasibility is not verified.
- `hlth_silc_08` and `hlth_silc_08b` have different denominator interpretations.
- The 2015 EU-SILC unmet-needs guideline/methodology change must be acknowledged.
- EHIS and EU-SILC unmet-needs indicators are not interchangeable.
- Substantive controls are not yet verified.
- The analysis can support descriptive and associational claims only.

## 12. Do Not Do This

- Do not claim a balanced NUTS2 panel exists.
- Do not merge EU-SILC and EHIS unmet-needs outcomes.
- Do not merge ISTAT and Eurostat without a dedicated comparability audit.
- Do not use microdata unless institutional access is already secured.
- Do not add Eurostat controls without verifying dataset code, definition, unit, geography, years, and missingness.
- Do not describe coefficients as causal effects.
- Do not hide missing data, flags, breaks, or denominator changes.

## 13. Open Questions For The Professor

1. Is a national European panel acceptable, or must the thesis be explicitly regional?
2. If regional scope is mandatory, is a latest-year regional cross-section acceptable?
3. Should the thesis prioritize the broad all-population indicator `hlth_silc_08` or the persons-with-need measure `hlth_silc_08b`?
4. Should predictive ML be excluded entirely or kept as an appendix-only extension?
5. Should ISTAT be excluded unless a separate compatibility audit passes?

## 14. Handoff Specification For The Next Agent

The next agent must start Phase 1 of the actual thesis build using the verified choices in this report:

- Primary source: Eurostat.
- Primary outcome: `hlth_silc_08` with `unit=PC`, `quantile=TOTAL`, `reason=TOOEFW`, `age=Y_GE16`, `sex=T`.
- Core geography: national/country-level Europe; exclude EU/EA aggregate codes from econometric models.
- Core years: 2008-2025 as extraction target, then restrict to verified non-missing country-year cells.
- Robustness outcome: `hlth_silc_08b` with `unit=PC`, `rskpovth=TOTAL`, `reason=TXP_TFAR_WLIST`, `age=Y_GE16`, `sex=T`, for 2021-2025 extraction target.
- Do not use NUTS2 panel, ISTAT, EHIS, microdata, or ML as the core unless new evidence is produced and documented.
- First technical task: create a reproducible Eurostat extraction and missingness audit before modeling.

## Final Checks

| Check | Result | Evidence |
|---|---|---|
| Official sources registered | PASS | `references/source_register.csv` and `notes/source_register_summary.md` |
| Dataset codes verified | PASS | `outputs/dataset_audit.xlsx`; SDMX endpoints for `hlth_silc_08`, `hlth_silc_08b`, `hlth_silc_08_r`, `hlth_silc_08b_r` |
| Geography feasibility verified | PASS with limitation | National/country-level feasible as safest core; NUTS2 panel not verified. |
| Year feasibility verified | PASS with limitation | `hlth_silc_08` standard filter returned 2008-2025; non-missing panel completeness still must be audited. |
| Methodology change acknowledged | PASS | `notes/source_register_summary.md`; `outputs/methodology_ladder.md` |
| Recommended design selected | PASS | Design A selected as safest core in `outputs/thesis_design_feasibility.md`. |
| Risky designs flagged | PASS | Designs B, D, E and NUTS2-panel assumptions flagged in `outputs/thesis_design_feasibility.md`. |
| Handoff prompt created | PASS | `outputs/phase1_handoff_prompt.md` |
| No unsupported claims in summary | PASS with caveat | Substantive controls, NUTS2 panel, ISTAT compatibility, and microdata access remain explicitly unverified. |
