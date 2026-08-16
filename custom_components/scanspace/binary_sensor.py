"""Binary sensor entities for ScanSpace rooms."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .sensor import ScanSpaceBaseSensor


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up ScanSpace binary sensor entities."""
    data = hass.data[DOMAIN][entry.entry_id]
    entities = [
        ScanSpaceRoomPresenceSensor(data, room_id, room_data)
        for room_id, room_data in data.rooms.items()
    ]
    async_add_entities(entities)


class ScanSpaceRoomPresenceSensor(ScanSpaceBaseSensor, BinarySensorEntity):
    """Binary sensor indicating presence in a ScanSpace room.

    Bound to a motion sensor that the user assigns to the room.
    """

    @property
    def name(self) -> str:
        return f"{self.room_data.get('name', self.room_id)} presence"

    @property
    def is_on(self) -> bool | None:
        # Placeholder: real implementation reads assigned motion entity state
        return False
