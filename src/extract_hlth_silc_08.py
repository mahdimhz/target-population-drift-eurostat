from __future__ import annotations

from pathlib import Path

from eurostat_api import build_country_year_table, download_json, eurostat_url


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_CODE = "hlth_silc_08"
YEARS = range(2008, 2026)
PARAMS = {
    "unit": "PC",
    "quantile": "TOTAL",
    "reason": "TOOEFW",
    "age": "Y_GE16",
    "sex": "T",
    "time": [str(year) for year in YEARS],
}


def main() -> None:
    raw_path = PROJECT_ROOT / "data" / "raw" / "hlth_silc_08_unmet_need_2008_2025.json"
    processed_path = PROJECT_ROOT / "data" / "processed" / "country_year_outcome.csv"
    url_path = PROJECT_ROOT / "outputs" / "hlth_silc_08_api_url.txt"

    data = download_json(DATASET_CODE, PARAMS, raw_path)
    country_year = build_country_year_table(data, "unmet_need_pc", YEARS)

    processed_path.parent.mkdir(parents=True, exist_ok=True)
    country_year.to_csv(processed_path, index=False)
    url_path.write_text(eurostat_url(DATASET_CODE, PARAMS), encoding="utf-8")

    print(f"saved {raw_path}")
    print(f"saved {processed_path}")
    print(f"rows: {len(country_year)}")


if __name__ == "__main__":
    main()
