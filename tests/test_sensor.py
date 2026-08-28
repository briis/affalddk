# ruff: noqa: S301, B023
"""Tests for the AffaldDK sensor entity definition."""

import datetime as dt
import json
import pickle
from pathlib import Path
from types import MappingProxyType

import pytest
from aiohttp import ClientSession
from freezegun import freeze_time

from custom_components.affalddk.const import (
    ATTR_CONTAINER_COUNT,
    ATTR_DATE_LONG,
    ATTR_DATE_SHORT,
    ATTR_DESCRIPTION,
    ATTR_DURATION,
    ATTR_LAST_UPDATE,
    CONF_ADDRESS,
    CONF_ADDRESS_ID,
    CONF_MUNICIPALITY,
    DEFAULT_ATTRIBUTION,
)
from homeassistant.const import ATTR_DATE, ATTR_NAME, ATTR_ENTITY_PICTURE
from custom_components.affalddk.pyaffalddk.api import GarbageCollection
from custom_components.affalddk.pyaffalddk.data import PickupType
from custom_components.affalddk.sensor import AffaldDKSensor, SENSOR_TYPES

DATADIR = Path(__file__).parent / "data"


def _find_description(key: str):
    for desc in SENSOR_TYPES:
        if desc.key == key:
            return desc
    raise AssertionError(f"no SENSOR_TYPES entry for {key!r}")


class FakeCoordinator:
    """Minimal coordinator exposing a data object with pickup_events."""

    def __init__(self, pickup_events):
        """Store the pickup_events dict on a data object."""
        self.data = type("Data", (), {"pickup_events": pickup_events})()


def _make_sensor(pickup_events, description_key="restaffaldmadaffald", unit_language="da"):
    """Build an AffaldDKSensor wired to the given pickup_events dict."""
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
            "options": MappingProxyType({"unit_language": unit_language}),
        },
    )()
    coordinator = FakeCoordinator(pickup_events)
    return AffaldDKSensor(coordinator, _find_description(description_key), config)


def _pickup(date, description="Rest & Madaffald", group=["restaffaldmadaffald"],
            container_count=None):
    return PickupType(
        date=date,
        group=group,
        description=description,
        container_count=container_count,
    )


def test_sensor_metadata():
    """Attributes set on the entity at construction time."""
    sensor = _make_sensor({})

    assert sensor._attr_attribution == DEFAULT_ATTRIBUTION
    assert sensor._attr_has_entity_name is True
    assert sensor.unique_id == "1111 restaffaldmadaffald"
    assert sensor.name == "Rest- & madaffald"
    # device info carries the address-based device name
    assert sensor._attr_device_info.name == "Affalddk Boulevarden 1, 7500 Holstebro"


def test_unknown_without_pickup():
    """No pickup data -> state is unknown, no unit, minimal attributes."""
    sensor = _make_sensor({})

    assert sensor.event is None
    assert sensor.native_value == "unknown"
    assert sensor.native_unit_of_measurement is None
    assert sensor.icon == "mdi:trash-can"

    attrs = sensor.extra_state_attributes
    assert ATTR_DATE not in attrs
    assert ATTR_DATE_LONG not in attrs
    assert ATTR_LAST_UPDATE in attrs


@freeze_time("2025-05-22")
def test_pickup_attributes_duration():
    """Full attribute set with a known pickup date."""
    event = _pickup(dt.date(2025, 5, 24), container_count=2)
    sensor = _make_sensor({"restaffaldmadaffald": event})

    assert sensor.event is event
    assert sensor.native_value == 2
    assert sensor.native_unit_of_measurement == "dage"

    attrs = sensor.extra_state_attributes
    assert attrs[ATTR_DATE] == dt.date(2025, 5, 24)
    assert attrs[ATTR_DATE_LONG] == "Lørdag d. 24-05-2025"
    assert attrs[ATTR_DATE_SHORT] == "Lør d. 24/05"
    assert attrs[ATTR_DESCRIPTION] == "Rest & Madaffald"
    assert attrs[ATTR_DURATION] == "Om 2 dage"
    assert attrs[ATTR_NAME] == "Rest & Madaffald"
    assert attrs[ATTR_CONTAINER_COUNT] == 2


@freeze_time("2025-05-22")
def test_english_unit_language():
    """The english variant uses 'days' and 'In N days'."""
    event = _pickup(dt.date(2025, 5, 23))
    sensor = _make_sensor({"restaffaldmadaffald": event}, unit_language="en")

    assert sensor.native_value == 1
    assert sensor.native_unit_of_measurement == "day"
    assert sensor.extra_state_attributes[ATTR_DURATION] == "Tomorrow"


@pytest.mark.asyncio
@freeze_time("2025-05-09")
async def test_sensor_attributes_from_smoke_data(capsys, monkeypatch):
    """friendly_name (and friends) flow from real API data into sensor attributes.

    Uses the datasets of the smoke test from test_api to exercise the
    full pipeline: raw data -> GarbageCollection -> sensor attributes.
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
                for key, event in pickup_events.items():
                    sensor = _make_sensor(pickup_events, description_key=key)

                    # the sensor's ATTR_NAME is the event's friendly_name
                    assert sensor.extra_state_attributes[ATTR_NAME] == sensor.waste_name(event.group)
                    assert sensor.extra_state_attributes[ATTR_DESCRIPTION] == event.description
                    assert sensor.extra_state_attributes[ATTR_ENTITY_PICTURE] == event.entity_picture

                    # against compare data
                    if key == 'next_pickup':
                        assert sensor.extra_state_attributes[ATTR_NAME] == smokecompare[_name][key]
                    else:
                        assert sensor.extra_state_attributes[ATTR_DESCRIPTION] == smokecompare[_name][key]
                        assert sensor.extra_state_attributes[ATTR_ENTITY_PICTURE] == f"/affalddk/img/{event.group[0]}.svg"


                    if event.container_count is not None:
                        assert (
                            sensor.extra_state_attributes[ATTR_CONTAINER_COUNT]
                            == event.container_count
                        )
