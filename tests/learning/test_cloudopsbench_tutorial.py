from __future__ import annotations

import json
import sys
import zipfile
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from cloudopsbench_tutorial import (  # noqa: E402
    ensure_external_path,
    freeze_artifact,
    freeze_validated_agent_run,
    freeze_validated_orientation_comparison,
    load_pre_reveal_case,
    prepare_tutorial_workspace,
    project_upstream_trajectory,
    replay_probe,
    reveal_comparison_material,
    sha256_file,
    validate_orientation_comparison,
    validate_orientation_report,
    validate_projected_trajectory,
    verify_runner_code_view,
    verify_agent_run_view,
    verify_pre_reveal_view,
)


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


@pytest.fixture
def prepared_workspace(tmp_path: Path) -> Path:
    source_root = tmp_path / "upstream"
    tutorial_root = tmp_path / "tutorial"
    (source_root / "LICENSE").parent.mkdir(parents=True, exist_ok=True)
    (source_root / "LICENSE").write_text("MIT License\n", encoding="utf-8")
    case_root = source_root / "benchmark" / "trainticket" / "service" / "1"
    _write_json(
        case_root / "metadata.json",
        {
            "namespace": "train-ticket",
            "query": "Partial Service Unreachability.",
            "result": {"root_cause": "SYNTHETIC_SECRET_CAUSE"},
        },
    )
    _write_json(
        case_root / "tool_cache.json",
        {
            "collection_timestamp": "synthetic",
            "GetClusterConfiguration": {"cluster": "synthetic"},
            'GetResources:{"namespace":"train-ticket","resource_type":"pods"}': {
                "items": ["synthetic-pod"]
            },
        },
    )
    _write_json(
        source_root
        / "process-label"
        / "trainticket"
        / "service"
        / "1"
        / "milestone.json",
        {"milestones": ["SYNTHETIC_SECRET_CAUSE"]},
    )
    archive_path = tmp_path / "synthetic-upstream.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        for path in (
            source_root / "LICENSE",
            case_root / "metadata.json",
            case_root / "tool_cache.json",
            source_root
            / "process-label"
            / "trainticket"
            / "service"
            / "1"
            / "milestone.json",
        ):
            relative = path.relative_to(source_root)
            archive.write(path, f"Cloud-OpsBench-test-revision/{relative.as_posix()}")
        archive.writestr(
            "Cloud-OpsBench-test-revision/cloudops_agent/run.py",
            "def run_single_case(**kwargs):\n    return None\n",
        )
    prepare_tutorial_workspace(
        source_root,
        tutorial_root,
        source_revision="test-revision",
        archive_sha256=sha256_file(archive_path),
        archive_path=archive_path,
    )
    return tutorial_root


def test_prepare_keeps_truth_out_of_pre_reveal(prepared_workspace: Path) -> None:
    pre_reveal_text = "".join(
        path.read_text(encoding="utf-8")
        for path in (prepared_workspace / "pre_reveal").glob("*.json")
    )
    assert "SYNTHETIC_SECRET_CAUSE" not in pre_reveal_text
    case = load_pre_reveal_case(prepared_workspace)
    assert case["symptom"] == "Partial Service Unreachability."
    assert "result" not in case
    run_metadata = json.loads(
        (
            prepared_workspace
            / "agent_run_view"
            / "benchmark"
            / "trainticket"
            / "service"
            / "1"
            / "metadata.json"
        ).read_text(encoding="utf-8")
    )
    assert "result" not in run_metadata
    assert "SYNTHETIC_SECRET_CAUSE" not in json.dumps(run_metadata)
    run_view_text = "".join(
        path.read_text(encoding="utf-8")
        for path in (prepared_workspace / "agent_run_view").rglob("*.json")
    )
    assert "SYNTHETIC_SECRET_CAUSE" not in run_view_text


