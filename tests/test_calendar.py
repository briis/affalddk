# ruff: noqa: S301, B023
"""Tests for the AffaldDK calendar entity definition."""

import datetime as dt
import json
import pickle
from pathlib import Path
from types import MappingProxyType

import pytest
from aiohttp import ClientSession
from freezegun import freeze_time

from custom_components.affalddk.calendar import AffaldDKCalendar
from custom_components.affalddk.const import (
    CONF_ADDRESS,
    CONF_ADDRESS_ID,
    CONF_CALENDAR_END_TIME,
    CONF_CALENDAR_START_TIME,
    CONF_MUNICIPALITY,
    DEFAULT_ATTRIBUTION,
    DEFAULT_END_TIME,
    DEFAULT_START_TIME,
    TRANSLATIONS,
)
from custom_components.affalddk.pyaffalddk.api import GarbageCollection
from custom_components.affalddk.pyaffalddk.data import PickupType

DATADIR = Path(__file__).parent / "data"


class FakeCoordinator:
    """Minimal coordinator exposing a data object with pickup_events."""

    def __init__(self, pickup_events):
        """Store the pickup_events dict on a data object."""
        self.data = type("Data", (), {"pickup_events": pickup_events})()


def _make_calendar(pickup_events, start_time=7, end_time=15, unit_language='da'):
    """Build an AffaldDKCalendar wired to the given pickup_events dict."""
    config_data = {
        CONF_MUNICIPALITY: "Holstebro",
        CONF_ADDRESS: "Boulevarden 1, 7500 Holstebro",
        CONF_ADDRESS_ID: "1111",
    }
    config = type(
        "FakeConfigEntry",
        (),
        {
            "data": MappingProxyType(config_data),
            "options": MappingProxyType(
                {
                    CONF_CALENDAR_START_TIME: start_time,
                    CONF_CALENDAR_END_TIME: end_time,
                }
            ),
        },
    )()
    coordinator = FakeCoordinator(pickup_events)
    coordinator.translations = TRANSLATIONS[unit_language]
    return AffaldDKCalendar(coordinator, config)


def _pickup(date, description="Rest & Madaffald", group=["restaffaldmadaffald"],
            container_count=None):
    return PickupType(
        date=date,
        group=group,
        description=description,
        container_count=container_count,
    )


def test_calendar_metadata():
    """Attributes set on the entity at construction time."""
    calendar = _make_calendar({})

    assert calendar._attr_attribution == DEFAULT_ATTRIBUTION
    assert calendar._attr_has_entity_name is True
    assert calendar._attr_name is None
    assert calendar.unique_id == "1111"
    assert calendar._attr_device_info.name == "Affalddk Boulevarden 1, 7500 Holstebro"


def test_no_next_pickup_event_none():
    """Without a next_pickup there is no current event and no entities returned."""
    calendar = _make_calendar({})
    assert calendar.event is None


def test_event_from_next_pickup():
    """The event summary/description/times come from the next_pickup PickupType."""
    next_pickup = _pickup(
        dt.date(2025, 5, 24),
        group=["genbrug"],
        description="Genbrug",
    )
    calendar = _make_calendar({"next_pickup": next_pickup})

    event = calendar.event
    assert event is not None
    assert event.summary == "Genbrug"
    assert event.description == "Genbrug"
    # DEFAULT_START_TIME/END_TIME are the fallbacks, but here they come from options
    assert event.start == dt.datetime(2025, 5, 24, DEFAULT_START_TIME, 0, 0, tzinfo=dt.timezone.utc)
    assert event.end == dt.datetime(2025, 5, 24, DEFAULT_END_TIME, 0, 0, tzinfo=dt.timezone.utc)


def test_custom_start_end_times():
    """The start/end times are read from the config options."""
    next_pickup = _pickup(dt.date(2025, 5, 24))
    calendar = _make_calendar({"next_pickup": next_pickup}, start_time=8, end_time=20)

    event = calendar.event
    assert event.start == dt.datetime(2025, 5, 24, 8, 0, 0, tzinfo=dt.timezone.utc)
    assert event.end == dt.datetime(2025, 5, 24, 20, 0, 0, tzinfo=dt.timezone.utc)


@pytest.mark.asyncio
async def test_async_get_events_range():
    """async_get_events returns pickup events overlapping the requested window."""
    events_data = {
        "restaffaldmadaffald": _pickup(dt.date(2025, 5, 24)),
        "papir": _pickup(dt.date(2025, 6, 1), description="Papir", group=["papir"]),
        # outside the window
        "storskrald": _pickup(dt.date(2025, 7, 1), description="Storskrald", group=["storskrald"]),
        "next_pickup": _pickup(dt.date(2025, 5, 24), group=["genbrug"]),
    }
    calendar = _make_calendar(events_data)

    events = await calendar.async_get_events(
        None,
        dt.datetime(2025, 5, 23, tzinfo=dt.timezone.utc),
        dt.datetime(2025, 6, 15, tzinfo=dt.timezone.utc),
    )

    # next_pickup and the July event are excluded
    assert {e.summary for e in events} == {"Rest & Madaffald", "Papir"}
    assert all(e.start.tzinfo is not None for e in events)


@pytest.mark.asyncio
@freeze_time("2025-05-09")
async def test_calendar_summary_from_smoke_data(capsys, monkeypatch):
    """The calendar summary follows friendly_name from real API data.

    Uses the datasets of the smoke test from test_api to exercise the
    full pipeline: raw data -> GarbageCollection -> calendar summary.
    """
    async with ClientSession() as session:
        smokedata = pickle.load((DATADIR / "smoketest_garbage_data.p").open("rb"))
        smokecompare_file = DATADIR / 'smoketest_fractions.json'
        with smokecompare_file.open('r') as fh:
            smokecompare = json.load(fh)

        with capsys.disabled():
            for _name, val in list(smokedata.items())[:]:
                gc = GarbageCollection(val["city"], session=session, fail=True)

                async def get_data(*args, **kwargs):
                    return val["data"]
                monkeypatch.setattr(gc._api, "get_garbage_data", get_data)

                pickup_events = await gc.get_pickup_data(1111)
                calendar = _make_calendar(pickup_events)

                # the calendar event summary is the next_pickup friendly_name
                assert calendar.event.summary == smokecompare[_name]["next_pickup"]
