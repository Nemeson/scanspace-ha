# Installation Guide / Installationsanleitung

---

## 🇩🇪 Installation

### Methode 1: Über HACS (Home Assistant Community Store) — Empfohlen

1. **HACS öffnen**: Navigiere in deiner Home-Assistant-Seitenleiste zu **HACS**.
2. **Benutzerdefiniertes Repository hinzufügen**:
   - Klicke oben rechts auf das Drei-Punkte-Menü `⋮` → **Benutzerdefinierte Repositories** (*Custom repositories*).
   - Gib die Repository-URL ein:
     ```text
     https://github.com/Nemeson/scanspace-ha
     ```
   - Wähle als Kategorie: **Integration**.
   - Klicke auf **Hinzufügen**.
3. **Integration herunterladen**:
   - Suche in HACS nach **ScanSpace**.
   - Klicke auf **Herunterladen** und wähle die gewünschte Version (z. B. `v0.1.0-alpha.1`).
4. **Home Assistant neu starten**:
   - Gehe zu *Entwicklerwerkzeuge* → *YAML* → *Neu starten*.
5. **Lovelace-Ressource hinzufügen**:
   - Gehe zu *Einstellungen* → *Dashboards* → *Ressourcen* (oben rechts `⋮`).
   - Klicke auf **Ressource hinzufügen**:
     - **URL**: `/scanspace/scanspace-floorplan-card.js`
     - **Ressourcentyp**: `JavaScript-Modul`

---

### Methode 2: Manuelle Installation

1. Lade das neueste Release-Archiv `scanspace.zip` von [GitHub Releases](https://github.com/Nemeson/scanspace-ha/releases) herunter.
2. Entpacke den Ordner `custom_components/scanspace/` in das Verzeichnis `<config>/custom_components/scanspace/` auf deinem Home-Assistant-Server.
3. Kopiere die Datei `scanspace-floorplan-card.js` in dein Verzeichnis `<config>/www/`.
4. Starte Home Assistant neu.
5. Füge unter *Einstellungen* → *Dashboards* → *Ressourcen* die URL `/local/scanspace-floorplan-card.js` als *JavaScript-Modul* hinzu.

---

## 🇬🇧 Installation (English)

### Method 1: Via HACS (Recommended)

1. Open **HACS** from the Home Assistant sidebar.
2. Click the top-right `⋮` menu → **Custom repositories**.
3. Add repository URL: `https://github.com/Nemeson/scanspace-ha` with category `Integration`.
4. Find **ScanSpace** in the integration list, download the release, and restart Home Assistant.
5. In *Settings* → *Dashboards* → *Resources*, register `/scanspace/scanspace-floorplan-card.js` as a *JavaScript Module*.

### Method 2: Manual Installation

1. Download `scanspace.zip` from [Releases](https://github.com/Nemeson/scanspace-ha/releases).
2. Extract into `<config>/custom_components/scanspace/`.
3. Restart Home Assistant and add the card resource.
