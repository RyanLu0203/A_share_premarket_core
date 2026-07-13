from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from ashare_premarket.application.workspace.repository import PremarketWorkspaceRepository
from ashare_premarket.interfaces.registry import api_paths


ROUTES = api_paths()


def create_quant_router(repo: PremarketWorkspaceRepository) -> APIRouter:
    router = APIRouter()

    @router.get(ROUTES["quant_capabilities"])
    def quant_capabilities() -> Any:
        return repo.quant_capabilities()

    @router.get(ROUTES["experiment"])
    def experiment() -> Any:
        return repo.experiment()

    return router
