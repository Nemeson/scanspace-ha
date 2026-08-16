# ScanSpace for Home Assistant

**ScanSpace** connects the ScanSpace AR 3D measurement Android App with Home Assistant.

## Key Features

- **AR Floorplan Ingestion**: Imports rooms, walls, doors, windows, and furniture.
- **MQTT Live Sync**: Real-time room and device updates over `scanspace/house/#`.
- **Sensors & Presence**: Creates area, furniture count, and presence binary sensors for each room.
- **Interactive Floorplan Card**: Interactive pan/zoom Lovelace card displaying the floorplan with live entity states.

## Quick Start

1. Install this integration via HACS.
2. Restart Home Assistant.
3. Go to **Settings** → **Devices & Services** → **Add Integration** → **ScanSpace**.
4. Choose your connection method (MQTT, Webhook, or QR Code) and start scanning with your phone!
