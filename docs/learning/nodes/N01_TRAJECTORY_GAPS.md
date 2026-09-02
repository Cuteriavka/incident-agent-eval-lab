# N01 | Analyze trajectory and evaluation gaps

> Status: Planned skeleton
> Previous: [N00 real replay diagnosis](N00_CLOUDOPSBENCH_ORIENTATION.md)
> Next: [N02 contracts and Ground Truth](N02_CONTRACTS_AND_TRUTH.md)

## 1. Audience and outcome

For a learner who has completed N00. The outcome is a `gap_table` that turns observed investigation behavior into testable evaluator questions.

## 2. Prerequisite artifact from N00

Input is the private external `orientation_report`, Ground-Truth-free `trajectory_projection`, and project-authored `orientation_comparison` frozen in N00. Raw upstream trajectory, third-party payload, Ground Truth, and process labels are not copied into this node or Git.

## 3. Running case

Reuse the N00 tutorial case only to compare ordered actions, evidence acquisition, conclusion, and limitations; it remains `tutorial/dev-only`.

## 4. Final-answer correctness versus investigation quality

Separate at least one case where a plausible/correct answer can coexist with missing evidence, unsafe behavior, or an unjustified conclusion.

## 5. Evidence acquisition, ordering, redundancy, and abstention

Inspect whether actions obtained discriminating evidence, repeated low-value probes, followed a useful order, and abstained when the available evidence was insufficient.

## 6. Map observed gaps to evaluator requirements

Each `gap_table` row has: `observed_event`, `missing_or_unsafe_behavior`, `evaluator_question`, `required_observable`, `owner_or_visibility`, and `candidate_pass_fail_fixture`.

## 7. Exercise and expected artifact

The single TODO is to write gap rows covering evidence acquisition, redundancy or ordering, and abstention. Each row must lead to one evaluator requirement rather than a generic recommendation.

## 8. Pass criteria and next node

Checks: required columns are complete; at least three observed gaps are covered; every gap maps to a pass/fail fixture candidate. N02 consumes this table to derive producers, consumers, fields, and visibility rules.

### Input contract / output handoff

- Input: N00 `orientation_report`, allowlisted `trajectory_projection`, and `orientation_comparison`.
- Output: `gap_table`; N02 must cite its row IDs when proposing a contract rule.
