"""Config flow for ScanSpace integration."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_URL

from .const import DOMAIN, LOGGER


class ScanSpaceConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for ScanSpace."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Ask the user how to pair with the app."""
        return self.async_show_menu(
            step_id="user",
            menu_options=["mqtt", "webhook", "qr_pairing"],
        )

    async def async_step_mqtt(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Set up via MQTT auto-discovery."""
        LOGGER.debug("MQTT setup selected")
        if user_input is not None:
            return self.async_create_entry(
                title="ScanSpace (MQTT)",
                data={"mode": "mqtt"},
            )
        return self.async_show_form(step_id="mqtt")

    async def async_step_webhook(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Set up via webhook URL."""
        LOGGER.debug("Webhook setup selected")
        if user_input is not None:
            return self.async_create_entry(
                title="ScanSpace (Webhook)",
                data={"mode": "webhook", CONF_URL: user_input.get(CONF_URL)},
            )
        return self.async_show_form(step_id="webhook")

    async def async_step_qr_pairing(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Display QR code for app pairing."""
        LOGGER.debug("QR pairing selected")
        return self.async_create_entry(
            title="ScanSpace (QR Pairing)",
            data={"mode": "qr_pairing"},
        )
