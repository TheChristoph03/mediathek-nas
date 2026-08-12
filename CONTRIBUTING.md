# Contributing

Thanks for looking. This is a small project maintained in spare time — pull
requests are welcome, and so is a good bug report.

## Before you start

For anything larger than a fix, open an issue or a discussion first. It saves
you writing code that turns out not to fit, and it saves me saying no to work
someone already did.

## Running it locally

No Docker needed for development:

```bash
git clone https://github.com/TheChristoph03/mediathek-nas.git
cd mediathek-nas
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

export APP_DATA_DIR=./data
export DOWNLOAD_ROOT=./downloads
uvicorn app.main:app --reload
```

Then open http://127.0.0.1:8000. The SQLite database is created on first start
under `APP_DATA_DIR`; delete it to get a clean slate.

`yt-dlp` and `ffmpeg` must be on your PATH for downloads to work. Search, rules
and the UI work without them.

## Running the tests

```bash
python -m unittest discover -s tests
```

They must pass before a pull request can be merged. If you change behaviour,
the test that covers it should change with it.

## Building the image

```bash
docker compose -f docker-compose.synology.yml up -d --build
```

Be warned: the `ffmpeg` apt layer takes 25–40 minutes on NAS hardware and a few
minutes on a laptop. Only rebuild when you touched the Dockerfile — for app
changes, run uvicorn directly.

## Project layout

```
app/
  api/routes.py          HTTP endpoints
  core/config.py         defaults, environment handling
  db/database.py         schema and migrations
  services/
    mediathek.py         MediathekViewWeb queries
    downloads.py         queue, yt-dlp process, sidecars
    rules.py             subscriptions
    scheduler.py         background loop
    media_servers.py     Plex, Jellyfin, Infuse
    imports.py           importing existing files
  templates/index.html   the whole UI
  static/js/app.js       all frontend logic
  static/css/styles.css  all styling
```

There is no build step for the frontend — plain HTML, CSS and JavaScript, no
bundler, no framework. That is deliberate: it keeps the image small and means
anyone can edit the UI without a Node toolchain.

## Conventions

- Comments explain *why*, not *what*. If a line needs a comment to say what it
  does, the line is usually the problem.
- Interface strings go through `t()` in `app.js` and need both a German and an
  English entry in `STRINGS`. A string only in one language will fall back to
  German and look broken to English users.
- Errors say which path or value failed. `"Unknown error"` costs someone an
  evening — this project has already paid that bill once.

## Scope

This project only handles publicly accessible content from the broadcasters'
own mediatheks, as indexed by MediathekViewWeb. Pull requests that add DRM
circumvention, bypass access restrictions, or add sources outside that scope
will be closed without discussion. That boundary is not negotiable.

## Not sure it's a bug?

Open a [discussion](https://github.com/TheChristoph03/mediathek-nas/discussions).
Setup questions about paths, UIDs and permissions are common and not
embarrassing — the Synology specifics are genuinely fiddly.
