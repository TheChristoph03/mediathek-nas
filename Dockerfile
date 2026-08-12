FROM python:3.12-slim

# Pin yt-dlp for reproducible builds. "latest" means two people building on two
# different days get different binaries -- fine for local use, not for a published image.
# Find the current version with: docker exec <container> yt-dlp --version
ARG YTDLP_VERSION=2026.07.04

# NOTE: the heavy apt layer comes first on purpose. ENV lines below it can be
# changed without invalidating the ffmpeg install, which takes ~25 minutes on a NAS.
RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg ca-certificates curl \
    && if [ "$YTDLP_VERSION" = "latest" ]; then \
         curl -fsSL https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o /usr/local/bin/yt-dlp; \
       else \
         curl -fsSL "https://github.com/yt-dlp/yt-dlp/releases/download/${YTDLP_VERSION}/yt-dlp" -o /usr/local/bin/yt-dlp; \
       fi \
    && chmod +x /usr/local/bin/yt-dlp \
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

# Created world-writable so the container can run as an arbitrary UID/GID
# (docker-compose `user:`) and still write config and downloads.
RUN mkdir -p /config /downloads && chmod 777 /config /downloads

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
