"""Safe learning helpers for one pinned Cloud-OpsBench tutorial case.

All third-party payloads and run artifacts must stay outside this repository.
The learner-facing notebook imports this module; it never imports a truth loader.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import zipfile
from pathlib import Path
from typing import Any, Mapping


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CASE_RELATIVE = Path("benchmark/trainticket/service/1")
MILESTONE_RELATIVE = Path("process-label/trainticket/service/1/milestone.json")
CASE_REF = "cloudopsbench@41a881e:trainticket/service/1"
SOURCE_URL = "https://github.com/LLM4Ops/Cloud-OpsBench"
TOOL_PURPOSES = {
    "CheckNodeServiceStatus": "检查节点上的系统服务状态",
    "CheckServiceConnectivity": "检查两个服务或端点之间的连通性",
    "DescribeResource": "查看某个 Kubernetes 资源的状态与事件摘要",
    "GetAlerts": "查看事故快照中的告警",
    "GetAppYAML": "查看应用资源的声明式配置",
    "GetClusterConfiguration": "查看集群级配置摘要",
    "GetErrorLogs": "查看指定工作负载的错误日志",
    "GetResources": "枚举指定类型的 Kubernetes 资源",
    "GetServiceDependencies": "查看服务依赖关系",
}
REQUIRED_REPORT_FIELDS = {
    "case_ref",
    "tutorial_manifest_sha256",
    "symptom",
    "initial_hypotheses",
    "steps",
    "frozen_diagnosis",
    "limitations",
    "probe_value_assessment",
}
REQUIRED_COMPARISON_FIELDS = {
    "agreement_pattern",
    "human_vs_agent_investigation",
    "most_discriminating_probe",
    "low_value_probe",
    "evaluator_gaps",
}


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_payload(payload: Any) -> str:
    canonical = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def sha256_tree(root: Path) -> str:
    """Hash relative paths and bytes for every file in a directory tree."""

    digest = hashlib.sha256()
    for path in sorted(
        item
        for item in root.rglob("*")
        if item.is_file()
        and "__pycache__" not in item.parts
        and item.suffix.casefold() != ".pyc"
    ):
        digest.update(path.relative_to(root).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(bytes.fromhex(sha256_file(path)))
    return digest.hexdigest()


def ensure_external_path(path: Path) -> Path:
    """Resolve a path and reject locations inside the public repository."""

    resolved = path.resolve()
    try:
        resolved.relative_to(PROJECT_ROOT.resolve())
    except ValueError:
        for parent in (resolved, *resolved.parents):
            if (parent / ".git").exists():
                raise ValueError(
                    "External learning data must not be placed inside any Git "
                    f"checkout or worktree: {resolved}"
                )
        return resolved
    raise ValueError(f"Third-party workspace must be outside the repository: {resolved}")


def _parse_cache_key(cache_key: str) -> tuple[str, dict[str, Any]]:
    tool_name, separator, raw_args = cache_key.partition(":")
    if not separator:
        return tool_name, {}
    args = json.loads(raw_args)
    if not isinstance(args, dict):
        raise ValueError(f"Tool args must be an object: {cache_key}")
    return tool_name, args


def _build_tool_index(tool_cache: Mapping[str, Any]) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for cache_key in sorted(tool_cache):
        if cache_key == "collection_timestamp":
            continue
        tool_name, args = _parse_cache_key(cache_key)
        ref = "probe-" + hashlib.sha256(cache_key.encode("utf-8")).hexdigest()[:12]
        entries.append(
            {
                "ref": ref,
                "tool_name": tool_name,
                "arguments": args,
                "cache_key": cache_key,
            }
        )
    return entries


def _verify_archive_sentinels(
    archive_path: Path,
    source_root: Path,
    relative_paths: list[Path],
) -> None:
    """Bind the extracted tutorial inputs to selected files in the pinned ZIP."""

    with zipfile.ZipFile(archive_path) as archive:
        names = archive.namelist()
        for relative_path in relative_paths:
            suffix = "/" + relative_path.as_posix()
            matches = [name for name in names if name.endswith(suffix)]
            if len(matches) != 1:
                raise ValueError(
                    f"Pinned archive must contain exactly one sentinel: {relative_path}"
                )
            if archive.read(matches[0]) != (source_root / relative_path).read_bytes():
                raise ValueError(
                    f"Extracted sentinel differs from pinned archive: {relative_path}"
                )


def _extract_runner_code_view(archive_path: Path, tutorial_root: Path) -> Path:
    """Extract the pinned upstream runner package into the external tutorial view."""

    runner_root = tutorial_root / "runner_code_view" / "cloudops_agent"
    with zipfile.ZipFile(archive_path) as archive:
        run_matches = [
            name for name in archive.namelist() if name.endswith("/cloudops_agent/run.py")
        ]
        if len(run_matches) != 1:
            raise ValueError("Pinned archive must contain one cloudops_agent/run.py")
        archive_prefix = run_matches[0][: -len("cloudops_agent/run.py")]
        package_prefix = archive_prefix + "cloudops_agent/"
        for info in archive.infolist():
            if info.is_dir() or not info.filename.startswith(package_prefix):
                continue
            file_type = (info.external_attr >> 16) & 0o170000
            if file_type == 0o120000:
                raise ValueError("Runner code archive must not contain symlinks")
            relative = Path(info.filename[len(package_prefix) :])
            target = (runner_root / relative).resolve()
            try:
                target.relative_to(runner_root.resolve())
            except ValueError as exc:
                raise ValueError("Unsafe runner archive path") from exc
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(info) as source, target.open("wb") as destination:
                shutil.copyfileobj(source, destination)
    if not (runner_root / "run.py").is_file():
        raise FileNotFoundError("Extracted runner code view has no run.py")
    return runner_root


def prepare_tutorial_workspace(
    source_root: Path,
    tutorial_root: Path,
    *,
    source_revision: str,
    archive_sha256: str,
    archive_path: Path,
) -> dict[str, Any]:
    """Split a pinned upstream case into pre-reveal and compare-only views."""

    source_root = ensure_external_path(source_root)
    tutorial_root = ensure_external_path(tutorial_root)
    archive_path = ensure_external_path(archive_path)
    actual_archive_sha256 = sha256_file(archive_path).upper()
    if actual_archive_sha256 != archive_sha256.upper():
        raise ValueError("Pinned source archive SHA-256 does not match the declaration")
    with zipfile.ZipFile(archive_path) as archive:
        roots = {
            name.split("/", 1)[0]
            for name in archive.namelist()
            if name and not name.startswith("/")
        }
    if len(roots) != 1 or not next(iter(roots)).endswith(source_revision):
        raise ValueError("Pinned archive root does not match source_revision")
    license_path = source_root / "LICENSE"
    case_root = source_root / CASE_RELATIVE
    metadata_path = case_root / "metadata.json"
    tool_cache_path = case_root / "tool_cache.json"
    milestone_path = source_root / MILESTONE_RELATIVE

    required = [license_path, metadata_path, tool_cache_path, milestone_path]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"Missing required upstream files: {missing}")
    _verify_archive_sentinels(
        archive_path,
        source_root,
        [
            Path("LICENSE"),
            CASE_RELATIVE / "metadata.json",
            CASE_RELATIVE / "tool_cache.json",
            MILESTONE_RELATIVE,
        ],
    )
    if "MIT License" not in license_path.read_text(encoding="utf-8"):
        raise ValueError("Pinned upstream root does not contain an MIT license")

    metadata = _read_json(metadata_path)
    if not isinstance(metadata, dict) or "result" not in metadata:
        raise ValueError("Expected upstream metadata to contain isolated result data")
    tool_cache = _read_json(tool_cache_path)
    if not isinstance(tool_cache, dict):
        raise ValueError("Expected tool_cache.json to contain an object")
    tool_index = _build_tool_index(tool_cache)

    pre_reveal = tutorial_root / "pre_reveal"
    compare_only = tutorial_root / "compare_only"
    if tutorial_root.exists() and any(tutorial_root.iterdir()):
        raise FileExistsError(
            f"Tutorial workspace already exists and is non-empty: {tutorial_root}"
        )

    case_payload = {
        "case_ref": CASE_REF,
        "namespace": metadata.get("namespace"),
        "symptom": metadata.get("query"),
        "allowed_tool_calls": [
            {key: entry[key] for key in ("ref", "tool_name", "arguments")}
            for entry in tool_index
        ],
    }
    _write_json(pre_reveal / "case.json", case_payload)
    _write_json(pre_reveal / "tool_index.json", tool_index)
    shutil.copy2(tool_cache_path, pre_reveal / "tool_cache.json")

    # The upstream runner stores metadata.result in its raw runtime state even though
    # the pinned prompt builder does not read metadata. Build an external derived
    # run view with a sanitized metadata file so Ground Truth is absent by
    # construction rather than relying only on that upstream implementation detail.
    run_case_root = (
        tutorial_root
        / "agent_run_view"
        / "benchmark"
        / "trainticket"
        / "service"
        / "1"
    )
    shutil.copytree(
        case_root,
        run_case_root,
        ignore=shutil.ignore_patterns("metadata.json"),
    )
    _write_json(
        run_case_root / "metadata.json",
        {"namespace": metadata.get("namespace"), "query": metadata.get("query")},
    )
    runner_code_root = _extract_runner_code_view(archive_path, tutorial_root)
    _write_json(compare_only / "truth.json", metadata["result"])
    shutil.copy2(milestone_path, compare_only / "milestone.json")

    manifest = {
        "purpose": "tutorial/dev-only",
        "source_url": SOURCE_URL,
        "source_revision": source_revision,
        "archive_sha256": actual_archive_sha256,
        "root_license_sha256": sha256_file(license_path).upper(),
        "case_ref": CASE_REF,
        "pre_reveal_case_sha256": sha256_file(pre_reveal / "case.json").upper(),
        "pre_reveal_tool_cache_sha256": sha256_file(
            pre_reveal / "tool_cache.json"
        ).upper(),
        "pre_reveal_view_sha256": sha256_tree(pre_reveal).upper(),
        "runner_code_sha256": sha256_tree(runner_code_root).upper(),
        "agent_run_view_sha256": sha256_tree(
            tutorial_root / "agent_run_view"
        ).upper(),
        "public_redistribution": False,
    }
    _write_json(tutorial_root / "manifest.json", manifest)
    return manifest


def verify_runner_code_view(tutorial_root: Path) -> Path:
    """Return the pinned external runner root only when its tree hash matches."""

    tutorial_root = ensure_external_path(tutorial_root)
    manifest = _read_json(tutorial_root / "manifest.json")
    runner_root = tutorial_root / "runner_code_view" / "cloudops_agent"
    if any(path.suffix.casefold() == ".pyc" for path in runner_root.rglob("*")):
        raise ValueError("Runner code view contains bytecode not present in pinned ZIP")
    if any(path.name == "__pycache__" for path in runner_root.rglob("*")):
        raise ValueError("Runner code view contains an unexpected __pycache__ directory")
    actual = sha256_tree(runner_root).upper()
    if actual != manifest.get("runner_code_sha256"):
        raise ValueError("Runner code view differs from the pinned prepared manifest")
    return runner_root


def verify_pre_reveal_view(tutorial_root: Path) -> Path:
    """Verify the complete human-visible case/index/cache view before every read."""

    tutorial_root = ensure_external_path(tutorial_root)
    manifest = _read_json(tutorial_root / "manifest.json")
    view_root = tutorial_root / "pre_reveal"
    if sha256_tree(view_root).upper() != manifest.get("pre_reveal_view_sha256"):
        raise ValueError("Pre-reveal view differs from the pinned prepared manifest")
    if (
        sha256_file(view_root / "case.json").upper()
        != manifest.get("pre_reveal_case_sha256")
    ):
        raise ValueError("Pre-reveal case differs from the pinned prepared manifest")
    if (
        sha256_file(view_root / "tool_cache.json").upper()
        != manifest.get("pre_reveal_tool_cache_sha256")
    ):
        raise ValueError("Pre-reveal tool cache differs from the prepared snapshot")
    return view_root


def verify_agent_run_view(tutorial_root: Path) -> Path:
    """Verify the exact snapshot tree that N00B will expose through tools."""

    tutorial_root = ensure_external_path(tutorial_root)
    manifest = _read_json(tutorial_root / "manifest.json")
    view_root = tutorial_root / "agent_run_view"
    actual = sha256_tree(view_root).upper()
    if actual != manifest.get("agent_run_view_sha256"):
        raise ValueError("Agent run view differs from the pinned prepared manifest")
    metadata_paths = list(view_root.rglob("metadata.json"))
    if len(metadata_paths) != 1:
        raise ValueError("Agent run view must contain exactly one metadata.json")
    metadata = _read_json(metadata_paths[0])
    if set(metadata) - {"namespace", "query"}:
        raise ValueError("Agent run view metadata contains non-visible fields")
    tool_cache_paths = list(view_root.rglob("tool_cache.json"))
    if len(tool_cache_paths) != 1:
        raise ValueError("Agent run view must contain exactly one tool_cache.json")
    if (
        sha256_file(tool_cache_paths[0]).upper()
        != manifest.get("pre_reveal_tool_cache_sha256")
    ):
        raise ValueError("Agent run view tool cache differs from pre-reveal snapshot")
    return view_root


def load_pre_reveal_case(tutorial_root: Path) -> dict[str, Any]:
    tutorial_root = ensure_external_path(tutorial_root)
    view_root = verify_pre_reveal_view(tutorial_root)
    payload = _read_json(view_root / "case.json")
    forbidden = {"result", "root_cause", "fault_object", "fault_taxonomy"}
    if forbidden.intersection(payload):
        raise ValueError("Ground Truth field found in pre-reveal case")
    return payload


def replay_probe(tutorial_root: Path, probe_ref: str) -> Any:
    """Return one cached read-only observation without loading Ground Truth."""

    tutorial_root = ensure_external_path(tutorial_root)
    verify_pre_reveal_view(tutorial_root)
    index = _read_json(tutorial_root / "pre_reveal" / "tool_index.json")
    matches = [entry for entry in index if entry.get("ref") == probe_ref]
    if len(matches) != 1:
        raise KeyError(f"Unknown or ambiguous probe ref: {probe_ref}")
    tool_cache = _read_json(tutorial_root / "pre_reveal" / "tool_cache.json")
    return tool_cache[matches[0]["cache_key"]]


def probe_catalog(tutorial_root: Path) -> list[dict[str, Any]]:
    """Return tool-family counts and purposes without exposing observations."""

    case = load_pre_reveal_case(tutorial_root)
    counts: dict[str, int] = {}
    for item in case["allowed_tool_calls"]:
        name = item["tool_name"]
        counts[name] = counts.get(name, 0) + 1
    return [
        {
            "tool_name": name,
            "purpose": TOOL_PURPOSES.get(name, "只读诊断探针"),
            "available_calls": counts[name],
        }
        for name in sorted(counts)
    ]


def search_probes(
    tutorial_root: Path,
    *,
    tool_name: str,
    argument_contains: str = "",
    limit: int = 10,
) -> list[dict[str, Any]]:
    """Find a bounded set of registered calls without loading observations."""

    if not 1 <= limit <= 10:
        raise ValueError("limit must be between 1 and 10")
    needle = argument_contains.casefold().strip()
    matches: list[dict[str, Any]] = []
    for item in load_pre_reveal_case(tutorial_root)["allowed_tool_calls"]:
        if item["tool_name"] != tool_name:
            continue
        encoded_args = json.dumps(item["arguments"], ensure_ascii=False, sort_keys=True)
        if needle and needle not in encoded_args.casefold():
            continue
        matches.append(item)
        if len(matches) >= limit:
            break
    return matches


def validate_orientation_report(
    tutorial_root: Path, report: Mapping[str, Any]
) -> list[str]:
    errors: list[str] = []
    missing = sorted(REQUIRED_REPORT_FIELDS - set(report))
    if missing:
        errors.append(f"missing fields: {missing}")

    case = load_pre_reveal_case(tutorial_root)
    if report.get("case_ref") != case["case_ref"]:
        errors.append("case_ref must match the prepared tutorial case")
    if report.get("symptom") != case["symptom"]:
        errors.append("symptom must match the prepared Agent-visible symptom")
    manifest_sha256 = sha256_file(tutorial_root / "manifest.json").upper()
    if report.get("tutorial_manifest_sha256") != manifest_sha256:
        errors.append("human report is not bound to the prepared tutorial manifest")
    allowed = {item["ref"] for item in case["allowed_tool_calls"]}
    hypotheses = report.get("initial_hypotheses", [])
    if not isinstance(hypotheses, list) or len(hypotheses) < 2:
        errors.append("initial_hypotheses must contain at least two candidates")
    elif any(not str(item).strip() for item in hypotheses):
        errors.append("initial_hypotheses must not contain blank candidates")

    steps = report.get("steps", [])
    step_refs: list[str] = []
    if not isinstance(steps, list) or not steps:
        errors.append("steps must be a non-empty list")
    else:
        step_numbers: list[int] = []
        for index, step in enumerate(steps, start=1):
            if not isinstance(step, Mapping):
                errors.append(f"step {index} must be an object")
                continue
            if step.get("step") != index:
                errors.append(f"step {index} must use sequential step number {index}")
            step_numbers.append(step.get("step"))
            probe_ref = str(step.get("probe_ref", "")).strip()
            step_refs.append(probe_ref)
            if probe_ref not in allowed:
                errors.append(f"step {index} uses unknown probe ref: {probe_ref}")
            for field in (
                "observation_summary",
                "effect_on_hypothesis",
                "why_next",
            ):
                if not str(step.get(field, "")).strip():
                    errors.append(f"step {index} field must not be blank: {field}")
        if len(set(step_numbers)) != len(step_numbers):
            errors.append("step numbers must be unique")

    if not str(report.get("frozen_diagnosis", "")).strip():
        errors.append("frozen_diagnosis must not be empty")
    limitations = report.get("limitations", [])
    if not isinstance(limitations, list) or not limitations:
        errors.append("limitations must be a non-empty list")
    elif any(not str(item).strip() for item in limitations):
        errors.append("limitations must not contain blank items")

    assessment = report.get("probe_value_assessment", {})
    if not isinstance(assessment, Mapping):
        errors.append("probe_value_assessment must be an object")
    else:
        step_ref_set = set(step_refs) if isinstance(steps, list) else set()
        assessment_refs: dict[str, str] = {}
        for label in ("useful", "low_value"):
            value = assessment.get(label, {})
            if not isinstance(value, Mapping):
                errors.append(f"probe_value_assessment.{label} must be an object")
                continue
            if value.get("probe_ref") not in step_ref_set:
                errors.append(
                    f"probe_value_assessment.{label}.probe_ref must reference a step"
                )
            assessment_refs[label] = str(value.get("probe_ref", ""))
            if not str(value.get("reason", "")).strip():
                errors.append(
                    f"probe_value_assessment.{label}.reason must not be blank"
                )
        if (
            assessment_refs.get("useful")
            and assessment_refs.get("useful") == assessment_refs.get("low_value")
        ):
            errors.append("useful and low_value must reference different probes")
    return errors


def freeze_artifact(
    tutorial_root: Path, name: str, payload: Mapping[str, Any]
) -> dict[str, str]:
    tutorial_root = ensure_external_path(tutorial_root)
    artifact_path = tutorial_root / "artifacts" / f"{name}.json"
    freeze_path = tutorial_root / "artifacts" / f"{name}.freeze.json"
    if artifact_path.exists() and freeze_path.exists():
        _verify_freeze(tutorial_root, name)
        if sha256_payload(_read_json(artifact_path)) != sha256_payload(payload):
            raise FileExistsError(
                f"Frozen artifact already exists with different content: {name}"
            )
        return _read_json(freeze_path)
    if artifact_path.exists() or freeze_path.exists():
        raise FileExistsError(f"Incomplete frozen artifact pair exists: {name}")
    _write_json(artifact_path, payload)
    record = {
        "artifact": artifact_path.name,
        "sha256": sha256_file(artifact_path).upper(),
    }
    _write_json(freeze_path, record)
    return record


def _verify_freeze(tutorial_root: Path, name: str) -> None:
    artifact_path = tutorial_root / "artifacts" / f"{name}.json"
    freeze_path = tutorial_root / "artifacts" / f"{name}.freeze.json"
    record = _read_json(freeze_path)
    actual = sha256_file(artifact_path).upper()
    if record.get("sha256") != actual:
        raise ValueError(f"Frozen artifact hash mismatch: {name}")


def verify_frozen_artifact(tutorial_root: Path, name: str) -> None:
    """Fail closed unless a named external artifact and its hash both match."""

    tutorial_root = ensure_external_path(tutorial_root)
    _verify_freeze(tutorial_root, name)


def project_upstream_trajectory(
    raw_trace: Mapping[str, Any],
    run_manifest: Mapping[str, Any],
    *,
    allowed_tool_calls: list[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Create the only upstream trajectory shape allowed to cross into N01."""

    steps: list[dict[str, Any]] = []
    probe_refs = {
        (
            str(item.get("tool_name")),
            json.dumps(item.get("arguments", {}), sort_keys=True),
        ): item.get("ref")
        for item in (allowed_tool_calls or [])
    }
    for raw_step in raw_trace.get("steps", []):
        call_key = (
            str(raw_step.get("action_name")),
            json.dumps(raw_step.get("action_input") or {}, sort_keys=True),
        )
        step = {
            "step_id": raw_step.get("step_id"),
            "action_type": raw_step.get("action_type"),
            "action_name": raw_step.get("action_name"),
            "action_input": raw_step.get("action_input"),
            "probe_ref": probe_refs.get(call_key),
            "observation_sha256": sha256_payload(raw_step.get("observation"))
            if raw_step.get("observation") is not None
            else None,
            "final_answer": raw_step.get("final_answer"),
            "model_latency": raw_step.get("model_latency"),
            "tool_latency": raw_step.get("tool_latency"),
            "input_tokens": raw_step.get("input_tokens"),
            "output_tokens": raw_step.get("output_tokens"),
            "error_type": type(raw_step.get("error")).__name__
            if raw_step.get("error") is not None
            else None,
        }
        steps.append(step)

    projection = {
        "case_ref": CASE_REF,
        "run_manifest": dict(run_manifest),
        "stop_reason": raw_trace.get("stop_reason"),
        "finished": raw_trace.get("finished"),
        "final_answer": raw_trace.get("final_answer"),
        "steps": steps,
    }
    forbidden_keys = {
        "metadata",
        "case_path",
        "prompt",
        "raw_model_output",
        "thought",
        "observation",
    }
    serialized = json.dumps(projection, ensure_ascii=False)
    if any(f'"{key}"' in serialized for key in forbidden_keys):
        raise ValueError("Forbidden raw trace field survived projection")
    return projection


