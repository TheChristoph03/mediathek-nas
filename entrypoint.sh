#!/bin/sh
# Keep yt-dlp current without giving up a reproducible image.
#
# The image ships a pinned yt-dlp at /usr/local/bin/yt-dlp. That one is owned by
# root and cannot be replaced by the unprivileged UID the container usually runs
# as, which is deliberate: it is the fallback that always works, offline included.
#
# On start we try to fetch the current release into the writable config volume
# and put it first on PATH. If the download fails -- no internet, GitHub down,
# read-only volume -- we simply keep using the pinned binary and say so.
#
# Set YTDLP_AUTO_UPDATE=0 to switch this off and stay on the pinned version.

set -e

UPDATE_DIR="${APP_DATA_DIR:-/config}/bin"
UPDATE_BIN="$UPDATE_DIR/yt-dlp"
MAX_AGE_MINUTES="${YTDLP_UPDATE_INTERVAL_MINUTES:-1440}"

# Skip the 3 MB download when the cached binary is younger than the interval.
# Restarting the container ten times a day should not mean ten downloads.
# Written with plain if-blocks on purpose: under `set -e`, a `[ ... ] && return`
# whose test fails would abort the whole script.
needs_update() {
  if [ ! -f "$UPDATE_BIN" ]; then
    return 0
  fi
  if [ -n "$(find "$UPDATE_BIN" -mmin "+$MAX_AGE_MINUTES" 2>/dev/null)" ]; then
    return 0
  fi
  return 1
}

if [ "${YTDLP_AUTO_UPDATE:-1}" = "1" ]; then
  if ! needs_update; then
    echo "[entrypoint] cached yt-dlp is recent, skipping update ($("$UPDATE_BIN" --version 2>/dev/null || echo unknown))"
  elif mkdir -p "$UPDATE_DIR" 2>/dev/null; then
    if curl -fsSL --max-time 90 --retry 3 --retry-all-errors --retry-delay 2 \
        https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp \
        -o "$UPDATE_BIN.new" 2>/dev/null; then
      chmod +x "$UPDATE_BIN.new" 2>/dev/null || true
      mv "$UPDATE_BIN.new" "$UPDATE_BIN"
      echo "[entrypoint] yt-dlp updated to $("$UPDATE_BIN" --version 2>/dev/null || echo unknown)"
    else
      rm -f "$UPDATE_BIN.new" 2>/dev/null || true
      echo "[entrypoint] yt-dlp update failed, using bundled $(yt-dlp --version 2>/dev/null || echo unknown)"
    fi
  else
    echo "[entrypoint] config volume not writable, using bundled $(yt-dlp --version 2>/dev/null || echo unknown)"
  fi
else
  echo "[entrypoint] auto-update disabled, using bundled $(yt-dlp --version 2>/dev/null || echo unknown)"
fi

if [ -x "$UPDATE_BIN" ]; then
  PATH="$UPDATE_DIR:$PATH"
  export PATH
fi

exec "$@"
