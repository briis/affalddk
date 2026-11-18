"""Tests for async_setup_entry."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from freezegun import freeze_time
from homeassistant.exceptions import ConfigEntryNotReady

import custom_components.affalddk as affalddk
from custom_components.affalddk.const import CONF_ADDRESS_ID, CONF_MUNICIPALITY

# affald.kk.dk answers HTTP 200 with this alert and no dates when its backend is unavailable
KK_UNAVAILABLE_HTML = """
<div data-drupal-messages><div role="alert">
  Tjenesten er ikke tilgængelig lige nu. Prøv venligst igen senere.
</div></div>
"""

KK_CALENDAR_HTML = """
<div class="calendar-waste-date">
  <div class="date">Tirsdag, 24. november 2026
    <span>Restaffald</span>
  </div>
</div>
"""


class FakeResponse:
    def __init__(self, text):
        self.status = 200
        self._text = text

    async def text(self):
        return self._text

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False


def _setup_args(monkeypatch, page_html):
    """Return (hass, entry) wired to a København session that serves page_html."""
    session = SimpleNamespace(request=lambda *a, **kw: FakeResponse(page_html))
    monkeypatch.setattr(affalddk, "async_get_clientsession", lambda hass: session)

    hass = SimpleNamespace(
        data={},
        config_entries=SimpleNamespace(
            async_forward_entry_setups=AsyncMock(),
            async_reload=AsyncMock(),
        ),
        http=SimpleNamespace(async_register_static_paths=AsyncMock()),
    )
    entry = SimpleNamespace(
        entry_id="entry1",
        data={CONF_MUNICIPALITY: "København", CONF_ADDRESS_ID: "abc"},
        options={},
        async_on_unload=MagicMock(),
        add_update_listener=MagicMock(),
    )
    return hass, entry


@pytest.mark.asyncio
async def test_setup_retries_when_first_fetch_has_no_events(monkeypatch):
    """A failed first fetch must make setup retry, not load the entry with no data."""
    hass, entry = _setup_args(monkeypatch, KK_UNAVAILABLE_HTML)

    with pytest.raises(ConfigEntryNotReady):
        await affalddk.async_setup_entry(hass, entry)

    hass.config_entries.async_forward_entry_setups.assert_not_called()


@pytest.mark.asyncio
@freeze_time("2026-11-18")
async def test_setup_forwards_platforms_when_first_fetch_succeeds(monkeypatch):
    hass, entry = _setup_args(monkeypatch, KK_CALENDAR_HTML)

    assert await affalddk.async_setup_entry(hass, entry) is True

    hass.config_entries.async_forward_entry_setups.assert_awaited_once()
    assert hass.data[affalddk.DOMAIN][entry.entry_id].data.pickup_events
