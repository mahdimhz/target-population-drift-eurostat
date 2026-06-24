from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd
import requests

from eurostat_api import dataset_to_tidy, eurostat_url, is_national_geo


ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
OUTPUTS = ROOT / "outputs"
TABLES = ROOT / "tables"

YEARS = range(2008, 2026)


@dataclass(frozen=True)
class IndicatorSpec:
    indicator_id: str
    dataset_code: str
    care_type: str
    barrier_type: str
    denominator: str
    reason_code: str
    reason_label_expected: str
    params: dict[str, str]
    valid_interpretation: str
    invalid_interpretation: str
    required: bool = True


INDICATOR_SPECS: tuple[IndicatorSpec, ...] = (
    IndicatorSpec(
        indicator_id="medical_population_combined",
        dataset_code="hlth_silc_08",
        care_type="medical",
        barrier_type="cost_distance_waiting",
        denominator="population",
        reason_code="TXP_TFAR_WLIST",
        reason_label_expected="Too expensive or too far or waiting list",
        params={"unit": "PC", "quantile": "TOTAL", "age": "Y_GE16", "sex": "T"},
        valid_interpretation="Share of the population aged 16+ reporting unmet medical examination need due to cost, distance, or waiting lists.",
        invalid_interpretation="Individual-level access effect or clinical need prevalence.",
    ),
    IndicatorSpec(
        indicator_id="medical_need_combined",
        dataset_code="hlth_silc_08b",
        care_type="medical",
        barrier_type="cost_distance_waiting",
        denominator="same_needs",
        reason_code="TXP_TFAR_WLIST",
        reason_label_expected="Too expensive or too far or waiting list",
        params={"unit": "PC", "rskpovth": "TOTAL", "age": "Y_GE16", "sex": "T"},
        valid_interpretation="Share among persons with the same medical needs reporting unmet need due to cost, distance, or waiting lists.",
        invalid_interpretation="Population prevalence of unmet medical need.",
    ),
    IndicatorSpec(
        indicator_id="dental_population_combined",
        dataset_code="hlth_silc_09",
        care_type="dental",
        barrier_type="cost_distance_waiting",
        denominator="population",
        reason_code="TXP_TFAR_WLIST",
        reason_label_expected="Too expensive or too far or waiting list",
        params={"unit": "PC", "quantile": "TOTAL", "age": "Y_GE16", "sex": "T"},
        valid_interpretation="Share of the population aged 16+ reporting unmet dental examination need due to cost, distance, or waiting lists.",
        invalid_interpretation="Medical-care access effect or individual-level dental treatment need.",
    ),
    IndicatorSpec(
        indicator_id="dental_need_combined",
        dataset_code="hlth_silc_09b",
        care_type="dental",
        barrier_type="cost_distance_waiting",
        denominator="same_needs",
        reason_code="TXP_TFAR_WLIST",
        reason_label_expected="Too expensive or too far or waiting list",
        params={"unit": "PC", "rskpovth": "TOTAL", "age": "Y_GE16", "sex": "T"},
        valid_interpretation="Share among persons with the same dental needs reporting unmet need due to cost, distance, or waiting lists.",
        invalid_interpretation="Population prevalence of unmet dental need.",
    ),
    IndicatorSpec(
        indicator_id="medical_population_cost",
        dataset_code="hlth_silc_08",
        care_type="medical",
        barrier_type="cost",
        denominator="population",
        reason_code="TXP",
        reason_label_expected="Too expensive",
        params={"unit": "PC", "quantile": "TOTAL", "age": "Y_GE16", "sex": "T"},
        valid_interpretation="Share of the population aged 16+ reporting unmet medical examination need because care was too expensive.",
        invalid_interpretation="All affordability barriers in the health system.",
    ),
    IndicatorSpec(
        indicator_id="medical_population_waiting",
        dataset_code="hlth_silc_08",
        care_type="medical",
        barrier_type="waiting",
        denominator="population",
        reason_code="WAITING",
        reason_label_expected="Waiting list",
        params={"unit": "PC", "quantile": "TOTAL", "age": "Y_GE16", "sex": "T"},
        valid_interpretation="Share of the population aged 16+ reporting unmet medical examination need because of waiting lists.",
        invalid_interpretation="Administrative waiting-time performance.",
    ),
    IndicatorSpec(
        indicator_id="medical_population_distance",
        dataset_code="hlth_silc_08",
        care_type="medical",
        barrier_type="distance",
        denominator="population",
        reason_code="TFAR",
        reason_label_expected="Too far",
        params={"unit": "PC", "quantile": "TOTAL", "age": "Y_GE16", "sex": "T"},
        valid_interpretation="Share of the population aged 16+ reporting unmet medical examination need because care was too far away.",
        invalid_interpretation="Objective travel-time accessibility.",
    ),
)


