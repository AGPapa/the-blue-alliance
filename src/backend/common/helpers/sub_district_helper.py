import json
import unicodedata
from pathlib import Path
from typing import Dict, Optional

from backend.common.models.keys import DistrictKey, TeamKey

SOUTH_CA_COUNTIES = frozenset(
    {
        "San Luis Obispo",
        "Kern",
        "San Bernardino",
        "Santa Barbara",
        "Ventura",
        "Los Angeles",
        "Orange",
        "Riverside",
        "San Diego",
        "Imperial",
    }
)

# Overrides for places not in the GNIS/Census dataset.
_CA_CITY_OVERRIDES: Dict[str, str] = {
    # LA neighborhoods (within City of Los Angeles)
    "canoga park": "Los Angeles",
    "chatsworth": "Los Angeles",
    "encino": "Los Angeles",
    "granada hills": "Los Angeles",
    "harbor city": "Los Angeles",
    "north hollywood": "Los Angeles",
    "san pedro": "Los Angeles",
    "sherman oaks": "Los Angeles",
    "studio city": "Los Angeles",
    "valley glen": "Los Angeles",
    "van nuys": "Los Angeles",
    "west hills": "Los Angeles",
    "wilmington": "Los Angeles",
    "winnetka": "Los Angeles",
    "woodland hills": "Los Angeles",
    # Communities within larger incorporated cities
    "la jolla": "San Diego",
    "newhall": "Los Angeles",
    "newbury park": "Ventura",
    "newport coast": "Orange",
    "valencia": "Los Angeles",
    # Unincorporated communities not in Census
    "la crescenta": "Los Angeles",
    "mira loma": "Riverside",
    "palos verdes peninsula": "Los Angeles",
    "pebble beach": "Monterey",
    "port hueneme cbc base": "Ventura",
    # FIRST API name variants (team-registered name differs from official name)
    "carmel": "Monterey",
    "okland": "Alameda",
}


def _load_gnis_city_to_county() -> Dict[str, str]:
    data_path = Path(__file__).parent / "data" / "ca_city_to_county.json"
    with open(data_path) as f:
        return json.load(f)

# ~1,450 California place names (incorporated cities, towns, and CDPs with
# population > 100) mapped to counties via USGS GNIS cross-referenced with
# Census population. Ambiguous names are resolved to the larger place.
_CA_GNIS_CITY_TO_COUNTY: Dict[str, str] = _load_gnis_city_to_county()


def _normalize_city(city: str) -> str:
    """Lowercase, strip whitespace, and remove diacritics (e.g. ñ -> n)."""
    key = city.lower().strip()
    key = unicodedata.normalize("NFD", key)
    return "".join(c for c in key if unicodedata.category(c) != "Mn")


class SubDistrictHelper:
    @staticmethod
    def get_sub_district(
        district_key: DistrictKey, team_key: TeamKey, city: Optional[str] = None
    ) -> Optional[str]:
        """
        Determines the sub-district pool (e.g. "north" or "south") for a team
        within a district that has multiple district championship pools.

        For California ("ca"), teams in the 10 southern counties are assigned
        "south" and all others are assigned "north". Returns None if the city
        is unknown (not in either mapping).

        Uses a two-tier lookup: manual overrides (LA neighborhoods, CDPs, name
        variants) checked first, then GNIS incorporated-cities data as fallback.

        Returns None for all non-California districts.
        """
        district_abbrev = district_key[4:]
        if district_abbrev != "ca":
            return None

        if not city:
            return None

        normalized = _normalize_city(city)
        county = _CA_CITY_OVERRIDES.get(normalized) or _CA_GNIS_CITY_TO_COUNTY.get(
            normalized
        )
        if county is None:
            return None

        if county in SOUTH_CA_COUNTIES:
            return "south"
        return "north"
