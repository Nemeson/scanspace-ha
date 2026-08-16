"""Unit and E2E tests for Webhook handling in ScanSpace integration."""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock
from homeassistant.config_entries import ConfigEntry
from custom_components.scanspace import ScanSpaceData
from custom_components.scanspace.const import DOMAIN
from custom_components.scanspace.webhook_handler import (
    async_setup_webhook,
    async_unload_webhook,
    _handle_webhook,
    _find_data_by_webhook,
)


class MockRequest:
    def __init__(self, text_content: str):
        self._text = text_content

    async def text(self):
        return self._text


@pytest.mark.asyncio
async def test_webhook_setup_and_unload(mock_hass):
    entry = ConfigEntry(entry_id="test_entry_wh", data={"mode": "webhook", "house_id": "h1"})
    mock_hass.data[DOMAIN] = {entry.entry_id: ScanSpaceData(mock_hass, entry)}

    webhook_id = await async_setup_webhook(mock_hass, entry)
    assert webhook_id == "test_webhook_id_12345"

    await async_unload_webhook(mock_hass, entry)


@pytest.mark.asyncio
async def test_webhook_success_processing(mock_hass, sample_house_dict):
    entry = ConfigEntry(
        entry_id="test_entry_wh",
        data={"mode": "webhook", "webhook_id": "wh_valid_123", "house_id": "house_alpha_01"}
    )
    space_data = ScanSpaceData(mock_hass, entry)
    mock_hass.data[DOMAIN] = {entry.entry_id: space_data}

    dispatcher_called = []
    mock_hass.helpers.dispatcher.async_dispatcher_send = lambda signal: dispatcher_called.append(signal)

    request = MockRequest(json.dumps(sample_house_dict))
    response = await _handle_webhook(mock_hass, "wh_valid_123", request)

    assert response.status_code == 200
    assert response.body == "OK"
    assert "room_living" in space_data.rooms
    assert f"{DOMAIN}_room_living_updated" in dispatcher_called


@pytest.mark.asyncio
async def test_webhook_invalid_json(mock_hass):
    request = MockRequest("NOT_JSON_BODY")
    response = await _handle_webhook(mock_hass, "wh_any", request)
    assert response.status_code == 400
    assert response.body == "Invalid JSON"


@pytest.mark.asyncio
async def test_webhook_not_found(mock_hass):
    mock_hass.data[DOMAIN] = {}
    request = MockRequest(json.dumps({"id": "house_1"}))
    response = await _handle_webhook(mock_hass, "wh_unregistered", request)
    assert response.status_code == 404
    assert response.body == "Config not found"
