from __future__ import annotations

from pathlib import Path

from eurostat_api import availability_matrix, build_country_year_table, download_json, eurostat_url


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_CODE = "hlth_silc_08b"
YEARS = range(2021, 2026)
PARAMS = {
    "unit": "PC",
    "rskpovth": "TOTAL",
    "reason": "TXP_TFAR_WLIST",
    "age": "Y_GE16",
    "sex": "T",
    "time": [str(year) for year in YEARS],
}


def main() -> None:
    raw_path = PROJECT_ROOT / "data" / "raw" / "hlth_silc_08b_unmet_need_2021_2025.json"
    processed_path = PROJECT_ROOT / "data" / "processed" / "country_year_outcome_08b.csv"
    missingness_path = PROJECT_ROOT / "outputs" / "hlth_silc_08b_missingness_2021_2025.csv"
    matrix_path = PROJECT_ROOT / "outputs" / "hlth_silc_08b_availability_matrix_2021_2025.csv"
    url_path = PROJECT_ROOT / "outputs" / "hlth_silc_08b_api_url.txt"

    data = download_json(DATASET_CODE, PARAMS, raw_path)
    country_year = build_country_year_table(data, "unmet_need_08b_pc", YEARS)
    missingness = availability_matrix(country_year, YEARS, "unmet_need_08b_pc")
    country_summary = (
        missingness.groupby("geo", as_index=False)["observed"]
        .sum()
        .rename(columns={"observed": "non_missing_years"})
        .sort_values(["non_missing_years", "geo"], ascending=[True, True])
    )
    matrix = missingness.pivot(index="geo", columns="year", values="observed").sort_index()

    processed_path.parent.mkdir(parents=True, exist_ok=True)
    country_year.to_csv(processed_path, index=False)
    country_summary.to_csv(missingness_path, index=False)
    matrix.to_csv(matrix_path)
    url_path.write_text(eurostat_url(DATASET_CODE, PARAMS), encoding="utf-8")

    print(f"saved {raw_path}")
    print(f"saved {processed_path}")
    print(f"saved {missingness_path}")
    print(f"saved {matrix_path}")
    print(f"rows: {len(country_year)}")


if __name__ == "__main__":
    main()
