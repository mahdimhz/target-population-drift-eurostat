# Source Register Summary

Date accessed: 2026-05-14

This Phase 2 note registers official and academic sources only. It does not recommend a thesis design and does not verify panel feasibility.

## Official primary sources

| Source ID | Safe factual use | Evidence source |
|---|---|---|
| S01 | Overview of unmet health care needs article, EU-SILC context, and cited online data codes for article figures. | https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Unmet_health_care_needs_statistics |
| S02 | EU-SILC health-variable definitions, unit of measure, target population, reference period, dissemination notes, and microdata access limits. | https://ec.europa.eu/eurostat/cache/metadata/en/hlth_silc_01_esms.htm |
| S03-S10 | Eurostat Data Browser pages and official SDMX dataflow endpoints for the candidate unmet medical-needs datasets. | https://ec.europa.eu/eurostat/databrowser/view/hlth_silc_08/default/table?lang=en ; https://ec.europa.eu/eurostat/api/dissemination/sdmx/3.0/structure/dataflow/ESTAT/hlth_silc_08/1.0?compress=false ; https://ec.europa.eu/eurostat/databrowser/view/hlth_silc_08b/default/table?lang=en ; https://ec.europa.eu/eurostat/api/dissemination/sdmx/3.0/structure/dataflow/ESTAT/hlth_silc_08b/1.0?compress=false ; https://ec.europa.eu/eurostat/databrowser/view/hlth_silc_08_r/default/table?lang=en ; https://ec.europa.eu/eurostat/api/dissemination/sdmx/3.0/structure/dataflow/ESTAT/hlth_silc_08_r/1.0?compress=false ; https://ec.europa.eu/eurostat/databrowser/view/hlth_silc_08b_r/default/table?lang=en ; https://ec.europa.eu/eurostat/api/dissemination/sdmx/3.0/structure/dataflow/ESTAT/hlth_silc_08b_r/1.0?compress=false |
| S11-S12 | Eurostat API retrieval and metadata/data access documentation. | https://ec.europa.eu/eurostat/web/user-guides/data-browser/api-data-access/api-getting-started ; https://ec.europa.eu/eurostat/web/user-guides/data-browser/api-data-access/api-detailed-guidelines |
| S13 | Official warning source for keeping EHIS and EU-SILC unmet-needs indicators separate. | https://ec.europa.eu/eurostat/cache/metadata/en/hlth_det_esms.htm |
| S14 | Official evidence that EU-SILC unmet-needs guideline changes were planned from 2015. | https://health.ec.europa.eu/system/files/2018-04/ev_20140520_co04_en_0.pdf |

## Academic secondary sources

| Source ID | Safe factual use | Evidence source |
|---|---|---|
| S15 | Secondary explanation of the 2015 EU-SILC unmet-needs questionnaire change and the later publication of new Eurostat datasets using the new denominator approach. | https://academic.oup.com/eurpub/article/35/3/447/7730124 |

## Safe citation map