def test_report_uses_only_registered_probe_refs(prepared_workspace: Path) -> None:
    case = load_pre_reveal_case(prepared_workspace)
    probe_ref = next(
        item["ref"]
        for item in case["allowed_tool_calls"]
        if item["tool_name"] == "GetResources"
    )
    observation = replay_probe(prepared_workspace, probe_ref)
    assert observation == {"items": ["synthetic-pod"]}

    second_probe_ref = next(
        item["ref"]
        for item in case["allowed_tool_calls"]
        if item["tool_name"] == "GetClusterConfiguration"
    )
    report = {
        "case_ref": case["case_ref"],
        "tutorial_manifest_sha256": sha256_file(
            prepared_workspace / "manifest.json"
        ).upper(),
        "symptom": case["symptom"],
        "initial_hypotheses": ["service unavailable", "platform unavailable"],
        "steps": [
            {
                "step": 1,
                "probe_ref": probe_ref,
                "observation_summary": "one pod",
                "effect_on_hypothesis": "supports service hypothesis",
                "why_next": "compare cluster state",
            },
            {
                "step": 2,
                "probe_ref": second_probe_ref,
                "observation_summary": "cluster is synthetic",
                "effect_on_hypothesis": "weakens platform hypothesis",
                "why_next": "freeze the bounded tutorial answer",
            },
        ],
        "frozen_diagnosis": "not enough evidence",
        "limitations": ["one probe only"],
        "probe_value_assessment": {
            "useful": {"probe_ref": probe_ref, "reason": "distinguishes a candidate"},
            "low_value": {
                "probe_ref": second_probe_ref,
                "reason": "did not narrow the service candidate",
            },
        },
    }
    assert validate_orientation_report(prepared_workspace, report) == []
    report["steps"][0]["probe_ref"] = "probe-not-registered"
    assert "unknown probe ref" in " ".join(
        validate_orientation_report(prepared_workspace, report)
    )
    report["steps"][0]["probe_ref"] = probe_ref
    report["probe_value_assessment"]["low_value"]["probe_ref"] = probe_ref
    assert "useful and low_value must reference different probes" in (
        validate_orientation_report(prepared_workspace, report)
    )


def test_reveal_requires_both_frozen_artifacts(prepared_workspace: Path) -> None:
    case = load_pre_reveal_case(prepared_workspace)
    first_ref = case["allowed_tool_calls"][0]["ref"]
    second_ref = case["allowed_tool_calls"][1]["ref"]
    freeze_artifact(
        prepared_workspace,
        "human_diagnosis",
        {
            "case_ref": case["case_ref"],
            "tutorial_manifest_sha256": sha256_file(
                prepared_workspace / "manifest.json"
            ).upper(),
            "symptom": case["symptom"],
            "initial_hypotheses": ["candidate one", "candidate two"],
            "steps": [
                {
                    "step": 1,
                    "probe_ref": first_ref,
                    "observation_summary": "first bounded summary",
                    "effect_on_hypothesis": "supports candidate one",
                    "why_next": "inspect another registered probe",
                },
                {
                    "step": 2,
                    "probe_ref": second_ref,
                    "observation_summary": "second bounded summary",
                    "effect_on_hypothesis": "weakens candidate two",
                    "why_next": "freeze the bounded answer",
                },
            ],
            "frozen_diagnosis": "synthetic learner answer",
            "limitations": ["synthetic evidence is intentionally small"],
            "probe_value_assessment": {
                "useful": {"probe_ref": first_ref, "reason": "changed a candidate"},
                "low_value": {
                    "probe_ref": second_ref,
                    "reason": "added little discrimination",
                },
            },
        },
    )
    with pytest.raises(FileNotFoundError):
        reveal_comparison_material(prepared_workspace)

    manifest_path = prepared_workspace / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    allowed_call = case["allowed_tool_calls"][0]
    run_manifest = {
        "source_revision": manifest["source_revision"],
        "tutorial_manifest_sha256": sha256_file(manifest_path).upper(),
        "runner_code_sha256": manifest["runner_code_sha256"],
        "agent_run_view_sha256": manifest["agent_run_view_sha256"],
    }
    raw_trace_path = prepared_workspace.parent / "raw-trace.json"
    _write_json(
        raw_trace_path,
        {
            "case_id": "1",
            "metadata": {"namespace": "train-ticket", "result": ""},
            "stop_reason": "final_answer",
            "finished": True,
            "steps": [
                {
                    "step_id": 1,
                    "raw_model_output": "Action: synthetic registered probe",
                    "action_type": "tool",
                    "action_name": allowed_call["tool_name"],
                    "action_input": allowed_call["arguments"],
                    "observation": "synthetic observation",
                    "final_answer": None,
                }
            ],
        },
    )
    freeze_validated_agent_run(
        prepared_workspace,
        raw_trace_path,
        run_manifest,
    )
    revealed = reveal_comparison_material(prepared_workspace)
    assert revealed["truth"]["root_cause"] == "SYNTHETIC_SECRET_CAUSE"


