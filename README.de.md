# Mediathek NAS

Eine selbst gehostete Web-App, die die Mediatheken der öffentlich-rechtlichen Sender
durchsucht und Sendungen direkt in die Medienbibliothek auf dem NAS lädt — benannt,
einsortiert und mit Metadaten versehen, sodass Plex, Jellyfin und Infuse sie ohne
Nacharbeit erkennen.

Gebaut für Synology DSM und den Container Manager. FastAPI + SQLite + `yt-dlp` + `ffmpeg`,
ein Container, kein Java, kein Desktop-Client.

> **Die Suchdaten stammen von [MediathekViewWeb](https://mediathekviewweb.de), Teil des
> [MediathekView](https://github.com/mediathekview)-Projekts.** Die eigentliche Arbeit —
> die Kataloge der Sender zu aggregieren und zu indizieren — leisten die dort. Dieses
> Projekt steht in keiner Verbindung zu ihnen; es ist eine NAS-taugliche Oberfläche auf
> der öffentlichen API, die sie dankenswerterweise bereitstellen. Wer das hier nutzt,
> sollte deren Repositories einen Stern geben.

![Suchergebnisse, zwei Downloads laufen](docs/screenshots/search-results.png)

![Die Warteschlange](docs/screenshots/downloads-queue.png)

## Warum es das gibt

MediathekView ist hervorragend, und wer eine Desktop-Anwendung möchte, sollte sie
verwenden. Dieses Projekt löst ein anderes Problem: **die Sendung soll schon auf dem NAS
liegen, wenn man sich abends aufs Sofa setzt.**

- Läuft headless und rund um die Uhr im Container — keine App zum Öffnen
- Regeln mit Intervall: Serie einmal anlegen, neue Folgen laden sich selbst
- Schreibt direkt in den vorhandenen Medienordner, inklusive `.nfo` und `.info.json`
- Stößt nach fertigem Download einen Plex- oder Jellyfin-Scan an
- Erzeugt Infuse-Deep-Links für Apple TV, iPhone und iPad
- Responsive Oberfläche, also auch vom Handy aus bedienbar

Verkürzt: MediathekView ist der Desktop-Client, das hier ist der Dauerläufer, der die
Bibliothek füllt.

## Schnellstart (fertiges Image)

Kein Build nötig. Ordner auf dem NAS anlegen, diese `docker-compose.yml` hineinlegen, die
drei markierten Werte anpassen, dann im Container Manager unter **Projekt** → **Erstellen**
auf diesen Ordner zeigen. Den Schritt „Webportal" im Assistenten überspringen.

```yaml
services:
  mediathek-nas:
    image: ghcr.io/thechristoph03/mediathek-nas:latest
    container_name: mediathek-nas

    # ANPASSEN: UID:GID, der die heruntergeladenen Dateien gehören sollen.
    # Ermitteln mit: stat -c '%u:%g' /volume1/video/DeinMedienordner
    user: "1026:100"

    ports:
      - "8000:8000"

    environment:
      APP_DATA_DIR: /config
      DOWNLOAD_ROOT: /media/mediathek
      HOME: /config
      TZ: Europe/Berlin

    volumes:
      - type: bind
        source: /volume1/docker/mediathek-nas/config   # ANPASSEN
        target: /config
      - type: bind
        source: /volume1/video/Movies/Mediathek        # ANPASSEN
        target: /media/mediathek

    restart: unless-stopped
```

Danach `http://<nas-ip>:8000` aufrufen.

Eine fertige Kopie dieser Datei liegt als [`docker-compose.ghcr.yml`](docker-compose.ghcr.yml) bei.

### Die Zeile `user:` ist nicht optional

Ohne sie läuft der Container als root, und jede heruntergeladene Datei gehört root —
womit Plex, Jellyfin und die File Station schlecht zurechtkommen. Auf die UID/GID setzen,
der der Medienordner gehört.

### Beide Bind-Mounts müssen existieren und beschreibbar sein

Im Config-Mount liegt die SQLite-Datenbank. Existiert der Pfad nicht, startet der
Container gar nicht erst und meldet `bind source path does not exist`.

## Konfiguration

| Variable | Standard | Bedeutung |
| --- | --- | --- |
| `DOWNLOAD_ROOT` | `/downloads` | Zielverzeichnis im Container |
| `APP_DATA_DIR` | `/config` | Enthält `mediathek_nas.db` |
| `HOME` | `/config` | Nötig, damit `yt-dlp` ein beschreibbares Cache-Verzeichnis hat |
| `TZ` | `Europe/Berlin` | Beeinflusst Scheduler und Log-Zeitstempel |

`DOWNLOAD_ROOT` wird **von der Umgebung verwaltet**: Was der Container vorgibt, gewinnt bei
jedem Start gegen den gespeicherten Wert, und das Feld ist in der Oberfläche schreibgeschützt.
Das ist beabsichtigt — im Container konfiguriert man den Pfad über den Volume-Mount, nicht
über ein Formularfeld. Alles Übrige wird in der Oberfläche eingestellt und in der Datenbank
gespeichert.

### Benennung und Ordner

Zwei Vorlagen bestimmen die Struktur, beide in der Oberfläche änderbar:

- **Unterordner** — Standard `{channel}/{topic}`, ergibt `zdf-tivi/logo/…`
- **Dateiname** — Standard `{date}_{channel}_{title}`

Platzhalter: `{date}`, `{year}`, `{channel}`, `{topic}`, `{title}`, `{quality}`.
Werte werden bereinigt und auf 80 Zeichen gekürzt.

## Funktionen

**Suche** — vollständige MediathekViewWeb-Abfragen mit Filtern für Sender, Thema, Datum,
Laufzeit und Qualität; Vorschau- und Streaming-Links je Treffer.

**Downloads** — Warteschlange mit Fortschritt, parallele Worker, Wiederholung und Abbruch,
globale Dublettenerkennung über Downloads und importierte Dateien hinweg.

**Regeln** — gespeicherte Suchen mit Intervall; ein Hintergrund-Scheduler führt sie aus und
kann Treffer automatisch laden. Trefferhistorie und RSS-Feed je Regel.

**Bibliotheks-Anbindung** — `.nfo`- und `.info.json`-Sidecars, Plex- und Jellyfin-Scans,
Infuse-Deep-Links sowie ein Import für bereits vorhandene Dateien.

**Diagnose** — `GET /api/system-check` prüft `yt-dlp`, `ffmpeg` und ob Config- und
Download-Pfad aus dem Container heraus beschreibbar sind.

![Einstellungen](docs/screenshots/settings.png)

## Aus dem Quellcode bauen

```bash
git clone https://github.com/TheChristoph03/mediathek-nas.git
cd mediathek-nas
docker compose -f docker-compose.synology.yml up -d --build
```

Zur Warnung: Die `ffmpeg`-Schicht braucht auf NAS-Hardware etwa 25–40 Minuten. Das fertige
Image ist deutlich sinnvoller, solange man nicht am Dockerfile arbeitet.

Lokal ohne Docker:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
python -m unittest discover -s tests
```

`yt-dlp` ist im Dockerfile auf eine Version festgelegt, damit Builds reproduzierbar sind.
Da die Sender ihre Seiten ändern, funktioniert eine feste Version irgendwann nicht mehr für
alle Quellen — sie wird mit jedem Release nachgezogen.

## Rahmen und Grenzen

Dieses Projekt verarbeitet ausschließlich **öffentlich zugängliche Inhalte aus den
Mediatheken der Sender**, so wie MediathekViewWeb sie indiziert. Es umgeht kein DRM, hebelt
keine Zugangsbeschränkungen aus und hat auch keinen Mechanismus dafür. Die Inhalte der
Öffentlich-Rechtlichen sind gebührenfinanziert und zum Abruf veröffentlicht; sie für den
privaten Gebrauch zu laden, ist das, was dieses Werkzeug tut. Für eine Weiterverbreitung
ist der Nutzer verantwortlich, nicht das Werkzeug.

Ebenfalls nicht vorhanden: Mehrbenutzerbetrieb, überhaupt keine Authentifizierung (nicht ins
Internet stellen), automatisches Auffinden von Plex- oder Jellyfin-Servern und der Import
nativer MediathekView-Datenformate.

## Geplant

- `linux/arm64`-Images für ARM-basierte Synology-Modelle
- Überarbeitung von UI und UX — kompakteres Layout, bessere Bedienung am Handy
- Englische Oberfläche
- Ordnerauswahl in den Einstellungen
- Screenshots

## Dank

- [MediathekView](https://github.com/mediathekview) und
  [MediathekViewWeb](https://github.com/mediathekview/mediathekviewweb) — der Suchindex,
  auf dem diese App aufsetzt
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) — die Download-Engine
- [FastAPI](https://fastapi.tiangolo.com) und [Uvicorn](https://www.uvicorn.org)

## Lizenz

MIT, siehe [LICENSE](LICENSE).

---

🇬🇧 [English version](README.md)
