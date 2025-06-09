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
import aiohttp

from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.helpers.selector import selector

from pyaffalddk import (
    GarbageCollection,
    AffaldDKNotSupportedError,
    AffaldDKNotValidAddressError,
    AffaldDKNoConnection,
)
from pyaffalddk.municipalities import MUNICIPALITIES_LIST

from .const import (
    CONF_ADDRESS,
    CONF_ADDRESS_ID,
    CONF_CALENDAR_END_TIME,
    CONF_CALENDAR_START_TIME,
    CONF_HOUSE_NUMBER,
    CONF_MUNICIPALITY,
    CONF_ROAD_NAME,
    CONF_ZIPCODE,
    DEFAULT_END_TIME,
    DEFAULT_START_TIME,
    DOMAIN,
)

GOBACK = '<- Tilbage'
_LOGGER = logging.getLogger(__name__)


async def municipalityFromCoor(lon, lat):
    """Municipality from longitude and latitude."""

    url = f"https://api.dataforsyningen.dk/kommuner/reverse?x={lon}&y={lat}"
    async with aiohttp.ClientSession() as session, session.get(url) as response:
        if response.status == 200:
            js = await response.json()
            return js.get("navn", '').capitalize()


class AffaldDKFlowHandler(ConfigFlow, domain=DOMAIN):
    """Config Flow for AffaldDK."""

    VERSION = 1

    @callback
    async def _show_setup_form(self, user_input={}, errors={}) -> ConfigFlowResult:
        """Show the setup form to the user."""

        options = list(MUNICIPALITIES_LIST.keys())

        municipality = user_input.get(CONF_MUNICIPALITY)
        if not municipality:
            server_municipality = await municipalityFromCoor(
                self.hass.config.longitude,
                self.hass.config.latitude,
            )
            if server_municipality in options:
                municipality = server_municipality

        schema = vol.Schema({
            vol.Required(CONF_MUNICIPALITY, default=municipality): selector(
                {"select": {"options": options}}
            ),
            vol.Required(CONF_ZIPCODE, default=user_input.get(CONF_ZIPCODE, '')): str,
            vol.Required(CONF_ROAD_NAME, default=user_input.get(CONF_ROAD_NAME, '')): str,
            vol.Optional(CONF_HOUSE_NUMBER, default=user_input.get(CONF_HOUSE_NUMBER, '')): str,
        })
        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors or {},
        )

    async def _create_entry(self, address_name) -> ConfigFlowResult:
        address_info = await self.affalddkapi.get_address(address_name)
        await self.async_set_unique_id(address_info.uid)
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title=address_info.address,
            data={
                CONF_MUNICIPALITY: address_info.kommunenavn,
                CONF_ADDRESS: address_info.address.capitalize(),
                CONF_ADDRESS_ID: address_info.address_id,
            },
        )

    async def async_step_user(self, user_input=None, from_select=False):
        """Handle a flow initialized by the user."""
        errors: dict[str, str] = {}

        if not user_input:
            return await self._show_setup_form()
        if from_select:
            return await self._show_setup_form(user_input=user_input)

        municipality = user_input[CONF_MUNICIPALITY]
        zipcode = user_input[CONF_ZIPCODE].strip()
        street = user_input[CONF_ROAD_NAME].strip()
        house_number = user_input.get(CONF_HOUSE_NUMBER, '').strip()
        self.user_input = user_input
        try:
            session = async_create_clientsession(self.hass)
            self.affalddkapi = await self.hass.async_add_executor_job(
                lambda: GarbageCollection(
                    municipality=municipality, session=session
                )
            )
            await self.affalddkapi.async_init()
            address_list = await self.affalddkapi.get_address_list(
                zipcode=zipcode, street=street, house_number=house_number,
            )
            if len(address_list) == 1:
                return await self._create_entry(address_list[0])
            elif len(address_list) > 1:
                return await self.async_step_select_address(options=[GOBACK] + address_list)
            else:
                errors["base"] = "location_not_found"

        except AffaldDKNotSupportedError:
            errors["base"] = "municipality_not_supported"
        except AffaldDKNotValidAddressError:
            errors["base"] = "location_not_found"
        except AffaldDKNoConnection:
            errors["base"] = "connection_error"

        if errors:
            return await self._show_setup_form(user_input=user_input, errors=errors)

    async def async_step_select_address(self, user_input=None, options=[]):
        """Handle a flow initialized by the select address."""
        if user_input is not None:
            if user_input['address'] == GOBACK:
                return await self.async_step_user(user_input=self.user_input, from_select=True)
            return await self._create_entry(user_input['address'])

        return self.async_show_form(
            step_id="select_address",
            description_placeholders={k: v.capitalize() for k, v in self.user_input.items()},
            data_schema=vol.Schema({
                vol.Required(CONF_ADDRESS): selector(
                    {"select": {"options": options}}
                )
            })
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
