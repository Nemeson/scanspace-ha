# Entities & Services Reference / Entitäten & Services

---

## 1. Automatisch generierte Entitäten

Für jeden vermessenen Raum erzeugt die ScanSpace-Integration automatisch folgende Entitäten:

| Entitäts-ID | Plattform | Einheit | Beschreibung (DE / EN) |
|---|---|---|---|
| `sensor.scanspace_{room_id}_area` | Sensor | $m^2$ | Berechnete Raumfläche aus Polygon / Room floor area |
| `sensor.scanspace_{room_id}_furniture_count` | Sensor | Stück / items | Anzahl der erfassten Möbelstücke / Total furniture count |
| `sensor.scanspace_{room_id}_ceiling_height` | Sensor | $m$ | Gemessene Deckenhöhe / Room ceiling height |
| `binary_sensor.scanspace_{room_id}_presence` | Binary Sensor | on/off | Präsenzerkennung via zugewiesenem Bewegungsmelder |
| `zone.scanspace_{room_id}` | Zone | Polygon | Räumliche Begrenzung des Raums als Polygon-Attribut |

---

## 2. Verfügbare Service-Aufrufe

Die Integration stellt folgende Services bereit:

### `scanspace.reload`
Lädt alle zwischengespeicherten ScanSpace-Daten und Entitäten neu.
```yaml
service: scanspace.reload
```

### `scanspace.import_file`
Importiert einen ScanSpace JSON-Grundriss direkt aus dem Dateisystem von Home Assistant.
```yaml
service: scanspace.import_file
data:
  file_path: "/config/scanspace/export.json"
```

### `scanspace.export_svg`
Generiert und speichert eine Layer-basierte SVG-Grundrissdatei einer bestimmten Etage.
```yaml
service: scanspace.export_svg
data:
  floor_id: "floor_ground"
```

### `scanspace.assign_entity`
Verknüpft eine beliebige Home Assistant Entität (z. B. Lampe oder Steckdose) mit einem Möbelstück oder einer Zone.
```yaml
service: scanspace.assign_entity
data:
  furniture_id: "furn_table_01"
  entity_id: "light.wohnzimmer_decke"
```
