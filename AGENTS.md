# Project Working Agreement

## Scope

This repository is a public clean-room portfolio project. Before changing it, read:

1. `docs/PROJECT_BRIEF.md` for the problem and boundaries.
2. `docs/PROJECT_ROADMAP.md` for milestones, requirements, and exit gates.
3. `STATE.md` for the current single next action.
4. `NOTICE.md` for attribution and data-license rules.

More specific instructions closer to a file may override this document. Personal career facts, salary, location, employer information, and private JD notes do not belong in this repository.

## Product boundaries

- Treat the independent evaluator as the primary product and the bounded reference diagnosis Agent as its first controlled system under test. Both remain required for v0.1.
- Keep the reference Agent core explicit: `ReferenceAgentDriver = ProjectController + Policy`. Its controller owns that Agent's internal state and termination. The outer runner always owns the Ground Truth firewall, tool gateway, global budget caps, canonical run events, and final validator; another conforming `AgentDriver` may own internal orchestration but may not bypass runner invariants.
- Keep replay-first: deterministic evidence playback is the v0.1 environment; a live cluster is optional later validation.
- Treat Runbook RAG as an independently evaluated subsystem, not as the whole product.
- Use `SystemKnowledgePack` on first mention; do not assume `SystemPack` is a standard industry term.
- v0.1 is read-only. Do not add arbitrary shell, kubectl, filesystem access, dynamic scripts, or automatic remediation.
- Never expose Ground Truth to the Agent through fields, filenames, manifests, indexes, prompts, or tools.
- Treat the project-authored `RunRecord` as the canonical source for observable run behavior, budgets, tool results, failures, and version metadata. Case/replay snapshots and evaluator-only Ground Truth/EvaluationRecord remain separate canonical sources. Framework traces are derived views only.
- Generalize only the three provisional v0.1 seams `AgentDriver`, `RunRecord`, and `BenchmarkSpec`. Their cross-task reuse is unverified. Keep incident cases, reports, probes, evidence, truth loading, and root-cause metrics domain-specific.
- LangGraph may be added later as an optional thin adapter after the custom vertical slice passes. It is not a v0.1 release gate and must use the same tool gateway, budgets, artifacts, and evaluator.
- `RunRecord` must never contain Ground Truth or evaluator details beyond an opaque report reference. Trace exporters may consume only an explicit pre-evaluation allowlist projection, with negative tests for Ground Truth canaries, credentials, and restricted payloads.
- Do not market v0.1 as a universal Agent evaluation platform. A future competition-Agent integration is a post-v0.1 portability experiment, not a current deliverable.
- Do not claim production readiness, accuracy improvements, or dataset compatibility before reproducible evidence exists.

## Clean-room and third-party content

- Do not use company code, logs, prompts, rules, architecture, names, customer information, or other non-public material.
- Raw and derived third-party payloads are not committed by default. A data card must explicitly establish redistribution permission before any exception. Clean-room synthetic fixtures and project-authored metadata may be committed when their provenance is recorded.
- The repository MIT License covers original repository content only; it does not relicense third-party data, code, or documentation.

## Learning task gate

Before issuing or revising a daily task for this repository:

- Show its position in the data flow, upstream/downstream consumer, concrete input/output, observed/unknown facts, terminology, and downstream use.
- Give a short AI explanation, one authoritative reading, and at most one adjacent source target before asking for a design.
- Limit the task to one project problem, one main concept, one primary artifact, and no more than three acceptance checks.
- Split the task when it combines a new domain concept, new technology syntax, and new implementation/testing work.
- Provide both a standard version and a 15-minute version.

The learner owns decisions about schemas, metrics, leakage prevention, core tests, security boundaries, and error analysis. AI may explain, question, and review before providing a rescue implementation.

The active learning route is `docs/learning/LEARNING_PATH.md`. Daily work is linear: publish only the current unlocked node, use its notebook as the learner-facing task entrypoint, and keep formal implementation in importable source and tests rather than notebook-only code. A credential wait state preserves completed offline work and never authorizes early Ground Truth reveal.

For a long lesson or roadmap, first freeze an article skeleton containing audience, outcome, running case, section purposes, input/output handoff, one exercise, checks, safety boundary, and previous/next links. Review that skeleton before filling prose. Release one complete minimum lesson at a time; future nodes may remain navigation skeletons but must not masquerade as ready教材.

## Mandatory review

Use subagents before publishing or materially revising:

- a daily learning task;
- a milestone or project plan;
- an architecture, data, evaluation, or safety decision;
- public portfolio or interview-evidence claims.

Daily tasks require two roles: a prerequisite/context critic and an execution/test/acceptance critic. Project decisions require three perspectives: domain/architecture; data/evaluation/safety; and scope/ownership/interview evidence. `P0` means privacy, credentials, company non-public material, Ground Truth, license, or dangerous-action risk; `P1` means the task cannot prove its requirement, breaks an interface, or makes an unsupported public claim. P0/P1 findings must be fixed before release. If subagents are unavailable, label the review as degraded, apply the same checklist, and request user confirmation before publishing the task or decision.

## Verification and ownership

- Contract and safety work starts with a failing example or test when implementation begins.
- A passing test is not enough: the author must explain the choice, predict one boundary input, modify one test, and name one alternative with its cost.
- Keep deterministic replay guarantees separate from external LLM output variance.
- `STATE.md` records the current gate and one next action; the roadmap records milestones, not daily history.
