# Project Working Agreement

## Scope

This repository is a public clean-room portfolio project. Before changing it, read:

1. `docs/PROJECT_BRIEF.md` for the problem and boundaries.
2. `docs/PROJECT_ROADMAP.md` for milestones, requirements, and exit gates.
3. `STATE.md` for the current single next action.
4. `NOTICE.md` for attribution and data-license rules.

More specific instructions closer to a file may override this document. Personal career facts, salary, location, employer information, and private JD notes do not belong in this repository.

## Product boundaries

- Deliver both a minimal reference diagnosis Agent and an independent evaluator.
- Keep replay-first: deterministic evidence playback is the v0.1 environment; a live cluster is optional later validation.
- Treat Runbook RAG as an independently evaluated subsystem, not as the whole product.
- Use `SystemKnowledgePack` on first mention; do not assume `SystemPack` is a standard industry term.
- v0.1 is read-only. Do not add arbitrary shell, kubectl, filesystem access, dynamic scripts, or automatic remediation.
- Never expose Ground Truth to the Agent through fields, filenames, manifests, indexes, prompts, or tools.
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