def test_projection_drops_raw_state_and_truth() -> None:
    raw = {
        "case_id": "1",
        "case_path": "C:/secret/local/path",
        "metadata": {"result": {"root_cause": "SECRET_CAUSE"}},
        "stop_reason": "final_answer",
        "finished": True,
        "final_answer": "agent-generated answer",
        "steps": [
            {
                "step_id": 1,
                "prompt": "contains private prompt",
                "raw_model_output": "raw model text",
                "thought": "hidden thought",
                "action_type": "tool",
                "action_name": "GetResources",
                "action_input": {"resource_type": "pods"},
                "observation": "raw third-party output",
                "error": None,
                "model_latency": 0.1,
                "input_tokens": 10,
                "output_tokens": 5,
            }
        ],
    }
    projection = project_upstream_trajectory(
        raw,
        {"model": "test-model", "max_steps": 6},
        allowed_tool_calls=[
            {
                "ref": "probe-get-resources",
                "tool_name": "GetResources",
                "arguments": {"resource_type": "pods"},
            }
        ],
    )
    encoded = json.dumps(projection)
    for forbidden in (
        "SECRET_CAUSE",
        "secret/local/path",
        "private prompt",
        "raw model text",
        "hidden thought",
        "raw third-party output",
    ):
        assert forbidden not in encoded
    assert validate_projected_trajectory(projection) == []
    assert projection["steps"][0]["probe_ref"] == "probe-get-resources"


def test_projection_rejects_tool_call_outside_frozen_allowlist() -> None:
    projection = {
        "case_ref": "cloudopsbench@41a881e:trainticket/service/1",
        "stop_reason": "final_answer",
        "steps": [
            {
                "action_type": "tool",
                "action_name": "RunArbitraryShell",
                "action_input": {},
                "probe_ref": "probe-not-allowed",
                "final_answer": None,
            }
        ],
    }
    assert validate_projected_trajectory(
        projection,
        allowed_tool_calls=[
            {"tool_name": "GetResources", "arguments": {"resource_type": "pods"}}
        ],
    ) == ["step 1 used a tool call outside frozen allowlist"]


def test_projection_rejects_credentials_and_local_paths() -> None:
    projection = {
        "case_ref": "cloudopsbench@41a881e:trainticket/service/1",
        "run_manifest": {"debug_path": "C:/Users/example/private/run.json"},
        "stop_reason": "final_answer",
        "steps": [
            {
                "action_type": "finish",
                "final_answer": "Bearer abcdefghijklmnopqrstuvwxyz",
            }
        ],
    }
    errors = validate_projected_trajectory(projection)
    assert "absolute local path" in errors
    assert "credential-like value" in errors


def test_reveal_rejects_unvalidated_agent_freeze(prepared_workspace: Path) -> None:
    case = load_pre_reveal_case(prepared_workspace)
    refs = [item["ref"] for item in case["allowed_tool_calls"][:2]]
    freeze_artifact(
        prepared_workspace,
        "human_diagnosis",
        {
            "case_ref": case["case_ref"],
            "tutorial_manifest_sha256": sha256_file(
                prepared_workspace / "manifest.json"
            ).upper(),
            "symptom": case["symptom"],
            "initial_hypotheses": ["candidate one", "candidate two"],
            "steps": [
                {
                    "step": index,
                    "probe_ref": ref,
                    "observation_summary": f"summary {index}",
                    "effect_on_hypothesis": "changes one candidate",
                    "why_next": "continue the bounded investigation",
                }
                for index, ref in enumerate(refs, start=1)
            ],
            "frozen_diagnosis": "bounded learner answer",
            "limitations": ["synthetic evidence is incomplete"],
            "probe_value_assessment": {
                "useful": {"probe_ref": refs[0], "reason": "changed a candidate"},
                "low_value": {"probe_ref": refs[1], "reason": "added little"},
            },
        },
    )
    freeze_artifact(
        prepared_workspace,
        "agent_projection",
        {
            "case_ref": case["case_ref"],
            "run_manifest": {
                "source_revision": "test-revision",
                "tutorial_manifest_sha256": sha256_file(
                    prepared_workspace / "manifest.json"
                ).upper(),
                "runner_code_sha256": json.loads(
                    (prepared_workspace / "manifest.json").read_text(encoding="utf-8")
                )["runner_code_sha256"],
                "agent_run_view_sha256": json.loads(
                    (prepared_workspace / "manifest.json").read_text(encoding="utf-8")
                )["agent_run_view_sha256"],
            },
            "stop_reason": "final_answer",
            "steps": [{"action_type": "finish", "final_answer": "fake"}],
        },
    )
    with pytest.raises(FileNotFoundError):
        reveal_comparison_material(prepared_workspace)


