import json

import pytest
from google.appengine.ext import ndb
from pyre_extensions import none_throws

from backend.common.consts.alliance_color import AllianceColor
from backend.common.consts.comp_level import CompLevel
from backend.common.helpers.match_tiebreakers import MatchTiebreakers
from backend.common.models.alliance import MatchAlliance
from backend.common.models.event import Event
from backend.common.models.match import Match


@pytest.fixture(autouse=True)
def auto_add_ndb_context(ndb_context) -> None:
    pass


def test_not_elim_match() -> None:
    m = Match(
        comp_level=CompLevel.QM,
    )
    assert MatchTiebreakers.tiebreak_winner(m) == ""


def test_no_breakdowns() -> None:
    m = Match(comp_level=CompLevel.SF)
    assert MatchTiebreakers.tiebreak_winner(m) == ""


def test_match_not_played() -> None:
    m = Match(
        comp_level=CompLevel.SF,
        alliances_json=json.dumps(
            {
                AllianceColor.RED: MatchAlliance(
                    teams=["frc1", "frc2", "frc3"],
                    score=-1,
                ),
                AllianceColor.BLUE: MatchAlliance(
                    teams=["frc4", "frc5", "frc6"],
                    score=-1,
                ),
            }
        ),
    )
    assert MatchTiebreakers.tiebreak_winner(m) == ""


def test_2016_tiebreakers(test_data_importer) -> None:
    test_data_importer.import_match(__file__, "data/2016cmp_f1m3.json")
    match: Match = none_throws(Match.get_by_id("2016cmp_f1m3"))
    assert match.winning_alliance == AllianceColor.RED


def test_2017_tiebreakers(test_data_importer) -> None:
    test_data_importer.import_match(__file__, "data/2017dal_qf3m2.json")
    match: Match = none_throws(Match.get_by_id("2017dal_qf3m2"))
    assert match.winning_alliance == AllianceColor.RED


def test_2019_tiebreakers(test_data_importer) -> None:
    test_data_importer.import_match(__file__, "data/2019hiho_qf4m1.json")
    match: Match = none_throws(Match.get_by_id("2019hiho_qf4m1"))
    assert match.winning_alliance == AllianceColor.RED


def test_2020_tiebreakers(test_data_importer) -> None:
    test_data_importer.import_match(__file__, "data/2020mndu2_sf2m2.json")
    match: Match = none_throws(Match.get_by_id("2020mndu2_sf2m2"))
    assert match.winning_alliance == AllianceColor.BLUE


def test_2022_tiebreakers(test_data_importer) -> None:
    test_data_importer.import_match(__file__, "data/2022wasam_qf2m2.json")
    match: Match = none_throws(Match.get_by_id("2022wasam_qf2m2"))
    assert match.winning_alliance == AllianceColor.BLUE


def test_2023_tiebreakers(test_data_importer) -> None:
    test_data_importer.import_match(__file__, "data/2023cmptx_sf12m1.json")
    match: Match = none_throws(Match.get_by_id("2023cmptx_sf12m1"))
    assert match.winning_alliance == AllianceColor.RED


def test_2024_tiebreakers(test_data_importer) -> None:
    # broken by tech fouls
    test_data_importer.import_match(__file__, "data/2024miket_sf13m1.json")
    match: Match = none_throws(Match.get_by_id("2024miket_sf13m1"))
    assert match.winning_alliance == AllianceColor.RED

    # broken by auto points
    test_data_importer.import_match(__file__, "data/2024isde1_sf12m1.json")
    match: Match = none_throws(Match.get_by_id("2024isde1_sf12m1"))
    assert match.winning_alliance == AllianceColor.RED

    # finals match - no tiebreakers
    test_data_importer.import_match(__file__, "data/2024isde1_f1m2.json")
    match: Match = none_throws(Match.get_by_id("2024isde1_f1m2"))
    assert match.winning_alliance == ""


def test_2025_tiebreakers(test_data_importer) -> None:
    # Broken by tech fouls
    test_data_importer.import_match(__file__, "data/2025nhsal_sf7m1.json")
    match: Match = none_throws(Match.get_by_id("2025nhsal_sf7m1"))
    assert match.winning_alliance == AllianceColor.BLUE

    # Broken by auto points
    test_data_importer.import_match(__file__, "data/2025vagle_sf8m1.json")
    match: Match = none_throws(Match.get_by_id("2025vagle_sf8m1"))
    assert match.winning_alliance == AllianceColor.BLUE


def _match_2026_elim_tie(
    *,
    red_score: int = 50,
    blue_score: int = 50,
    red_major_fouls: int = 0,
    blue_major_fouls: int = 0,
    red_hub_auto: int = 0,
    blue_hub_auto: int = 0,
    red_tower: int = 0,
    blue_tower: int = 0,
    comp_level: CompLevel = CompLevel.SF,
    match_number: int = 1,
) -> Match:
    return Match(
        id="2026tie_sf1m1",
        year=2026,
        comp_level=comp_level,
        match_number=match_number,
        set_number=1,
        event=ndb.Key(Event, "2026tie"),
        alliances_json=json.dumps(
            {
                AllianceColor.RED: {
                    "teams": ["frc1", "frc2", "frc3"],
                    "score": red_score,
                },
                AllianceColor.BLUE: {
                    "teams": ["frc4", "frc5", "frc6"],
                    "score": blue_score,
                },
            }
        ),
        score_breakdown_json=json.dumps(
            {
                AllianceColor.RED: {
                    "majorFoulCount": red_major_fouls,
                    "totalTowerPoints": red_tower,
                    "hubScore": {"autoPoints": red_hub_auto},
                },
                AllianceColor.BLUE: {
                    "majorFoulCount": blue_major_fouls,
                    "totalTowerPoints": blue_tower,
                    "hubScore": {"autoPoints": blue_hub_auto},
                },
            }
        ),
    )


def test_2026_tiebreak_major_foul_proxy() -> None:
    # Blue committed more major fouls → red receives more major foul points → red wins
    m = _match_2026_elim_tie(red_major_fouls=0, blue_major_fouls=2)
    assert m.winning_alliance == AllianceColor.RED


def test_2026_tiebreak_auto_fuel_points() -> None:
    m = _match_2026_elim_tie(
        red_major_fouls=1,
        blue_major_fouls=1,
        red_hub_auto=12,
        blue_hub_auto=10,
    )
    assert m.winning_alliance == AllianceColor.RED


def test_2026_tiebreak_tower_points() -> None:
    m = _match_2026_elim_tie(
        red_major_fouls=1,
        blue_major_fouls=1,
        red_hub_auto=5,
        blue_hub_auto=5,
        red_tower=30,
        blue_tower=20,
    )
    assert m.winning_alliance == AllianceColor.RED


def test_2026_finals_early_no_tiebreak() -> None:
    m = _match_2026_elim_tie(comp_level=CompLevel.F, match_number=2)
    assert m.winning_alliance == ""


def test_2026_finals_overtime_uses_tiebreak() -> None:
    m = _match_2026_elim_tie(
        comp_level=CompLevel.F,
        match_number=4,
        red_major_fouls=0,
        blue_major_fouls=1,
    )
    assert m.winning_alliance == AllianceColor.RED
