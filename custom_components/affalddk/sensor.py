"""Support for AffaldDK sensor data."""

from __future__ import annotations

import logging

from dataclasses import dataclass
import datetime
from datetime import datetime as dt
from types import MappingProxyType
from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import ATTR_DATE, ATTR_NAME, ATTR_ENTITY_PICTURE
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)
from homeassistant.util.dt import now

from . import AffaldDKDataUpdateCoordinator
from .const import (
    ATTR_DATE_LONG,
    ATTR_DATE_SHORT,
    ATTR_DESCRIPTION,
    ATTR_DURATION,
    ATTR_LAST_UPDATE,
    CONF_ADDRESS,
    CONF_ADDRESS_ID,
    CONF_HOUSE_NUMBER,
    CONF_MUNICIPALITY,
    CONF_ROAD_NAME,
    DEFAULT_ATTRIBUTION,
    DEFAULT_BRAND,
    DOMAIN,
)
from .pyaffalddk.const import (
    ICON_LIST,
    WEEKDAYS,
    WEEKDAYS_SHORT,
)
from .pyaffalddk.data import PickupType

git_images = 'https://github.com/briis/affalddk/raw/refs/heads/main/images/affalddk/'

@dataclass(frozen=True)
class AffaldDKSensorEntityDescription(SensorEntityDescription):
    """Describes AffaldDK sensor entity."""


SENSOR_TYPES: tuple[AffaldDKSensorEntityDescription, ...] = (
    AffaldDKSensorEntityDescription(
        key="restaffaldmadaffald",
        name="Rest- & madaffald",
        native_unit_of_measurement="dage",
    ),
    AffaldDKSensorEntityDescription(
        key="batterier",
        name="Batterier",
        native_unit_of_measurement="dage",
    ),
    AffaldDKSensorEntityDescription(
        key="elektronik",
        name="Elektronik",
        native_unit_of_measurement="dage",
    ),
    AffaldDKSensorEntityDescription(
        key="glas",
        name="Glas",
        native_unit_of_measurement="dage",
    ),
    AffaldDKSensorEntityDescription(
        key="madaffald",
        name="Madaffald",
        native_unit_of_measurement="dage",
    ),
    AffaldDKSensorEntityDescription(
        key="dagrenovation",
        name="Dagrenovation",
        native_unit_of_measurement="dage",
    ),
    AffaldDKSensorEntityDescription(
        key="metalglas",
        name="Metal & Glas",
        native_unit_of_measurement="dage",
    ),
    AffaldDKSensorEntityDescription(
        key="papirglas",
        name="Papir, Pap & Glas",
        native_unit_of_measurement="dage",
    ),
    AffaldDKSensorEntityDescription(
        key="papirglasdaaser",
        name="Papir, Glas & Dåser",
        native_unit_of_measurement="dage",
    ),
    AffaldDKSensorEntityDescription(
        key="pappi",
        name="Papir & Plast",
        native_unit_of_measurement="dage",
    ),
    AffaldDKSensorEntityDescription(
        key="farligtaffald",
        name="Farligt affald",
        native_unit_of_measurement="dage",
    ),
    AffaldDKSensorEntityDescription(
        key="farligtaffaldmiljoboks",
        name="Farligt affald & Miljøboks",
        native_unit_of_measurement="dage",
    ),
    AffaldDKSensorEntityDescription(
        key="flis",
        name="Flis",
        native_unit_of_measurement="dage",
    ),
    AffaldDKSensorEntityDescription(
        key="genbrug",
        name="Genbrug",
        native_unit_of_measurement="dage",
    ),
    AffaldDKSensorEntityDescription(
        key="jern",
        name="Metal",
        native_unit_of_measurement="dage",
    ),
    AffaldDKSensorEntityDescription(
        key="papir",
        name="Papir",
        native_unit_of_measurement="dage",
    ),
    AffaldDKSensorEntityDescription(
        key="papirmetal",
        name="Papir & Metal",
        native_unit_of_measurement="dage",
    ),
    AffaldDKSensorEntityDescription(
        key="pap",
        name="Pap",
        native_unit_of_measurement="dage",
    ),
    AffaldDKSensorEntityDescription(
        key="plast",
        name="Plast",
        native_unit_of_measurement="dage",
    ),
    AffaldDKSensorEntityDescription(
        key="plastmetal",
        name="Plast & Metal",
        native_unit_of_measurement="dage",
    ),
    AffaldDKSensorEntityDescription(
        key="plastmdkglasmetal",
        name="Plast, Madkarton, Glas & Metal",
        native_unit_of_measurement="dage",
    ),
    AffaldDKSensorEntityDescription(
        key="storskrald",
        name="Storskrald",
        native_unit_of_measurement="dage",
    ),
    AffaldDKSensorEntityDescription(
        key="storskraldogfarligtaffald",
        name="Storskrald & Farligt affald",
        native_unit_of_measurement="dage",
    ),
    AffaldDKSensorEntityDescription(
        key="storskraldogtekstilaffald",
        name="Storskrald & Tekstilaffald",
        native_unit_of_measurement="dage",
    ),
    AffaldDKSensorEntityDescription(
        key="haveaffald",
        name="Haveaffald",
        native_unit_of_measurement="dage",
    ),
    AffaldDKSensorEntityDescription(
        key="pappapirglasmetal",
        name="Pap, Papir, Glas & Metal",
        native_unit_of_measurement="dage",
    ),
    AffaldDKSensorEntityDescription(
        key="papirglasmetalplast",
        name="Papir, Glas, Metal & Plast",
        native_unit_of_measurement="dage",
    ),
    AffaldDKSensorEntityDescription(
        key="plastmetalmdk",
        name="Plast, Metal, Mad & Drikkekartoner",
        native_unit_of_measurement="dage",
    ),
    AffaldDKSensorEntityDescription(
        key="plastmadkarton",
        name="Plast & Mad-Drikkekartoner",
        native_unit_of_measurement="dage",
    ),
    AffaldDKSensorEntityDescription(
        key="pappapir",
        name="Pap & Papir",
        native_unit_of_measurement="dage",
    ),
    AffaldDKSensorEntityDescription(
        key="pappapirtekstil",
        name="Pap, Papir & Tekstil",
        native_unit_of_measurement="dage",
    ),
    AffaldDKSensorEntityDescription(
        key="restaffald",
        name="Restaffald",
        native_unit_of_measurement="dage",
    ),
    AffaldDKSensorEntityDescription(
        key="restplast",
        name="Restaffald & Plast/Madkartoner",
        native_unit_of_measurement="dage",
    ),
    AffaldDKSensorEntityDescription(
        key="tekstil",
        name="Tekstiler",
        native_unit_of_measurement="dage",
    ),
    AffaldDKSensorEntityDescription(
        key="glasplast",
        name="Glas & Plast",
        native_unit_of_measurement="dage",
    ),
    AffaldDKSensorEntityDescription(
        key="plastmetalpapir",
        name="Plast, Metal & Papir",
        native_unit_of_measurement="dage",
    ),
    AffaldDKSensorEntityDescription(
        key="next_pickup",
        name="Næste afhentning",
        native_unit_of_measurement="dage",
    ),
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """AffaldDK sensor platform."""
    coordinator: AffaldDKDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]

    if coordinator.data.pickup_events == {}:
        return

    entities: list[AffaldDKSensor[Any]] = [
        AffaldDKSensor(coordinator, description, config_entry)
        for description in SENSOR_TYPES
        if coordinator.data.pickup_events.get(description.key) is not None
    ]

    async_add_entities(entities, False)


