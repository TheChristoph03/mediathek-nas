# Mediathek NAS

Mediathek NAS ist eine Synology-taugliche Web-App zum Suchen, Vorschauen, Herunterladen und Organisieren von Inhalten aus oeffentlich erreichbaren Mediatheken auf Basis von MediathekViewWeb-Daten. Das Projekt ist fuer Docker und Synology Container Manager vorbereitet und nutzt FastAPI, SQLite, `yt-dlp` und `ffmpeg`.

## Status heute

Stand: **Mittwoch, 12. August 2026**

Was bereits laeuft:

- Suche ueber MediathekViewWeb-Daten
- Filter fuer Sender, Thema, Datum, Laufzeit und Qualitaet
- Detailansicht mit Vorschau- und Streaming-Link
- Einzel-Download mit Queue, Fortschritt, Retry und Cancel
- Mehrere gleichzeitige Downloads
- Regeln und Serien-Abos mit Intervallen
- Hintergrund-Scheduler fuer faellige Regeln
- Konfigurierbare Dateinamen und Unterordner per Platzhalter
- `.nfo` und `.info.json` Sidecars fuer Plex/Jellyfin-Vorbereitung
- Plex- und Jellyfin-Refresh per API nach fertigen Downloads
- Infuse-Deep-Links fuer Apple-Geraete
- Import vorhandener Mediendateien und einfacher Listen
- RSS-Feeds fuer Suchanfragen und Regeln
- Globale Dublettenpruefung ueber Downloads und Importe
- Responsive, kompaktere Weboberflaeche fuer Desktop, iPhone und iPad
- Preflight- und System-Check fuer Container, Werkzeuge, Pfade und Synology-Voraussetzungen

Was noch bewusst fehlt:

- Kein DRM-Bypass
- Keine Verarbeitung zugangsbeschraenkter Quellen
- Noch keine Mehrbenutzerverwaltung
- Noch keine vollautomatische Server-Erkennung fuer fremde Plex- oder Jellyfin-Instanzen
- Noch kein nativer Import des originalen MediathekView-Datenformats mit garantierter 1:1-Abbildung

## Projektstruktur

```text
.
├── app
│   ├── api
│   ├── core
│   ├── db
│   ├── models
│   ├── services
│   ├── static
│   └── templates
├── Dockerfile
├── LICENSE
├── README.en.md
├── README.md
├── docker-compose.yml
├── docker-compose.synology.yml
├── outputs
└── tests
```

## Wo liegen die Dateien lokal?

Projektordner:

`/Users/christophdudy/Documents/Codex/2026-08-12/referenced-chatgpt-conversation-this-is-an-2`

Wichtige Unterordner:

- `app/` fuer Backend, API und Weboberflaeche
- `data/` fuer SQLite und Laufzeitdaten im lokalen Test
- `downloads/` fuer lokale Testdownloads
- `outputs/` fuer nutzernahe Anleitungen
- `tests/` fuer Grundtests

## Lokal starten

Empfohlen ist Python 3.12.

```bash
cd /Users/christophdudy/Documents/Codex/2026-08-12/referenced-chatgpt-conversation-this-is-an-2
python3.12 -m venv .venv312
source .venv312/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Danach im Browser:

`http://127.0.0.1:8000`

## Schnelltest lokal

1. Suche nach `Terra X`
2. Oeffne `Details`
3. Lege einen Download in die Queue
4. Aktiviere testweise `.nfo` und `.info.json`
5. Lege eine Regel an und fuehre `Faellige Regeln jetzt ausfuehren` aus
6. Pruefe den Bereich `System-Check`

## Teststatus

Am 12. August 2026 erfolgreich geprueft:

- `python -m compileall app tests`
- `python -m unittest discover -s tests`
- App-Start mit `uvicorn`
- `GET /api/system-check`
- `GET /api/media-servers/status`
- `GET /api/rss/search?query=Terra X`

## Installation auf Synology

Zielsystem im aktuellen Setup:

- Synology `DS1520+`
- DSM `7.3.2-86009 Update 4`
- Container Manager installiert
- Medienordner: `/volume1/video/Movies/Fernseh Mediathek`

