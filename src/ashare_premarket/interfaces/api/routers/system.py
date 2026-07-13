from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter

from ashare_premarket.application.workspace.repository import PremarketWorkspaceRepository
from ashare_premarket.interfaces.api.errors import safe_call
from ashare_premarket.interfaces.registry import api_paths


ROUTES = api_paths()


def create_system_router(repo: PremarketWorkspaceRepository) -> APIRouter:
    router = APIRouter()

    @router.get(ROUTES["market_context"])
    def market_context(snapshot_date: Optional[str] = None) -> Any:
        return safe_call(lambda: repo.market_context(snapshot_date))

    @router.get(ROUTES["data_quality"])
    def data_quality(snapshot_date: Optional[str] = None) -> Any:
        return safe_call(lambda: repo.data_quality(snapshot_date))

    @router.get(ROUTES["provider_health"])
    def provider_health(snapshot_date: Optional[str] = None) -> Any:
        return safe_call(lambda: repo.provider_health(snapshot_date))

    @router.get(ROUTES["snapshots"])
    def snapshots() -> Any:
        return repo.snapshots()

    @router.get(ROUTES["provenance"])
    def provenance(snapshot_date: Optional[str] = None) -> Any:
        return safe_call(lambda: repo.provenance(snapshot_date))

    return router
