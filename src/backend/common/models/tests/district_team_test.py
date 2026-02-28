import pytest
from google.appengine.ext import ndb

from backend.common.models.district import District
from backend.common.models.district_team import DistrictTeam
from backend.common.models.event_team import Team


@pytest.mark.parametrize("key", ["2010ne_frc177", "2016fim_frc33"])
def test_valid_key_names(key: str) -> None:
    assert DistrictTeam.validate_key_name(key) is True


@pytest.mark.parametrize("key", ["frc177_2010ct", "2010ctfrc177", "asdf"])
def test_invalid_key_name(key: str) -> None:
    assert DistrictTeam.validate_key_name(key) is False


def test_key_name() -> None:
    dt = DistrictTeam(
        id="2010ne_frc177",
        district_key=ndb.Key(District, "2010ne"),
        team=ndb.Key(Team, "frc177"),
        year=2010,
    )
    assert dt.key_name == "2010ne_frc177"


def test_sub_district_default_none() -> None:
    dt = DistrictTeam(
        id="2026ca_frc254",
        district_key=ndb.Key(District, "2026ca"),
        team=ndb.Key(Team, "frc254"),
        year=2026,
    )
    assert dt.sub_district is None


def test_sub_district_set() -> None:
    dt = DistrictTeam(
        id="2026ca_frc254",
        district_key=ndb.Key(District, "2026ca"),
        team=ndb.Key(Team, "frc254"),
        year=2026,
        sub_district="north",
    )
    assert dt.sub_district == "north"
