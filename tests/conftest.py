# tests/conftest.py
import sys
import types
import pathlib
import datetime
from dataclasses import dataclass

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# Mock homeassistant if not installed
if "homeassistant" not in sys.modules:
    homeassistant = types.ModuleType("homeassistant")
    homeassistant.__path__ = []

    Platform = types.SimpleNamespace(SENSOR="sensor", CALENDAR="calendar")

    homeassistant.config_entries = types.SimpleNamespace(ConfigEntry=object, ConfigEntryState=object)
    homeassistant.core = types.SimpleNamespace(HomeAssistant=object)
    homeassistant.exceptions = types.SimpleNamespace(HomeAssistantError=Exception, ConfigEntryNotReady=Exception)
    homeassistant.const = types.SimpleNamespace(
        Platform=Platform,
        ATTR_DATE="date",
        ATTR_NAME="name",
        ATTR_ENTITY_PICTURE="entity_picture",
        UnitOfTime=types.SimpleNamespace(DAYS="d"),
        STATE_UNKNOWN="unknown",
    )

    homeassistant.util = types.ModuleType("homeassistant.util")
    homeassistant.util.__path__ = []
    homeassistant.util.dt = types.ModuleType("homeassistant.util.dt")
    # Call at runtime so freezegun's patch of datetime.datetime.now() applies.
    homeassistant.util.dt.now = lambda: datetime.datetime.now()
    # Fixed tz for calendar event start/end comparisons.
    homeassistant.util.dt.get_default_time_zone = lambda: datetime.timezone.utc

    class SensorEntity:
        """Fake SensorEntity base with entity_description."""

        entity_description = None

        @property
        def name(self):
            return getattr(self.entity_description, "name", None)

    class CoordinatorEntity:
        """Fake CoordinatorEntity base (no Home Assistant machinery)."""

        def __class_getitem__(cls, _item):
            return cls

        _attr_attribution = None
        _attr_has_entity_name = False
        _attr_native_unit_of_measurement = None

        def __init__(self, coordinator):
            self.coordinator = coordinator
            self.hass = None
            self._attr_device_info = None
            self._attr_unique_id = None
            self.async_on_remove = lambda _cb: None

        @property
        def unique_id(self):
            return self._attr_unique_id

    class DeviceInfo:
        """Stub DeviceInfo accepting kwargs."""

        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

    # homeassistant.components subpackage (real modules so that
    # `from homeassistant.components.sensor import X` resolves).
    components = types.ModuleType("homeassistant.components")
    components.__path__ = []

    http = types.ModuleType("homeassistant.components.http")
    http.StaticPathConfig = object
    components.http = http

    @dataclass(frozen=True)
    class SensorEntityDescription:
        """Minimal dataclass so entity descriptions support key/name kwargs."""

        key: str | None = None
        name: str | None = None

    sensor_mod = types.ModuleType("homeassistant.components.sensor")
    sensor_mod.SensorEntity = SensorEntity
    sensor_mod.SensorEntityDescription = SensorEntityDescription
    components.sensor = sensor_mod

    calendar_mod = types.ModuleType("homeassistant.components.calendar")

    class CalendarEntity:
        """Fake CalendarEntity base."""

        _attr_attribution = None
        _attr_has_entity_name = False
        _attr_name = None

    class CalendarEvent:
        """Fake CalendarEvent carrying summary/description/start/end."""

        def __init__(self, summary=None, description=None, start=None, end=None):
            self.summary = summary
            self.description = description
            self.start = start
            self.end = end

    calendar_mod.CalendarEntity = CalendarEntity
    calendar_mod.CalendarEvent = CalendarEvent
    components.calendar = calendar_mod

    homeassistant.components = components

    # homeassistant.helpers subpackage (real modules).
    helpers = types.ModuleType("homeassistant.helpers")
    helpers.__path__ = []

    aiohttp_client = types.ModuleType("homeassistant.helpers.aiohttp_client")
    aiohttp_client.async_get_clientsession = lambda *a, **kw: None
    helpers.aiohttp_client = aiohttp_client

    update_coordinator = types.ModuleType("homeassistant.helpers.update_coordinator")
    update_coordinator.DataUpdateCoordinator = object
    update_coordinator.UpdateFailed = Exception
    update_coordinator.CoordinatorEntity = CoordinatorEntity
    helpers.update_coordinator = update_coordinator

    entity_platform = types.ModuleType("homeassistant.helpers.entity_platform")
    entity_platform.AddEntitiesCallback = object
    helpers.entity_platform = entity_platform

    entity_registry = types.ModuleType("homeassistant.helpers.entity_registry")
    entity_registry.async_get = lambda *a, **kw: types.SimpleNamespace(
        async_get_entity_id=lambda *a, **kw: None
    )
    helpers.entity_registry = entity_registry

    device_registry = types.ModuleType("homeassistant.helpers.device_registry")
    device_registry.DeviceEntryType = types.SimpleNamespace(SERVICE="service")
    device_registry.DeviceInfo = DeviceInfo
    helpers.device_registry = device_registry

    typing_mod = types.ModuleType("homeassistant.helpers.typing")
    typing_mod.StateType = object
    helpers.typing = typing_mod

    entity = types.ModuleType("homeassistant.helpers.entity")
    entity.SensorEntity = SensorEntity
    helpers.entity = entity

    homeassistant.helpers = helpers

    sys.modules["homeassistant"] = homeassistant
    sys.modules["homeassistant.config_entries"] = homeassistant.config_entries
    sys.modules["homeassistant.const"] = homeassistant.const
    sys.modules["homeassistant.core"] = homeassistant.core
    sys.modules["homeassistant.exceptions"] = homeassistant.exceptions
    sys.modules["homeassistant.util"] = homeassistant.util
    sys.modules["homeassistant.util.dt"] = homeassistant.util.dt
    sys.modules["homeassistant.components"] = components
    sys.modules["homeassistant.components.http"] = http
    sys.modules["homeassistant.components.sensor"] = sensor_mod
    sys.modules["homeassistant.components.calendar"] = calendar_mod
    sys.modules["homeassistant.helpers"] = helpers
    sys.modules["homeassistant.helpers.aiohttp_client"] = aiohttp_client
    sys.modules["homeassistant.helpers.update_coordinator"] = update_coordinator
    sys.modules["homeassistant.helpers.entity_platform"] = entity_platform
    sys.modules["homeassistant.helpers.entity_registry"] = entity_registry
    sys.modules["homeassistant.helpers.device_registry"] = device_registry
    sys.modules["homeassistant.helpers.typing"] = typing_mod
    sys.modules["homeassistant.helpers.entity"] = entity
