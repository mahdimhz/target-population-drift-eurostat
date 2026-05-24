from __future__ import annotations

import json
from itertools import product
from pathlib import Path
from typing import Any

import pandas as pd
import requests


EUROSTAT_BASE_URL = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"


def eurostat_url(dataset_code: str, params: dict[str, str | list[str]]) -> str:
    query_parts: list[tuple[str, str]] = [("lang", "en")]
    for key, value in params.items():
        if isinstance(value, list):
            query_parts.extend((key, item) for item in value)
        else:
            query_parts.append((key, value))
    request = requests.Request(
        "GET",
        f"{EUROSTAT_BASE_URL}/{dataset_code}",
        params=query_parts,
    ).prepare()
    return request.url or ""


def download_json(dataset_code: str, params: dict[str, str | list[str]], raw_path: Path) -> dict[str, Any]:
    url = eurostat_url(dataset_code, params)
    response = requests.get(url, timeout=90)
    response.raise_for_status()
    data = response.json()

    raw_path.parent.mkdir(parents=True, exist_ok=True)
    raw_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return data


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _ordered_codes(category_index: dict[str, int] | list[str]) -> list[str]:
    if isinstance(category_index, list):
        return category_index
    return [code for code, _ in sorted(category_index.items(), key=lambda item: item[1])]


def dataset_to_tidy(data: dict[str, Any]) -> pd.DataFrame:
    dimension_ids = data["id"]
    sizes = data["size"]
    dimensions = data["dimension"]

    codes_by_dimension: list[list[str]] = []
    for dim_id in dimension_ids:
        category_index = dimensions[dim_id]["category"]["index"]
        codes_by_dimension.append(_ordered_codes(category_index))

    multipliers: list[int] = []
    for dim_pos in range(len(sizes)):
        multiplier = 1
        for later_size in sizes[dim_pos + 1 :]:
            multiplier *= later_size
        multipliers.append(multiplier)

    values = {int(key): value for key, value in data.get("value", {}).items()}
    statuses = {int(key): value for key, value in data.get("status", {}).items()}

    rows: list[dict[str, Any]] = []
    for index_tuple, code_tuple in zip(
        product(*[range(size) for size in sizes]),
        product(*codes_by_dimension),
    ):
        flat_index = sum(pos * multiplier for pos, multiplier in zip(index_tuple, multipliers))
        value = values.get(flat_index)
        if value is None:
            continue
        row = dict(zip(dimension_ids, code_tuple))
        row["value"] = value
        row["status"] = statuses.get(flat_index, "")
        rows.append(row)

    return pd.DataFrame(rows)


def is_national_geo(code: str) -> bool:
    if code.startswith(("EU", "EA")):
        return False
    if len(code) != 2:
        return False
    return code.isalpha()


def build_country_year_table(
    data: dict[str, Any],
    value_column: str,
    years: range,
) -> pd.DataFrame:
    tidy = dataset_to_tidy(data)
    if tidy.empty:
        return pd.DataFrame(columns=["geo", "year", value_column, "status"])

    tidy["year"] = pd.to_numeric(tidy["time"], errors="coerce").astype("Int64")
    tidy = tidy[tidy["year"].isin(list(years))].copy()
    tidy = tidy[tidy["geo"].map(is_national_geo)].copy()
    tidy[value_column] = pd.to_numeric(tidy["value"], errors="coerce")
    tidy = tidy.dropna(subset=[value_column])
    tidy = tidy[["geo", "year", value_column, "status"]].sort_values(["geo", "year"])
    return tidy.reset_index(drop=True)


def availability_matrix(df: pd.DataFrame, years: range, value_column: str) -> pd.DataFrame:
    countries = sorted(df["geo"].dropna().unique())
    base = pd.MultiIndex.from_product([countries, list(years)], names=["geo", "year"]).to_frame(index=False)
    observed = df[["geo", "year", value_column]].copy()
    observed["observed"] = observed[value_column].notna().astype(int)
    matrix = base.merge(observed[["geo", "year", "observed"]], on=["geo", "year"], how="left")
    matrix["observed"] = matrix["observed"].fillna(0).astype(int)
    return matrix
