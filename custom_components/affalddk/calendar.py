"""Support for AffaldDK Waste calendars."""
from __future__ import annotations

import datetime
from datetime import datetime as dt, timedelta
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
from homeassistant.util import dt as dt_util

from pyrenoweb import NAME_LIST, PickupType
from . import AffaldDKtDataUpdateCoordinator
from .const import (
    CONF_ADDRESS_ID,
    CONF_HOUSE_NUMBER,
    CONF_ROAD_NAME,
    DEFAULT_ATTRIBUTION,
    DEFAULT_BRAND,
    DOMAIN,
)


_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up AffaldDK Waste calendard items based on a config entry."""

    coordinator: AffaldDKtDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]

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
        coordinator: AffaldDKtDataUpdateCoordinator,
        config: MappingProxyType[str, Any]
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

    @property
    def event(self) -> CalendarEvent | None:
        """Return the next upcoming event."""
        return self._event

    async def async_get_events(self, hass: HomeAssistant, start_date: datetime.datetime, end_date: datetime.datetime) -> list[CalendarEvent]:
        """"Return calendar events within a datetime range."""

        events = []
        for item in self._coordinator.data.pickup_events:
            if self._coordinator.data.pickup_events.get(item) is None:
                continue
            if item == 'next_pickup':
                continue

            _pickup_events: PickupType = self._coordinator.data.pickup_events.get(item) if self._coordinator.data.pickup_events else None

            _summary = NAME_LIST.get(item)
            _start: dt = _pickup_events.date
            _end: dt = _start + timedelta(days=1)

            if _start and _end:
                events.append(
                    CalendarEvent(
                        summary=_summary,
                        description=_pickup_events.description,
                        start=dt_util.as_local(_start),
                        end=dt_util.as_local(_end),
                    )
                )
        return events


    async def async_added_to_hass(self):
        """When entity is added to hass."""
        self.async_on_remove(
            self._coordinator.async_add_listener(self.async_write_ha_state)
        )
