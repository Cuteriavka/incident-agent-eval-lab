# Cloud-OpsBench tutorial source record

> Status: Prepared for N00; not approved as a v0.1 benchmark data card

## 1. Purpose and non-claim

This record supports one staged project-orientation exercise over an upstream case. It does not approve Cloud-OpsBench as the v0.1 core dataset, prove adapter compatibility, or authorize publishing benchmark results. The selected case is permanently `tutorial/dev-only` after reveal.

## 2. Source, revision, archive checksum, and license

- Source: <https://github.com/LLM4Ops/Cloud-OpsBench>
- Pinned revision: `41a881e4e3fb0696f6ed519c882e76e020c3689a`
- Download form: GitHub codeload ZIP for the pinned revision
- Archive size: `388,534,020` bytes
- Archive SHA-256: `D3DFB1976F49EC5A18EFF60A103FA6C103AADFF18CAF52500819919ADC8AB22D`
- Extracted payload size observed locally: `3,835,673,178` bytes
- Root license at the pinned revision: MIT, copyright 2026 Yilun Wang

This project's MIT license does not replace Cloud-OpsBench's upstream license. The third-party checkout remains governed by its upstream license, and the source, revision, file-level provenance, and redistribution rights must be rechecked before any formal benchmark integration.

## 3. Local storage and redistribution boundary

The ZIP, checkout, prepared pre-reveal bundle, Ground Truth, process labels, golden trajectories, raw traces, model outputs, and run logs remain under a repository-external local data area. None is copied into this public repository. A real API credential is never written into an upstream YAML file, notebook, committed environment file, or log.

The committed notebook is an empty-output starter that cannot execute directly. `scripts/start_n00.py` copies it into the repository-external tutorial workspace and starts Jupyter there. Public artifacts may refer to upstream file IDs and contain project-authored summaries, but they must not reproduce raw tool responses, labels, Ground Truth text, expert paths, absolute local paths, or secrets.

## 4. Selected tutorial case

- Case reference: `cloudopsbench@41a881e:trainticket/service/1`
- Upstream location: `benchmark/trainticket/service/1`
- Initial symptom: `Partial Service Unreachability.`
- Namespace: `train-ticket`
- Local case payload size observed: `8,399,677` bytes

The upstream `metadata.json` contains both Agent-visible symptom fields and evaluator-only result fields. The upstream `interact.py` randomly chooses a case, so N00 uses a project-owned teaching wrapper to select this exact case and create separated tutorial views.

## 5. Pre-reveal and compare-only views

The preparation step writes two repository-external views:

```text
pre_reveal/
  case.json          # case ref, namespace, symptom only
  tool_cache.json    # cached read-only tool responses

agent_run_view/
  benchmark/trainticket/service/1/
                     # derived upstream-compatible snapshot
                     # metadata contains namespace/query, never result

runner_code_view/
  cloudops_agent/     # extracted directly from the verified pinned ZIP
                     # tree hash is frozen in manifest and rechecked before key use

compare_only/
  truth.json         # Ground Truth copied from the pinned metadata
  milestone.json     # upstream process annotations
```

The external working notebook uses `pre_reveal/` for N00A. N00B imports only the `runner_code_view` extracted from the verified archive and gives it only `agent_run_view/`, which excludes Ground Truth metadata, process labels, and golden trajectories. The runner tree hash is rechecked before the credential is passed to it, and a project-owned exact-call guard rejects non-frozen tool requests before upstream execution. Ground Truth and process labels load only after a valid human report, a wrapper-validated Agent projection, their hashes, and the run validation marker all match. These are directory and workflow gates under one user's permissions—not a strong authorization boundary. Golden trajectories remain outside all required views.

Leakage tests use injected, unique canaries in evaluator-only annotation fields. They do not ban every scalar value that also occurs in Ground Truth: a true faulty resource name can legitimately appear in Agent-visible observations and must remain available as evidence. The boundary excludes the answer annotation channel, not the observable system facts needed to infer an answer.

## 6. N00 artifact publication state

Only the empty-output starter, project-authored code/tests, this source record, and upstream links are public in N00. The frozen `orientation_report`, Agent projection, `orientation_comparison`, hashes, run marker, and working notebook all remain private in the repository-external tutorial workspace.

No generated N00 artifact is publication-approved yet. A later `export-public-artifact` design must scan credentials and local paths, reject long/structural overlap with raw observations, truth and process labels, and still require a human clean-room/ownership review. Until that gate exists, do not copy any N00 generated artifact into Git.

## 7. Formal integration gate

After the clean-room replay/evaluator slice passes, formal smoke work must choose a different, still-unrevealed case. It requires a full data card, refreshed license/provenance/checksum review, separate Agent-visible and evaluator-only paths, the project runner/evaluator, and leakage tests. Until then Cloud-OpsBench remains an orientation source, not the declared v0.1 core dataset.