def validate_projected_trajectory(
    projection: Mapping[str, Any],
    *,
    allowed_tool_calls: list[Mapping[str, Any]] | None = None,
    expected_source_revision: str | None = None,
    expected_manifest_sha256: str | None = None,
) -> list[str]:
    errors: list[str] = []
    if projection.get("case_ref") != CASE_REF:
        errors.append("trajectory case_ref does not match the tutorial case")
    run_manifest = projection.get("run_manifest", {})
    if not isinstance(run_manifest, Mapping):
        errors.append("run_manifest must be an object")
        run_manifest = {}
    if (
        expected_source_revision is not None
        and run_manifest.get("source_revision") != expected_source_revision
    ):
        errors.append("trajectory source revision does not match tutorial manifest")
    if (
        expected_manifest_sha256 is not None
        and run_manifest.get("tutorial_manifest_sha256")
        != expected_manifest_sha256
    ):
        errors.append("trajectory is not bound to the prepared tutorial manifest")
    if projection.get("stop_reason") not in {"final_answer", "max_steps"}:
        errors.append("stop_reason must be final_answer or max_steps")
    steps = projection.get("steps", [])
    if not isinstance(steps, list) or not steps:
        errors.append("at least one successful model step is required")
    elif not any(
        step.get("action_name") or step.get("final_answer") for step in steps
    ):
        errors.append("trajectory has no parseable action or final answer")
    if allowed_tool_calls is not None:
        frozen_calls = {
            (
                str(item.get("tool_name")),
                json.dumps(item.get("arguments", {}), sort_keys=True),
            )
            for item in allowed_tool_calls
        }
        for index, step in enumerate(steps, start=1):
            if step.get("action_type") != "tool":
                continue
            call = (
                str(step.get("action_name")),
                json.dumps(step.get("action_input") or {}, sort_keys=True),
            )
            if call not in frozen_calls:
                errors.append(f"step {index} used a tool call outside frozen allowlist")
            if not step.get("probe_ref"):
                errors.append(f"step {index} has no registered evidence ref")

    credential_pattern = re.compile(
        r"(?i)(?:sk-[a-z0-9_-]{12,}|bearer\s+[a-z0-9._-]{12,}|api[_-]?key\s*[:=])"
    )
    windows_path = re.compile(r"(?i)(?:^|\s|[\"'])[a-z]:[\\/]")
    unc_path = re.compile(r"^\\\\[^\\]+\\[^\\]+")
    posix_local_path = re.compile(
        r"^/(?:Users|home|root|tmp|var|opt|etc|usr|mnt|srv|data|private|Volumes)/"
    )

    def _unsafe_strings(value: Any, key: str = "") -> list[str]:
        found: list[str] = []
        if isinstance(value, Mapping):
            for child_key, child in value.items():
                found.extend(_unsafe_strings(child, str(child_key)))
        elif isinstance(value, list):
            for child in value:
                found.extend(_unsafe_strings(child, key))
        elif isinstance(value, str):
            if credential_pattern.search(value):
                found.append("credential-like value")
            if (
                windows_path.search(value)
                or unc_path.search(value)
                or posix_local_path.search(value)
                or value.casefold().startswith("file://")
            ):
                found.append("absolute local path")
            if "../" in value or "..\\" in value:
                found.append("path traversal segment")
        return found

    errors.extend(sorted(set(_unsafe_strings(projection))))
    return errors


