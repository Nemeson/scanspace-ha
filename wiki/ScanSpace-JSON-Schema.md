# ScanSpace JSON Schema v1.0

Das proprietäre ScanSpace JSON Schema v1.0 beschreibt Häuser, Etagen, Räume, Wände, Fenster, Türen und Möbelstücke mit exakten metrischen Koordinaten ($m$).

---

## Beispiel-Payload (`HousePayload`)

```json
{
  "schema_version": "1.0",
  "id": "house_001",
  "name": "Musterhaus",
  "floors": [
    {
      "id": "floor_ground",
      "name": "Erdgeschoss",
      "elevation": 0.0,
      "rooms": [
        {
          "id": "room_living",
          "name": "Wohnzimmer",
          "floor_id": "floor_ground",
          "ceiling_height": 2.5,
          "floor_outline": [
            [0.0, 0.0],
            [5.0, 0.0],
            [5.0, 4.0],
            [0.0, 4.0]
          ],
          "walls": [
            {
              "id": "wall_1",
              "start": [0.0, 0.0, 0.0],
              "end": [5.0, 0.0, 0.0],
              "thickness": 0.15,
              "height": 2.5
            }
          ],
          "doors": [
            {
              "id": "door_1",
              "wall_id": "wall_1",
              "position": 2.0,
              "width": 0.9
            }
          ],
          "furniture": [
            {
              "id": "furn_sofa_01",
              "type": "sofa",
              "position": [2.0, 0.0, 1.5],
              "rotation": [0.0, 0.0, 0.0, 1.0],
              "dimensions": [2.2, 0.85, 0.9],
              "entity_id": "light.wohnzimmer_decke"
            }
          ]
        }
      ]
    }
  ]
}
```
