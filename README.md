# ScanSpace — Home Assistant Integration & Interactive Floorplan Card

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg?style=flat-square)](https://github.com/hacs/default)
[![GitHub Release](https://img.shields.io/github/v/release/Nemeson/scanspace-ha?include_prereleases&style=flat-square&color=blue)](https://github.com/Nemeson/scanspace-ha/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2024.10%2B-blue?style=flat-square&logo=home-assistant)](https://www.home-assistant.io/)
[![CI Validation](https://img.shields.io/github/actions/workflow/status/Nemeson/scanspace-ha/validate.yml?branch=main&label=CI&style=flat-square)](https://github.com/Nemeson/scanspace-ha/actions)

> ⚠️ **Alpha-Version (v0.1.0-alpha.1)**: Dies ist eine frühe Entwickler- und Tester-Version. Feedback und Feature-Requests sind im [Issue Tracker](https://github.com/Nemeson/scanspace-ha/issues) herzlich willkommen!

---

## 🇩🇪 Deutsch

### Übersicht

**ScanSpace** ist eine ganzheitliche Home-Assistant-Integration mit zugehöriger interaktiver Lovelace Floorplan Card. Sie verbindet die ScanSpace Android-App (ARCore/Filament Raum- & Inventar-Vermessung) direkt mit deinem Home Assistant Smart Home.

Vermessene Räume, Wände, Fenster, Türen und Möbelstücke werden automatisch als Home Assistant Entitäten angelegt und können auf einem interaktiven, maßstabsgetreuen SVG-Grundriss mit Echtzeit-Statusanzeigen und Touch-Steuerung visualisiert werden.

```
┌─────────────────────────┐         MQTT / Webhook        ┌──────────────────────────────┐
│   ScanSpace Android App │ ─────────────────────────────►│        Home Assistant        │
│   (ARCore / Filament)   │    scanspace/house/{id}/...   │                              │
│                         │                               │  ┌────────────────────────┐  │
│  - 3D Raum-Vermessung   │                               │  │ Custom Integration     │  │
│  - Möbel & Zonen        │                               │  │ (custom_components/)  │  │
│  - Live Delta-Sync      │                               │  └──────────┬─────────────┘  │
│  - SVG & JSON Export    │                               │             │                │
└─────────────────────────┘                               │  ┌──────────▼─────────────┐  │
                                                          │  │ Lovelace Floorplan Card│  │
                                                          │  │ (Pan, Zoom, Touch, UI) │  │
                                                          │  └────────────────────────┘  │
                                                          └──────────────────────────────┘
```

### Highlights & Funktionen

- 📐 **Automatischer Raum- & Möbelimport**: Erzeugt Entitäten für Raumflächen ($m^2$), Möbelzähler, Deckenhöhe und Präsenzerkennung.
- ⚡ **MQTT Live-Synchronisation**: Echtzeit-Updates bei Änderungen im Scan direkt über den MQTT-Broker (`scanspace/house/#`).
- 🌐 **HTTP Webhook Fallback**: Direkter Upload aus der App via Webhook ohne zwingenden MQTT-Broker.
- 🗺️ **Interaktive Floorplan Card**:
  - Flüssiges Pan & Zoom mit Touch- und Maus-Gesten.
  - Bindung von Home-Assistant-Entitäten an Möbel, Lampen oder Zonen.
  - Dynamische Farb- und Deckkraft-Änderungen bei Statuswechsel (z. B. Licht an/aus, Bewegung erkannt).
  - Tap-, Double-Tap- und Hold-Aktionen (z. B. Licht schalten, Dialog öffnen).
- 📦 **Inklusive Frontend-Bundle**: Die Lovelace-Karte ist direkt in der Integration enthalten und wird automatisch als statische Ressource bereitgestellt.

---

### Installation

#### Methode 1: Über HACS (Empfohlen)

1. Öffne **HACS** in deiner Home Assistant Instanz.
2. Klicke oben rechts auf das Drei-Punkte-Menü `⋮` → **Benutzerdefinierte Repositories** (*Custom repositories*).
3. Füge folgende Repository-URL ein:
   ```text
   https://github.com/Nemeson/scanspace-ha
   ```
4. Wähle als Typ/Kategorie: **Integration**.
5. Klicke auf **Hinzufügen**.
6. Suche nach **ScanSpace**, wähle **Herunterladen** und installiere die neueste Version (`v0.1.0-alpha.1`).
7. **Starte Home Assistant neu**.

#### Methode 2: Manuelle Installation

1. Lade das neueste Release-Archiv `scanspace.zip` von [GitHub Releases](https://github.com/Nemeson/scanspace-ha/releases) herunter.
2. Entpacke den Ordner `custom_components/scanspace` in das Verzeichnis `<config>/custom_components/scanspace/` deiner Home Assistant Installation.
3. Starte Home Assistant neu.

---

### Einrichtung & Kopplung

1. Gehe in Home Assistant zu **Einstellungen** → **Geräte & Dienste** → **Integration hinzufügen**.
2. Suche nach **ScanSpace**.
3. Wähle die gewünschte Verbindungsmethode:
   - **MQTT (Empfohlen)**: Abonniert automatisch Topics unter `scanspace/house/#`.
   - **Webhook**: Registriert einen sicheren Webhook-Endpunkt für direkte Uploads.
   - **QR-Code Pairing**: Zeigt Verbindungsdaten für die ScanSpace Android-App an.
4. Nach dem ersten Scan oder Import erscheinen deine Räume und Möbel automatisch als Geräte und Entitäten.

---

### Lovelace Floorplan Card einbinden

Die Lovelace-Karte wird nach der Installation automatisch unter `/scanspace/scanspace-floorplan-card.js` bereitgestellt.

1. Gehe zu **Einstellungen** → **Dashboards** → **Ressourcen** (oben rechts Drei-Punkte-Menü).
2. Füge eine neue Ressource hinzu:
   - **URL**: `/scanspace/scanspace-floorplan-card.js`
   - **Ressourcentyp**: `JavaScript-Modul`
3. Füge auf deinem Dashboard eine neue Karte als **Manuelles YAML** hinzu:

```yaml
type: custom:scanspace-floorplan
title: Erdgeschoss
floor_id: floor_eg
svg_url: /local/sample_floorplan.svg
pan_zoom: true
entity_styles:
  light.wohnzimmer_decke:
    on:
      fill: "#ffeb3b"
      opacity: 0.85
    off:
      fill: "#424242"
      opacity: 0.3
  binary_sensor.wohnzimmer_bewegung:
    on:
      stroke: "#00e676"
      stroke_width: 3
tap_actions:
  furn_table_01:
    action: call-service
    service: light.toggle
    target:
      entity_id: light.wohnzimmer_decke
```

---

## 🇬🇧 English

### Overview

**ScanSpace** is a comprehensive Home Assistant integration and interactive Lovelace Floorplan Card designed to seamlessly interface with the ScanSpace Android App (ARCore/Filament spatial room and furniture scanner).

Measured rooms, walls, doors, windows, and furniture items are automatically converted into Home Assistant entities and displayed on a precise, scale-accurate SVG floorplan with live status overlays and interactive touch controls.

### Features

- 📐 **AR Floorplan & Inventory Ingestion**: Automatically creates entities for room dimensions ($m^2$), furniture counts, ceiling height, and room presence.
- ⚡ **MQTT Live Synchronization**: Real-time state synchronisation over MQTT (`scanspace/house/#`).
- 🌐 **HTTP Webhook Fallback**: Direct app upload support without requiring an MQTT broker.
- 🗺️ **Interactive Lovelace Floorplan Card**:
  - Smooth pan & zoom navigation on mobile and desktop.
  - Entity-to-furniture bindings with dynamic styling based on state.
  - Tap, double-tap, and hold action support (toggle lights, call services, open popups).
- 📦 **Self-Contained Distribution**: The floorplan card bundle is shipped inside the integration and registered automatically.

---

### Installation via HACS

1. In Home Assistant, open **HACS** → **Integrations**.
2. Click the top-right menu `⋮` → **Custom repositories**.
3. Enter: `https://github.com/Nemeson/scanspace-ha`
4. Select category: **Integration**.
5. Click **Add**, find **ScanSpace**, download and restart Home Assistant.

---

### Services

| Service | Description | Parameters |
|---|---|---|
| `scanspace.reload` | Reloads all ScanSpace houses and rooms | None |
| `scanspace.import_file` | Imports a ScanSpace JSON floorplan file | `file_path` (string) |
| `scanspace.export_svg` | Generates and exports SVG floorplan for a floor | `floor_id` (string) |
| `scanspace.assign_entity` | Binds a Home Assistant entity to a furniture/room item | `furniture_id`, `entity_id` |

---

### Development & Testing

```bash
# Python Integration Tests
pytest tests/

# Frontend Floorplan Card Build & Tests
cd scanspace-floorplan-card
npm install
npm test
npm run build
```

---

### License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for more information.