def _freeze_validated_agent_projection(
    tutorial_root: Path,
    projection: Mapping[str, Any],
    *,
    raw_trace_sha256: str,
) -> dict[str, str]:
    """Validate, freeze, and mark a projection produced by the N00B wrapper."""

    tutorial_root = ensure_external_path(tutorial_root)
    manifest_path = tutorial_root / "manifest.json"
    manifest = _read_json(manifest_path)
    allowed_calls = load_pre_reveal_case(tutorial_root)["allowed_tool_calls"]
    errors = validate_projected_trajectory(
        projection,
        allowed_tool_calls=allowed_calls,
        expected_source_revision=manifest["source_revision"],
        expected_manifest_sha256=sha256_file(manifest_path).upper(),
    )
    projected_manifest = projection.get("run_manifest", {})
    if projected_manifest.get("runner_code_sha256") != manifest.get(
        "runner_code_sha256"
    ):
        errors.append("trajectory is not bound to the pinned runner code view")
    if projected_manifest.get("agent_run_view_sha256") != manifest.get(
        "agent_run_view_sha256"
    ):
        errors.append("trajectory is not bound to the pinned Agent run view")
    if errors:
        raise ValueError(f"Agent projection is not reveal-eligible: {errors}")
    record = freeze_artifact(tutorial_root, "agent_projection", projection)
    marker = {
        "validator": "n00-agent-projection@1",
        "case_ref": CASE_REF,
        "projection_sha256": record["sha256"],
        "raw_trace_sha256": raw_trace_sha256.upper(),
        "tutorial_manifest_sha256": sha256_file(manifest_path).upper(),
        "runner_code_sha256": manifest["runner_code_sha256"],
        "agent_run_view_sha256": manifest["agent_run_view_sha256"],
    }
    marker_path = tutorial_root / "artifacts" / "agent_projection.validation.json"
    if marker_path.exists() and _read_json(marker_path) != marker:
        raise FileExistsError("Agent projection validation marker already differs")
    _write_json(marker_path, marker)
    return record


