FROM python:3.12-slim

# Pin yt-dlp for reproducible builds. "latest" means two people building on two
# different days get different binaries -- fine for local use, not for a published image.
# Find the current version with: docker exec <container> yt-dlp --version
ARG YTDLP_VERSION=2026.07.04

# NOTE: the heavy apt layer comes first on purpose. ENV lines below it can be
# changed without invalidating the ffmpeg install, which takes ~25 minutes on a NAS.
# curl retries because a single dropped connection to GitHub would otherwise fail
# the whole build -- exit 56 on a CI runner cost one run already.
RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg ca-certificates curl \
    && if [ "$YTDLP_VERSION" = "latest" ]; then \
         YTDLP_URL="https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp"; \
       else \
         YTDLP_URL="https://github.com/yt-dlp/yt-dlp/releases/download/${YTDLP_VERSION}/yt-dlp"; \
       fi \
    && curl -fsSL --retry 5 --retry-all-errors --retry-delay 3 --connect-timeout 20 \
         "$YTDLP_URL" -o /usr/local/bin/yt-dlp \
    && chmod +x /usr/local/bin/yt-dlp \
    && /usr/local/bin/yt-dlp --version \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_DATA_DIR=/config \
    DOWNLOAD_ROOT=/downloads \
    HOME=/config \
    TZ=Europe/Berlin

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY README.md .
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Created world-writable so the container can run as an arbitrary UID/GID
# (docker-compose `user:`) and still write config and downloads.
RUN mkdir -p /config /downloads && chmod 777 /config /downloads

EXPOSE 8000

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
