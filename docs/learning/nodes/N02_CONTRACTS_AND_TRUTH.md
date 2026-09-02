# N02 | Define contracts and Ground Truth isolation

> Status: Planned skeleton
> Previous: [N01 trajectory and evaluation gaps](N01_TRAJECTORY_GAPS.md)
> Next: [N03 clean-room replay/evaluator slice](N03_CLEANROOM_SLICE.md)

## 1. Audience and outcome

For a learner who can name concrete evaluator gaps but has not yet defined data contracts. The output is a field/rule table plus one legal and one leakage-invalid ordinary JSON example.

## 2. Prerequisite artifact from N01

Input is the `gap_table`. Every proposed field or rule cites the gap row that requires it; fields are not invented from an abstract schema checklist.

## 3. Producers, consumers, and visibility zones

Freeze this flow: adapter produces Agent-visible `IncidentCase`; replay/runner produces canonical `RunRecord`; FixtureAgentDriver or Agent produces `DiagnosisReport`; evaluator-only truth loader produces Ground Truth after report freeze; evaluator produces isolated `EvaluationRecord`.

The field/rule table records `producer`, `consumer`, `visibility`, `required_when`, and `source_gap`. Ground Truth cannot appear in hidden fields, filenames, case IDs, manifests, debug traces, prompts, tool results, or Agent-visible indexes.

## 4. Minimum case and report rules

Define only the rules required by N01 gaps and the minimum N03 clean-room slice. Formal JSON Schema syntax is a later implementation step.

## 5. Provenance and opaque joins

The join key is opaque and cannot encode an answer. Runtime/Agent packages cannot import the evaluator-only truth loader; report and RunRecord must freeze before truth is loaded.

## 6. Legal and leakage-invalid examples

The legal example contains only Agent-visible case material. The invalid example demonstrates one explicit leakage path and must be rejected by a named rule.

## 7. Exercise and expected artifact

The single TODO is to complete the rule table and two JSON examples. The exercise includes one negative assertion that the Agent-visible path cannot load truth.

## 8. Pass criteria and next node

Checks: legal JSON passes the stated business rules; leakage-invalid JSON fails for the intended reason; no Agent-visible producer depends on the truth loader. N03 implements only this minimum contract.

### Input contract / output handoff

- Input: N01 `gap_table` with stable row IDs.
- Output: field/rule table, legal JSON, leakage-invalid JSON, and the producer/consumer/visibility diagram used by N03.
