"""Unit and integration tests for ScanSpace Sensors and Binary Sensors."""

import pytest
from unittest.mock import MagicMock
from homeassistant.config_entries import ConfigEntry
from custom_components.scanspace import ScanSpaceData
from custom_components.scanspace.const import DOMAIN
from custom_components.scanspace.sensor import (
    ScanSpaceRoomAreaSensor,
    ScanSpaceRoomFurnitureCountSensor,
    async_setup_entry as async_setup_sensor_entry,
)
from custom_components.scanspace.binary_sensor import (
    ScanSpaceRoomPresenceSensor,
    async_setup_entry as async_setup_binary_sensor_entry,
)


@pytest.fixture
def populated_space_data(mock_hass, sample_house_dict):
    entry = ConfigEntry(entry_id="entry_sensors_01", data={"mode": "mqtt"})
    data = ScanSpaceData(mock_hass, entry)
    room_dict = sample_house_dict["floors"][0]["rooms"][0]
    data.rooms[room_dict["id"]] = room_dict
    mock_hass.data[DOMAIN] = {entry.entry_id: data}
    return data, room_dict


def test_area_sensor(mock_hass, populated_space_data):
    data, room_dict = populated_space_data
    sensor = ScanSpaceRoomAreaSensor(data, "room_living", room_dict)
    sensor.hass = mock_hass

    assert sensor.name == "Wohnzimmer area"
    assert sensor.native_value == pytest.approx(20.0, rel=1e-3)
    assert sensor._attr_native_unit_of_measurement == "m²"
    assert "room_living" in sensor._attr_device_info["identifiers"].pop()


def test_furniture_count_sensor(mock_hass, populated_space_data):
    data, room_dict = populated_space_data
    sensor = ScanSpaceRoomFurnitureCountSensor(data, "room_living", room_dict)
    sensor.hass = mock_hass

    assert sensor.name == "Wohnzimmer furniture count"
    assert sensor.native_value == 2


def test_presence_binary_sensor(mock_hass, populated_space_data):
    data, room_dict = populated_space_data
    sensor = ScanSpaceRoomPresenceSensor(data, "room_living", room_dict)
    sensor.hass = mock_hass

    assert sensor.name == "Wohnzimmer presence"
    assert sensor.is_on is False


@pytest.mark.asyncio
async def test_sensor_dispatcher_lifecycle(mock_hass, populated_space_data):
    data, room_dict = populated_space_data
    sensor = ScanSpaceRoomAreaSensor(data, "room_living", room_dict)
    sensor.hass = mock_hass

    update_triggered = []
    sensor.async_schedule_update_ha_state = lambda force: update_triggered.append(force)

    await sensor.async_added_to_hass()
    assert f"{DOMAIN}_room_living_updated" in mock_hass._dispatcher_listeners

    # Simulate room update trigger
    mock_hass.send_dispatcher_update(f"{DOMAIN}_room_living_updated")
    assert len(update_triggered) == 1

    # Cleanup
    await sensor.async_will_remove_from_hass()
    mock_hass.send_dispatcher_update(f"{DOMAIN}_room_living_updated")
    assert len(update_triggered) == 1  # No further trigger


@pytest.mark.asyncio
async def test_async_setup_entries(mock_hass, populated_space_data):
    data, _ = populated_space_data
    entry = data.entry

    # Sensor entry setup
    added_sensors = []
    await async_setup_sensor_entry(mock_hass, entry, lambda entities: added_sensors.extend(entities))
    assert len(added_sensors) == 2
    assert any(isinstance(s, ScanSpaceRoomAreaSensor) for s in added_sensors)
    assert any(isinstance(s, ScanSpaceRoomFurnitureCountSensor) for s in added_sensors)

    # Binary sensor entry setup
    added_binary_sensors = []
    await async_setup_binary_sensor_entry(mock_hass, entry, lambda entities: added_binary_sensors.extend(entities))
    assert len(added_binary_sensors) == 1
    assert isinstance(added_binary_sensors[0], ScanSpaceRoomPresenceSensor)
