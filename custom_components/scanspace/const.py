"""Constants for the ScanSpace integration."""

from __future__ import annotations

import logging

DOMAIN = "scanspace"
LOGGER = logging.getLogger(__package__)

# MQTT topic prefixes
MQTT_TOPIC_PREFIX = "scanspace/house"

# Config entry keys
CONF_HOUSE_ID = "house_id"
CONF_MQTT_ENABLED = "mqtt_enabled"
CONF_WEBHOOK_ID = "webhook_id"
CONF_PAIRING_TOKEN = "pairing_token"

# Schema version support
SUPPORTED_SCHEMA_MAJOR = {"1"}
DEFAULT_SCHEMA_VERSION = "1.0"

# Entity name templates
ENTITY_AREA = "sensor.scanspace_{room_id}_area"
ENTITY_FURNITURE_COUNT = "sensor.scanspace_{room_id}_furniture_count"
ENTITY_CEILING_HEIGHT = "sensor.scanspace_{room_id}_ceiling_height"
ENTITY_PRESENCE = "binary_sensor.scanspace_{room_id}_presence"
ENTITY_ZONE = "zone.scanspace_{room_id}"

# SVG data attributes used by the floorplan card
ATTR_SCANSPACE_TYPE = "data-scanspace-type"
ATTR_ROOM_ID = "data-room-id"
ATTR_FURNITURE_ID = "data-furniture-id"
ATTR_FURNITURE_TYPE = "data-furniture-type"
ATTR_ENTITY_ID = "data-entity-id"
ATTR_ZONE_ID = "data-zone-id"
ATTR_CONNECTS_TO = "data-connects-to"
