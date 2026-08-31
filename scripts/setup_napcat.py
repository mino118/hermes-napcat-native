"""One-command Windows setup helper for Hermes + NapCat.

This script downloads the official NapCat Shell release, creates a local
OneBot 11 configuration, configures Hermes, and starts both processes.
It never stores credentials in this repository.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import secrets
import shutil
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path

OWNER = "NapNeko"
REPO = "NapCatQQ"
DEFAULT_VERSION = "v4.18.19"
DEFAULT_WS_PORT = 18800
DEFAULT_HTTP_PORT = 18801


def find_qq_executable(candidates: list[Path] | None = None) -> Path | None:
    """Return the first existing QQ executable from common Windows paths."""
    candidates = candidates or [
        Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "Tencent/QQ/Bin/QQ.exe",
        Path(os.environ.get("ProgramFiles(x86)", "C:/Program Files (x86)")) / "Tencent/QQ/Bin/QQ.exe",
        Path("D:/Tencent/QQNT/QQ.exe"),
        Path("D:/Tencent/QQ/QQ.exe"),
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def build_onebot_config(
    *, ws_port: int, http_port: int, http_token: str, ws_token: str
) -> dict:
    """Build NapCat's OneBot 11 network configuration."""
    return {
        "network": {
            "httpServers": [{
                "enable": True, "name": "HermesHTTP", "host": "127.0.0.1",
                "port": http_port, "enableCors": False, "enableWebsocket": True,
                "messagePostFormat": "array", "token": http_token, "debug": False,
            }],
            "httpSseServers": [], "httpClients": [], "websocketServers": [],
            "websocketClients": [{
                "enable": True, "name": "HermesNapCat",
                "url": f"ws://127.0.0.1:{ws_port}",
                "reportSelfMessage": False, "messagePostFormat": "array",
                "token": ws_token, "debug": False, "heartInterval": 30000,
                "reconnectInterval": 5000, "verifyCertificate": True,
            }],
            "plugins": [],
        }
    }


def download_release(version: str, destination: Path) -> Path:
    destination.mkdir(parents=True, exist_ok=True)
    archive = destination / f"NapCat.Shell.{version}.zip"
    url = f"https://github.com/{OWNER}/{REPO}/releases/download/{version}/NapCat.Shell.zip"
    print(f"Downloading NapCat {version}...")
    urllib.request.urlretrieve(url, archive)
    return archive


def configure_hermes(hermes: str, *, http_port: int, ws_port: int, token: str) -> None:
    values = [
        ("platforms.napcat.enabled", "true"),
        ("platforms.napcat.extra.http_api", f"http://127.0.0.1:{http_port}"),
        ("platforms.napcat.extra.ws_port", str(ws_port)),
        ("platforms.napcat.extra.access_token", token),
        ("platforms.napcat.extra.dm_policy", "allowlist"),
        ("platforms.napcat.extra.group_policy", "allowlist"),
    ]
    for key, value in values:
        subprocess.run([hermes, "config", "set", key, value], check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Set up Hermes with NapCat on Windows")
    parser.add_argument("--version", default=DEFAULT_VERSION, help="NapCat release tag")
    parser.add_argument("--hermes", default="hermes", help="Hermes executable")
    parser.add_argument("--qq-path", type=Path, help="QQ.exe path, if auto-detection fails")
    parser.add_argument("--root", type=Path, help="NapCat installation directory")
    parser.add_argument("--ws-port", type=int, default=DEFAULT_WS_PORT)
    parser.add_argument("--http-port", type=int, default=DEFAULT_HTTP_PORT)
    parser.add_argument("--token", default="", help="OneBot token; generated locally if omitted")
    parser.add_argument("--no-start", action="store_true", help="Configure only")
    args = parser.parse_args()

    if platform.system() != "Windows":
        print("This helper currently targets Windows NapCat Shell.", file=sys.stderr)
        return 2
    qq = args.qq_path or find_qq_executable()
    if not qq:
        print("QQ.exe was not found. Re-run with --qq-path C:/path/to/QQ.exe", file=sys.stderr)
        return 2
    if not shutil.which(args.hermes) and not Path(args.hermes).exists():
        print(f"Hermes executable not found: {args.hermes}", file=sys.stderr)
        return 2

    hermes_dir = Path(os.environ.get("HERMES_AGENT_DIR", "")) if os.environ.get("HERMES_AGENT_DIR") else None
    if hermes_dir is None:
        hermes_dir = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "hermes/hermes-agent"
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from install import install as install_adapter
    if not (hermes_dir / "gateway/platforms/napcat_adapter.py").exists():
        install_adapter(hermes_dir)
    root = args.root or Path(os.environ.get("LOCALAPPDATA", Path.home())) / "hermes/napcat-shell"
    archive = download_release(args.version, root.parent / "napcat-downloads")
    root.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive) as zf:
        zf.extractall(root)

    token = args.token or secrets.token_urlsafe(24)
    config_dir = root / "config"
    config_dir.mkdir(exist_ok=True)
    config_path = config_dir / "onebot11_auto.json"
    config_path.write_text(
        json.dumps(build_onebot_config(ws_port=args.ws_port, http_port=args.http_port,
                                       http_token=token, ws_token=token), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    configure_hermes(args.hermes, http_port=args.http_port, ws_port=args.ws_port, token=token)
    print(f"QQ detected: {qq}")
    print(f"NapCat files: {root}")
    print(f"OneBot config: {config_path}")
    print("Next: start Hermes, start NapCat, scan the QQ QR code, then enable the generated OneBot config in NapCat WebUI.")
    if not args.no_start:
        subprocess.run([args.hermes, "gateway", "restart"], check=False)
        launcher = root / "launcher-win10-user.bat"
        subprocess.Popen([str(launcher)], cwd=root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
