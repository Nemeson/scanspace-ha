# Pairing & Communication Methods / Kopplungsmethoden

ScanSpace unterstützt drei nahtlose Kommunikationswege zwischen der Android-App und Home Assistant:

---

## 1. MQTT Live-Synchronisation (Empfohlen / Recommended)

Die MQTT-Kopplung ermöglicht Live-Streaming aller Vermessungsdaten in Echtzeit während des Scannens.

### Funktionsweise
1. Bei der Integrationseinrichtung in Home Assistant wählst du **MQTT Live-Synchronisation**.
2. ScanSpace abonniert das Topic-Präfix `scanspace/house/#`.
3. Die Android-App publiziert auf folgenden Topics:

| Topic | Typ | Beschreibung / Description |
|---|---|---|
| `scanspace/house/{house_id}/manifest` | JSON | Haus-Metadaten (Name, Etagen-Liste) |
| `scanspace/house/{house_id}/floor/{floor_id}` | JSON | Etagen-Update mit Raum-IDs |
| `scanspace/house/{house_id}/room/{room_id}` | JSON | Vollständiger Raumzustand (Wände, Türen, Möbel) |
| `scanspace/house/{house_id}/room/{room_id}/delta` | JSON | Inkrementelles Möbel-Update |
| `scanspace/house/{house_id}/status` | Text/JSON | App-Status (`scanning`, `idle`, `online`) |

---

## 2. HTTP Webhook Fallback

Falls kein MQTT-Broker zur Verfügung steht, kann die App Daten direkt via HTTP-POST an einen sicheren Home Assistant Webhook senden.

### Einrichtung
1. In Home Assistant: **Einstellungen** → **Geräte & Dienste** → **Integration hinzufügen** → **ScanSpace**.
2. Wähle **HTTP Webhook Upload**.
3. Home Assistant generiert eine eindeutige Webhook-ID.
4. Trage die Webhook-URL in den Einstellungen der ScanSpace Android-App ein:
   ```text
   http://<HA-IP>:8123/api/webhook/<WEBHOOK_ID>
   ```

---

## 3. QR-Code Pairing

1. Wähle beim Setup den Modus **QR-Code Pairing**.
2. Es wird ein QR-Code mit den Verbindungsdaten (Host, Port, Topic/Webhook-Token) generiert.
3. Scanne den QR-Code direkt in den Einstellungen der ScanSpace Android-App.
