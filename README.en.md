# Mediathek NAS

Mediathek NAS is a Synology-friendly web application for searching, previewing, downloading, and organizing content from publicly accessible media libraries using MediathekViewWeb data. It is built for Docker and Synology Container Manager and uses FastAPI, SQLite, `yt-dlp`, and `ffmpeg`.

## Status as of August 12, 2026

Already working:

- Search powered by MediathekViewWeb data
- Filters for channel, topic, date, runtime, and quality
- Detail view with preview and streaming links
- Single-download flow with queue, progress, retry, and cancel
- Parallel downloads
- Series rules and subscriptions with intervals
- Background scheduler for due rules
- Configurable file naming and subfolder templates
- `.nfo` and `.info.json` sidecars for Plex/Jellyfin preparation
- Plex and Jellyfin refresh hooks after completed downloads
- Infuse deep links for Apple devices
- Import of existing media files and simple lists
- RSS feeds for searches and saved rules
- Global duplicate detection across downloads and imports
- Responsive, denser UI for desktop, iPhone, and iPad
- Runtime and preflight checks for container tools, writable paths, and Synology prerequisites

Still missing:

- No DRM circumvention
- No support for access-restricted sources
- No multi-user model yet
- No automatic discovery of third-party Plex or Jellyfin servers
- No guaranteed 1:1 import of native MediathekView data formats yet

## Synology deployment notes

For the current DS1520+ setup there is a dedicated deployment file and SSH guide:

- `docker-compose.synology.yml`
- `outputs/synology-ssh-setup.md`

Default Synology target paths:

- App config: `/volume1/docker/mediathek-nas/config`
- Media root: `/volume1/video/Movies/Fernseh Mediathek`

Container paths:

- Config: `/config`
- Media: `/media/fernseh-mediathek`

The app can automatically verify container-side requirements through `GET /api/system-check`:

- Python runtime available
- `yt-dlp` installed
- `ffmpeg` installed
- config path writable
- download path writable
- scheduler setting loaded
- metadata sidecars enabled

Host-side DSM requirements cannot be detected reliably from inside the container, so they are exposed as manual checks in the UI:

- Container Manager installed
- shared media folder exists
- write permissions for the app and media folders
- Plex/Jellyfin/Infuse reading the same media location

Additional app endpoints now include:

- `GET /api/media-servers/status`
- `POST /api/media-servers/scan`
- `GET /api/duplicates`
- `POST /api/imports/filesystem`
- `POST /api/imports/list`
- `GET /api/rss/search`
- `GET /api/rss/rules/{id}`

## Public release readiness

This project is suitable for GitHub and for sharing with the Synology community.

Already prepared:

- MIT license
- German README
- English README
- Synology-specific Compose file
- Synology SSH installation guide
- explicit legal boundary: public, allowed sources only, no DRM bypass

Before a broader public release, the next sensible steps would be:

1. Finalize the repository name
2. Add desktop and mobile screenshots
3. Add a CI workflow for tests and image builds
4. Generalize Synology setup notes beyond a single NAS model
5. Publish a release image to GHCR or Docker Hub
6. Translate the UI itself into English

## Comparison with MediathekView

According to the current official sources, MediathekView and MediathekViewWeb already provide search, filtering, playback, downloads, subscriptions and automatic downloads, plus RSS feeds in the web project. Sources: [MediathekView GitHub](https://github.com/mediathekview), [MediathekViewWeb GitHub](https://github.com/mediathekview/mediathekviewweb), [Flathub page](https://flathub.org/en/apps/de.mediathekview.MediathekView).

Main gaps compared with MediathekView today:

- Less advanced search syntax than MediathekViewWeb
- Less mature import support for native MediathekView data formats
- Less advanced history and duplicate handling
- Less mature in-browser playback for all stream types
- No desktop-specific workflows such as VLC integration

Current strengths of this project:

- Built specifically for Synology DSM and Container Manager
- Shared media target for Plex, Jellyfin, and Infuse
- No Java desktop dependency
- Configurable naming and folder structure
- Sidecar metadata support
- RSS feeds for searches and rules
- Existing-library import support
- Built-in deployment and runtime checks
