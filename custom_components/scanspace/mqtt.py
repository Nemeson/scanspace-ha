"""MQTT subscriber for ScanSpace integration."""

from __future__ import annotations

import json
from typing import Any

from homeassistant.components import mqtt
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, MQTT_TOPIC_PREFIX, LOGGER
from .models import HousePayload, RoomPayload


class ScanSpaceMqttSubscriber:
    """Subscribes to ScanSpace MQTT topics and dispatches updates."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        self._unsubscribe: Any = None

    async def async_start(self) -> None:
        """Subscribe to scanspace/# MQTT topics."""
        topic = f"{MQTT_TOPIC_PREFIX}/#"
        LOGGER.debug("Subscribing to %s", topic)
        self._unsubscribe = await mqtt.async_subscribe(
            self.hass,
            topic,
            self._on_message,
            qos=1,
        )

    async def async_stop(self) -> None:
        """Unsubscribe from MQTT topics."""
        if self._unsubscribe:
            self._unsubscribe()
            self._unsubscribe = None

    @callback
    def _on_message(self, msg: mqtt.ReceiveMessage) -> None:
        """Handle incoming MQTT message."""
        topic: str = msg.topic
        payload = msg.payload
        LOGGER.debug("MQTT message on %s", topic)

        try:
            data = json.loads(payload)
        except json.JSONDecodeError as err:
            LOGGER.warning("Invalid JSON on %s: %s", topic, err)
            return

        if "/room/" in topic and not topic.endswith("/delta"):
            self._handle_room_update(topic, data)
        elif topic.endswith("/delta"):
            self._handle_delta(topic, data)
        elif "/manifest" in topic:
            self._handle_manifest(data)

    def _handle_manifest(self, data: dict[str, Any]) -> None:
        """Process house manifest update."""
        scan_space_data = self.hass.data[DOMAIN][self.entry.entry_id]
        house_id = data.get("house", {}).get("id") if "house" in data else data.get("id")
        if house_id:
            LOGGER.debug("Manifest update for house %s", house_id)

    def _handle_room_update(self, topic: str, data: dict[str, Any]) -> None:
        """Process full room update."""
        room_id = topic.split("/")[-1]
        scan_space_data = self.hass.data[DOMAIN][self.entry.entry_id]
        room = RoomPayload.from_dict(data)
        scan_space_data.rooms[room_id] = data
        LOGGER.debug("Room update: %s", room_id)
        self._trigger_state_updates(room_id)

    def _handle_delta(self, topic: str, data: dict[str, Any]) -> None:
        """Process incremental delta update."""
        room_id = topic.split("/")[-2]
        scan_space_data = self.hass.data[DOMAIN][self.entry.entry_id]
        room_data = scan_space_data.rooms.get(room_id, {})
        furniture = room_data.setdefault("furniture", [])

        furniture_id = data.get("furniture_id")
        if furniture_id:
            # Update existing furniture or append
            for item in furniture:
                if item.get("id") == furniture_id:
                    item.update(data)
                    break
            else:
                furniture.append(data)

        LOGGER.debug("Delta update for room %s furniture %s", room_id, furniture_id)
        self._trigger_state_updates(room_id)

    def _trigger_state_updates(self, room_id: str) -> None:
        """Signal entity coordinators that data changed."""
        # HA entity state will be refreshed via DataUpdateCoordinator
        async_dispatcher_send = self.hass.helpers.dispatcher.async_dispatcher_send
        async_dispatcher_send(f"{DOMAIN}_{room_id}_updated")