Die komplette SSH-Schrittfolge liegt hier:

[synology-ssh-setup.md](/Users/christophdudy/Documents/Codex/2026-08-12/referenced-chatgpt-conversation-this-is-an-2/outputs/synology-ssh-setup.md:1)

Die Compose-Datei fuer die Synology liegt hier:

[docker-compose.synology.yml](/Users/christophdudy/Documents/Codex/2026-08-12/referenced-chatgpt-conversation-this-is-an-2/docker-compose.synology.yml:1)

Kurzfassung:

```bash
ssh <dein-synology-user>@<deine-synology-ip>
mkdir -p /volume1/docker/mediathek-nas/config
mkdir -p /volume1/docker/mediathek-nas/app
```

Dann vom Mac auf die Synology:

```bash
rsync -av \
  /Users/christophdudy/Documents/Codex/2026-08-12/referenced-chatgpt-conversation-this-is-an-2/ \
  <dein-synology-user>@<deine-synology-ip>:/volume1/docker/mediathek-nas/app/
```

Dann auf der Synology:

```bash
cd /volume1/docker/mediathek-nas/app
docker compose -f docker-compose.synology.yml up -d --build
docker logs mediathek-nas --tail 100
```

Danach im Browser:

```text
http://<deine-synology-ip>:8000
```

## Synology-Voraussetzungen

Automatisch in der App pruefbar ueber `System-Check`:

- Python-Laufzeit aktiv
- `yt-dlp` vorhanden
- `ffmpeg` vorhanden
- Konfigurationsordner beschreibbar
- Download-Zielordner beschreibbar
- Scheduler-Einstellung geladen
- Sidecar-Einstellungen geladen

Manuell auf dem NAS zu pruefen:

- `Container Manager` ist installiert
- Der gemeinsame Medienordner ist vorhanden
- Der Container darf auf Konfigurations- und Medienordner schreiben
- Plex, Jellyfin oder Infuse koennen denselben Medienordner lesen

Wichtig: Host-seitige DSM-Pakete und Berechtigungen kann die App im Container nicht vollautomatisch erkennen. Deshalb zeigt die Weboberflaeche diese Punkte bewusst als manuelle Synology-Checkliste an.

## Neue Funktionen im Detail

### Medienserver

- Plex kann per Basis-URL, Token und Section-ID angebunden werden
- Jellyfin kann per Basis-URL und API-Key angebunden werden
- fuer beide Server kann nach fertigen Downloads ein Scan bzw. Refresh angestossen werden
- Infuse wird ueber offizielle Deep-Links fuer `play` und `save` auf iPhone, iPad und Mac vorbereitet

### Dubletten

- neue Downloads werden global gegen vorhandene Downloads und importierte Eintraege geprueft
- bei aktiver Dublettenvermeidung wird kein zweiter Download angelegt
- erkannte Bestandsgruppen werden im Bereich `Import & Dubletten` angezeigt

### Import

- vorhandene Video-Dateien koennen aus einem Ordnerbestand eingelesen werden
- einfache `.json`- und `.txt`-Listen koennen als Download-Warteschlange importiert werden
- importierte Dateien erscheinen als abgeschlossene Eintraege in Queue und Historie

### RSS

- aktuelle Suche als RSS: `GET /api/rss/search`
- gespeicherte Regel als RSS: `GET /api/rss/rules/{id}`

## Einstellungen fuer Medienserver

Sinnvolle Defaults:

- Download-Root: `/media/fernseh-mediathek`
- Dateiname: `{date}_{channel}_{title}`
- Unterordner: `{channel}/{topic}`
- Gleichzeitige Downloads: `2`
- Auto-Retrys: `1`
- `.nfo` aktivieren
- `.info.json` aktivieren

Verfuegbare Platzhalter:

- `{date}`
- `{year}`
- `{channel}`
- `{topic}`
- `{title}`
- `{quality}`

## API-Ueberblick

