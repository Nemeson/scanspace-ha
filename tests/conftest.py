"""Test configuration and Home Assistant mock harness."""

import sys
from types import ModuleType
from unittest.mock import AsyncMock, MagicMock
from enum import Enum


def create_ha_mocks():
    """Create and inject Home Assistant mock modules into sys.modules."""
    
    # 1. homeassistant
    ha_mod = ModuleType("homeassistant")
    
    # 2. homeassistant.const
    const_mod = ModuleType("homeassistant.const")
    class Platform(str, Enum):
        SENSOR = "sensor"
        BINARY_SENSOR = "binary_sensor"
        ZONE = "zone"
    const_mod.Platform = Platform
    const_mod.CONF_URL = "url"
    
    # 3. homeassistant.core
    core_mod = ModuleType("homeassistant.core")
    def callback(func):
        return func
    core_mod.callback = callback
    
    class HomeAssistant:
        def __init__(self):
            self.data = {}
            self.services = MagicMock()
            self.services.async_register = MagicMock()
            self.services.async_call = AsyncMock()
            self.config_entries = MagicMock()
            self.config_entries.async_forward_entry_setups = AsyncMock(return_value=True)
            self.config_entries.async_unload_platforms = AsyncMock(return_value=True)
            self.config_entries.async_update_entry = MagicMock()
            self.helpers = MagicMock()
            self.helpers.dispatcher = MagicMock()
            self._dispatcher_listeners = {}

        def send_dispatcher_update(self, signal: str, *args, **kwargs):
            for listener in self._dispatcher_listeners.get(signal, []):
                listener(*args, **kwargs)

    core_mod.HomeAssistant = HomeAssistant
    
    class ServiceCall:
        def __init__(self, domain, service, data=None):
            self.domain = domain
            self.service = service
            self.data = data or {}
    core_mod.ServiceCall = ServiceCall

    # 4. homeassistant.config_entries
    config_entries_mod = ModuleType("homeassistant.config_entries")
    class ConfigEntry:
        def __init__(self, entry_id="test_entry_id", domain="scanspace", data=None, title="ScanSpace"):
            self.entry_id = entry_id
            self.domain = domain
            self.data = data or {"house_id": "house_001", "mode": "mqtt"}
            self.title = title
    config_entries_mod.ConfigEntry = ConfigEntry
    
    class ConfigFlowResult(dict):
        pass

    class ConfigFlow:
        def __init_subclass__(cls, domain=None, **kwargs):
            super().__init_subclass__(**kwargs)
            cls.domain = domain

        def async_show_menu(self, step_id, menu_options):
            return {"type": "menu", "step_id": step_id, "menu_options": menu_options}

        def async_show_form(self, step_id, data_schema=None, errors=None):
            return {"type": "form", "step_id": step_id, "errors": errors or {}}

        def async_create_entry(self, title, data):
            return {"type": "create_entry", "title": title, "data": data}

    config_entries_mod.ConfigFlow = ConfigFlow
    config_entries_mod.ConfigFlowResult = ConfigFlowResult

    # 5. homeassistant.components
    components_mod = ModuleType("homeassistant.components")
    
    # 5a. homeassistant.components.mqtt
    mqtt_mod = ModuleType("homeassistant.components.mqtt")
    class ReceiveMessage:
        def __init__(self, topic: str, payload: str, qos: int = 0):
            self.topic = topic
            self.payload = payload
            self.qos = qos
    mqtt_mod.ReceiveMessage = ReceiveMessage
    mqtt_mod.async_subscribe = AsyncMock(return_value=MagicMock())
    
    # 5b. homeassistant.components.webhook
    webhook_mod = ModuleType("homeassistant.components.webhook")
    webhook_mod.async_generate_id = MagicMock(return_value="test_webhook_id_12345")
    webhook_mod.async_register = MagicMock()
    webhook_mod.async_unregister = MagicMock()
    
    class Response:
        def __init__(self, body, status_code=200):
            self.body = body
            self.status_code = status_code
    webhook_mod.Response = Response

    # 5c. homeassistant.components.sensor
    sensor_mod = ModuleType("homeassistant.components.sensor")
    class SensorEntity:
        _attr_should_poll = False
        _attr_device_class = None
        _attr_native_unit_of_measurement = None
        _attr_suggested_display_precision = None
        _attr_unique_id = None
        _attr_device_info = None

        def __init__(self):
            self.hass = None

        def async_schedule_update_ha_state(self, force_refresh=False):
            pass
    sensor_mod.SensorEntity = SensorEntity

    # 5d. homeassistant.components.binary_sensor
    binary_sensor_mod = ModuleType("homeassistant.components.binary_sensor")
    class BinarySensorEntity(SensorEntity):
        pass
    binary_sensor_mod.BinarySensorEntity = BinarySensorEntity

    # 6. homeassistant.helpers
    helpers_mod = ModuleType("homeassistant.helpers")
    
    # 6a. homeassistant.helpers.dispatcher
    dispatcher_mod = ModuleType("homeassistant.helpers.dispatcher")
    def async_dispatcher_connect(hass, signal, target):
        listeners = hass._dispatcher_listeners.setdefault(signal, [])
        listeners.append(target)
        def unsub():
            if target in listeners:
                listeners.remove(target)
        return unsub
    
    def async_dispatcher_send(signal, *args, **kwargs):
        pass

    dispatcher_mod.async_dispatcher_connect = async_dispatcher_connect
    dispatcher_mod.async_dispatcher_send = async_dispatcher_send

    # 6b. homeassistant.helpers.entity
    entity_mod = ModuleType("homeassistant.helpers.entity")
    class EntityDescription:
        pass
    entity_mod.EntityDescription = EntityDescription

    # 6c. homeassistant.helpers.entity_platform
    entity_platform_mod = ModuleType("homeassistant.helpers.entity_platform")
    AddEntitiesCallback = MagicMock()
    entity_platform_mod.AddEntitiesCallback = AddEntitiesCallback

    # 6d. homeassistant.helpers.config_validation
    cv_mod = ModuleType("homeassistant.helpers.config_validation")
    cv_mod.string = str
    cv_mod.boolean = bool

    # 7. voluptuous
    try:
        import voluptuous
    except ImportError:
        vol_mod = ModuleType("voluptuous")
        class Schema:
            def __init__(self, schema):
                self.schema = schema
            def __call__(self, data):
                return data
        def Required(key, default=None):
            return key
        def Optional(key, default=None):
            return key
        vol_mod.Schema = Schema
        vol_mod.Required = Required
        vol_mod.Optional = Optional
        sys.modules["voluptuous"] = vol_mod

    # Register into sys.modules
    sys.modules["homeassistant"] = ha_mod
    sys.modules["homeassistant.const"] = const_mod
    sys.modules["homeassistant.core"] = core_mod
    sys.modules["homeassistant.config_entries"] = config_entries_mod
    sys.modules["homeassistant.components"] = components_mod
    sys.modules["homeassistant.components.mqtt"] = mqtt_mod
    sys.modules["homeassistant.components.webhook"] = webhook_mod
    sys.modules["homeassistant.components.sensor"] = sensor_mod
    sys.modules["homeassistant.components.binary_sensor"] = binary_sensor_mod
    sys.modules["homeassistant.helpers"] = helpers_mod
    sys.modules["homeassistant.helpers.dispatcher"] = dispatcher_mod
    sys.modules["homeassistant.helpers.entity"] = entity_mod
    sys.modules["homeassistant.helpers.entity_platform"] = entity_platform_mod
    sys.modules["homeassistant.helpers.config_validation"] = cv_mod