def _download_dataset(spec: IndicatorSpec) -> tuple[dict[str, Any] | None, str, str]:
    params: dict[str, str | list[str]] = {
        **spec.params,
        "reason": spec.reason_code,
        "time": [str(year) for year in YEARS],
    }
    url = eurostat_url(spec.dataset_code, params)
    raw_path = DATA_RAW / f"multi_outcome_{spec.indicator_id}.json"
    response = requests.get(url, timeout=90)
    if response.status_code != 200:
        return None, url, f"http_{response.status_code}"
    data = response.json()
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    raw_path.write_text(response.text, encoding="utf-8")
    return data, url, ""


def _reason_label(data: dict[str, Any], reason_code: str) -> str:
    return (
        data.get("dimension", {})
        .get("reason", {})
        .get("category", {})
        .get("label", {})
        .get(reason_code, "")
    )


def _build_indicator_rows(spec: IndicatorSpec, data: dict[str, Any]) -> pd.DataFrame:
    tidy = dataset_to_tidy(data)
    if tidy.empty:
        return pd.DataFrame()
    tidy["year"] = pd.to_numeric(tidy["time"], errors="coerce")
    tidy["value_pc"] = pd.to_numeric(tidy["value"], errors="coerce")
    tidy = tidy[tidy["geo"].map(is_national_geo)].copy()
    tidy = tidy[tidy["year"].isin(list(YEARS))].copy()
    tidy = tidy.dropna(subset=["value_pc"])
    if tidy.empty:
        return pd.DataFrame()
    out = tidy[["geo", "year", "value_pc", "status"]].copy()
    out["year"] = out["year"].astype(int)
    out.insert(0, "indicator_id", spec.indicator_id)
    out.insert(1, "dataset_code", spec.dataset_code)
    out.insert(2, "care_type", spec.care_type)
    out.insert(3, "barrier_type", spec.barrier_type)
    out.insert(4, "denominator", spec.denominator)
    out.insert(5, "reason_code", spec.reason_code)
    out.insert(6, "reason_label", _reason_label(data, spec.reason_code))
    return out.sort_values(["indicator_id", "geo", "year"]).reset_index(drop=True)


def _population_coverage(rows: pd.DataFrame) -> tuple[str, int, int]:
    population_path = DATA_PROCESSED / "feature_population_total.csv"
    if rows.empty or not population_path.exists():
        return "no", 0, len(rows)
    population = pd.read_csv(population_path, usecols=["geo", "year", "population_total"])
    merged = rows.merge(population, on=["geo", "year"], how="left")
    missing = int(merged["population_total"].isna().sum())
    available = int(merged["population_total"].notna().sum())
    status = "yes" if missing == 0 else "partial"
    return status, available, missing


def _registry_row(
    spec: IndicatorSpec,
    data: dict[str, Any] | None,
    rows: pd.DataFrame,
    api_url: str,
    download_error: str,
) -> dict[str, Any]:
    reason_label = _reason_label(data, spec.reason_code) if data is not None else ""
    reason_verified = bool(reason_label)
    population_weight_available, population_rows, population_missing = _population_coverage(rows)
    feasible = data is not None and reason_verified and not rows.empty
    infeasibility_reasons = []
    if data is None:
        infeasibility_reasons.append(download_error or "download_failed")
    if data is not None and not reason_verified:
        infeasibility_reasons.append("reason_code_not_returned_by_eurostat")
    if rows.empty:
        infeasibility_reasons.append("no_national_country_year_values")

    return {
        "indicator_id": spec.indicator_id,
        "dataset_code": spec.dataset_code,
        "care_type": spec.care_type,
        "barrier_type": spec.barrier_type,
        "denominator": spec.denominator,
        "unit": spec.params["unit"],
        "age": spec.params["age"],
        "sex": spec.params["sex"],
        "income_or_risk_filter": spec.params.get("quantile", spec.params.get("rskpovth", "")),
        "reason_code": spec.reason_code,
        "reason_label": reason_label,
        "reason_verified": reason_verified,
        "country_count": int(rows["geo"].nunique()) if not rows.empty else 0,
        "year_min": int(rows["year"].min()) if not rows.empty else "",
        "year_max": int(rows["year"].max()) if not rows.empty else "",
        "observed_rows": int(len(rows)),
        "population_weight_available": population_weight_available,
        "population_weight_rows": population_rows,
        "population_weight_missing_rows": population_missing,
        "valid_interpretation": spec.valid_interpretation,
        "invalid_interpretation": spec.invalid_interpretation,
        "feasibility_status": "feasible" if feasible else "infeasible",
        "infeasibility_reason": "; ".join(infeasibility_reasons),
        "required": spec.required,
        "extraction_date": date.today().isoformat(),
        "api_url": api_url,
    }


