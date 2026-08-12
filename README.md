# Mediathek NAS

A self-hosted web app that searches the German public broadcasters' mediatheks and
downloads shows straight into your NAS media library — named, foldered, and tagged
so Plex, Jellyfin and Infuse pick them up without further work.

Built for Synology DSM and Container Manager. FastAPI + SQLite + `yt-dlp` + `ffmpeg`,
one container, no Java, no desktop client.

> **Search data comes from [MediathekViewWeb](https://mediathekviewweb.de), part of the
> [MediathekView](https://github.com/mediathekview) project.** All the hard work of
> aggregating and indexing the broadcasters' catalogues is theirs. This project is not
> affiliated with them — it is a NAS-shaped front end built on top of the public API
> they generously provide. If you use this, go star their repositories.

## Why this exists

MediathekView is excellent, and if you want a desktop application you should use it
instead. This project solves a different problem: **the show should already be on the
NAS by the time you sit down on the sofa.**

- Runs headless, 24/7, in a container — no desktop app to open
- Rules with intervals: define a series once, new episodes download themselves
- Writes directly into your existing media folder with `.nfo` and `.info.json` sidecars
- Triggers a Plex or Jellyfin library refresh when a download finishes
- Generates Infuse deep links for Apple TV, iPhone and iPad
- Responsive UI, so you can queue something from your phone

Roughly: MediathekView is the desktop client, this is the always-on library filler.

## Quick start (prebuilt image)

No build required. Create a folder on your NAS, put this `docker-compose.yml` in it,
adjust the three marked values, then point Container Manager → **Project** → **Create**
at that folder. Skip the "Web Portal" step in the wizard.

```yaml
services:
  mediathek-nas:
    image: ghcr.io/thechristoph03/mediathek-nas:latest
    container_name: mediathek-nas

    # CHANGE ME: the UID:GID that should own downloaded files.
    # Find yours with: stat -c '%u:%g' /volume1/video/YourMediaFolder
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
        source: /volume1/docker/mediathek-nas/config   # CHANGE ME
        target: /config
      - type: bind
        source: /volume1/video/Movies/Mediathek        # CHANGE ME
        target: /media/mediathek

    restart: unless-stopped
```

Then open `http://<nas-ip>:8000`.

A ready-made copy of this file ships as [`docker-compose.ghcr.yml`](docker-compose.ghcr.yml).

### The `user:` line is not optional

Without it the container runs as root and every downloaded file ends up root-owned,
which Plex, Jellyfin and File Station all handle badly. Set it to the UID/GID that owns
your media folder.

### Both bind mounts must exist and be writable

The config mount holds the SQLite database. If the path does not exist, the container
will refuse to start with a `bind source path does not exist` error.

## Configuration

| Variable | Default | Meaning |
| --- | --- | --- |
| `DOWNLOAD_ROOT` | `/downloads` | Where downloads are written, inside the container |
| `APP_DATA_DIR` | `/config` | Holds `mediathek_nas.db` |
| `HOME` | `/config` | Needed so `yt-dlp` has a writable cache directory |
| `TZ` | `Europe/Berlin` | Affects scheduler timing and log timestamps |

`DOWNLOAD_ROOT` is **environment-managed**: whatever the container environment says wins
over the stored value on every start, and the field is read-only in the UI. This is
deliberate — in a container you configure the path with a volume mount, not by typing it
into a form. Everything else is configured in the UI and persisted in the database.

### Naming and folders

Two templates control the layout, both editable in the UI:

- **Subfolder** — default `{channel}/{topic}`, giving `zdf-tivi/logo/…`
- **Filename** — default `{date}_{channel}_{title}`

Placeholders: `{date}`, `{year}`, `{channel}`, `{topic}`, `{title}`, `{quality}`.
Values are slugified and truncated to 80 characters.

## Features

**Search** — full MediathekViewWeb query support with filters for channel, topic, date,
runtime and quality; preview and streaming links per result.

**Downloads** — queue with live progress, parallel workers, retry and cancel,
global duplicate detection across downloads and previously imported files.

**Rules** — saved searches with an interval; a background scheduler runs them and can
download matches automatically. Per-rule match history and RSS feed.

**Library integration** — `.nfo` and `.info.json` sidecars, Plex and Jellyfin refresh
hooks, Infuse deep links, and an importer for media you already have on disk.

**Diagnostics** — `GET /api/system-check` verifies `yt-dlp`, `ffmpeg`, and that the
config and download paths are writable from inside the container.

## Building from source

```bash
git clone https://github.com/TheChristoph03/mediathek-nas.git
cd mediathek-nas
docker compose -f docker-compose.synology.yml up -d --build
```

Be warned: the `ffmpeg` apt layer takes roughly 25–40 minutes on NAS hardware. Using the
prebuilt image is strongly preferred unless you are changing the Dockerfile.

Running locally without Docker:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
python -m unittest discover -s tests
```

`yt-dlp` is pinned in the Dockerfile for reproducible builds. Because broadcasters change
their sites, a pinned version will eventually stop working for some sources — the pin gets
bumped with each release.

## Scope and limits

This project only handles **publicly accessible content from the broadcasters' own
mediatheks**, as indexed by MediathekViewWeb. It does not circumvent DRM, does not bypass
access restrictions, and has no mechanism to do so. German public broadcaster content is
funded by licence fee and published for public retrieval; downloading it for private use
is what this tool does. Redistribution is your responsibility, not the tool's.

Also not present: multi-user accounts, authentication of any kind (do not expose this to
the internet), automatic discovery of Plex or Jellyfin servers, and import of native
MediathekView data formats.

## Roadmap

- `linux/arm64` images for ARM-based Synology models
- UI and UX rework — denser layout, better mobile ergonomics
- English UI
- Folder picker in settings
- Screenshots

## Credits

- [MediathekView](https://github.com/mediathekview) and
  [MediathekViewWeb](https://github.com/mediathekview/mediathekviewweb) — the search
  index this app runs on
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) — the download engine
- [FastAPI](https://fastapi.tiangolo.com) and [Uvicorn](https://www.uvicorn.org)

## License

MIT. See [LICENSE](LICENSE).

---

🇩🇪 [Deutsche Fassung](README.de.md)