- `POST /api/search`
- `GET /api/downloads`
- `POST /api/downloads`
- `POST /api/downloads/{id}/retry`
- `POST /api/downloads/{id}/cancel`
- `GET /api/rules`
- `POST /api/rules`
- `GET /api/rules/{id}/matches`
- `POST /api/rules/{id}/run`
- `POST /api/rules/run-all`
- `POST /api/rules/run-due`
- `GET /api/settings`
- `PUT /api/settings`
- `GET /api/system-check`
- `GET /api/media-servers/status`
- `POST /api/media-servers/scan`
- `GET /api/duplicates`
- `GET /api/imports`
- `POST /api/imports/filesystem`
- `POST /api/imports/list`
- `GET /api/rss/search`
- `GET /api/rss/rules/{id}`

## Oeffentliche Veroeffentlichung

Ja, das Projekt laesst sich sinnvoll oeffentlich machen:

- als GitHub-Repository
- spaeter als Container-Image
- mit deutscher und englischer Dokumentation
- mit Post in der Synology Community

Bereits vorbereitet:

- MIT-Lizenz
- deutsche README
- englische README
- Synology-spezifische Compose-Datei
- SSH-Installationsanleitung
- klare Abgrenzung gegen DRM- oder Zugangsumgehung

Vor einem wirklichen Public Release noch sinnvoll:

1. Repo-Namen finalisieren
2. Screenshots fuer Desktop und Mobil aufnehmen
3. Beispiel-Suchbegriffe und Demo-Daten dokumentieren
4. GitHub Actions fuer Tests und Build ergaenzen
5. Optional Release-Container auf GitHub Container Registry veroeffentlichen
6. UI-Texte komplett zweisprachig machen

## Englisch

Eine erste englische Projektfassung liegt hier:

[README.en.md](/Users/christophdudy/Documents/Codex/2026-08-12/referenced-chatgpt-conversation-this-is-an-2/README.en.md:1)

Die Weboberflaeche selbst ist aktuell noch ueberwiegend deutschsprachig und waere fuer eine internationale Veroeffentlichung der naechste naheliegende Schritt.

## Vergleich zu MediathekView

Nach den aktuell verfuegbaren offiziellen Quellen bieten MediathekView und MediathekViewWeb unter anderem Suche, Filter, Downloads, Abspielen, Abos beziehungsweise automatische Downloads und bei MediathekViewWeb auch RSS-Feeds. Quellen: [MediathekView GitHub](https://github.com/mediathekview), [MediathekViewWeb GitHub](https://github.com/mediathekview/mediathekviewweb), [MediathekView auf Flathub](https://flathub.org/en/apps/de.mediathekview.MediathekView).

Im Vergleich fehlen hier aktuell vor allem:

- ausgereiftere Suchsyntax und Feinfilter
- tieferes Dubletten- und Historienmanagement
- reifere Importfunktionen direkt fuer das native MediathekView-Datenformat
- komfortableres direktes Abspielen verschiedener Streamtypen
- Desktop-spezifische Workflows rund um externe Player

Staerken dieses Projekts:

- direkt fuer Synology DSM und Container Manager gedacht
- gemeinsamer Medienordner fuer Plex, Jellyfin und Infuse
- keine Desktop-Java-App notwendig
- konfigurierbare Ordner- und Dateibenennung
- vorbereitete Medienserver-Sidecars
- integrierte RSS-Feeds fuer Regeln und Suchen
- Import vorhandener Dateien und Listen
- eingebauter Deployment-Check fuer Synology-Nutzer

## Sinnvolle naechste Ausbaustufen

- zweisprachige UI
- Release-Image fuer Docker Hub oder GHCR
- nativer MediathekView-Formatimport
- bessere Metadaten-Zuordnung fuer Serien und Dokus
- Webhooks fuer Regeln
- feinere Regeltypen wie Sender-Mapping oder Themen-Sammlungen

## Quellen

- [MediathekView GitHub](https://github.com/mediathekview)
- [MediathekViewWeb GitHub](https://github.com/mediathekview/mediathekviewweb)
- [MediathekView auf Flathub](https://flathub.org/en/apps/de.mediathekview.MediathekView)
- [Synology Container Manager Package](https://www.synology.com/en-us/dsm/packages/ContainerManager)
- [Synology Container Manager Release Notes](https://www.synology.com/releaseNote/ContainerManager)
