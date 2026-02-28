import pytest

from backend.common.helpers.sub_district_helper import SubDistrictHelper


def test_non_ca_district_returns_none() -> None:
    assert SubDistrictHelper.get_sub_district("2026fim", "frc1124", "Detroit") is None


def test_non_ca_district_returns_none_even_with_ca_city() -> None:
    assert (
        SubDistrictHelper.get_sub_district("2026ne", "frc1124", "Los Angeles") is None
    )


def test_ca_south_la_county() -> None:
    assert (
        SubDistrictHelper.get_sub_district("2026ca", "frc1234", "Los Angeles")
        == "south"
    )


def test_ca_south_san_diego_county() -> None:
    assert (
        SubDistrictHelper.get_sub_district("2026ca", "frc5678", "Chula Vista")
        == "south"
    )


def test_ca_south_orange_county() -> None:
    assert SubDistrictHelper.get_sub_district("2026ca", "frc9999", "Irvine") == "south"


def test_ca_south_ventura_county() -> None:
    assert (
        SubDistrictHelper.get_sub_district("2026ca", "frc100", "Camarillo") == "south"
    )


def test_ca_south_imperial_county() -> None:
    assert (
        SubDistrictHelper.get_sub_district("2026ca", "frc200", "El Centro") == "south"
    )


def test_ca_south_kern_county_via_override() -> None:
    # Rosamond is unincorporated (not in GNIS Civil), resolved via override
    assert SubDistrictHelper.get_sub_district("2026ca", "frc300", "Rosamond") == "south"


def test_ca_south_riverside_county() -> None:
    assert SubDistrictHelper.get_sub_district("2026ca", "frc400", "Temecula") == "south"


def test_ca_south_san_bernardino_county() -> None:
    assert SubDistrictHelper.get_sub_district("2026ca", "frc500", "Highland") == "south"


def test_ca_south_santa_barbara_county() -> None:
    assert SubDistrictHelper.get_sub_district("2026ca", "frc600", "Goleta") == "south"


def test_ca_south_san_luis_obispo_county() -> None:
    assert (
        SubDistrictHelper.get_sub_district("2026ca", "frc700", "Arroyo Grande")
        == "south"
    )


def test_ca_north_santa_clara_county() -> None:
    assert SubDistrictHelper.get_sub_district("2026ca", "frc254", "San Jose") == "north"


def test_ca_north_alameda_county() -> None:
    assert SubDistrictHelper.get_sub_district("2026ca", "frc800", "Fremont") == "north"


def test_ca_north_sacramento_county() -> None:
    assert (
        SubDistrictHelper.get_sub_district("2026ca", "frc900", "Elk Grove") == "north"
    )


def test_ca_north_san_francisco() -> None:
    assert (
        SubDistrictHelper.get_sub_district("2026ca", "frc1000", "San Francisco")
        == "north"
    )


def test_unknown_city_returns_none() -> None:
    assert (
        SubDistrictHelper.get_sub_district("2026ca", "frc1111", "Nonexistent City")
        is None
    )


def test_none_city_returns_none() -> None:
    assert SubDistrictHelper.get_sub_district("2026ca", "frc1111", None) is None


def test_empty_city_returns_none() -> None:
    assert SubDistrictHelper.get_sub_district("2026ca", "frc1111", "") is None


def test_case_insensitive_lookup() -> None:
    assert SubDistrictHelper.get_sub_district("2026ca", "frc254", "san jose") == "north"
    assert SubDistrictHelper.get_sub_district("2026ca", "frc254", "SAN JOSE") == "north"
    assert SubDistrictHelper.get_sub_district("2026ca", "frc254", "San Jose") == "north"


def test_case_insensitive_south() -> None:
    assert (
        SubDistrictHelper.get_sub_district("2026ca", "frc1234", "INGLEWOOD") == "south"
    )
    assert (
        SubDistrictHelper.get_sub_district("2026ca", "frc1234", "inglewood") == "south"
    )


def test_whitespace_stripped() -> None:
    assert (
        SubDistrictHelper.get_sub_district("2026ca", "frc254", "  San Jose  ")
        == "north"
    )


def test_diacritic_normalization() -> None:
    assert (
        SubDistrictHelper.get_sub_district(
            "2026ca", "frc1", "La Ca\u00f1ada Flintridge"
        )
        == "south"
    )
    assert (
        SubDistrictHelper.get_sub_district("2026ca", "frc1", "La Canada Flintridge")
        == "south"
    )


def test_gnis_fallback_for_incorporated_city() -> None:
    # Cupertino is in the GNIS data but not in the overrides dict
    assert SubDistrictHelper.get_sub_district("2026ca", "frc1", "Cupertino") == "north"


def test_override_takes_precedence() -> None:
    # "Canoga Park" is an LA neighborhood only in overrides, not GNIS Civil
    assert (
        SubDistrictHelper.get_sub_district("2026ca", "frc1", "Canoga Park") == "south"
    )


def test_gnis_ambiguous_resolved_correctly() -> None:
    # "Alameda" exists in both Alameda County (north) and Kern County (south)
    # in GNIS; should resolve to Alameda County (the incorporated city)
    assert SubDistrictHelper.get_sub_district("2026ca", "frc1", "Alameda") == "north"


def test_gnis_covers_city_not_in_original_curated_list() -> None:
    # Bakersfield is a major city that was not in the original 168-city list
    assert (
        SubDistrictHelper.get_sub_district("2026ca", "frc1", "Bakersfield") == "south"
    )
    # Stockton is in San Joaquin county (north)
    assert SubDistrictHelper.get_sub_district("2026ca", "frc1", "Stockton") == "north"


@pytest.mark.parametrize(
    "city",
    [
        "Los Angeles",
        "Anaheim",
        "San Diego",
        "Pasadena",
        "Ventura",
        "Oxnard",
        "Lancaster",
        "Long Beach",
    ],
)
def test_various_south_cities(city: str) -> None:
    assert SubDistrictHelper.get_sub_district("2026ca", "frc1", city) == "south"


@pytest.mark.parametrize(
    "city",
    [
        "Oakland",
        "Berkeley",
        "Palo Alto",
        "Sacramento",
        "Fresno",
        "Davis",
        "Monterey",
        "Santa Rosa",
    ],
)
def test_various_north_cities(city: str) -> None:
    assert SubDistrictHelper.get_sub_district("2026ca", "frc1", city) == "north"
