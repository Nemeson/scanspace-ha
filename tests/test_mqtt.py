"""Unit and E2E tests for MQTT subscriber in ScanSpace integration."""

import json
import pytest
from unittest.mock import MagicMock
from homeassistant.components.mqtt import ReceiveMessage
from homeassistant.config_entries import ConfigEntry
from custom_components.scanspace import ScanSpaceData
from custom_components.scanspace.const import DOMAIN
from custom_components.scanspace.mqtt import ScanSpaceMqttSubscriber


@pytest.mark.asyncio
async def test_mqtt_subscriber_start_and_stop(mock_hass):
    entry = ConfigEntry(entry_id="test_entry_1", data={"mode": "mqtt"})
    mock_hass.data[DOMAIN] = {entry.entry_id: ScanSpaceData(mock_hass, entry)}

    subscriber = ScanSpaceMqttSubscriber(mock_hass, entry)
    await subscriber.async_start()
    assert subscriber._unsubscribe is not None

    await subscriber.async_stop()
    assert subscriber._unsubscribe is None


def test_mqtt_room_update_and_dispatcher(mock_hass):
    entry = ConfigEntry(entry_id="test_entry_1", data={"mode": "mqtt"})
    space_data = ScanSpaceData(mock_hass, entry)
    mock_hass.data[DOMAIN] = {entry.entry_id: space_data}

    # Setup dispatcher spy
    dispatcher_called = []
    mock_hass.helpers.dispatcher.async_dispatcher_send = lambda signal: dispatcher_called.append(signal)

    subscriber = ScanSpaceMqttSubscriber(mock_hass, entry)

    room_payload = {
        "id": "room_kitchen",
        "name": "Küche",
        "floor_id": "floor_1",
        "floorOutline": [[0.0, 0.0], [3.0, 0.0], [3.0, 3.0], [0.0, 3.0]],
        "furniture": []
    }

    msg = ReceiveMessage(
        topic="scanspace/house/house_01/room/room_kitchen",
        payload=json.dumps(room_payload),
    )

    subscriber._on_message(msg)

    assert "room_kitchen" in space_data.rooms
    assert space_data.rooms["room_kitchen"]["name"] == "Küche"
    assert f"{DOMAIN}_room_kitchen_updated" in dispatcher_called


def test_mqtt_delta_update(mock_hass):
    entry = ConfigEntry(entry_id="test_entry_1", data={"mode": "mqtt"})
    space_data = ScanSpaceData(mock_hass, entry)
    mock_hass.data[DOMAIN] = {entry.entry_id: space_data}

    # Pre-populate room
    space_data.rooms["room_kitchen"] = {
        "id": "room_kitchen",
        "name": "Küche",
        "furniture": [
            {"id": "furn_stove", "type": "stove", "position": [1.0, 0.0, 1.0]}
        ]
    }

    dispatcher_called = []
    mock_hass.helpers.dispatcher.async_dispatcher_send = lambda signal: dispatcher_called.append(signal)

    subscriber = ScanSpaceMqttSubscriber(mock_hass, entry)

    # 1. Update existing furniture
    delta_update_msg = ReceiveMessage(
        topic="scanspace/house/house_01/room/room_kitchen/delta",
        payload=json.dumps({
            "furniture_id": "furn_stove",
            "position": [1.2, 0.0, 1.0]
        }),
    )
    subscriber._on_message(delta_update_msg)

    room = space_data.rooms["room_kitchen"]
    assert room["furniture"][0]["position"] == [1.2, 0.0, 1.0]
    assert f"{DOMAIN}_room_kitchen_updated" in dispatcher_called

    # 2. Add new furniture via delta
    delta_new_msg = ReceiveMessage(
        topic="scanspace/house/house_01/room/room_kitchen/delta",
        payload=json.dumps({
            "furniture_id": "furn_fridge",
            "id": "furn_fridge",
            "type": "refrigerator",
            "position": [2.5, 0.0, 2.0]
        }),
    )
    subscriber._on_message(delta_new_msg)
    assert len(room["furniture"]) == 2


def test_mqtt_invalid_json(mock_hass):
    entry = ConfigEntry(entry_id="test_entry_1", data={"mode": "mqtt"})
    space_data = ScanSpaceData(mock_hass, entry)
    mock_hass.data[DOMAIN] = {entry.entry_id: space_data}

    subscriber = ScanSpaceMqttSubscriber(mock_hass, entry)
    msg = ReceiveMessage(
        topic="scanspace/house/house_01/room/room_kitchen",
        payload="INVALID_NON_JSON_DATA",
    )
    # Should not raise exception
    subscriber._on_message(msg)
    assert "room_kitchen" not in space_data.rooms
