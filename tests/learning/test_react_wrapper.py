from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from run_cloudopsbench_react import (  # noqa: E402
    _install_frozen_tool_guard,
    _safe_api_origin,
    _safe_path_component,
)


def test_remote_http_is_rejected_but_loopback_http_is_allowed() -> None:
    with pytest.raises(ValueError, match="must use HTTPS"):
        _safe_api_origin("http://provider.example/v1")
    assert _safe_api_origin("http://127.0.0.1:8000/v1") == "http://127.0.0.1:8000"
    assert _safe_api_origin("https://provider.example/v1") == "https://provider.example"


def test_model_name_becomes_safe_result_component() -> None:
    assert _safe_path_component("provider/model:name") == "provider-model-name"


def test_tool_guard_rejects_before_calling_upstream_executor() -> None:
    executed: list[tuple[str, dict]] = []

    class FakeExecutor:
        def execute(self, action_name: str, action_input: dict) -> dict:
            executed.append((action_name, action_input))
            return {"success": True, "observation": "safe", "error": None}

    upstream = SimpleNamespace(ToolExecutor=FakeExecutor)
    allowed = [{"tool_name": "GetResources", "arguments": {"kind": "pods"}}]
    _install_frozen_tool_guard(upstream, allowed)
    executor = upstream.ToolExecutor()

    rejected = executor.execute("GetResources", {"kind": "secrets"})
    assert rejected["success"] is False
    assert executed == []

    accepted = executor.execute("GetResources", {"kind": "pods"})
    assert accepted["success"] is True
    assert executed == [("GetResources", {"kind": "pods"})]
