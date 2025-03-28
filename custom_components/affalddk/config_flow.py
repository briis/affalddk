"""Config Flow for AffaldDK Integration."""

from __future__ import annotations

import logging
import voluptuous as vol
from typing import Any
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.helpers.event import async_call_later
from homeassistant.helpers.selector import selector

from pyaffalddk import (
    GarbageCollection,
    MUNICIPALITIES_ARRAY,
    AffaldDKAddressInfo,
    AffaldDKNotSupportedError,
    AffaldDKNotValidAddressError,
    AffaldDKNoConnection,
)

from . import async_setup_entry, async_unload_entry
from .const import (
    CONF_ADDRESS_ID,
    CONF_HOUSE_NUMBER,
    CONF_MUNICIPALITY,
    CONF_ROAD_NAME,
    CONF_UPDATE_INTERVAL,
    CONF_ZIPCODE,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class RenowebFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config Flow for AffaldDK."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        """Get the options flow for AffaldDK."""
        return AffaldDKOptionsFlowHandler(config_entry)

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Handle a flow initialized by the user."""

        if user_input is None:
            return await self._show_setup_form(user_input)

        errors = {}
        session = async_create_clientsession(self.hass)

        try:
            renoweb = await self.hass.async_add_executor_job(
                lambda: GarbageCollection(
                    municipality=user_input[CONF_MUNICIPALITY], session=session
                )
            )
            await renoweb.async_init()
            address_info: AffaldDKAddressInfo = await renoweb.get_address_id(
                zipcode=user_input[CONF_ZIPCODE],
                street=user_input[CONF_ROAD_NAME],
                house_number=user_input[CONF_HOUSE_NUMBER],
            )
        except AffaldDKNotSupportedError:
            errors["base"] = "municipality_not_supported"
            return await self._show_setup_form(errors)
        except AffaldDKNotValidAddressError:
            errors["base"] = "location_not_found"
            return await self._show_setup_form(errors)
        except AffaldDKNoConnection:
            errors["base"] = "connection_error"
            return await self._show_setup_form(errors)

        await self.async_set_unique_id(address_info.address_id)
        self._abort_if_unique_id_configured

        return self.async_create_entry(
            title=f"{address_info.vejnavn} {address_info.husnr}",
            data={
                CONF_MUNICIPALITY: address_info.kommunenavn,
                CONF_ROAD_NAME: address_info.vejnavn,
                CONF_HOUSE_NUMBER: address_info.husnr,
                CONF_ADDRESS_ID: address_info.address_id,
            },
        )

    async def _show_setup_form(self, errors=None):
        """Show the setup form to the user."""
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_MUNICIPALITY): selector(
                        {"select": {"options": MUNICIPALITIES_ARRAY}}
                    ),
                    vol.Required(CONF_ZIPCODE): str,
                    vol.Required(CONF_ROAD_NAME): str,
                    vol.Required(CONF_HOUSE_NUMBER): str,
                }
            ),
            errors=errors or {},
        )


class AffaldDKOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle a AffaldDK options flow."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize the options flow."""
        self.config_entry = config_entry

    async def _do_update(
        self,
        *args,
        **kwargs,  # pylint: disable=unused-argument
    ) -> None:
        """Update after settings change."""
        await async_unload_entry(self.hass, self.config_entry)
        await async_setup_entry(self.hass, self.config_entry)

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        """Manage the options."""
        if user_input is not None:
            async_call_later(self.hass, 2, self._do_update)
            return self.async_create_entry(
                title="Options for Affaldshåndtering DK", data=user_input
            )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_UPDATE_INTERVAL,
                        default=self.config_entry.options.get(
                            CONF_UPDATE_INTERVAL, DEFAULT_SCAN_INTERVAL
                        ),
                    ): vol.All(vol.Coerce(int), vol.Range(min=1, max=24)),
                }
            ),
        )