def test_freeze_is_idempotent_only_for_identical_payload(
    prepared_workspace: Path,
) -> None:
    payload = {"frozen_diagnosis": "same answer"}
    first = freeze_artifact(prepared_workspace, "human_diagnosis", payload)
    second = freeze_artifact(prepared_workspace, "human_diagnosis", payload)
    assert first == second
    with pytest.raises(FileExistsError):
        freeze_artifact(
            prepared_workspace,
            "human_diagnosis",
            {"frozen_diagnosis": "changed after freeze"},
        )


def test_external_path_rejects_another_git_checkout(tmp_path: Path) -> None:
    other_checkout = tmp_path / "other-checkout"
    (other_checkout / ".git").mkdir(parents=True)
    with pytest.raises(ValueError, match="any Git checkout"):
        ensure_external_path(other_checkout / "data" / "tutorial")


def test_runner_code_view_detects_mutation(prepared_workspace: Path) -> None:
    runner_root = verify_runner_code_view(prepared_workspace)
    (runner_root / "run.py").write_text("# mutated after prepare\n", encoding="utf-8")
    with pytest.raises(ValueError, match="differs from the pinned"):
        verify_runner_code_view(prepared_workspace)


def test_pre_reveal_view_detects_tool_cache_mutation(
    prepared_workspace: Path,
) -> None:
    cache_path = prepared_workspace / "pre_reveal" / "tool_cache.json"
    cache_path.write_text('{"injected": "GT_CANARY"}', encoding="utf-8")
    with pytest.raises(ValueError, match="Pre-reveal view differs"):
        verify_pre_reveal_view(prepared_workspace)
    with pytest.raises(ValueError, match="Pre-reveal view differs"):
        load_pre_reveal_case(prepared_workspace)


def test_agent_run_view_detects_snapshot_mutation(prepared_workspace: Path) -> None:
    cache_path = next(
        (prepared_workspace / "agent_run_view").rglob("tool_cache.json")
    )
    cache_path.write_text('{"injected": "GT_CANARY"}', encoding="utf-8")
    with pytest.raises(ValueError, match="Agent run view differs"):
        verify_agent_run_view(prepared_workspace)


def test_runner_verify_survives_import_when_bytecode_is_disabled(
    prepared_workspace: Path,
) -> None:
    import importlib.util

    runner_root = verify_runner_code_view(prepared_workspace)
    original = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec = importlib.util.spec_from_file_location(
            "n00_synthetic_pinned_run", runner_root / "run.py"
        )
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = original
    verify_runner_code_view(prepared_workspace)


def test_comparison_validation_cannot_bypass_reveal_gate(
    prepared_workspace: Path,
) -> None:
    comparison = {
        "agreement_pattern": "not yet available",
        "human_vs_agent_investigation": "not yet available",
        "most_discriminating_probe": "not yet available",
        "low_value_probe": "not yet available",
        "evaluator_gaps": ["not yet available"],
    }
    with pytest.raises(FileNotFoundError):
        validate_orientation_comparison(prepared_workspace, comparison)
    with pytest.raises(FileNotFoundError):
        freeze_validated_orientation_comparison(prepared_workspace, comparison)
