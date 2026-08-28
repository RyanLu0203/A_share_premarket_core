from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

from _bootstrap import ROOT
from ashare_premarket.dashboard.api import create_app
from ashare_premarket.interfaces.api.network import require_loopback_host


FRONTEND = ROOT / "apps" / "premarket-workspace"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the local A-Share Premarket Workspace")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--api-port", type=int, default=8000)
    parser.add_argument("--web-port", type=int, default=3000)
    parser.add_argument(
        "--frontend-mode",
        choices=("production", "development"),
        default="production",
        help="Use the validated production build by default; development is explicit opt-in.",
    )
    parser.add_argument("--check", action="store_true", help="validate both services without starting them")
    args = parser.parse_args()
    args.host = require_loopback_host(args.host)

    api_url = f"http://{args.host}:{args.api_port}"
    web_url = f"http://{args.host}:{args.web_port}"
    npm = shutil.which("npm.cmd" if os.name == "nt" else "npm")
    package_file = FRONTEND / "package.json"

    app = create_app(ROOT)
    api_routes = [path for path, methods in app.openapi()["paths"].items() if path.startswith("/api/") and set(methods).issubset({"get"})]
    package = json.loads(package_file.read_text(encoding="utf-8")) if package_file.exists() else {}
    required_scripts = {"dev", "start", "build", "typecheck", "lint", "test"}
    missing_scripts = required_scripts - set(package.get("scripts", {}))
    if not api_routes:
        raise RuntimeError("read-only API exposes no GET routes")
    if missing_scripts:
        raise RuntimeError(f"frontend package is missing scripts: {sorted(missing_scripts)}")
    if npm is None:
        raise RuntimeError("npm executable is unavailable")

    if args.check:
        print(
            "workspace launcher check: PASS | "
            f"api={api_url} | frontend={web_url} | routes={len(api_routes)} | "
            f"default_frontend_mode={args.frontend_mode}"
        )
        return 0

    if args.frontend_mode == "production" and not (FRONTEND / ".next" / "BUILD_ID").is_file():
        raise RuntimeError("validated frontend production build is unavailable; run npm run build before startup")

    environment = os.environ.copy()
    environment["NEXT_PUBLIC_PREMARKET_API_URL"] = api_url
    environment["ASHARE_RUNTIME_CODE_COMMIT"] = _git_head()
    environment["ASHARE_RUNTIME_REPOSITORY_ROOT"] = str(ROOT.resolve())
    environment["HOSTNAME"] = args.host
    environment["PORT"] = str(args.web_port)
    if args.frontend_mode == "production":
        node = shutil.which("node.exe" if os.name == "nt" else "node")
        if node is None:
            raise RuntimeError("node executable is unavailable")
        frontend_command = [node, str(_prepare_standalone(FRONTEND))]
        frontend_working_directory = FRONTEND / ".next" / "standalone"
    else:
        frontend_command = [
            npm,
            "run",
            "dev",
            "--",
            "--hostname",
            args.host,
            "--port",
            str(args.web_port),
        ]
        frontend_working_directory = FRONTEND
    api = subprocess.Popen(
        [sys.executable, str(ROOT / "scripts" / "run_premarket_workspace_api.py"), "--host", args.host, "--port", str(args.api_port)],
        cwd=ROOT,
        env=environment,
    )
    frontend = subprocess.Popen(
        frontend_command,
        cwd=frontend_working_directory,
        env=environment,
    )
    print(f"A-Share Premarket Workspace: {web_url}")
    print(f"Read-only evidence API: {api_url}/docs")
    try:
        while api.poll() is None and frontend.poll() is None:
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        _stop(frontend)
        _stop(api)
    if api.returncode not in {0, None}:
        return int(api.returncode)
    if frontend.returncode not in {0, None}:
        return int(frontend.returncode)
    return 0


def _stop(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=8)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=3)


def _git_head() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    commit = result.stdout.strip()
    if len(commit) != 40:
        raise RuntimeError("unable to resolve the deployment commit SHA")
    return commit


def _prepare_standalone(frontend: Path) -> Path:
    standalone = frontend / ".next" / "standalone"
    server = standalone / "server.js"
    static = frontend / ".next" / "static"
    if not server.is_file() or not static.is_dir():
        raise RuntimeError("complete standalone frontend build is unavailable; run npm run build")
    shutil.copytree(static, standalone / ".next" / "static", dirs_exist_ok=True)
    public = frontend / "public"
    if public.is_dir():
        shutil.copytree(public, standalone / "public", dirs_exist_ok=True)
    return server


if __name__ == "__main__":
    raise SystemExit(main())
