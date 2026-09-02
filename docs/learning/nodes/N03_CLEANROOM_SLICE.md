# N03 | Build a clean-room replay/evaluator slice

> Status: Planned skeleton
> Previous: [N02 contracts and Ground Truth](N02_CONTRACTS_AND_TRUTH.md)
> Next: project MS-1 continuation

## 1. Audience and outcome

For a learner who has completed the contract and visibility exercise. The outcome is a project-authored, executable case-to-evaluation slice that does not need an LLM or third-party data.

## 2. Prerequisite artifact from N02

Input is the N02 rule table, visibility diagram, and legal/invalid examples. Only the minimum rules required for one clean-room case are implemented.

## 3. Project-authored fixture

Create one original case with an initial symptom, one or two registered read-only probes, fixed observations, and evaluator-only Ground Truth. The output set includes `IncidentCase`, replay snapshot, good/bad `DiagnosisReport`, canonical `RunRecord`, and isolated `EvaluationRecord`.

## 4. Deterministic replay behavior

`FixtureAgentDriver` emits a preset report and is not called an intelligent Agent. The runner owns canonical tool, budget, sequence, and terminal events; replay returns the same observation for the same case snapshot and valid probe request.

## 5. Frozen report and independent validation

Separate structural contract validation from independent factual/evidence evaluation. Freeze `DiagnosisReport` and `RunRecord`, then and only then load Ground Truth through the evaluator-only loader and write a separate `EvaluationRecord`; `RunRecord` contains neither truth nor evaluator details.

## 6. Negative case and expected failure

The primary bad report is structurally valid but has a wrong cause or nonexistent evidence ref, so only the evaluator catches it. Add a Ground Truth canary/dependency-boundary negative test to prove the runtime cannot access truth.

## 7. Exercise and formal project artifact

The single TODO modifies formal source/test artifacts; the notebook imports and demonstrates them rather than duplicating implementation. It must produce one passing and one expected failing evaluation.

## 8. Pass criteria and MS-1 handoff

Checks: good report passes; bad report fails for the named evaluator reason; `Restart & Run All` and the formal tests reproduce the same outcome. Only then continue MS-1 and later consider formal public-case smoke integration.

### Input contract / output handoff

- Input: N02 minimum contracts and visibility rules.
- Output: project source/tests for the clean-room slice plus reproducible notebook evidence; ReferenceAgentDriver remains after this node.
