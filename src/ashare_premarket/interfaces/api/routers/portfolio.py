from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter

from ashare_premarket.application.workspace.repository import PremarketWorkspaceRepository
from ashare_premarket.interfaces.api.errors import safe_call
from ashare_premarket.interfaces.registry import api_paths


ROUTES = api_paths()


def create_portfolio_router(repo: PremarketWorkspaceRepository) -> APIRouter:
    router = APIRouter()

    @router.get(ROUTES["portfolio_overview"])
    def portfolio_overview(snapshot_date: Optional[str] = None) -> Any:
        return safe_call(lambda: repo.portfolio_overview(snapshot_date))

    @router.get(ROUTES["portfolio_bands"])
    def portfolio_bands(snapshot_date: Optional[str] = None) -> Any:
        return safe_call(lambda: repo.portfolio_bands(snapshot_date))

    @router.get(ROUTES["portfolio_risk"])
    def portfolio_risk(snapshot_date: Optional[str] = None) -> Any:
        return safe_call(lambda: repo.portfolio_risk(snapshot_date))

    @router.get(ROUTES["portfolio_constraints"])
    def portfolio_constraints(snapshot_date: Optional[str] = None) -> Any:
        return safe_call(lambda: repo.portfolio_constraints(snapshot_date))

    @router.get(ROUTES["portfolio_abstentions"])
    def portfolio_abstentions(snapshot_date: Optional[str] = None) -> Any:
        return safe_call(lambda: repo.portfolio_abstentions(snapshot_date))

    return router
