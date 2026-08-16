# Lovelace Floorplan Card Guide / Anleitung zur Grundriss-Karte

Die **ScanSpace Floorplan Card** (`custom:scanspace-floorplan`) visualisiert deinen Grundriss mit Pan- & Zoom-Gesten und synchronisiert Entitätszustände direkt mit den SVG-Elementen.

---

## Grundkonfiguration (YAML)

Füge auf deinem Dashboard eine manuelle Karte ein:

```yaml
type: custom:scanspace-floorplan
title: Erdgeschoss
floor_id: floor_ground
svg_url: /local/sample_floorplan.svg
pan_zoom: true
entity_styles:
  light.wohnzimmer_decke:
    on:
      fill: "#ffeb3b"
      opacity: 0.85
    off:
      fill: "#424242"
      opacity: 0.25
  binary_sensor.wohnzimmer_bewegung:
    on:
      stroke: "#00e676"
      stroke_width: 4
tap_actions:
  furn_table_01:
    action: call-service
    service: light.toggle
    target:
      entity_id: light.wohnzimmer_decke
```

---

## Konfigurationsparameter

| Parameter | Typ | Standard | Beschreibung |
|---|---|---|---|
| `type` | string | **Pflicht** | `custom:scanspace-floorplan` |
| `floor_id` | string | **Pflicht** | Eindeutige ID der Etage |
| `svg_url` | string | optional | Pfad zur SVG-Datei (z. B. `/local/floorplan.svg`) |
| `title` | string | optional | Titel der Lovelace-Karte |
| `pan_zoom` | boolean | `true` | Aktiviert Pan- und Pinch-to-Zoom Gesten |
| `entity_styles` | dict | `{}` | Styling-Regeln pro Home-Assistant-Entität |
| `tap_actions` | dict | `{}` | Service-Aufrufe bei Klick/Tap auf Möbel oder Räume |

---

## Interaktionsmöglichkeiten

- **Pan & Zoom**: Mit zwei Fingern (Mobile) oder Mausrad / Drag (Desktop).
- **Zustandsdarstellung**: Automatisches Einfärben bei Statusänderung von `light`, `switch`, `binary_sensor`, `climate`, etc.
- **Aktionen**:
  - `call-service`: Schaltet Lampen, ruft Szenen auf.
  - `navigate`: Wechselt auf eine andere Dashboard-Ansicht.
  - `more-info`: Öffnet den Standard-Dialog der Entität.