def freeze_validated_agent_run(
    tutorial_root: Path,
    raw_trace_path: Path,
    run_manifest: Mapping[str, Any],
    *,
    credential_values: tuple[str, ...] = (),
) -> dict[str, str]:
    """Project and freeze a wrapper trace; callers cannot self-report its hash."""

    tutorial_root = ensure_external_path(tutorial_root)
    raw_trace_path = ensure_external_path(raw_trace_path)
    verify_runner_code_view(tutorial_root)
    verify_agent_run_view(tutorial_root)
    raw_trace = _read_json(raw_trace_path)
    if raw_trace.get("case_id") != "1":
        raise ValueError("Raw trace is not the pinned tutorial case")
    metadata = raw_trace.get("metadata", {})
    if isinstance(metadata, Mapping) and metadata.get("result"):
        raise ValueError("Ground Truth found in the raw Agent runtime state")
    steps = raw_trace.get("steps", [])
    if not isinstance(steps, list) or not any(
        str(step.get("raw_model_output", "")).strip() for step in steps
    ):
        raise ValueError("Raw trace contains no recorded non-empty model response")
    raw_serialized = json.dumps(raw_trace, ensure_ascii=False)
    if any(value and value in raw_serialized for value in credential_values):
        raise ValueError("Credential value found in raw trace")

    allowed_calls = load_pre_reveal_case(tutorial_root)["allowed_tool_calls"]
    projection = project_upstream_trajectory(
        raw_trace,
        run_manifest,
        allowed_tool_calls=allowed_calls,
    )
    return _freeze_validated_agent_projection(
        tutorial_root,
        projection,
        raw_trace_sha256=sha256_file(raw_trace_path),
    )


