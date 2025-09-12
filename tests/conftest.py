# tests/conftest.py
import sys
import types
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# Mock homeassistant if not installed
if "homeassistant" not in sys.modules:
    # Create fake "homeassistant" module
    homeassistant = types.ModuleType("homeassistant")
    Platform = types.SimpleNamespace(SENSOR="sensor", CALENDAR="calendar")
    homeassistant.config_entries = types.SimpleNamespace(ConfigEntry=object, ConfigEntryState=object)
    homeassistant.components = types.SimpleNamespace(http=types.SimpleNamespace(StaticPathConfig=object))
    homeassistant.const = types.SimpleNamespace(Platform=Platform)
    homeassistant.core = types.SimpleNamespace(HomeAssistant=object)
    homeassistant.exceptions = types.SimpleNamespace(HomeAssistantError=Exception, ConfigEntryNotReady=Exception)
    homeassistant.helpers = types.SimpleNamespace(
        aiohttp_client=types.SimpleNamespace(async_get_clientsession=lambda *a, **kw: None),
        update_coordinator=types.SimpleNamespace(DataUpdateCoordinator=object, UpdateFailed=Exception),
    )

    sys.modules["homeassistant"] = homeassistant
    sys.modules["homeassistant.config_entries"] = homeassistant.config_entries
    sys.modules["homeassistant.components.http"] = homeassistant.components.http
    sys.modules["homeassistant.const"] = homeassistant.const
    sys.modules["homeassistant.core"] = homeassistant.core
    sys.modules["homeassistant.exceptions"] = homeassistant.exceptions
    sys.modules["homeassistant.helpers"] = homeassistant.helpers
    sys.modules["homeassistant.helpers.aiohttp_client"] = homeassistant.helpers.aiohttp_client
    sys.modules["homeassistant.helpers.update_coordinator"] = homeassistant.helpers.update_coordinator
