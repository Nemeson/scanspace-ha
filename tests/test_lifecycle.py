"""End-to-End lifecycle tests for ScanSpace Home Assistant integration."""

import pytest
from homeassistant.config_entries import ConfigEntry
from custom_components.scanspace import async_setup_entry, async_unload_entry, ScanSpaceData
from custom_components.scanspace.const import DOMAIN
from custom_components.scanspace.services import async_setup_services


@pytest.mark.asyncio
async def test_integration_full_lifecycle_mqtt_mode(mock_hass):
    entry = ConfigEntry(entry_id="lifecycle_entry_mqtt", data={"mode": "mqtt", "house_id": "h_test"})

    # Setup
    setup_ok = await async_setup_entry(mock_hass, entry)
    assert setup_ok is True
    assert entry.entry_id in mock_hass.data[DOMAIN]
    assert isinstance(mock_hass.data[DOMAIN][entry.entry_id], ScanSpaceData)
    assert hasattr(mock_hass.data[DOMAIN][entry.entry_id], "mqtt_subscriber")

    # Unload
    unload_ok = await async_unload_entry(mock_hass, entry)
    assert unload_ok is True
    assert entry.entry_id not in mock_hass.data[DOMAIN]


@pytest.mark.asyncio
async def test_integration_full_lifecycle_webhook_mode(mock_hass):
    entry = ConfigEntry(entry_id="lifecycle_entry_wh", data={"mode": "webhook", "house_id": "h_wh"})

    # Setup
    setup_ok = await async_setup_entry(mock_hass, entry)
    assert setup_ok is True
    assert entry.entry_id in mock_hass.data[DOMAIN]

    # Unload
    unload_ok = await async_unload_entry(mock_hass, entry)
    assert unload_ok is True
    assert entry.entry_id not in mock_hass.data[DOMAIN]


@pytest.mark.asyncio
async def test_services_registration(mock_hass):
    await async_setup_services(mock_hass)
    registered_services = [call[0][1] for call in mock_hass.services.async_register.call_args_list]
    assert "reload" in registered_services
    assert "import_file" in registered_services
    assert "export_svg" in registered_services
    assert "assign_entity" in registered_services
