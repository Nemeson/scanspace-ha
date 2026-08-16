"""Webhook receiver for ScanSpace app uploads."""

from __future__ import annotations

import json
from typing import Any

from homeassistant.components import webhook
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, LOGGER
from .models import HousePayload


async def async_setup_webhook(hass: HomeAssistant, entry: ConfigEntry) -> str:
    """Register a webhook for this config entry."""
    webhook_id = webhook.async_generate_id()
    webhook.async_register(
        hass,
        DOMAIN,
        f"ScanSpace {entry.data.get('house_id', entry.entry_id)}",
        webhook_id,
        _handle_webhook,
        allowed_methods=["POST"],
    )

    # Persist webhook_id in config entry data for the app
    hass.config_entries.async_update_entry(
        entry,
        data={**entry.data, "webhook_id": webhook_id},
    )
    LOGGER.debug("Registered webhook %s", webhook_id)
    return webhook_id


async def async_unload_webhook(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Unregister the webhook."""
    webhook_id = entry.data.get("webhook_id")
    if webhook_id:
        webhook.async_unregister(hass, webhook_id)


async def _handle_webhook(
    hass: HomeAssistant,
    webhook_id: str,
    request: Any,
) -> Any:
    """Handle incoming ScanSpace webhook."""
    try:
        body = await request.text()
        data = json.loads(body)
    except json.JSONDecodeError as err:
        LOGGER.warning("Invalid JSON in webhook %s: %s", webhook_id, err)
        return webhook.Response("Invalid JSON", status_code=400)
    except Exception as err:
        LOGGER.warning("Webhook error: %s", err)
        return webhook.Response("Error", status_code=500)

    scan_space_data = _find_data_by_webhook(hass, webhook_id)
    if not scan_space_data:
        return webhook.Response("Config not found", status_code=404)

    house = HousePayload.from_dict(data.get("house", data))
    scan_space_data.house = data
    for floor in house.floors:
        for room in floor.rooms:
            scan_space_data.rooms[room.id] = room.model_dump()
            hass.helpers.dispatcher.async_dispatcher_send(f"{DOMAIN}_{room.id}_updated")

    LOGGER.debug("Webhook processed for house %s", house.id)
    return webhook.Response("OK", status_code=200)


def _find_data_by_webhook(hass: HomeAssistant, webhook_id: str) -> Any:
    for entry_id, data in hass.data.get(DOMAIN, {}).items():
        if isinstance(data, dict):
            continue
        if getattr(data, "entry", None) and data.entry.data.get("webhook_id") == webhook_id:
            return data
    return None