def _verify_reveal_ready(tutorial_root: Path) -> dict[str, Any]:
    """Enforce the only path that may read evaluator-only comparison material."""

    tutorial_root = ensure_external_path(tutorial_root)
    _verify_freeze(tutorial_root, "human_diagnosis")
    _verify_freeze(tutorial_root, "agent_projection")
    human_report = _read_json(tutorial_root / "artifacts" / "human_diagnosis.json")
    human_errors = validate_orientation_report(tutorial_root, human_report)
    if human_errors:
        raise ValueError(f"Frozen human report is invalid: {human_errors}")

    manifest_path = tutorial_root / "manifest.json"
    manifest = _read_json(manifest_path)
    projection = _read_json(tutorial_root / "artifacts" / "agent_projection.json")
    projection_errors = validate_projected_trajectory(
        projection,
        allowed_tool_calls=load_pre_reveal_case(tutorial_root)["allowed_tool_calls"],
        expected_source_revision=manifest["source_revision"],
        expected_manifest_sha256=sha256_file(manifest_path).upper(),
    )
    if projection_errors:
        raise ValueError(f"Frozen Agent projection is invalid: {projection_errors}")
    marker = _read_json(
        tutorial_root / "artifacts" / "agent_projection.validation.json"
    )
    agent_freeze = _read_json(
        tutorial_root / "artifacts" / "agent_projection.freeze.json"
    )
    if (
        marker.get("validator") != "n00-agent-projection@1"
        or marker.get("case_ref") != CASE_REF
        or marker.get("projection_sha256") != agent_freeze.get("sha256")
        or marker.get("tutorial_manifest_sha256")
        != sha256_file(manifest_path).upper()
        or marker.get("runner_code_sha256") != manifest.get("runner_code_sha256")
        or marker.get("agent_run_view_sha256")
        != manifest.get("agent_run_view_sha256")
        or not str(marker.get("raw_trace_sha256", "")).strip()
    ):
        raise ValueError("Agent projection validation marker is invalid")
    return {
        "truth": _read_json(tutorial_root / "compare_only" / "truth.json"),
        "milestone": _read_json(
            tutorial_root / "compare_only" / "milestone.json"
        ),
    }


