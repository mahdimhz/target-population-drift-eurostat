# Thesis Design Feasibility

Date accessed: 2026-05-14

This Phase 4 file evaluates feasible thesis designs using only evidence registered in Phases 2-3 plus official ISTAT source checks for the optional Italy extension. It does not select a regression model.

Workbook: `outputs/thesis_design_feasibility.xlsx`

## Best Design

**Recommended: Design A — National-level panel on unmet healthcare needs using Eurostat aggregates.**

Reason: `hlth_silc_08` has the clearest verified national aggregate structure and the longest verified standard-filter time categories in this audit: 2008-2025. The Phase 3 API check used `unit=PC&quantile=TOTAL&reason=TOOEFW&age=Y_GE16&sex=T` and returned 46 geo categories and 18 time categories. Eurostat Statistics Explained confirms the EU-SILC context and distinguishes the broad all-population unmet-need indicator from the persons-with-need denominator. Evidence: https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/hlth_silc_08?lang=en&unit=PC&quantile=TOTAL&reason=TOOEFW&age=Y_GE16&sex=T ; https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Unmet_health_care_needs_statistics

Limit: this is the safest data design, but it is not a regional design. If the professor requires regional inequality, use Design C as the conservative regional route.

## Best Conservative Design

**Recommended if the thesis must remain regional: Design C — Cross-sectional regional analysis for the latest verified year only.**

Reason: regional Eurostat tables exist (`hlth_silc_08_r`, `hlth_silc_08b_r`), but Phase 3 found mixed country-like and regional-looking geo codes in the API responses. A latest-year cross-section avoids unverified balanced-panel claims while preserving a regional inequality framing. Evidence: https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/hlth_silc_08_r?lang=en&unit=PC&reason=TOOEFW ; https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/hlth_silc_08b_r?lang=en&unit=PC&reason=TXP_TFAR_WLIST

Required boundary: before any analysis, filter valid NUTS2 regions, report excluded country-level or NUTS1-level records, and show missingness for the selected year.

## Best Ambitious Design

**Possible but risky: Design B — NUTS2 regional panel on reason-specific unmet need using Eurostat aggregates.**

Reason: it best matches a regional inequality thesis and has potentially strong sample size. The standard Phase 3 checks returned 2,819 values for `hlth_silc_08_r` and 1,100 values for `hlth_silc_08b_r`. However, a usable NUTS2 panel is not verified because the API response mixes geographic levels and the `08b_r` table has only 2021-2025 under the standard filter. Evidence: https://ec.europa.eu/eurostat/api/dissemination/sdmx/3.0/structure/dataflow/ESTAT/hlth_silc_08_r/1.0?compress=false ; https://ec.europa.eu/eurostat/api/dissemination/sdmx/3.0/structure/dataflow/ESTAT/hlth_silc_08b_r/1.0?compress=false

Decision rule: do not commit to Design B unless a year-by-year NUTS2 completeness audit proves that the panel is usable.

## Designs To Avoid

| Design | Recommendation | Evidence-based reason |
|---|---|---|
| Design D — Eurostat panel + Italy-focused ISTAT extension | Possible but risky; not recommended as core scope yet. | ISTAT has official evidence on health-service access and surveys, including 2024 statements about people renouncing specialist visits or tests, but a Eurostat-compatible ISTAT dataset, definition, geography, and time structure were not verified in this audit. Evidence: https://www.istat.it/infografiche/infografiche-rapporto-annuale-2025/ ; https://www.istat.it/informazioni-sulla-rilevazione/condizioni-di-salute-e-ricorso-ai-servizi-sanitari-anni-2004-e-2005/ |
| Design E — Microdata-based design | Not recommended as default. | Eurostat metadata states that direct EU-SILC microdata access is by research contracts and individuals cannot be granted direct access. ISTAT microdata exist, but a compatible microdata route is not verified. Evidence: https://ec.europa.eu/eurostat/cache/metadata/en/hlth_silc_01_esms.htm ; https://www.istat.it/dati/microdati/ |
| Design B as an assumed balanced NUTS2 panel | Not recommended without additional audit. | Regional dataflow existence is verified, but balanced NUTS2 panel feasibility is not verified. Evidence: https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/hlth_silc_08_r?lang=en&unit=PC&reason=TOOEFW |

## Why The Conclusions Follow

| Conclusion | Verified evidence | Implication |
|---|---|---|
| `hlth_silc_08` is the safest core dataset. | Direct API standard filter returned 2008-2025 categories and national/aggregate data; Eurostat article cites the dataset for unmet medical needs. | Recommended for a reproducible national panel. |
| Regional analysis is possible but not yet panel-safe. | `hlth_silc_08_r` and `hlth_silc_08b_r` are verified dataflows, but Phase 3 API output includes mixed geographic code levels. | Regional cross-section is safer than regional panel until more auditing is done. |
| `hlth_silc_08b` and `hlth_silc_08b_r` change the denominator. | Dataset titles state “% of the persons having the same needs”; Statistics Explained distinguishes the second indicator from the all-population indicator. | Do not mix `08` and `08b` outcomes without explaining denominator differences. |
| EHIS should remain separate. | Eurostat EHIS metadata states differences in questions, denominator, age, sequence, concept, and context. | Do not use EHIS as a substitute for EU-SILC. Evidence: https://ec.europa.eu/eurostat/cache/metadata/en/hlth_det_esms.htm |
| Microdata is unsafe as default. | Eurostat metadata says direct access to anonymised EU-SILC microdata is restricted to research contracts and individuals cannot be granted direct access. | Avoid a microdata core unless access is already institutionally secured. |

## Recommendation Categories

| Category | Designs |
|---|---|
| Recommended | Design A; Design C only if regional framing is mandatory. |
| Possible but risky | Design B; Design D. |
| Not recommended | Design E; any design that assumes balanced NUTS2 panel feasibility before verification. |
