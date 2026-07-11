from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from ashare_premarket.dashboard.repository import PremarketWorkspaceRepository


def create_app(root: Path | None = None) -> FastAPI:
    repository_root = (root or Path(__file__).resolve().parents[3]).resolve()
    repo = PremarketWorkspaceRepository(repository_root)
    app = FastAPI(
        title="A-Share Premarket Workspace Read-Only API",
        version="1.0.0",
        description="Local research-only API over validated immutable snapshots.",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=r"^http://(?:127\.0\.0\.1|localhost)(?::\d+)?$",
        allow_credentials=False,
        allow_methods=["GET"],
        allow_headers=["*"],
    )

    def safe(call: Callable[[], Any]) -> Any:
        try:
            return call()
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "mode": "local_research_only"}

    @app.get("/api/status")
    def status(mode: str = Query("live", pattern="^(live|replay)$"), snapshot_date: Optional[str] = None) -> Any:
        return safe(lambda: repo.status(mode, snapshot_date))

    @app.get("/api/command-center")
    def command_center(mode: str = Query("live", pattern="^(live|replay)$"), snapshot_date: Optional[str] = None) -> Any:
        return safe(lambda: repo.command_center(mode, snapshot_date))

    @app.get("/api/watchlists")
    def watchlists() -> Any:
        return repo.watchlist_seed()

    @app.get("/api/stocks")
    def stocks(snapshot_date: Optional[str] = None) -> Any:
        return safe(lambda: {"rows": repo.stocks(snapshot_date), "count": len(repo.stocks(snapshot_date))})

    @app.get("/api/stocks/{symbol}")
    def stock(symbol: str, snapshot_date: Optional[str] = None) -> Any:
        return safe(lambda: repo.stock(symbol.upper(), snapshot_date))

    @app.get("/api/stocks/{symbol}/market")
    def stock_market(symbol: str, snapshot_date: Optional[str] = None) -> Any:
        return safe(lambda: repo.stock_market(symbol.upper(), snapshot_date))

    @app.get("/api/stocks/{symbol}/fundamentals")
    def stock_fundamentals(symbol: str) -> Any:
        return safe(lambda: repo.stock_fundamentals(symbol.upper()))

    @app.get("/api/stocks/{symbol}/risk")
    def stock_risk(symbol: str, snapshot_date: Optional[str] = None) -> Any:
        return safe(lambda: repo.stock_risk(symbol.upper(), snapshot_date))

    @app.get("/api/stocks/{symbol}/position")
    def stock_position(symbol: str, snapshot_date: Optional[str] = None) -> Any:
        return safe(lambda: repo.stock_position(symbol.upper(), snapshot_date))

    @app.get("/api/portfolio/overview")
    def portfolio_overview(snapshot_date: Optional[str] = None) -> Any:
        return safe(lambda: repo.portfolio_overview(snapshot_date))

    @app.get("/api/portfolio/bands")
    def portfolio_bands(snapshot_date: Optional[str] = None) -> Any:
        return safe(lambda: repo.portfolio_bands(snapshot_date))

    @app.get("/api/portfolio/risk")
    def portfolio_risk(snapshot_date: Optional[str] = None) -> Any:
        return safe(lambda: repo.portfolio_risk(snapshot_date))

    @app.get("/api/portfolio/constraints")
    def portfolio_constraints(snapshot_date: Optional[str] = None) -> Any:
        return safe(lambda: repo.portfolio_constraints(snapshot_date))

    @app.get("/api/portfolio/abstentions")
    def portfolio_abstentions(snapshot_date: Optional[str] = None) -> Any:
        return safe(lambda: repo.portfolio_abstentions(snapshot_date))

    @app.get("/api/market/context")
    def market_context(snapshot_date: Optional[str] = None) -> Any:
        return safe(lambda: repo.market_context(snapshot_date))

    @app.get("/api/quant/capabilities")
    def quant_capabilities() -> Any:
        return repo.quant_capabilities()

    @app.get("/api/experiment")
    def experiment() -> Any:
        return repo.experiment()

    @app.get("/api/data-quality")
    def data_quality(snapshot_date: Optional[str] = None) -> Any:
        return safe(lambda: repo.data_quality(snapshot_date))

    @app.get("/api/provider-health")
    def provider_health(snapshot_date: Optional[str] = None) -> Any:
        return safe(lambda: repo.provider_health(snapshot_date))

    @app.get("/api/snapshots")
    def snapshots() -> Any:
        return repo.snapshots()

    @app.get("/api/provenance")
    def provenance(snapshot_date: Optional[str] = None) -> Any:
        return safe(lambda: repo.provenance(snapshot_date))

    return app


app = create_app()
