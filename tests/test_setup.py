import json
from pathlib import Path

from scripts.setup_napcat import build_onebot_config, find_qq_executable


def test_build_onebot_config_contains_hermes_endpoints():
    config = build_onebot_config(
        ws_port=18800,
        http_port=18801,
        http_token="http-token",
        ws_token="ws-token",
    )
    assert config["network"]["httpServers"][0]["port"] == 18801
    assert config["network"]["websocketClients"][0]["url"] == "ws://127.0.0.1:18800"
    assert config["network"]["httpServers"][0]["token"] == "http-token"
    assert config["network"]["websocketClients"][0]["token"] == "ws-token"


def test_find_qq_executable_prefers_existing_candidates(tmp_path):
    candidate = tmp_path / "QQ.exe"
    candidate.write_bytes(b"")
    assert find_qq_executable([candidate, tmp_path / "missing.exe"]) == candidate
