import os
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


# Settings whose default comes from an environment variable (typically set by
# docker-compose). The environment provides the STARTING value on a fresh
# install; the user stays free to change it in the UI afterwards. Changes are
# validated on save, so a bad path fails loudly instead of silently.
ENV_DEFAULT_KEYS: dict[str, str] = {
    "download_root": "DOWNLOAD_ROOT",
}


def env_defaults() -> dict[str, str]:
    """Return the env-provided defaults that are actually set in the environment."""
    resolved: dict[str, str] = {}
    for key, env_var in ENV_DEFAULT_KEYS.items():
        raw = os.getenv(env_var)
        if raw and raw.strip():
            resolved[key] = raw.strip()
    return resolved


DEFAULT_APP_SETTINGS: dict[str, str] = {
    "download_root": os.getenv("DOWNLOAD_ROOT", str(PROJECT_ROOT / "downloads")),
    "concurrent_downloads": "2",
    "max_retries": "1",
    "skip_duplicates": "1",
    "scheduler_enabled": "1",
    "filename_template": "{date}_{channel}_{title}",
    "subfolder_template": "{channel}/{show}",
    "create_nfo_sidecar": "1",
    "create_json_sidecar": "1",
    "rule_run_limit": "15",
    "plex_enabled": "0",
    "plex_base_url": "",
    "plex_token": "",
    "plex_library_section": "",
    "plex_auto_scan": "0",
    "jellyfin_enabled": "0",
    "jellyfin_base_url": "",
    "jellyfin_api_key": "",
    "jellyfin_library_id": "",
    "jellyfin_auto_scan": "0",
    "infuse_enabled": "1",
}


@dataclass(frozen=True)
class Settings:
    app_name: str = "Mediathek NAS"
    mediathek_api_url: str = "https://mediathekviewweb.de/api/query"
    app_data_dir: str = os.getenv("APP_DATA_DIR", str(PROJECT_ROOT / "data"))
    download_root: str = os.getenv("DOWNLOAD_ROOT", DEFAULT_APP_SETTINGS["download_root"])
    page_size: int = 25
    scheduler_tick_seconds: int = 60

    @property
    def database_path(self) -> Path:
        return Path(self.app_data_dir) / "mediathek_nas.db"


settings = Settings()
