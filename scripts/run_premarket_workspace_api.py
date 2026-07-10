from __future__ import annotations

import argparse

import uvicorn

from _bootstrap import ROOT
from ashare_premarket.dashboard.api import create_app


def main() -> int:
    parser = argparse.ArgumentParser(description="A-Share Premarket Workspace read-only API")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--check", action="store_true", help="load contracts and routes without serving")
    args = parser.parse_args()

    app = create_app(ROOT)
    if args.check:
        schema = app.openapi()
        api_routes = [path for path in schema["paths"] if path.startswith("/api/")]
        if not api_routes:
            raise RuntimeError("read-only API exposes no routes")
        for path in api_routes:
            if not set(schema["paths"][path]).issubset({"get"}):
                raise RuntimeError(f"write method exposed at {path}")
        print(f"read-only API check: PASS | routes={len(api_routes)}")
        return 0

    uvicorn.run(app, host=args.host, port=args.port, access_log=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
