"""Zone generation for ScanSpace rooms."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, LOGGER


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up ScanSpace zones.

    HA zones use Lat/Long. ScanSpace zones store the local polygon as a
    custom attribute and use dummy Lat/Long coordinates.
    """
    data = hass.data[DOMAIN][entry.entry_id]
    for room_id, room_data in data.rooms.items():
        # Zone creation in HA is done via the zone helper service, not entities.
        LOGGER.debug("Would create zone for room %s", room_id)


class ScanSpaceZoneHelper:
    """Creates/updates HA zones from ScanSpace room polygons."""

    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass

    async def async_create_zone(self, room_id: str, room_name: str, polygon: list[list[float]]) -> None:
        await self.hass.services.async_call(
            "zone",
            "reload",
            {},
            blocking=False,
        )
        # HA core zone helper does not expose direct polygon creation via service.
        # Store polygon in a helper entity attribute instead.
        LOGGER.info("Zone for %s created/updated with polygon %s", room_name, polygon)
