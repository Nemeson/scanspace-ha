"""Sensor entities for ScanSpace rooms."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, LOGGER
from .models import RoomPayload


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up ScanSpace sensor entities."""
    data = hass.data[DOMAIN][entry.entry_id]
    sensors = []

    for room_id, room_data in data.rooms.items():
        sensors.append(ScanSpaceRoomAreaSensor(data, room_id, room_data))
        sensors.append(ScanSpaceRoomFurnitureCountSensor(data, room_id, room_data))

    async_add_entities(sensors)


class ScanSpaceBaseSensor(SensorEntity):
    """Base class for ScanSpace sensors."""

    _attr_should_poll = False

    def __init__(self, data, room_id: str, room_data: dict) -> None:
        self.data = data
        self.room_id = room_id
        self.room_data = room_data
        self._attr_unique_id = f"{data.entry.entry_id}_{room_id}_{self.__class__.__name__}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, room_id)},
            "name": room_data.get("name", room_id),
        }
        self._unsub = None

    async def async_added_to_hass(self) -> None:
        """Subscribe to update dispatcher."""
        @callback
        def _on_update() -> None:
            self.async_schedule_update_ha_state(True)

        self._unsub = async_dispatcher_connect(
            self.hass,
            f"{DOMAIN}_{self.room_id}_updated",
            _on_update,
        )

    async def async_will_remove_from_hass(self) -> None:
        if self._unsub:
            self._unsub()

    def _room(self) -> RoomPayload | None:
        room_data = self.data.rooms.get(self.room_id)
        if not room_data:
            return None
        return RoomPayload.from_dict(room_data)


class ScanSpaceRoomAreaSensor(ScanSpaceBaseSensor):
    """Sensor for room area in m²."""

    _attr_device_class = None
    _attr_native_unit_of_measurement = "m²"
    _attr_suggested_display_precision = 2

    @property
    def name(self) -> str:
        return f"{self.room_data.get('name', self.room_id)} area"

    @property
    def native_value(self) -> float | None:
        room = self._room()
        return room.area_m2() if room else None


class ScanSpaceRoomFurnitureCountSensor(ScanSpaceBaseSensor):
    """Sensor for number of furniture items in room."""

    @property
    def name(self) -> str:
        return f"{self.room_data.get('name', self.room_id)} furniture count"

    @property
    def native_value(self) -> int | None:
        room = self._room()
        return len(room.furniture) if room else None
