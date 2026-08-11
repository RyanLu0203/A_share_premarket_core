from __future__ import annotations

import argparse
import json

from _bootstrap import ROOT

from ashare_premarket.providers.ifind_http import (
    IfindCredentials,
    IfindHttpClient,
    IfindProviderError,
    ifind_readiness,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Check the bounded iFinD AI financial-data adapter without printing credentials."
    )
    parser.add_argument(
        "--live-auth",
        action="store_true",
        help="Verify access-token exchange only. Requires both network opt-ins and rotated env-only credentials.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    contract = ROOT / "configs/providers/ifind_ai_financial_data_service_contract.yaml"
    try:
        json.loads(contract.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        print(
            json.dumps(
                {"status": "BLOCKED", "failure_code": "IFIND_CONTRACT_INVALID"},
                ensure_ascii=False,
            )
        )
        return 1

    result = {"status": "PASS", "contract_valid": True, "readiness": ifind_readiness()}
    if args.live_auth:
        credentials = IfindCredentials.from_environment()
        if not credentials.refresh_token:
            result.update(
                {
                    "status": "BLOCKED",
                    "failure_code": "IFIND_REFRESH_TOKEN_REQUIRED_FOR_AUTH_PROBE",
                    "token_value_exposed": False,
                    "token_persisted": False,
                }
            )
            print(json.dumps(result, ensure_ascii=False, sort_keys=True))
            return 1
        try:
            IfindHttpClient(
                credentials=IfindCredentials(refresh_token=credentials.refresh_token)
            ).get_access_token()
        except IfindProviderError as exc:
            result.update(
                {
                    "status": "BLOCKED",
                    "failure_code": exc.failure_code,
                    "http_status": exc.http_status,
                    "token_value_exposed": False,
                    "token_persisted": False,
                }
            )
            print(json.dumps(result, ensure_ascii=False, sort_keys=True))
            return 1
        result.update(
            {
                "live_auth_verified": True,
                "token_value_exposed": False,
                "token_persisted": False,
            }
        )
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
