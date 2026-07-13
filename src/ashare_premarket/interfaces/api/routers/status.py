from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Query

from ashare_premarket.application.workspace.repository import PremarketWorkspaceRepository
from ashare_premarket.interfaces.api.errors import safe_call
from ashare_premarket.interfaces.registry import api_paths


ROUTES = api_paths()


def create_status_router(repo: PremarketWorkspaceRepository) -> APIRouter:
    router = APIRouter()

    @router.get(ROUTES["health"])
    def health() -> dict[str, str]:
        return {"status": "ok", "mode": "local_research_only"}

    @router.get(ROUTES["status"])
    def status(mode: str = Query("live", pattern="^(live|replay)$"), snapshot_date: Optional[str] = None) -> Any:
        return safe_call(lambda: repo.status(mode, snapshot_date))

    @router.get(ROUTES["command_center"])
    def command_center(mode: str = Query("live", pattern="^(live|replay)$"), snapshot_date: Optional[str] = None) -> Any:
        return safe_call(lambda: repo.command_center(mode, snapshot_date))

    @router.get(ROUTES["watchlists"])
    def watchlists() -> Any:
        return repo.watchlist_seed()

    return router
