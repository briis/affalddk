"""Support for AffaldDK Waste calendars."""

from __future__ import annotations

import datetime
from datetime import datetime as dt, timedelta, time
import logging
from types import MappingProxyType
from typing import Any

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)
from homeassistant.util.dt import get_default_time_zone
from pyaffalddk import NAME_LIST, PickupType
from . import AffaldDKDataUpdateCoordinator
from .const import (
    CONF_ADDRESS_ID,
    CONF_CALENDAR_END_TIME,
    CONF_CALENDAR_START_TIME,
    CONF_HOUSE_NUMBER,
    CONF_ROAD_NAME,
    DEFAULT_ATTRIBUTION,
    DEFAULT_BRAND,
    DEFAULT_END_TIME,
    DEFAULT_START_TIME,
    DOMAIN,
)


_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up AffaldDK Waste calendard items based on a config entry."""

    coordinator: AffaldDKDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]

    # entities: list[AffaldDKCalendar[Any]] = [
    #     AffaldDKCalendar(coordinator, config[1])
    #     for config in coordinator.data.items()
    # ]
    # async_add_entities(entities, False)
    coordinator.data.pickup_events = coordinator.data.pickup_events or {}
    if coordinator.data.pickup_events == {}:
        return

    async_add_entities([AffaldDKCalendar(coordinator, config_entry)])


class AffaldDKCalendar(CoordinatorEntity[DataUpdateCoordinator], CalendarEntity):
    """Define a AffaldDK Waste calendar."""

    _attr_attribution = DEFAULT_ATTRIBUTION
    _attr_has_entity_name = True
    _attr_name = None

    def __init__(
        self,
        coordinator: AffaldDKDataUpdateCoordinator,
        config: MappingProxyType[str, Any],
    ) -> None:
        """Initialize a AffaldDK sensor."""
        super().__init__(coordinator)
        self._config = config
        self._coordinator = coordinator

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._config.data[CONF_ADDRESS_ID])},
            entry_type=DeviceEntryType.SERVICE,
            manufacturer=DEFAULT_BRAND,
            name=f"{DOMAIN.capitalize()} {self._config.data[CONF_ROAD_NAME]} {self._config.data[CONF_HOUSE_NUMBER]}",
            configuration_url="https://github.com/briis/affalddk",
        )

        self._attr_unique_id = config.data[CONF_ADDRESS_ID]
        self._event: CalendarEvent | None = None
        self._end_time = self._config.options.get(CONF_CALENDAR_END_TIME, DEFAULT_END_TIME)
        self._start_time = self._config.options.get(CONF_CALENDAR_START_TIME, DEFAULT_START_TIME)

    @property
    def event(self) -> CalendarEvent | None:
        """Return the next upcoming event."""
        item = None
        _next_pickup: dt = dt(2030, 12, 31, self._start_time, 0, 0).replace(tzinfo=get_default_time_zone())
        # _next_pickup = _next_pickup.date()
        _pickup_event: PickupType = None
        _pickup_events: PickupType = None
        if self._coordinator.data.pickup_events is None:
            return None

        # Find the next pickup event
        for row in self._coordinator.data.pickup_events:
            if row == "next_pickup":
                continue
            _pickup_event: PickupType = self._coordinator.data.pickup_events.get(row)
            _start_dt = dt.combine(_pickup_event.date, time(self._start_time, 0, 0)).replace(tzinfo=get_default_time_zone())
            _end_dt = dt.combine(_pickup_event.date, time(self._end_time, 0, 0)).replace(tzinfo=get_default_time_zone())
            if _start_dt is not None and _next_pickup is not None and _start_dt <= _next_pickup:
                _next_pickup = _start_dt
                _pickup_events = _pickup_event
                item = row

        _start: datetime.date = _pickup_events.date
        _end: datetime.date = _start + timedelta(days=1)

        return CalendarEvent(
            summary=NAME_LIST.get(item, "Unknown") if item else "Unknown",
            description=_pickup_events.description,
            start=_start_dt,
            end=_end_dt,
        )

    async def async_get_events(
        self,
        hass: HomeAssistant,
        start_date: datetime.datetime,
        end_date: datetime.datetime,
    ) -> list[CalendarEvent]:
        """Return calendar events within a datetime range."""

        events: list[CalendarEvent] = []
        for item in self._coordinator.data.pickup_events:
            if self._coordinator.data.pickup_events.get(item) is None:
                continue
            if item == "next_pickup":
                continue

            _pickup_events: PickupType = (
                self._coordinator.data.pickup_events.get(item)
                if self._coordinator.data.pickup_events
                else None
            )

            if start_date > dt.combine(_pickup_events.date, time(self._start_time, 0, 0)).replace(tzinfo=get_default_time_zone()):
                continue
            if end_date < dt.combine(_pickup_events.date, time(self._end_time, 0, 0)).replace(tzinfo=get_default_time_zone()):
                continue

            _summary = NAME_LIST.get(item,"Unknown") if item else "Unknown"
            # _start: datetime.date = _pickup_events.date
            # _end: datetime.date = _start + timedelta(days=1)

            _start_dt = dt.combine(_pickup_events.date, time(self._start_time, 0, 0)).replace(tzinfo=get_default_time_zone())
            _end_dt = dt.combine(_pickup_events.date, time(self._end_time, 0, 0)).replace(tzinfo=get_default_time_zone())

            if start_date > _start_dt:
                continue
            if end_date < _end_dt:
                continue

            if _start_dt and _end_dt:
                events.append(
                    CalendarEvent(
                        summary=_summary,
                        description=_pickup_events.description,
                        start=_start_dt,
                        end=_end_dt,
                    )
                )
        return events

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        self.async_on_remove(
            self._coordinator.async_add_listener(self.async_write_ha_state)
        )