def _annotation_strings(value: Any) -> list[str]:
    if isinstance(value, Mapping):
        return [item for child in value.values() for item in _annotation_strings(child)]
    if isinstance(value, list):
        return [item for child in value for item in _annotation_strings(child)]
    text = str(value).strip()
    return [text] if len(text) >= 4 else []


def validate_orientation_comparison(
    tutorial_root: Path, comparison: Mapping[str, Any]
) -> list[str]:
    """Validate a post-reveal note through the same reveal-ready gate."""

    tutorial_root = ensure_external_path(tutorial_root)
    materials = _verify_reveal_ready(tutorial_root)
    errors: list[str] = []
    missing = sorted(REQUIRED_COMPARISON_FIELDS - set(comparison))
    if missing:
        errors.append(f"missing comparison fields: {missing}")
    for field in REQUIRED_COMPARISON_FIELDS:
        value = comparison.get(field)
        if isinstance(value, list):
            if not value or any(not str(item).strip() for item in value):
                errors.append(f"comparison field must contain non-blank items: {field}")
        elif not str(value or "").strip():
            errors.append(f"comparison field must not be blank: {field}")

    encoded = json.dumps(comparison, ensure_ascii=False)
    restricted = _annotation_strings(materials["truth"]) + _annotation_strings(
        materials["milestone"]
    )
    if any(secret in encoded for secret in restricted):
        errors.append("comparison must not reproduce truth or process-label values")
    return errors


def freeze_validated_orientation_comparison(
    tutorial_root: Path, comparison: Mapping[str, Any]
) -> dict[str, str]:
    """Atomically gate, validate, and freeze the N00C project-authored note."""

    errors = validate_orientation_comparison(tutorial_root, comparison)
    if errors:
        raise ValueError(errors)
    return freeze_artifact(tutorial_root, "orientation_comparison", comparison)


def reveal_comparison_material(tutorial_root: Path) -> dict[str, Any]:
    """Load compare-only data through the single reveal-ready gate."""

    return _verify_reveal_ready(tutorial_root)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    prepare = subparsers.add_parser("prepare")
    prepare.add_argument("--source-root", type=Path, required=True)
    prepare.add_argument("--tutorial-root", type=Path, required=True)
    prepare.add_argument("--source-revision", required=True)
    prepare.add_argument("--archive-sha256", required=True)
    prepare.add_argument("--archive-path", type=Path, required=True)
    return parser


def main() -> None:
    args = _build_parser().parse_args()
    if args.command == "prepare":
        manifest = prepare_tutorial_workspace(
            args.source_root,
            args.tutorial_root,
            source_revision=args.source_revision,
            archive_sha256=args.archive_sha256,
            archive_path=args.archive_path,
        )
        print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
