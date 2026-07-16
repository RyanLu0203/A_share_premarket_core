from __future__ import annotations

import hashlib
import json
from pathlib import Path

from ashare_premarket.providers.governed_stock_history import (
    POLICY_PATH,
    audit_independent_verification,
    load_policy,
)

AMOUNT_CONSUMER_AUDIT_PATH = "configs/providers/tencent_amount_consumer_audit_v1.json"


def audit_tencent_primary_operational_contract(root: Path) -> dict[str, object]:
    policy = load_policy(root)
    consumer_path = root / AMOUNT_CONSUMER_AUDIT_PATH
    inventory = json.loads(consumer_path.read_text(encoding="utf-8"))
    consumer_results: list[dict[str, object]] = []
    for consumer in inventory["consumers"]:
        path = root / str(consumer["path"])
        body = path.read_text(encoding="utf-8") if path.exists() else ""
        missing = [token for token in consumer["required_tokens"] if token not in body]
        consumer_results.append(
            {
                "path": consumer["path"],
                "scope": consumer["scope"],
                "disposition": consumer["disposition"],
                "status": "PASS" if path.exists() and not missing else "BLOCKED",
                "missing_required_tokens": missing,
            }
        )

    verification = audit_independent_verification(root, policy, set())
    checks = {
        "tencent_operational_primary": policy["operational_primary"]["upstream"] == "Tencent",
        "tencent_direct_function": policy["operational_primary"]["function"] == "stock_zh_a_hist_tx",
        "east_money_probe_only": policy["east_money"]["mode"] == "probe_only",
        "east_money_canonical_requests_zero": policy["east_money"]["canonical_request_count_required"] == 0,
        "automatic_failback_forbidden": policy["automatic_failback_to_east_money"] is False,
        "qfq_only": policy["adjustment_policy"] == "qfq",
        "hfq_unsupported_disabled": policy["non_production_adjustments"]["hfq_status"] == "UNSUPPORTED_DISABLED",
        "amount_unavailable_not_zero": inventory["canonical_amount_state"] == "UNAVAILABLE_NULL_NOT_ZERO",
        "all_amount_consumers_safe": all(result["status"] == "PASS" for result in consumer_results),
        "independent_verification": verification["status"] == "PASS",
        "independent_rows_never_canonical": verification["canonical_row_contribution_count"] == 0,
    }
    return {
        "contract_id": "issue36-tencent-primary-operational-hardening-v1",
        "status": "PASS" if all(checks.values()) else "BLOCKED",
        "checks": checks,
        "amount_consumer_inventory": consumer_results,
        "amount_consumer_inventory_checksum": hashlib.sha256(consumer_path.read_bytes()).hexdigest(),
        "provider_policy_path": POLICY_PATH,
        "provider_policy_checksum": hashlib.sha256((root / POLICY_PATH).read_bytes()).hexdigest(),
        "independent_verification": verification,
        "deployment_performed": False,
        "services_started": False,
    }
