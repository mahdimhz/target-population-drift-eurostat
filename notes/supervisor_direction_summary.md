# Supervisor Direction Summary: Target-Population Drift Audit Protocol

## Purpose of the Change

The current thesis is a single-outcome Eurostat sensitivity audit. It studies `hlth_silc_08`, documents that 608 outcome-observed country-years become 282 complete-case fixed-effects rows, and interprets the poverty/social-exclusion coefficient as an estimand-sensitive stress test rather than a durable substantive finding.

The proposed upgrade changes the thesis identity from a single-outcome applied audit to a methodological-applied public-data study:

**Target-Population Drift in Eurostat Unmet-Care Panels: A Reproducible Sensitivity Audit**

## New Thesis Identity

Public Eurostat unmet-care indicators are valuable for monitoring European health-access barriers, but aggregate conclusions can silently change when analysts change denominator, country universe, population weighting, covariate completeness, or missing-data assumptions.

The upgraded thesis formalizes a reproducible target-population drift audit protocol, applies it across multiple Eurostat unmet-care indicators, and uses semi-synthetic missingness simulations to show when complete-case fixed-effects estimates remain stable, become selected-panel artifacts, or are not identifiable from the available public data.

The thesis remains:

- aggregate, using country-year units;
- public-data-based, using Eurostat sources only;
- associational and non-causal;
- focused on target-population drift, not individual-level mechanisms;
- centered on poverty/social exclusion as the main stress-test covariate.

## Research Questions

1. **Indicator dependence:** How do unmet-care monitoring conclusions change across medical versus dental care, population-denominator versus need-denominator indicators, and barrier-specific definitions such as cost, distance, and waiting lists?
2. **Target-population drift:** How much do country coverage, year coverage, country-universe restriction, population weighting, and covariate completeness change the analytical target population of public Eurostat aggregate analyses?
3. **Coefficient stability:** Are social-vulnerability coefficients stable across complete-case, population-weighted, balanced-outcome, IPW, MAR-imputed, and MNAR-shifted estimands?
4. **Simulation validity:** Under semi-synthetic Eurostat-style missingness, when does complete-case fixed-effects estimation recover the reference estimand, and when does it produce bias, sign instability, interval undercoverage, or wrong substantive conclusions?
5. **Reporting protocol:** Can a reproducible target-population drift audit classify public aggregate-panel findings as stable, target-dependent, denominator-dependent, missingness-dependent, imputation-model-dependent, or non-identifiable?

## Proposed Chapter Structure

1. **Introduction:** target-population drift problem, five RQs, contributions.
2. **Literature and Methodological Background:** access theory, EU-SILC measurement, ecological limits, estimands, missing data, panel inference.
3. **Public Data and Estimand Registry:** multi-outcome Eurostat indicator registry with feasibility labels.
4. **Multi-Outcome Monitoring Benchmark:** monitoring differences before regression.
5. **Target-Population Drift Diagnostics:** multi-outcome attrition, retention, and included/excluded imbalance.
6. **Estimand Stability Across Outcomes:** outcome-by-estimand poverty coefficient matrix and deterministic classification.
7. **Semi-Synthetic Missingness Simulation:** reference-estimand simulation under controlled missingness mechanisms.
8. **Reporting Protocol and Conclusion:** checklist, failure modes, final classification, limits.

## Expected New Outputs

- Public-data estimand registry for medical/dental, population/need-denominator, and barrier-specific Eurostat unmet-care indicators.
- Multi-outcome monitoring trend and coverage benchmark.
- Multi-outcome target-population attrition matrix.
- Outcome-by-estimand coefficient stability matrix.
- Deterministic failure classification: stable, target-dependent, denominator-dependent, missingness-dependent, imputation-model-dependent, or non-identifiable.
- Semi-synthetic missingness simulation with bias, sign reversal, coverage, retention, target-distance, and wrong-conclusion diagnostics.
- Reusable code module and reproducibility package.

## Approval Question

Do you approve changing the thesis from a single-outcome target-population sensitivity audit to a multi-outcome public-data target-population drift audit with semi-synthetic missingness simulation, while keeping the thesis aggregate, Eurostat-based, associational, and non-causal?

## Current Approval Status

Pending supervisor confirmation or no-objection response.
