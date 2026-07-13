from __future__ import annotations

from ashare_premarket.dashboard.repositories.portfolio_repository import PortfolioRepository
from ashare_premarket.dashboard.repositories.stock_repository import StockRepository
from ashare_premarket.dashboard.repositories.system_evidence_repository import SystemEvidenceRepository
from ashare_premarket.dashboard.services.capability_service import CapabilityService
from ashare_premarket.dashboard.services.status_service import WorkspaceStatusService


class PremarketWorkspaceRepository(
    WorkspaceStatusService,
    StockRepository,
    PortfolioRepository,
    SystemEvidenceRepository,
    CapabilityService,
):
    """Compatibility-stable facade over focused workspace read responsibilities."""
