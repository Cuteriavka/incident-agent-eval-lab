"""Run one pinned upstream ReAct case without writing a credential to YAML."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

from cloudopsbench_tutorial import (
    CASE_REF,
    ensure_external_path,
    freeze_validated_agent_run,
    load_pre_reveal_case,
    sha256_file,
    verify_frozen_artifact,
    verify_agent_run_view,
    verify_runner_code_view,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _load_local_settings() -> dict:
    settings: dict = {}
    learning_path = PROJECT_ROOT / ".learning.local.json"
    if learning_path.is_file():
        learning = json.loads(learning_path.read_text(encoding="utf-8"))
        settings["tutorial_root"] = learning.get("cloudopsbench_tutorial_root")
    n00b_path = PROJECT_ROOT / ".n00b.local.json"
    if n00b_path.is_file():
        n00b = json.loads(n00b_path.read_text(encoding="utf-8"))
        if "api_key" in n00b:
            raise ValueError(".n00b.local.json must contain an API key variable name, not a key")
        settings.update(n00b)
    return settings


def _required_setting(env_name: str, settings: dict, key: str) -> str:
    value = os.environ.get(env_name, "").strip() or str(settings.get(key, "")).strip()
    if not value:
        raise RuntimeError(
            f"Missing N00B setting: {key} (local config or {env_name})"
        )
    return value


def _safe_api_origin(api_base: str) -> str:
    parsed = urlsplit(api_base)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("CLOUDOPSBENCH_API_BASE must be an HTTP(S) URL")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError("API base must not contain credentials, query, or fragment")
    if parsed.scheme == "http" and parsed.hostname not in {
        "localhost",
        "127.0.0.1",
        "::1",
    }:
        raise ValueError("Remote API endpoints must use HTTPS; HTTP is loopback-only")
    return f"{parsed.scheme}://{parsed.netloc}"


def _safe_path_component(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip(".-")
    if not slug:
        raise ValueError("Model name cannot produce a safe result-directory name")
    return slug[:80]


def _install_frozen_tool_guard(upstream_run: object, allowed_calls: list[dict]) -> None:
    """Replace the upstream executor with an exact-call fail-closed subclass."""

    base_executor = getattr(upstream_run, "ToolExecutor")
    frozen = {
        (item["tool_name"], json.dumps(item["arguments"], sort_keys=True))
        for item in allowed_calls
    }

    class FrozenToolExecutor(base_executor):  # type: ignore[misc, valid-type]
        def execute(self, action_name: str, action_input: dict) -> dict:
            call = (action_name, json.dumps(action_input or {}, sort_keys=True))
            if call not in frozen:
                return {
                    "success": False,
                    "observation": None,
                    "error": "Tool call rejected by the frozen N00 allowlist.",
                    "latency": None,
                }
            return super().execute(action_name, action_input)

    setattr(upstream_run, "ToolExecutor", FrozenToolExecutor)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--preflight",
        action="store_true",
        help="Validate local N00B configuration without calling the model.",
    )
    args = parser.parse_args()

    settings = _load_local_settings()
    tutorial_root = ensure_external_path(
        Path(
            _required_setting(
                "CLOUDOPSBENCH_TUTORIAL_ROOT", settings, "tutorial_root"
            )
        )
    )
    results_root = ensure_external_path(
        Path(_required_setting("CLOUDOPSBENCH_RESULTS", settings, "results_root"))
    )
    model = _required_setting("CLOUDOPSBENCH_MODEL", settings, "model")
    api_base = _required_setting("CLOUDOPSBENCH_API_BASE", settings, "api_base")
    key_env_name = _required_setting(
        "CLOUDOPSBENCH_API_KEY_ENV", settings, "api_key_env"
    )
    max_steps = int(
        os.environ.get("CLOUDOPSBENCH_MAX_STEPS", "").strip()
        or settings.get("max_steps", 6)
    )
    if not 1 <= max_steps <= 10:
        raise ValueError("CLOUDOPSBENCH_MAX_STEPS must be between 1 and 10")

    manifest = json.loads(
        (tutorial_root / "manifest.json").read_text(encoding="utf-8")
    )
    if manifest.get("case_ref") != CASE_REF:
        raise ValueError("Tutorial manifest does not match the pinned case")
    verify_frozen_artifact(tutorial_root, "human_diagnosis")
    manifest_sha256 = sha256_file(tutorial_root / "manifest.json").upper()
    allowed_tool_calls = load_pre_reveal_case(tutorial_root)["allowed_tool_calls"]
    model_path_component = _safe_path_component(model)

    agent_run_view_root = verify_agent_run_view(tutorial_root)
    agent_root = verify_runner_code_view(tutorial_root)
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(agent_root))
    import run as upstream_run  # type: ignore[import-not-found]

    _install_frozen_tool_guard(upstream_run, allowed_tool_calls)
    run_single_case = upstream_run.run_single_case

    run_manifest = {
        "case_ref": CASE_REF,
        "source_revision": manifest["source_revision"],
        "tutorial_manifest_sha256": manifest_sha256,
        "runner_code_sha256": manifest["runner_code_sha256"],
        "agent_run_view_sha256": manifest["agent_run_view_sha256"],
        "provider": "openai_compatible",
        "model": model,
        "api_origin": _safe_api_origin(api_base),
        "temperature": 0,
        "max_tokens": 4096,
        "max_steps": max_steps,
    }

    raw_trace_path = (
        results_root
        / "trainticket"
        / model_path_component
        / "service"
        / "1"
        / "1.json"
    )
    if raw_trace_path.exists():
        raise FileExistsError(
            "A trace already exists for this model/case. Choose a fresh external "
            "CLOUDOPSBENCH_RESULTS directory so the wrapper cannot reuse a stale run."
        )

    api_key = os.environ.get(key_env_name, "").strip()
    if not api_key:
        raise RuntimeError(
            f"Credential environment variable is missing: {key_env_name}"
        )

    if args.preflight:
        print("N00B local preflight passed.")
        print(f"Case             : {CASE_REF}")
        print(f"Source revision  : {manifest['source_revision'][:12]}")
        print(f"Model            : {model}")
        print(f"API origin       : {_safe_api_origin(api_base)}")
        print(f"Maximum steps    : {max_steps}")
        print("Credential       : present in named environment variable (value redacted)")
        print("Agent input view : sanitized external agent_run_view")
        return

    run_single_case(
        case_name="1",
        workspace_path=str(
            agent_run_view_root / "benchmark" / "trainticket"
        ),
        save_path=str(results_root / "trainticket"),
        fault_category="service",
        model_name=model_path_component,
        max_iterations=max_steps,
        llm_conf={
            "model": model,
            "provider": "openai_compatible",
            "api_base": api_base,
            "api_key": api_key,
            "temperature": 0,
            "max_tokens": 4096,
            "timeout": 60,
        },
    )

    freeze_validated_agent_run(
        tutorial_root,
        raw_trace_path,
        run_manifest,
        credential_values=(api_key,),
    )
    print("N00B trajectory projection frozen successfully.")
    print("Raw upstream trace remains outside the public repository.")


if __name__ == "__main__":
    main()