create_ha_mocks()

import pytest


@pytest.fixture
def mock_hass():
    """Fixture providing a mock HomeAssistant instance."""
    from homeassistant.core import HomeAssistant
    hass = HomeAssistant()
    return hass


@pytest.fixture
def sample_house_dict():
    """Fixture providing a realistic ScanSpace House JSON structure."""
    return {
        "id": "house_alpha_01",
        "name": "Musterhaus",
        "floors": [
            {
                "id": "floor_ground",
                "name": "Erdgeschoss",
                "elevation": 0.0,
                "rooms": [
                    {
                        "id": "room_living",
                        "name": "Wohnzimmer",
                        "floor_id": "floor_ground",
                        "ceiling_height": 2.6,
                        "floorOutline": [
                            [0.0, 0.0],
                            [5.0, 0.0],
                            [5.0, 4.0],
                            [0.0, 4.0]
                        ],
                        "walls": [
                            {"id": "w1", "start": [0.0, 0.0, 0.0], "end": [5.0, 0.0, 0.0], "thickness": 0.2, "height": 2.6},
                            {"id": "w2", "start": [5.0, 0.0, 0.0], "end": [5.0, 4.0, 0.0], "thickness": 0.2, "height": 2.6},
                            {"id": "w3", "start": [5.0, 4.0, 0.0], "end": [0.0, 4.0, 0.0], "thickness": 0.2, "height": 2.6},
                            {"id": "w4", "start": [0.0, 4.0, 0.0], "end": [0.0, 0.0, 0.0], "thickness": 0.2, "height": 2.6}
                        ],
                        "doors": [
                            {"id": "d1", "wall_id": "w1", "position": 2.0, "width": 0.9}
                        ],
                        "windows": [
                            {"id": "win1", "wall_id": "w2", "position": 1.5, "width": 1.2, "sill_height": 0.9, "height": 1.3}
                        ],
                        "furniture": [
                            {
                                "id": "furn_sofa",
                                "type": "sofa",
                                "position": [1.5, 0.4, 2.0],
                                "rotation": [0.0, 0.0, 0.0, 1.0],
                                "dimensions": [2.2, 0.85, 0.9],
                                "entity_id": "light.living_room_corner"
                            },
                            {
                                "id": "furn_table",
                                "type": "dining_table",
                                "position": [3.0, 0.0, 2.0],
                                "rotation": [0.0, 0.707, 0.0, 0.707],
                                "dimensions": [1.6, 0.76, 0.9]
                            }
                        ],
                        "scan_state": "completed"
                    }
                ]
            }
        ]
    }
