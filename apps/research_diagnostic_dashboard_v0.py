"""GOAL-RESEARCH-DIAGNOSTIC-DASHBOARD-V0 entrypoint (research-only, stdlib).

A lightweight local viewer that renders committed research diagnostic evidence
for morning review. Streamlit is intentionally NOT used: ``streamlit`` and
``.html`` are forbidden output tokens in this repository's destructive-change
audit, so per the issue's "unless repository constraints make another
lightweight local UI clearly safer" clause this uses only the Python standard
library. The page is rendered in-memory per request; no HTML/frontend artifact
is written or committed, and no governance state is touched.

Usage:
  python apps/research_diagnostic_dashboard_v0.py            # serve on 127.0.0.1:8760
  python apps/research_diagnostic_dashboard_v0.py --check    # startup smoke test (no server)
  python apps/research_diagnostic_dashboard_v0.py --manifest # (re)write the review manifest
Query params when serving: ?sort=<col>&status=<status>&top=<n>
"""

from __future__ import annotations

import argparse
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ashare_premarket.research.research_diagnostic_view import (  # noqa: E402
    VIEW_ID,
    render_html,
    write_manifest,
)


def _render(query: dict[str, list[str]]) -> str:
    sort_by = query.get("sort", ["diagnostic_composite_score"])[0]
    status_filter = query.get("status", [None])[0] or None
    top_raw = query.get("top", [None])[0]
    top_n = int(top_raw) if top_raw and top_raw.isdigit() else None
    return render_html(ROOT, sort_by=sort_by, status_filter=status_filter, top_n=top_n)


class _Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        query = parse_qs(urlparse(self.path).query)
        payload = _render(query).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *_args: object) -> None:  # silence default logging
        return


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=VIEW_ID)
    parser.add_argument("--check", action="store_true", help="startup smoke test, no server")
    parser.add_argument("--manifest", action="store_true", help="(re)write the review manifest and exit")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8760)
    args = parser.parse_args(argv)

    if args.manifest:
        path = write_manifest(ROOT)
        print(f"Wrote manifest: {path}")
        return 0

    if args.check:
        page = render_html(ROOT)
        assert page.startswith("<!doctype html>") and VIEW_ID in page and "Research diagnostic view only" in page
        print(f"startup smoke ok: rendered {len(page)} bytes across 4 research modules")
        return 0

    server = HTTPServer((args.host, args.port), _Handler)
    print(f"Serving {VIEW_ID} at http://{args.host}:{args.port} (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