class AffaldDKSensor(CoordinatorEntity[DataUpdateCoordinator], SensorEntity):
    """A AffaldDK sensor."""

    entity_description: AffaldDKSensorEntityDescription
    _attr_attribution = DEFAULT_ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: AffaldDKDataUpdateCoordinator,
        description: AffaldDKSensorEntityDescription,
        config: MappingProxyType[str, Any],
    ) -> None:
        """Initialize a AffaldDK sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._config = config
        self._coordinator = coordinator
        self._pickup_events: PickupType = None
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
            model=f"Kommune: {config.data[CONF_MUNICIPALITY]}",
            model_id=f"ID: {config.data[CONF_ADDRESS_ID]}",
        )
        self._attr_unique_id = f"{config.data[CONF_ADDRESS_ID]} {description.key}"

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return unit of sensor."""

        self._pickup_events = (
            self._coordinator.data.pickup_events.get(self.entity_description.key)
            if self._coordinator.data.pickup_events
            else None
        )
        if self._pickup_events is not None:
            current_time = now().date()
            pickup_time: datetime.date = self._pickup_events.date
            _pickup_days = (pickup_time - current_time).days
            if pickup_time:
                if _pickup_days == 1:
                    return "dag"

            return super().native_unit_of_measurement

    @property
    def native_value(self) -> StateType:
        """Return state of the sensor."""

        self._pickup_events = (
            self._coordinator.data.pickup_events.get(self.entity_description.key)
            if self._coordinator.data.pickup_events
            else None
        )
        if self._pickup_events is not None:
            current_time = now().date()
            pickup_time: datetime.date = self._pickup_events.date
            _pickup_days = (pickup_time - current_time).days
            if pickup_time:
                return _pickup_days

    @property
    def icon(self) -> str | None:
        """Return icon for sensor."""

        return ICON_LIST.get(self.entity_description.key)

    @property
    def extra_state_attributes(self) -> None:
        """Return non standard attributes."""

        self._pickup_events = (
            self._coordinator.data.pickup_events.get(self.entity_description.key)
            if self._coordinator.data.pickup_events
            else None
        )
        _categori = self.entity_description.key
        if _categori == "next_pickup":
            _categori = "genbrug"

        att = {
            ATTR_ENTITY_PICTURE: f'{git_images}{_categori}.svg',
            ATTR_LAST_UPDATE: now().isoformat()
        }

        if self._pickup_events is not None:
            _date: datetime.date = self._pickup_events.date
            _current_date = dt.today().date()
            _state = (_date - _current_date).days
            if _state < 0:
                _state = 0
            _day_number = _date.weekday()
            _day_name = WEEKDAYS_SHORT[_day_number]
            _day_name_long = WEEKDAYS[_day_number]
            if _state == 0:
                _day_text = "I dag"
            elif _state == 1:
                _day_text = "I morgen"
            else:
                _day_text = f"Om {_state} dage"

            att[ATTR_DATE] = _date if _date else None
            att[ATTR_DATE_LONG] = (
                f"{_day_name_long} "
                f"{_date.strftime('d. %d-%m-%Y') if _date else None}"
            )
            att[ATTR_DATE_SHORT] = f"{_day_name} {_date.strftime('d. %d/%m') if _date else None}"
            att[ATTR_DESCRIPTION] = self._pickup_events.description
            att[ATTR_DURATION] = _day_text
            att[ATTR_NAME] = self._pickup_events.friendly_name
        return att

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        self.async_on_remove(
            self._coordinator.async_add_listener(self.async_write_ha_state)
        )
