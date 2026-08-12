from typing import Literal

from pydantic import BaseModel, Field


QualityChoice = Literal["best", "high", "medium", "low"]


class SearchRequest(BaseModel):
    query: str = Field(default="", max_length=200)
    channel: str = Field(default="", max_length=100)
    topic: str = Field(default="", max_length=100)
    start_date: str | None = None
    end_date: str | None = None
    min_duration_minutes: int | None = Field(default=None, ge=0)
    max_duration_minutes: int | None = Field(default=None, ge=0)
    quality: QualityChoice = "best"
    offset: int = Field(default=0, ge=0)
    size: int = Field(default=25, ge=1, le=50)


class DownloadCreateRequest(BaseModel):
    title: str
    channel: str | None = None
    topic: str | None = None
    description: str | None = None
    website_url: str | None = None
    preview_url: str | None = None
    subtitle_url: str | None = None
    source_url: str
    quality: QualityChoice = "best"
    air_date: str | None = None
    duration_seconds: int | None = None
    target_directory: str | None = None
    filename_template: str | None = None
    folder_template: str | None = None
    external_id: str | None = None
    format_hint: str | None = None
    metadata: dict = Field(default_factory=dict)


class SettingsUpdateRequest(BaseModel):
    download_root: str | None = None
    concurrent_downloads: int | None = Field(default=None, ge=1, le=5)
    max_retries: int | None = Field(default=None, ge=0, le=5)
    skip_duplicates: bool | None = None
    scheduler_enabled: bool | None = None
    filename_template: str | None = Field(default=None, min_length=3, max_length=200)
    subfolder_template: str | None = Field(default=None, max_length=200)
    create_nfo_sidecar: bool | None = None
    create_json_sidecar: bool | None = None
    rule_run_limit: int | None = Field(default=None, ge=1, le=100)
    plex_enabled: bool | None = None
    plex_base_url: str | None = Field(default=None, max_length=200)
    plex_token: str | None = Field(default=None, max_length=300)
    plex_library_section: str | None = Field(default=None, max_length=50)
    plex_auto_scan: bool | None = None
    jellyfin_enabled: bool | None = None
    jellyfin_base_url: str | None = Field(default=None, max_length=200)
    jellyfin_api_key: str | None = Field(default=None, max_length=300)
    jellyfin_library_id: str | None = Field(default=None, max_length=100)
    jellyfin_auto_scan: bool | None = None
    infuse_enabled: bool | None = None


class RuleCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    query: str = Field(default="", max_length=200)
    channel: str = Field(default="", max_length=100)
    topic: str = Field(default="", max_length=100)
    quality: QualityChoice = "best"
    min_duration_minutes: int | None = Field(default=None, ge=0)
    max_duration_minutes: int | None = Field(default=None, ge=0)
    target_directory: str | None = None
    keep_latest: int | None = Field(default=None, ge=1, le=500)
    interval_minutes: int = Field(default=180, ge=5, le=1440)
    folder_template: str | None = Field(default=None, max_length=200)
    filename_template: str | None = Field(default=None, max_length=200)
    auto_download: bool = False
    enabled: bool = True


class RuleRunRequest(BaseModel):
    limit: int = Field(default=15, ge=1, le=100)


class ImportFilesystemRequest(BaseModel):
    source_path: str = Field(min_length=1, max_length=400)
    max_files: int = Field(default=500, ge=1, le=5000)


class ImportListRequest(BaseModel):
    source_path: str = Field(min_length=1, max_length=400)
