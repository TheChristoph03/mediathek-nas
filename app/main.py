from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.routes import api_router
from app.core.config import DEFAULT_APP_SETTINGS, settings
from app.db.database import database
from app.services.downloads import download_manager
from app.services.scheduler import scheduler


BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@asynccontextmanager
async def lifespan(_: FastAPI):
    database.initialize()
    await download_manager.start()
    await scheduler.start()
    try:
        yield
    finally:
        await scheduler.stop()
        await download_manager.stop()


app = FastAPI(
    title="Mediathek NAS",
    description="Synology-friendly web app for public mediathek search and downloads.",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(api_router, prefix="/api")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def index(request: Request):
    return templates.TemplateResponse(
        name="index.html",
        context={
            "request": request,
            "app_name": settings.app_name,
            "default_download_root": DEFAULT_APP_SETTINGS["download_root"],
        },
    )
