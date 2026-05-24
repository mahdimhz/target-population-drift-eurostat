# Advisor Decision Brief

Student: Mahdi Mohammadzadeh  
Topic area: regional health inequality / unmet healthcare needs in Europe  
Audit stage: pre-Phase-1 data-feasibility scoping

## Evidence-Based Position

The safest thesis core is a Eurostat EU-SILC aggregate design using `hlth_silc_08`, focused on self-reported unmet needs for medical examination due to financial reasons, distance, or waiting lists. In the Phase 3 audit, the standard Eurostat API filter `unit=PC&quantile=TOTAL&reason=TOOEFW&age=Y_GE16&sex=T` returned time categories 2008-2025. Eurostat Statistics Explained and EU-SILC metadata verify the broad indicator context, population aged 16+ in private households, and EU-SILC source basis.

Evidence: https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/hlth_silc_08?lang=en&unit=PC&quantile=TOTAL&reason=TOOEFW&age=Y_GE16&sex=T ; https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Unmet_health_care_needs_statistics ; https://ec.europa.eu/eurostat/cache/metadata/en/hlth_silc_01_esms.htm

## Design Recommendation

Recommended core: **national-level European panel using Eurostat aggregates**.

Recommended regional alternative: **latest-year regional cross-section**, not a regional panel, unless a separate NUTS2 year-by-year completeness audit proves that a regional panel is usable.

Not recommended as default: EU-SILC microdata or ISTAT extension. Eurostat microdata access is restricted by research contracts, and the ISTAT extension has not yet been proven comparable with Eurostat definitions.

## Main Risk

The regional Eurostat tables `hlth_silc_08_r` and `hlth_silc_08b_r` exist, but the API responses include mixed country-like and regional-looking geography codes. Therefore, a NUTS2 panel should not be promised until missingness, NUTS level, and year coverage are audited.

Evidence: https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/hlth_silc_08_r?lang=en&unit=PC&reason=TOOEFW ; https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/hlth_silc_08b_r?lang=en&unit=PC&reason=TXP_TFAR_WLIST

## Decision Needed From Advisor

The key decision is whether the thesis must be explicitly regional. If yes, the conservative route is a latest-year NUTS2 cross-section after a strict geography audit. If no, the national Eurostat panel is the safest reproducible core.
