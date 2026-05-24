# Dataset Audit Summary

Date accessed: 2026-05-14

This Phase 3 summary verifies candidate Eurostat datasets and indicators for unmet healthcare needs. It does not select a final research design and does not make modeling recommendations beyond data feasibility.

Detailed workbook: `outputs/dataset_audit.xlsx`

## Ranked Candidate Outcome Datasets

This ranking is a data-feasibility ranking only.

| Rank | Dataset | Feasibility status | Evidence |
|---:|---|---|---|
| 1 | `hlth_silc_08` — Self-reported unmet needs for medical examination by sex, age, main reason declared and income quintile | Recommended as the safest national aggregate outcome candidate. The standard API filter `unit=PC&quantile=TOTAL&reason=TOOEFW&age=Y_GE16&sex=T` returned time categories 2008-2025 and 46 geo categories; the 2024 EU27 value matches the Eurostat Statistics Explained article’s 2.5% for unmet medical needs due to expense, distance, or waiting lists. | https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/hlth_silc_08?lang=en&unit=PC&quantile=TOTAL&reason=TOOEFW&age=Y_GE16&sex=T ; https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Unmet_health_care_needs_statistics |
| 2 | `hlth_silc_08b` — Self-reported unmet needs for medical examination due to financial reasons, long waiting list or distance by sex, age and risk of poverty threshold — % of the persons having the same needs | Recommended only if the thesis explicitly wants the denominator to be persons having medical needs. The standard API filter returned time categories 2021-2025, not the longer 2008-2025 span seen for `hlth_silc_08`. | https://ec.europa.eu/eurostat/api/dissemination/sdmx/3.0/structure/dataflow/ESTAT/hlth_silc_08b/1.0?compress=false ; https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/hlth_silc_08b?lang=en&unit=PC&rskpovth=TOTAL&reason=TXP_TFAR_WLIST&age=Y_GE16&sex=T |
| 3 | `hlth_silc_08b_r` — Self-reported unmet needs for medical examination due to financial reasons, long waiting list or distance by NUTS-2-region — % of the persons having the same needs | Possible but risky for regional analysis. The title verifies the persons-with-need denominator and regional table existence, but the standard API filter returned only 2021-2025 and mixed country-like and regional-looking geo codes. | https://ec.europa.eu/eurostat/api/dissemination/sdmx/3.0/structure/dataflow/ESTAT/hlth_silc_08b_r/1.0?compress=false ; https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/hlth_silc_08b_r?lang=en&unit=PC&reason=TXP_TFAR_WLIST |
| 4 | `hlth_silc_08_r` — Self-reported unmet needs for medical examination by main reason declared and NUTS 2 region | Possible but risky for regional analysis. The regional table exists and the standard API filter returned 2008-2025, but the response includes mixed country-like, NUTS1-like, and NUTS2-like geo codes; a clean NUTS2 panel is not verified. | https://ec.europa.eu/eurostat/api/dissemination/sdmx/3.0/structure/dataflow/ESTAT/hlth_silc_08_r/1.0?compress=false ; https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/hlth_silc_08_r?lang=en&unit=PC&reason=TOOEFW |

## National-Only Options

| Dataset | Verified role | Key constraints | Evidence |
|---|---|---|---|
| `hlth_silc_08` | Primary national aggregate candidate. | Denominator is the broad all-population indicator described by Eurostat: self-reported unmet needs as a percentage of all people aged 16+ including people not reporting medical needs. | https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Unmet_health_care_needs_statistics ; https://ec.europa.eu/eurostat/cache/metadata/en/hlth_silc_01_esms.htm |
| `hlth_silc_08b` | National need-denominator candidate or robustness comparison. | Shorter verified time categories in standard filter: 2021-2025; reason is only the composite financial reasons, long waiting list, or distance. | https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/hlth_silc_08b?lang=en&unit=PC&rskpovth=TOTAL&reason=TXP_TFAR_WLIST&age=Y_GE16&sex=T |
| `hlth_silc_14` | Possible national subgroup analysis by education. | Not a primary outcome table; useful only if education breakdown is needed and denominator/unit are documented for the chosen filter. | https://ec.europa.eu/eurostat/api/dissemination/sdmx/3.0/structure/dataflow/ESTAT/hlth_silc_14/1.0?compress=false |
| `hlth_silc_22` and `hlth_silc_09b` | Dental-care comparison or robustness context. | Dental care is a separate service type from medical care and should not be merged with medical-care outcomes. | https://ec.europa.eu/eurostat/cache/metadata/en/hlth_silc_01_esms.htm ; https://ec.europa.eu/eurostat/api/dissemination/sdmx/3.0/structure/dataflow/ESTAT/hlth_silc_22/1.0?compress=false ; https://ec.europa.eu/eurostat/api/dissemination/sdmx/3.0/structure/dataflow/ESTAT/hlth_silc_09b/1.0?compress=false |

## NUTS2 Options

