from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter

from ashare_premarket.application.workspace.repository import PremarketWorkspaceRepository
from ashare_premarket.interfaces.api.errors import safe_call
from ashare_premarket.interfaces.registry import api_paths


ROUTES = api_paths()


def create_stocks_router(repo: PremarketWorkspaceRepository) -> APIRouter:
    router = APIRouter()

    @router.get(ROUTES["stocks"])
    def stocks(snapshot_date: Optional[str] = None) -> Any:
        rows = repo.stocks(snapshot_date)
        return {"rows": rows, "count": len(rows)}

    @router.get(ROUTES["stock"])
    def stock(symbol: str, snapshot_date: Optional[str] = None) -> Any:
        return safe_call(lambda: repo.stock(symbol.upper(), snapshot_date))

    @router.get(ROUTES["stock_market"])
    def stock_market(symbol: str, snapshot_date: Optional[str] = None) -> Any:
        return safe_call(lambda: repo.stock_market(symbol.upper(), snapshot_date))

    @router.get(ROUTES["stock_fundamentals"])
    def stock_fundamentals(symbol: str) -> Any:
        return safe_call(lambda: repo.stock_fundamentals(symbol.upper()))

    @router.get(ROUTES["stock_risk"])
    def stock_risk(symbol: str, snapshot_date: Optional[str] = None) -> Any:
        return safe_call(lambda: repo.stock_risk(symbol.upper(), snapshot_date))

    @router.get(ROUTES["stock_position"])
    def stock_position(symbol: str, snapshot_date: Optional[str] = None) -> Any:
        return safe_call(lambda: repo.stock_position(symbol.upper(), snapshot_date))

    return router
