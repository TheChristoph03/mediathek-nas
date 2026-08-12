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

![Search results, with two downloads running](docs/screenshots/search-results.png)

![The download queue](docs/screenshots/downloads-queue.png)

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

## Requirements

- A NAS or Docker host with an **x86_64** or **ARM64** CPU. Images are published
  for both; Container Manager picks the right one automatically.
- Synology DSM 7 with **Container Manager** installed, or any Docker host with
  Compose v2.
- A shared folder for your media, and one for the app's config.
- Internet access from the container: it queries MediathekViewWeb and fetches
  yt-dlp updates.

## Quick start

Roughly ten minutes, entirely in the DSM interface.

### 1. Create the config folder

In **File Station**, inside your `docker` shared folder, create:

```
docker/mediathek-nas/config
```

This must exist before you create the project. A bind mount pointing at a
missing folder makes the container refuse to start.

### 2. Find the UID and GID that own your media

Start the app once with the defaults below, open **Settings → System check**, and
it tells you the line to use — including which account owns the media folder if
that differs from the one it is running as. No SSH needed.

If you prefer to get it right the first time, over SSH:

```bash
stat -c '%u:%g' "/volume1/video/Movies/YourMediaFolder"
```

Either way you end up with something like `1026:100`. That is the account the
container should run as, so downloaded files belong to you rather than to root.

### 3. Write the compose file

In File Station, create `docker/mediathek-nas/app/docker-compose.yml` — the name
matters, Container Manager looks for exactly this file.

```yaml
services:
  mediathek-nas:
    image: ghcr.io/thechristoph03/mediathek-nas:latest
    container_name: mediathek-nas

    # From step 2.
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
        source: /volume1/docker/mediathek-nas/config      # from step 1
        target: /config
      - type: bind
        source: /volume1/video/Movies/YourMediaFolder     # your media folder
        target: /media/mediathek

    restart: unless-stopped
```

Watch the volume paths. On DSM they start with `/volume1` or `/volume2` depending
on where the shared folder lives — File Station shows this under folder
properties. A path that merely looks right will fail at start.

A ready-made copy is [`docker-compose.ghcr.yml`](docker-compose.ghcr.yml).

### 4. Create the project

**Container Manager → Project → Create**

- Project name: `mediathek-nas`
- Path: browse to `docker/mediathek-nas/app`
- Source: use the existing `docker-compose.yml`
- **Next** → skip the *Web Portal* step, nothing to configure there → **Done**

It pulls the image and starts. Under **Container**, `mediathek-nas` should read
*Running*; the log tab shows `Uvicorn running on http://0.0.0.0:8000`.

### 5. Open it

`http://<nas-ip>:8000`

Under **Settings → System check**, everything should be green. Then search for
something and use the download arrow on a result.

## Updating

**Container Manager → Project → mediathek-nas → Action → Build.** That pulls the
current image and recreates the container. Your config and database survive —
they live in the mounted config folder, not in the container.

From a shell, the same thing is:

```bash
cd /volume1/docker/mediathek-nas/app
docker compose pull && docker compose up -d
```

## Things that trip people up

**The `user:` line is not optional.** Without it the container runs as root and
every downloaded file ends up root-owned, which Plex, Jellyfin and File Station
all handle badly.

**Both bind mounts must exist.** A missing source path gives
`bind source path does not exist` and the container never starts.

**Port 8000 already taken?** Change the left side only: `- "8123:8000"` serves
the app on 8123. The right side is the port inside the container and stays 8000.

**Spaces in folder names work**, but the path must be exact, including case.

## Configuration

| Variable | Default | Meaning |
| --- | --- | --- |
| `DOWNLOAD_ROOT` | `/downloads` | Initial download location, changeable in the UI |
| `APP_DATA_DIR` | `/config` | Holds `mediathek_nas.db` |
| `HOME` | `/config` | Needed so `yt-dlp` has a writable cache directory |
| `YTDLP_AUTO_UPDATE` | `1` | Fetch the current yt-dlp on start; `0` keeps the pinned one |
| `TZ` | `Europe/Berlin` | Affects scheduler timing and log timestamps |

`DOWNLOAD_ROOT` seeds the value on a fresh install; after that the UI owns it.
Saving a path that cannot be created or written to fails with an explicit error
rather than being silently ignored.

### Keeping yt-dlp current

Broadcasters change their players regularly, and a yt-dlp release from months ago
will eventually fail on some of them. The image ships a pinned version so builds
stay reproducible, and the container fetches the current release into the config
volume on start. If that download fails — no internet, GitHub unreachable — it
falls back to the pinned binary and logs which one it is using. Set
`YTDLP_AUTO_UPDATE=0` to always stay on the pinned version.

### Naming and folders

Two templates control the layout, both editable in the UI:

- **Subfolder** — default `{channel}/{topic}`, giving `zdf-tivi/logo/…`
- **Filename** — default `{date}_{channel}_{title}`

Placeholders: `{date}`, `{year}`, `{channel}`, `{topic}`, `{title}`, `{quality}`.
Values are slugified and truncated to 80 characters.

## Features

**Search** — full MediathekViewWeb query support with filters for channel, topic, date,
runtime and quality; preview and streaming links per result. The channel picker keeps
itself current by sampling recent entries upstream.

**Interface** — German and English, switchable in the header; the initial language
follows your browser.

**Downloads** — queue with live progress, parallel workers, retry and cancel,
global duplicate detection across downloads and previously imported files.

**Rules** — saved searches with an interval; a background scheduler runs them and can
download matches automatically. Per-rule match history and RSS feed.

**Library integration** — `.nfo` and `.info.json` sidecars, Plex and Jellyfin refresh
hooks, Infuse deep links, and an importer for media you already have on disk.

**Diagnostics** — `GET /api/system-check` verifies `yt-dlp`, `ffmpeg`, and that the
config and download paths are writable from inside the container.

![Settings](docs/screenshots/settings.png)

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

`yt-dlp` is pinned in the Dockerfile so builds are reproducible; the running
container updates it on start unless you disable that.

## Contributing

Bug reports and pull requests are welcome — see
[CONTRIBUTING.md](CONTRIBUTING.md) for how to run it locally and what the tests
expect. Questions that are not bugs belong in
[Discussions](https://github.com/TheChristoph03/mediathek-nas/discussions).

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

- Tests running in CI before an image is published
- Date filtering currently happens locally after paging, so a filtered page can
  be short and the total stays unfiltered
- A folder picker in settings instead of typing a path

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
