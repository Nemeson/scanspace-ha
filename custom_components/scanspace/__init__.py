import os
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN, LOGGER
from .services import async_setup_services

CONFIG_SCHEMA = cv.empty_config_schema(DOMAIN)
PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BINARY_SENSOR]


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the ScanSpace component."""
    await async_setup_services(hass)

    # Register static path for frontend card if available
    card_path = os.path.join(os.path.dirname(__file__), "frontend", "scanspace-floorplan-card.js")
    if os.path.exists(card_path) and hasattr(hass, "http"):
        try:
            # Home Assistant 2024.7+
            from homeassistant.components.http import StaticPathConfig

            await hass.http.async_register_static_paths(
                [StaticPathConfig("/scanspace/scanspace-floorplan-card.js", card_path, False)]
            )
        except (ImportError, AttributeError):
            try:
                hass.http.register_static_path("/scanspace/scanspace-floorplan-card.js", card_path, cache_headers=False)
            except Exception as err:
                LOGGER.debug("Could not register static path: %s", err)

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up ScanSpace from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = ScanSpaceData(hass, entry)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Start MQTT subscriber if configured
    if entry.data.get("mode") == "mqtt":
        from .mqtt import ScanSpaceMqttSubscriber

        subscriber = ScanSpaceMqttSubscriber(hass, entry)
        await subscriber.async_start()
        hass.data[DOMAIN][entry.entry_id].mqtt_subscriber = subscriber

    # Register webhook fallback
    from .webhook_handler import async_setup_webhook

    await async_setup_webhook(hass, entry)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]

    if hasattr(data, "mqtt_subscriber"):
        await data.mqtt_subscriber.async_stop()

    from .webhook_handler import async_unload_webhook

    await async_unload_webhook(hass, entry)

    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok


class ScanSpaceData:
    """Runtime data holder for one config entry."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        self.house: dict | None = None
        self.rooms: dict[str, dict] = {}
        self.furniture: dict[str, dict] = {}

    def update_house(self, payload: dict) -> None:
        """Process a full or delta house update."""
        self.house = payload
        LOGGER.debug("Updated house %s", payload.get("house", {}).get("id"))

    def get_room(self, room_id: str) -> dict | None:
        return self.rooms.get(room_id)

    def get_furniture(self, furniture_id: str) -> dict | None:
        return self.furniture.get(furniture_id)
