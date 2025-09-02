"""Support for AffaldDK Waste calendars."""

from __future__ import annotations

import datetime
from datetime import datetime as dt, time
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
from . import AffaldDKDataUpdateCoordinator
from .const import (
    CONF_ADDRESS,
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

    if coordinator.data.pickup_events:
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
        name = DOMAIN.capitalize()
        if CONF_ADDRESS in self._config.data:
            name += f" {self._config.data[CONF_ADDRESS]}"
        else:
            # backwards compatible
            name += f" {self._config.data[CONF_ROAD_NAME]} {self._config.data[CONF_HOUSE_NUMBER]}"

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._config.data[CONF_ADDRESS_ID])},
            entry_type=DeviceEntryType.SERVICE,
            manufacturer=DEFAULT_BRAND,
            name=name,
            configuration_url="https://github.com/briis/affalddk",
        )

        self._attr_unique_id = config.data[CONF_ADDRESS_ID]
        self._event: CalendarEvent | None = None
        self._end_time = self._config.options.get(CONF_CALENDAR_END_TIME, DEFAULT_END_TIME)
        self._start_time = self._config.options.get(CONF_CALENDAR_START_TIME, DEFAULT_START_TIME)

    @property
    def event(self) -> CalendarEvent | None:
        """Return the next upcoming event."""
        if next_pickup := self._coordinator.data.pickup_events.get('next_pickup'):
            _start_dt = dt.combine(next_pickup.date, time(self._start_time, 0, 0)).replace(tzinfo=get_default_time_zone())
            _end_dt = dt.combine(next_pickup.date, time(self._end_time, 0, 0)).replace(tzinfo=get_default_time_zone())
            return CalendarEvent(
                summary=next_pickup.friendly_name,
                description=next_pickup.description,
                start=_start_dt,
                end=_end_dt,
            )
        return None

    async def async_get_events(
        self,
        hass: HomeAssistant,
        start_date: datetime.datetime,
        end_date: datetime.datetime,
    ) -> list[CalendarEvent]:
        """Return calendar events within a datetime range."""

        events: list[CalendarEvent] = []
        for name, event in self._coordinator.data.pickup_events.items():
            if event and name != "next_pickup":
                event_start = dt.combine(event.date, time(self._start_time, 0, 0)).replace(tzinfo=get_default_time_zone())
                event_end = dt.combine(event.date, time(self._end_time, 0, 0)).replace(tzinfo=get_default_time_zone())
                if (start_date <= event_start) and (end_date >= event_end):
                    events.append(
                        CalendarEvent(
                            summary=event.friendly_name,
                            description=event.description,
                            start=event_start,
                            end=event_end,
                        )
                    )
        return events

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        self.async_on_remove(
            self._coordinator.async_add_listener(self.async_write_ha_state)
        )
