"""Support for the Affald DK Garbage Collection Service."""

from __future__ import annotations

from datetime import timedelta
import logging
from pathlib import Path
from typing import Self

from .pyaffalddk.api import GarbageCollection
from .pyaffalddk.data import PickupEvents
from .pyaffalddk.interface import (
    AffaldDKNotSupportedError,
    AffaldDKNotValidAddressError,
    AffaldDKNoConnection,
)

from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry, ConfigEntryState
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError, ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .const import (
    CONF_ADDRESS_ID,
    CONF_MUNICIPALITY,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

PLATFORMS = [Platform.SENSOR, Platform.CALENDAR]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up AffaldDK from a config entry."""

    coordinator = AffaldDKDataUpdateCoordinator(hass, config_entry)
    if ConfigEntryState == ConfigEntryState.SETUP_IN_PROGRESS:
        await coordinator.async_config_entry_first_refresh()
    else:
        await coordinator.async_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][config_entry.entry_id] = coordinator
    config_entry.async_on_unload(config_entry.add_update_listener(async_update_entry))

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)
    if not hass.data[DOMAIN].get("static_registered"):
        static_dir = (Path(__file__).parent / "images").resolve()
        if not static_dir.exists():
            _LOGGER.warning(f"AffaldDK static image dir not found: {static_dir}")
        else:
            cache_headers=True
            await hass.http.async_register_static_paths([
                StaticPathConfig("/affalddk/img", str(static_dir), cache_headers)
            ])
            hass.data[DOMAIN]["static_registered"] = True
    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Unload a config entry."""

    unload_ok = await hass.config_entries.async_unload_platforms(
        config_entry, PLATFORMS
    )

    hass.data[DOMAIN].pop(config_entry.entry_id)

    return unload_ok


async def async_update_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    """Reload AffaldDK component when options changed."""
    await hass.config_entries.async_reload(config_entry.entry_id)


class CannotConnect(HomeAssistantError):
    """Unable to connect to the web site."""


class AffaldDKDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching AffaldDK data."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize global AffaldDK data updater."""
        self.affalddk = AffaldDKData(hass, config_entry)
        self.affalddk.initialize_data()
        self.hass = hass
        self.config_entry = config_entry

        update_interval = timedelta(hours=DEFAULT_SCAN_INTERVAL)
        # update_interval = timedelta(
        #     hours=self.config_entry.options.get(
        #         CONF_UPDATE_INTERVAL, DEFAULT_SCAN_INTERVAL
        #     )
        # )

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=update_interval,
            config_entry=config_entry,
        )

    async def _async_update_data(self) -> AffaldDKData:
        """Fetch data from AffaldDK."""
        try:
            return await self.affalddk.fetch_data()
        except Exception as err:
            raise UpdateFailed(f"Update failed: {err}") from err


class AffaldDKData:
    """Keep data for AffaldDK."""

    def __init__(self, hass: HomeAssistant, config: ConfigEntry) -> None:
        """Initialise affalddk entity data."""

        self.hass = hass
        self._config = config.data
        self._affalddk_data: GarbageCollection
        self.pickup_events: PickupEvents

    def initialize_data(self) -> bool:
        """Establish connection to API."""
        self._affalddk_data = GarbageCollection(
            municipality=self._config[CONF_MUNICIPALITY],
            session=async_get_clientsession(self.hass),
        )

        return True

    async def fetch_data(self) -> Self:
        """Fetch data from API."""

        try:
            self.pickup_events = await self._affalddk_data.get_pickup_data(
                address_id=self._config[CONF_ADDRESS_ID]
            )
        except AffaldDKNotSupportedError as err:
            _LOGGER.debug(err)
            raise CannotConnect() from err
        except AffaldDKNotValidAddressError as err:
            _LOGGER.debug(err)
            raise CannotConnect() from err
        except AffaldDKNoConnection as notreadyerror:
            _LOGGER.debug(notreadyerror)
            raise ConfigEntryNotReady from notreadyerror
        except Exception as notreadyerror:
            _LOGGER.debug(notreadyerror)
            raise ConfigEntryNotReady from notreadyerror

        if not self.pickup_events:
            raise CannotConnect()

        return self