def _latex_escape(value: object) -> str:
    text = str(value)
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def write_registry_table(registry: pd.DataFrame, path: Path) -> None:
    indicator_labels = {
        "medical_population_combined": "Medical population",
        "medical_need_combined": "Medical need",
        "dental_population_combined": "Dental population",
        "dental_need_combined": "Dental need",
        "medical_population_cost": "Medical cost",
        "medical_population_waiting": "Medical waiting",
        "medical_population_distance": "Medical distance",
    }
    barrier_labels = {
        "cost_distance_waiting": "Cost, distance, waiting",
        "cost": "Cost",
        "waiting": "Waiting",
        "distance": "Distance",
    }
    denominator_labels = {
        "population": "Population",
        "same_needs": "Need",
    }
    columns = [
        "indicator_id",
        "dataset_code",
        "barrier_type",
        "denominator",
        "year_min",
        "year_max",
        "country_count",
        "observed_rows",
        "feasibility_status",
    ]
    display = registry[columns].copy()
    display["indicator_id"] = display["indicator_id"].map(indicator_labels).fillna(display["indicator_id"])
    display["barrier_type"] = display["barrier_type"].map(barrier_labels).fillna(display["barrier_type"])
    display["denominator"] = display["denominator"].map(denominator_labels).fillna(display["denominator"])
    display["years"] = display["year_min"].astype(str) + "--" + display["year_max"].astype(str)
    table_columns = [
        "indicator_id",
        "dataset_code",
        "barrier_type",
        "denominator",
        "years",
        "country_count",
        "observed_rows",
        "feasibility_status",
    ]
    header = [
        "Indicator",
        "Dataset",
        "Barrier",
        "Denom.",
        "Years",
        "Countries",
        "Rows",
        "Status",
    ]
    lines = [
        r"\begingroup",
        r"\scriptsize",
        r"\setlength{\tabcolsep}{3pt}",
        r"\begin{tabularx}{\linewidth}{@{}p{0.21\linewidth}p{0.13\linewidth}Yp{0.11\linewidth}p{0.12\linewidth}rrp{0.09\linewidth}@{}}",
        r"\toprule",
        " & ".join(header) + r" \\",
        r"\midrule",
    ]
    for _, row in display.iterrows():
        values = [_latex_escape(row[column]) for column in table_columns]
        lines.append(" & ".join(values) + r" \\")
    lines.extend([r"\bottomrule", r"\end{tabularx}", r"\endgroup", ""])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    TABLES.mkdir(parents=True, exist_ok=True)

    registry_rows: list[dict[str, Any]] = []
    indicator_frames: list[pd.DataFrame] = []
    validation_rows: list[dict[str, Any]] = []

    for spec in INDICATOR_SPECS:
        data, api_url, error = _download_dataset(spec)
        rows = _build_indicator_rows(spec, data) if data is not None else pd.DataFrame()
        registry_row = _registry_row(spec, data, rows, api_url, error)
        registry_rows.append(registry_row)
        validation_rows.append(
            {
                "indicator_id": spec.indicator_id,
                "dataset_code": spec.dataset_code,
                "reason_code": spec.reason_code,
                "reason_label_expected": spec.reason_label_expected,
                "reason_label_returned": registry_row["reason_label"],
                "reason_verified": registry_row["reason_verified"],
                "observed_rows": registry_row["observed_rows"],
                "feasibility_status": registry_row["feasibility_status"],
                "infeasibility_reason": registry_row["infeasibility_reason"],
            }
        )
        if not rows.empty:
            indicator_frames.append(rows)

    registry = pd.DataFrame(registry_rows)
    validation = pd.DataFrame(validation_rows)
    multi_outcome = pd.concat(indicator_frames, ignore_index=True) if indicator_frames else pd.DataFrame()

    registry.to_csv(OUTPUTS / "multi_outcome_indicator_registry.csv", index=False)
    validation.to_csv(OUTPUTS / "eurostat_reason_code_validation.csv", index=False)
    multi_outcome.to_csv(DATA_PROCESSED / "multi_outcome_unmet_care.csv", index=False)
    write_registry_table(registry, TABLES / "public_data_estimand_registry.tex")

    print(f"saved {OUTPUTS / 'multi_outcome_indicator_registry.csv'}")
    print(f"saved {OUTPUTS / 'eurostat_reason_code_validation.csv'}")
    print(f"saved {DATA_PROCESSED / 'multi_outcome_unmet_care.csv'}")
    print(f"saved {TABLES / 'public_data_estimand_registry.tex'}")
    print(f"feasible indicators: {(registry['feasibility_status'] == 'feasible').sum()} / {len(registry)}")


if __name__ == "__main__":
    main()
