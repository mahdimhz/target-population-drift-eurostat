# Raw Eurostat Download Instructions

Run the pipeline from the project root. The first command downloads or refreshes the raw Eurostat JSON files used by the thesis:

```powershell
python src/run_full_thesis_analysis.py
```

The extraction code calls the Eurostat dissemination API through `src/eurostat_api.py`. Dataset codes, filters, extraction notes, and source verification are documented in:

- `references/source_register.csv`
- `tables/eurostat_sources_appendix.tex`
- `outputs/population_extraction_notes.txt`
- `outputs/hlth_silc_08_api_url.txt`
- `outputs/hlth_silc_08b_api_url.txt`
- `outputs/hlth_silc_32_extraction_notes.txt`

The main raw inputs are stored in `data/raw/`; processed country-year files are written to `data/processed/`. No external substantive covariates outside the Eurostat scope are required.
