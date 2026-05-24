from __future__ import annotations

EU27 = {
    "AT",
    "BE",
    "BG",
    "CY",
    "CZ",
    "DE",
    "DK",
    "EE",
    "EL",
    "ES",
    "FI",
    "FR",
    "HR",
    "HU",
    "IE",
    "IT",
    "LT",
    "LU",
    "LV",
    "MT",
    "NL",
    "PL",
    "PT",
    "RO",
    "SE",
    "SI",
    "SK",
}

EEA_COUNTRIES = {"IS", "LI", "NO"}
SWITZERLAND = {"CH"}
UK_COUNTRIES = {"UK"}
CANDIDATE_POTENTIAL = {"AL", "BA", "ME", "MK", "RS", "TR", "XK"}

WEST_NORTH = {
    "AT",
    "BE",
    "CH",
    "DE",
    "DK",
    "FI",
    "FR",
    "IE",
    "IS",
    "LU",
    "NL",
    "NO",
    "SE",
    "UK",
}

EAST_SOUTH = {
    "AL",
    "BA",
    "BG",
    "CY",
    "CZ",
    "EE",
    "EL",
    "ES",
    "HR",
    "HU",
    "IT",
    "LT",
    "LV",
    "ME",
    "MK",
    "MT",
    "PL",
    "PT",
    "RO",
    "RS",
    "SI",
    "SK",
    "TR",
    "XK",
}


def country_universe_category(geo: str) -> str:
    if geo in EU27:
        return "EU-27"
    if geo in EEA_COUNTRIES:
        return "EEA country"
    if geo in SWITZERLAND:
        return "Switzerland"
    if geo in UK_COUNTRIES:
        return "UK"
    if geo in CANDIDATE_POTENTIAL:
        return "Candidate/potential candidate"
    return "Other Eurostat-available national unit"


def country_group(geo: str) -> str:
    if geo in WEST_NORTH:
        return "Western/Northern"
    if geo in EAST_SOUTH:
        return "Eastern/Southern"
    return "Other"