| Topic | Sources safe to cite | Status |
|---|---|---|
| Indicator definition | S02 first; S01 for article-level context. | VERIFIED from official Eurostat metadata and Statistics Explained: https://ec.europa.eu/eurostat/cache/metadata/en/hlth_silc_01_esms.htm ; https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Unmet_health_care_needs_statistics |
| Dataset structure | S04, S06, S08, S10 for official dataflow existence and exact titles; S03, S05, S07, S09 for Data Browser pages. | PARTLY VERIFIED: dataset code existence and titles verified; dimensions, filters, years, and missingness are not yet audited. Sources: https://ec.europa.eu/eurostat/api/dissemination/sdmx/3.0/structure/dataflow/ESTAT/hlth_silc_08/1.0?compress=false ; https://ec.europa.eu/eurostat/api/dissemination/sdmx/3.0/structure/dataflow/ESTAT/hlth_silc_08b/1.0?compress=false ; https://ec.europa.eu/eurostat/api/dissemination/sdmx/3.0/structure/dataflow/ESTAT/hlth_silc_08_r/1.0?compress=false ; https://ec.europa.eu/eurostat/api/dissemination/sdmx/3.0/structure/dataflow/ESTAT/hlth_silc_08b_r/1.0?compress=false |
| Methodology break | S14 as official but limited evidence; S15 as peer-reviewed secondary interpretation. | VERIFIED that an official 2014 Eurostat presentation mentions unmet-needs guideline changes from 2015; detailed implications require secondary evidence unless a fuller official source is found. Sources: https://health.ec.europa.eu/system/files/2018-04/ev_20140520_co04_en_0.pdf ; https://academic.oup.com/eurpub/article/35/3/447/7730124 |
| API retrieval | S11 for API overview and base URI; S12 for detailed API documentation index. | VERIFIED from official Eurostat user-guide pages: https://ec.europa.eu/eurostat/web/user-guides/data-browser/api-data-access/api-getting-started ; https://ec.europa.eu/eurostat/web/user-guides/data-browser/api-data-access/api-detailed-guidelines |
| Regional availability | S08 and S10 verify regional dataflow existence for NUTS 2 titled datasets. | PARTLY VERIFIED: source existence and titles verified; geographic coverage, NUTS level completeness, and year-by-year feasibility are not yet verified. Sources: https://ec.europa.eu/eurostat/api/dissemination/sdmx/3.0/structure/dataflow/ESTAT/hlth_silc_08_r/1.0?compress=false ; https://ec.europa.eu/eurostat/api/dissemination/sdmx/3.0/structure/dataflow/ESTAT/hlth_silc_08b_r/1.0?compress=false |

## Verified information

- Eurostat has an official Statistics Explained page titled "Unmet health care needs statistics"; the page states that the data come from EU-SILC and cites online data code `hlth_silc_08` for medical-care figures. Source: https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Unmet_health_care_needs_statistics
- Eurostat has official reference metadata titled "Health variables of EU-SILC"; it defines self-reported unmet needs, medical care, dental care, reasons of barriers of access, unit of measure, target population, and microdata access conditions. Source: https://ec.europa.eu/eurostat/cache/metadata/en/hlth_silc_01_esms.htm
- Official Eurostat SDMX dataflow endpoints returned HTTP 200 for `hlth_silc_08`, `hlth_silc_08b`, `hlth_silc_08_r`, and `hlth_silc_08b_r`; exact titles are recorded in `references/source_register.csv`. Sources: https://ec.europa.eu/eurostat/api/dissemination/sdmx/3.0/structure/dataflow/ESTAT/hlth_silc_08/1.0?compress=false ; https://ec.europa.eu/eurostat/api/dissemination/sdmx/3.0/structure/dataflow/ESTAT/hlth_silc_08b/1.0?compress=false ; https://ec.europa.eu/eurostat/api/dissemination/sdmx/3.0/structure/dataflow/ESTAT/hlth_silc_08_r/1.0?compress=false ; https://ec.europa.eu/eurostat/api/dissemination/sdmx/3.0/structure/dataflow/ESTAT/hlth_silc_08b_r/1.0?compress=false
- Eurostat API documentation states that SDMX 3.0 supports public dataset lists, complete structure definitions, and full or subset data downloads. Source: https://ec.europa.eu/eurostat/web/user-guides/data-browser/api-data-access/api-getting-started
- Eurostat EHIS metadata explicitly warns that EHIS and EU-SILC unmet-needs indicators differ in question structure, denominator, age population, sequence, concept, and context. Source: https://ec.europa.eu/eurostat/cache/metadata/en/hlth_det_esms.htm

## Unverified information for later phases

- Year-by-year availability is not verified in Phase 2.
- Geographic completeness is not verified in Phase 2.
- Whether a balanced or usable unbalanced regional panel exists is not verified in Phase 2.
- Exact dimension filters and code lists are not verified in Phase 2.
- Denominator behavior for each candidate dataset must still be verified dataset by dataset in Phase 3.
- ISTAT relevance is not verified in Phase 2.
