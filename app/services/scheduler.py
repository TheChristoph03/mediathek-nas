from __future__ import annotations

import asyncio

from app.core.config import settings
from app.services.app_settings import app_settings_service
from app.services.rules import rule_service


class RuleScheduler:
    def __init__(self) -> None:
        self.task: asyncio.Task | None = None
        self.running = False
        self.lock = asyncio.Lock()

    async def start(self) -> None:
        self.running = True
        self.task = asyncio.create_task(self._loop(), name="rule-scheduler")

    async def stop(self) -> None:
        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass

    async def _loop(self) -> None:
        while self.running:
            try:
                await self.run_due_rules()
            except Exception:
                pass
            await asyncio.sleep(settings.scheduler_tick_seconds)

    async def run_due_rules(self) -> dict:
        async with self.lock:
            app_settings = app_settings_service.get_all()
            if not app_settings["scheduler_enabled"]:
                return {"items": []}
            return await rule_service.run_due_rules(limit=app_settings["rule_run_limit"])


scheduler = RuleScheduler()
