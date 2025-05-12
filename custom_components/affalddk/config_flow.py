"""Config Flow for AffaldDK Integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
import logging

from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.helpers.selector import selector

from pyaffalddk import (
    GarbageCollection,
    AffaldDKAddressInfo,
    AffaldDKNotSupportedError,
    AffaldDKNotValidAddressError,
    AffaldDKNoConnection,
)
from pyaffalddk.municipalities import MUNICIPALITIES_LIST

from .const import (
    CONF_ADDRESS_ID,
    CONF_CALENDAR_END_TIME,
    CONF_CALENDAR_START_TIME,
    CONF_HOUSE_NUMBER,
    CONF_MUNICIPALITY,
    CONF_ROAD_NAME,
    CONF_UPDATE_INTERVAL,
    CONF_ZIPCODE,
    DEFAULT_END_TIME,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_START_TIME,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)



class AffaldDKFlowHandler(ConfigFlow, domain=DOMAIN):
    """Config Flow for AffaldDK."""

    VERSION = 1

    @callback
    def _show_setup_form(
            self,
            user_input: dict[str, Any] | None = None,
            errors: dict[str, str] | None = None,
    ) -> ConfigFlowResult:
        """Show the setup form to the user."""

        if user_input is None:
            user_input = {}

        options = [key for key, val in MUNICIPALITIES_LIST.items() if val[1] in ['2', '3', '4', '5', '6']]
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_MUNICIPALITY): selector(
                        {"select": {"options": options}}
                    ),
                    vol.Required(CONF_ZIPCODE): str,
                    vol.Required(CONF_ROAD_NAME): str,
                    vol.Required(CONF_HOUSE_NUMBER): str,
                }
            ),
            errors=errors or {},
        )

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Handle a flow initialized by the user."""
        errors: dict[str, str] = {}

        if user_input is None:
            return self._show_setup_form(user_input, errors)

        municipality = user_input[CONF_MUNICIPALITY]
        zipcode = user_input[CONF_ZIPCODE]
        street = user_input[CONF_ROAD_NAME]
        house_number = user_input[CONF_HOUSE_NUMBER]

        try:
            session = async_create_clientsession(self.hass)
            affalddkapi = await self.hass.async_add_executor_job(
                lambda: GarbageCollection(
                    municipality=municipality, session=session
                )
            )
            await affalddkapi.async_init()
            address_info: AffaldDKAddressInfo = await affalddkapi.get_address_id(
                zipcode=zipcode,
                street=street,
                house_number=house_number,
            )
        except AffaldDKNotSupportedError:
            errors["base"] = "municipality_not_supported"
            return self._show_setup_form(errors)
        except AffaldDKNotValidAddressError:
            errors["base"] = "location_not_found"
            return self._show_setup_form(errors)
        except AffaldDKNoConnection:
            errors["base"] = "connection_error"
            return self._show_setup_form(errors)

        await self.async_set_unique_id(address_info.uid)
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

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> OptionsFlow:
        """Get the options flow for this handler."""
        return OptionsFlowHandler()

class OptionsFlowHandler(OptionsFlow):
    """Handle Options."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

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
                    vol.Optional(
                        CONF_CALENDAR_START_TIME,
                        default=self.config_entry.options.get(
                            CONF_CALENDAR_START_TIME, DEFAULT_START_TIME
                        ),
                    ): vol.All(vol.Coerce(int), vol.Range(min=5, max=12)),
                    vol.Optional(
                        CONF_CALENDAR_END_TIME,
                        default=self.config_entry.options.get(
                            CONF_CALENDAR_END_TIME, DEFAULT_END_TIME
                        ),
                    ): vol.All(vol.Coerce(int), vol.Range(min=12, max=20)),
                }
            ),
        )
