"""Unit tests for ScanSpace Config Flow."""

import pytest
from custom_components.scanspace.config_flow import ScanSpaceConfigFlow
from custom_components.scanspace.const import DOMAIN


@pytest.mark.asyncio
async def test_config_flow_user_step():
    flow = ScanSpaceConfigFlow()
    result = await flow.async_step_user()
    assert result["type"] == "menu"
    assert result["step_id"] == "user"
    assert "mqtt" in result["menu_options"]
    assert "webhook" in result["menu_options"]
    assert "qr_pairing" in result["menu_options"]


@pytest.mark.asyncio
async def test_config_flow_mqtt_step():
    flow = ScanSpaceConfigFlow()
    # Form display
    form_res = await flow.async_step_mqtt(None)
    assert form_res["type"] == "form"
    assert form_res["step_id"] == "mqtt"

    # Submit
    create_res = await flow.async_step_mqtt({})
    assert create_res["type"] == "create_entry"
    assert create_res["title"] == "ScanSpace (MQTT)"
    assert create_res["data"]["mode"] == "mqtt"


@pytest.mark.asyncio
async def test_config_flow_webhook_step():
    flow = ScanSpaceConfigFlow()
    # Form display
    form_res = await flow.async_step_webhook(None)
    assert form_res["type"] == "form"
    assert form_res["step_id"] == "webhook"

    # Submit
    create_res = await flow.async_step_webhook({"url": "https://ha.local/api/webhook/scanspace"})
    assert create_res["type"] == "create_entry"
    assert create_res["title"] == "ScanSpace (Webhook)"
    assert create_res["data"]["mode"] == "webhook"
    assert create_res["data"]["url"] == "https://ha.local/api/webhook/scanspace"


@pytest.mark.asyncio
async def test_config_flow_qr_pairing_step():
    flow = ScanSpaceConfigFlow()
    result = await flow.async_step_qr_pairing()
    assert result["type"] == "create_entry"
    assert result["title"] == "ScanSpace (QR Pairing)"
    assert result["data"]["mode"] == "qr_pairing"