| Dataset | Verified status | Risk label | Evidence |
|---|---|---|---|
| `hlth_silc_08_r` | Regional-titled Eurostat dataflow exists; dimensions verified as `freq`, `reason`, `unit`, `geo`, and `time`. | Possible but risky. The standard filter returned 242 geo categories and 2,819 values, but the geo list mixes country-like, NUTS1-like, and NUTS2-like codes. | https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/hlth_silc_08_r?lang=en&unit=PC&reason=TOOEFW |
| `hlth_silc_08b_r` | Regional-titled Eurostat dataflow exists; dimensions verified as `freq`, `reason`, `unit`, `geo`, and `time`. | Possible but risky. The standard filter returned 249 geo categories and 1,100 values for 2021-2025, but clean NUTS2-only completeness is not verified. | https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/hlth_silc_08b_r?lang=en&unit=PC&reason=TXP_TFAR_WLIST |

Not verified: balanced regional panel feasibility, NUTS vintage stability, country-by-country NUTS2 completeness, and whether national/NUTS1 substitutes should be excluded or retained.

## Do Not Confuse These Datasets

| Item | Verified distinction | Evidence |
|---|---|---|
| `hlth_silc_08` vs `hlth_silc_08b` | `hlth_silc_08` supports the broad all-population indicator used in the Statistics Explained article; `hlth_silc_08b` is explicitly a percentage of persons having the same needs. | https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Unmet_health_care_needs_statistics ; https://ec.europa.eu/eurostat/api/dissemination/sdmx/3.0/structure/dataflow/ESTAT/hlth_silc_08b/1.0?compress=false |
| EU-SILC vs EHIS | Eurostat metadata says EHIS and EU-SILC differ in reason questions, denominator, age population, question sequence, concept, and context. They should not be pooled or treated as the same outcome. | https://ec.europa.eu/eurostat/cache/metadata/en/hlth_det_esms.htm |
| Medical vs dental care | Eurostat EU-SILC metadata defines medical care and dental care separately. Dental tables are context or robustness options, not substitutes for the medical-care outcome. | https://ec.europa.eu/eurostat/cache/metadata/en/hlth_silc_01_esms.htm |
| Aggregate open data vs microdata | The audited Eurostat tables are aggregate published outputs. Eurostat metadata says direct EU-SILC microdata access is only through research contracts and individuals cannot be granted direct access. | https://ec.europa.eu/eurostat/cache/metadata/en/hlth_silc_01_esms.htm |

## Verified Constraints

- `hlth_silc_08`, `hlth_silc_08b`, `hlth_silc_08_r`, and `hlth_silc_08b_r` are verified Eurostat dataflows by direct SDMX HTTP 200 responses and parsed English titles. Evidence: https://ec.europa.eu/eurostat/api/dissemination/sdmx/3.0/structure/dataflow/ESTAT/hlth_silc_08/1.0?compress=false ; https://ec.europa.eu/eurostat/api/dissemination/sdmx/3.0/structure/dataflow/ESTAT/hlth_silc_08b/1.0?compress=false ; https://ec.europa.eu/eurostat/api/dissemination/sdmx/3.0/structure/dataflow/ESTAT/hlth_silc_08_r/1.0?compress=false ; https://ec.europa.eu/eurostat/api/dissemination/sdmx/3.0/structure/dataflow/ESTAT/hlth_silc_08b_r/1.0?compress=false
- `hlth_silc_08` standard filter used in this audit returned time categories 2008-2025. Evidence: https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/hlth_silc_08?lang=en&unit=PC&quantile=TOTAL&reason=TOOEFW&age=Y_GE16&sex=T
- `hlth_silc_08b` standard filter used in this audit returned time categories 2021-2025. Evidence: https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/hlth_silc_08b?lang=en&unit=PC&rskpovth=TOTAL&reason=TXP_TFAR_WLIST&age=Y_GE16&sex=T
- `hlth_silc_08_r` standard filter used in this audit returned time categories 2008-2025 and mixed geography-code patterns. Evidence: https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/hlth_silc_08_r?lang=en&unit=PC&reason=TOOEFW
- `hlth_silc_08b_r` standard filter used in this audit returned time categories 2021-2025 and mixed geography-code patterns. Evidence: https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/hlth_silc_08b_r?lang=en&unit=PC&reason=TXP_TFAR_WLIST
- EU-SILC unmet-needs variables refer to the past 12 months, and the statistical unit is individuals aged 16+ living in private households. Evidence: https://ec.europa.eu/eurostat/cache/metadata/en/hlth_silc_01_esms.htm
- Methodology change must be acknowledged: an official Eurostat/European Commission presentation records changes of guidelines on unmet-needs variables from 2015, and a peer-reviewed article explains the split between having a need and the probability that it was unmet. Evidence: https://health.ec.europa.eu/system/files/2018-04/ev_20140520_co04_en_0.pdf ; https://academic.oup.com/eurpub/article/35/3/447/7730124

## Still Not Verified

- A balanced NUTS2 regional panel.
- A final geography filter for pure NUTS2 regions.
- Whether regional values are available for every country and every year.
- Whether regional denominator documentation is sufficient for `hlth_silc_08_r`.
- Whether ISTAT adds value.
- Any regression, causal, or predictive design.
