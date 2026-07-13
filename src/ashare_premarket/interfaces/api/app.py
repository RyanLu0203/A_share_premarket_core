from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ashare_premarket.application.workspace.repository import PremarketWorkspaceRepository
from ashare_premarket.interfaces.api.routers.portfolio import create_portfolio_router
from ashare_premarket.interfaces.api.routers.quant import create_quant_router
from ashare_premarket.interfaces.api.routers.status import create_status_router
from ashare_premarket.interfaces.api.routers.stocks import create_stocks_router
from ashare_premarket.interfaces.api.routers.system import create_system_router


def create_app(root: Path | None = None) -> FastAPI:
    repository_root = (root or Path(__file__).resolve().parents[4]).resolve()
    repo = PremarketWorkspaceRepository(repository_root)
    application = FastAPI(
        title="A-Share Premarket Workspace Read-Only API",
        version="1.0.0",
        description="Local research-only API over validated immutable snapshots.",
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origin_regex=r"^http://(?:127\.0\.0\.1|localhost)(?::\d+)?$",
        allow_credentials=False,
        allow_methods=["GET"],
        allow_headers=["*"],
    )
    application.include_router(create_status_router(repo))
    application.include_router(create_stocks_router(repo))
    application.include_router(create_portfolio_router(repo))
    application.include_router(create_quant_router(repo))
    application.include_router(create_system_router(repo))
    return application


app = create_app()
