"""Services for ScanSpace integration."""

from __future__ import annotations

import voluptuous as vol
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN

SERVICE_RELOAD = "reload"
SERVICE_IMPORT_FILE = "import_file"
SERVICE_EXPORT_SVG = "export_svg"
SERVICE_ASSIGN_ENTITY = "assign_entity"

SERVICES_SCHEMA = {
    SERVICE_RELOAD: vol.Schema({}),
    SERVICE_IMPORT_FILE: vol.Schema(
        {vol.Required("file_path"): cv.string}
    ),
    SERVICE_EXPORT_SVG: vol.Schema(
        {vol.Required("floor_id"): cv.string}
    ),
    SERVICE_ASSIGN_ENTITY: vol.Schema(
        {
            vol.Required("furniture_id"): cv.string,
            vol.Required("entity_id"): cv.string,
        }
    ),
}


async def async_setup_services(hass: HomeAssistant) -> None:
    """Register ScanSpace services."""

    async def handle_reload(call: ServiceCall) -> None:
        # TODO: trigger coordinator refresh
        pass

    async def handle_import_file(call: ServiceCall) -> None:
        # TODO: parse JSON file and update house data
        pass

    async def handle_export_svg(call: ServiceCall) -> None:
        # TODO: generate SVG for floor_id
        pass

    async def handle_assign_entity(call: ServiceCall) -> None:
        # TODO: persist entity-to-furniture mapping
        pass

    hass.services.async_register(DOMAIN, SERVICE_RELOAD, handle_reload)
    hass.services.async_register(DOMAIN, SERVICE_IMPORT_FILE, handle_import_file)
    hass.services.async_register(DOMAIN, SERVICE_EXPORT_SVG, handle_export_svg)
    hass.services.async_register(DOMAIN, SERVICE_ASSIGN_ENTITY, handle_assign_entity)
