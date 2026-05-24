from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import requests

from eurostat_api import (
    build_country_year_table,
    dataset_to_tidy,
    download_json,
    eurostat_url,
    is_national_geo,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
YEARS = range(2008, 2026)
DATAFLOW_URL = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/3.0/structure/dataflow/ESTAT/{code}/1.0?compress=false"


@dataclass(frozen=True)
class CandidateControl:
    variable_name: str
    dataset_code: str
    params: dict[str, str | list[str]]
    value_column: str
    short_title: str
    filter_description: str


CANDIDATES = [
    CandidateControl(
        variable_name="gdp_per_capita_eur",
        dataset_code="nama_10_pc",
        params={"unit": "CP_EUR_HAB", "na_item": "B1GQ"},
        value_column="gdp_per_capita_eur",
        short_title="GDP per capita",
        filter_description="unit=CP_EUR_HAB, na_item=B1GQ",
    ),
    CandidateControl(
        variable_name="unemployment_rate_pc",
        dataset_code="une_rt_a",
        params={"unit": "PC_ACT", "sex": "T", "age": "Y15-74"},
        value_column="unemployment_rate_pc",
        short_title="Unemployment rate",
        filter_description="unit=PC_ACT, sex=T, age=Y15-74",
    ),
    CandidateControl(
        variable_name="poverty_or_social_exclusion_pc",
        dataset_code="ilc_peps01n",
        params={"unit": "PC", "sex": "T", "age": "TOTAL"},
        value_column="poverty_or_social_exclusion_pc",
        short_title="People at risk of poverty or social exclusion",
        filter_description="unit=PC, sex=T, age=TOTAL",
    ),
    CandidateControl(
        variable_name="government_health_expenditure_gdp_pc",
        dataset_code="gov_10a_exp",
        params={"unit": "PC_GDP", "sector": "S13", "cofog99": "GF07", "na_item": "TE"},
        value_column="government_health_expenditure_gdp_pc",
        short_title="General government health expenditure",
        filter_description="unit=PC_GDP, sector=S13, cofog99=GF07, na_item=TE",
    ),
    CandidateControl(
        variable_name="compulsory_health_financing_gdp_pc",
        dataset_code="hlth_sha11_hf",
        params={"unit": "PC_GDP", "icha11_hf": "HF1"},
        value_column="compulsory_health_financing_gdp_pc",
        short_title="Compulsory health financing",
        filter_description="unit=PC_GDP, icha11_hf=HF1",
    ),
]


def category_label(data: dict, dim_id: str, code: str) -> str:
    labels = data.get("dimension", {}).get(dim_id, {}).get("category", {}).get("label", {})
    return labels.get(code, code)


def dataflow_available(dataset_code: str) -> str:
    response = requests.get(DATAFLOW_URL.format(code=dataset_code), timeout=45)
    return "yes" if response.ok else f"no: HTTP {response.status_code}"


def candidate_params(candidate: CandidateControl) -> dict[str, str | list[str]]:
    params = dict(candidate.params)
    params["time"] = [str(year) for year in YEARS]
    return params


def tidy_control(candidate: CandidateControl, data: dict) -> pd.DataFrame:
    tidy = build_country_year_table(data, candidate.value_column, YEARS)
    if tidy.empty:
        return pd.DataFrame(columns=["geo", "year", candidate.value_column])
    return tidy[["geo", "year", candidate.value_column]]


def main() -> None:
    raw_dir = PROJECT_ROOT / "data" / "raw"
    processed_dir = PROJECT_ROOT / "data" / "processed"
    outputs_dir = PROJECT_ROOT / "outputs"

    outcome = pd.read_csv(processed_dir / "country_year_outcome.csv")
    outcome_pairs = set(zip(outcome["geo"], outcome["year"]))

    feasibility_rows: list[dict[str, str | int]] = []
    control_frames: list[pd.DataFrame] = []
    metadata_rows: list[dict[str, str]] = []

    for candidate in CANDIDATES:
        params = candidate_params(candidate)
        raw_path = raw_dir / f"control_{candidate.dataset_code}_{candidate.variable_name}.json"
        data = download_json(candidate.dataset_code, params, raw_path)
        tidy = tidy_control(candidate, data)
        control_frames.append(tidy)

        national_codes = sorted(code for code in tidy["geo"].dropna().unique() if is_national_geo(str(code)))
        years_available = sorted(int(year) for year in tidy["year"].dropna().unique())
        control_pairs = set(zip(tidy["geo"], tidy["year"]))
        overlap_pairs = control_pairs.intersection(outcome_pairs)
        missing_after_merge = len(outcome_pairs) - len(overlap_pairs)

        unit_code = str(candidate.params.get("unit", ""))
        unit_label = category_label(data, "unit", unit_code)
        official_title = data.get("label", candidate.short_title)
        years_text = f"{min(years_available)}-{max(years_available)}" if years_available else "none"
        overlap = "yes" if overlap_pairs else "no"
        geography = "national country codes" if national_codes else "not verified"
        notes = (
            f"{len(overlap_pairs)} outcome country-year cells match this exact filter; "
            f"{missing_after_merge} outcome cells would have a missing value after a left merge."
        )

        feasibility_rows.append(
            {
                "dataset_code": candidate.dataset_code,
                "short_title": candidate.short_title,
                "official_title": official_title,
                "variable_name": candidate.variable_name,
                "filter": candidate.filter_description,
                "unit": unit_label,
                "geography_level": geography,
                "years_available": years_text,
                "countries_available": len(national_codes),
                "overlaps_with_outcome": overlap,
                "non_missing_country_years": len(tidy),
                "overlap_country_years": len(overlap_pairs),
                "missingness_notes": notes,
                "dataflow_endpoint_available": dataflow_available(candidate.dataset_code),
                "merge_approved": "yes" if overlap == "yes" and national_codes else "no",
            }
        )
        metadata_rows.append(
            {
                "dataset_code": candidate.dataset_code,
                "variable_name": candidate.variable_name,
                "api_url": eurostat_url(candidate.dataset_code, params),
                "raw_file": str(raw_path.relative_to(PROJECT_ROOT)),
            }
        )

    feasibility = pd.DataFrame(feasibility_rows)
    feasibility.to_csv(outputs_dir / "control_feasibility.csv", index=False)
    (outputs_dir / "control_feasibility.md").write_text(
        "# Control feasibility audit\n\n"
        "Date accessed: 2026-05-14\n\n"
        "This table records candidate Eurostat controls that were checked with exact national filters. "
        "The audit checks dataset code, unit, geography, year overlap, and missingness against the primary outcome file. "
        "It does not select a regression model.\n\n"
        + feasibility.to_markdown(index=False)
        + "\n",
        encoding="utf-8",
    )
    (outputs_dir / "control_api_requests.json").write_text(
        json.dumps(metadata_rows, indent=2),
        encoding="utf-8",
    )

    controls = None
    for frame in control_frames:
        controls = frame if controls is None else controls.merge(frame, on=["geo", "year"], how="outer")
    if controls is None:
        controls = pd.DataFrame(columns=["geo", "year"])
    controls = controls.sort_values(["geo", "year"]).reset_index(drop=True)
    controls.to_csv(processed_dir / "verified_control_candidates.csv", index=False)

    print(f"saved {outputs_dir / 'control_feasibility.csv'}")
    print(f"saved {outputs_dir / 'control_feasibility.md'}")
    print(f"saved {processed_dir / 'verified_control_candidates.csv'}")


if __name__ == "__main__":
    main()
