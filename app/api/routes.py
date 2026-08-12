from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import Response

from app.models.schemas import (
    DownloadCreateRequest,
    ImportFilesystemRequest,
    ImportListRequest,
    RuleCreateRequest,
    RuleRunRequest,
    SearchRequest,
    SettingsUpdateRequest,
)
from app.services.channels import channel_service
from app.services.downloads import download_manager
from app.services.imports import import_service
from app.services.mediathek import mediathek_service
from app.services.media_servers import media_server_service
from app.services.rss import rss_service
from app.services.rules import rule_service
from app.services.scheduler import scheduler
from app.services.system_check import system_check_service


api_router = APIRouter()


@api_router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@api_router.post("/search")
async def search(payload: SearchRequest) -> dict:
    try:
        response = await mediathek_service.search(payload)
        response["results"] = download_manager.annotate_library_state(response["results"])
        return response
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"Search failed: {exc}") from exc


@api_router.get("/downloads")
async def list_downloads() -> dict[str, list[dict]]:
    return {"items": download_manager.list_downloads()}


@api_router.post("/downloads", status_code=201)
async def create_download(payload: DownloadCreateRequest) -> dict:
    if not payload.source_url:
        raise HTTPException(status_code=400, detail="No downloadable source URL available for this item.")
    try:
        return download_manager.create_download(payload.model_dump())
    except PermissionError as exc:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Zielordner '{exc.filename or download_manager.get_download_root()}' ist nicht "
                "beschreibbar. Prüfe den Download-Root in den Einstellungen sowie die "
                "Rechte des gemounteten Verzeichnisses."
            ),
        ) from exc
    except OSError as exc:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Zielordner '{exc.filename or download_manager.get_download_root()}' konnte nicht "
                f"angelegt werden: {exc.strerror or exc}"
            ),
        ) from exc


@api_router.get("/settings")
async def get_settings() -> dict:
    data = download_manager.get_settings()
    data["container_defaults"] = download_manager.container_default_settings()
    return data


@api_router.put("/settings")
async def update_settings(payload: SettingsUpdateRequest) -> dict:
    try:
        return await download_manager.update_settings(payload.model_dump(exclude_none=True))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@api_router.post("/downloads/{download_id}/retry")
async def retry_download(download_id: int) -> dict:
    item = download_manager.retry_download(download_id)
    if not item:
        raise HTTPException(status_code=404, detail="Download not found.")
    return item


@api_router.post("/downloads/{download_id}/cancel")
async def cancel_download(download_id: int) -> dict:
    item = await download_manager.cancel_download(download_id)
    if not item:
        raise HTTPException(status_code=404, detail="Download not found.")
    return item


@api_router.delete("/downloads/{download_id}", status_code=204)
async def delete_download(download_id: int) -> None:
    if not download_manager.delete_download(download_id):
        raise HTTPException(status_code=404, detail="Download not found.")


@api_router.get("/rules")
async def list_rules() -> dict[str, list[dict]]:
    return {"items": rule_service.list_rules()}


@api_router.post("/rules", status_code=201)
async def create_rule(payload: RuleCreateRequest) -> dict:
    try:
        return rule_service.create_rule(payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@api_router.get("/rules/{rule_id}/matches")
async def list_rule_matches(rule_id: int) -> dict[str, list[dict]]:
    if not rule_service.get_rule(rule_id):
        raise HTTPException(status_code=404, detail="Rule not found.")
    return {"items": rule_service.list_rule_matches(rule_id)}


@api_router.get("/duplicates")
async def list_duplicates() -> dict[str, list[dict]]:
    return {"items": download_manager.list_duplicates()}


@api_router.get("/imports")
async def list_import_runs() -> dict[str, list[dict]]:
    return {"items": import_service.list_runs()}


@api_router.post("/imports/filesystem")
async def import_filesystem(payload: ImportFilesystemRequest) -> dict:
    try:
        return import_service.import_filesystem(payload.source_path, payload.max_files)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@api_router.post("/imports/list")
async def import_list(payload: ImportListRequest) -> dict:
    try:
        return import_service.import_list(payload.source_path)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@api_router.post("/rules/{rule_id}/run")
async def run_rule(rule_id: int, payload: RuleRunRequest) -> dict:
    try:
        return await rule_service.run_rule(rule_id, limit=payload.limit)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@api_router.post("/rules/run-all")
async def run_all_rules(payload: RuleRunRequest) -> dict:
    return await rule_service.run_all_enabled_rules(limit=payload.limit)


@api_router.post("/rules/run-due")
async def run_due_rules(payload: RuleRunRequest) -> dict:
    return await scheduler.run_due_rules()


@api_router.get("/channels")
async def list_channels(refresh: bool = False) -> dict:
    """Broadcasters currently present in the index.

    Refreshed lazily: the first request after 24 hours pays for one upstream
    call, everything else is served from the local cache.
    """
    if refresh or channel_service.is_stale():
        result = await channel_service.refresh()
        return {"items": result["channels"], "refreshed": result["refreshed"], "reason": result.get("reason")}
    return {"items": channel_service.list_channels(), "refreshed": False}


@api_router.get("/system-check")
async def system_check() -> dict:
    return system_check_service.run()


@api_router.get("/media-servers/status")
async def media_server_status() -> dict:
    return await media_server_service.get_status()


@api_router.post("/media-servers/scan")
async def media_server_scan() -> dict:
    return await media_server_service.trigger_scans()


@api_router.get("/rss/search")
async def rss_search(
    request: Request,
    query: str = "",
    channel: str = "",
    topic: str = "",
    start_date: str | None = None,
    end_date: str | None = None,
    min_duration_minutes: int | None = None,
    max_duration_minutes: int | None = None,
    quality: str = "best",
) -> Response:
    payload = SearchRequest(
        query=query,
        channel=channel,
        topic=topic,
        start_date=start_date,
        end_date=end_date,
        min_duration_minutes=min_duration_minutes,
        max_duration_minutes=max_duration_minutes,
        quality=quality,
        size=25,
        offset=0,
    )
    try:
        response = await mediathek_service.search(payload)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"Search failed: {exc}") from exc
    xml = rss_service.build_feed(
        title=f"Mediathek NAS Suche: {payload.query or payload.channel or payload.topic or 'Alle'}",
        description="RSS-Feed fuer eine Mediathek-Suche",
        items=response["results"],
        feed_url=str(request.url),
    )
    return Response(content=xml, media_type="application/rss+xml")


@api_router.get("/rss/rules/{rule_id}")
async def rss_rule_feed(request: Request, rule_id: int) -> Response:
    rule = rule_service.get_rule(rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found.")
    items = rule_service.list_rule_matches(rule_id, limit=50)
    xml = rss_service.build_feed(
        title=f"Mediathek NAS Regel: {rule['name']}",
        description="RSS-Feed fuer gespeicherte Regel-Treffer",
        items=items,
        feed_url=str(request.url),
    )
    return Response(content=xml, media_type="application/rss+xml")
