# Linear Learning Path

> Status: Active learning route
> Rule: unlock one node at a time; the notebook is the daily task entrypoint

## Why this route exists

The project must begin with an observable diagnosis experience, then turn that experience into contracts, safety boundaries, replay behavior, and evaluator requirements. A completed tutorial run is learning evidence only; it is not evidence that this repository has implemented or outperformed a diagnosis Agent.

## The first continuous segment

```text
N00 Observe one real replay case
  -> N01 Analyze the trajectory and evaluation gaps
  -> N02 Define contracts and Ground Truth isolation
  -> N03 Build a clean-room replay/evaluator slice
```

| Node | Concrete question | Input | Observable artifact | Unlocks |
|---|---|---|---|---|
| [N00](nodes/N00_CLOUDOPSBENCH_ORIENTATION.md) | What does an Agent actually see, query, miss, and report? | Cloud-OpsBench `trainticket/service/1` outside this repository | Frozen `orientation_report`, validated `trajectory_projection`, and post-reveal `orientation_comparison` | N01 |
| [N01](nodes/N01_TRAJECTORY_GAPS.md) | Why can a correct final answer still be a poor investigation? | Human/tool trajectory and an upstream trajectory | Gap table linking observations to evaluator requirements | N02 |
| [N02](nodes/N02_CONTRACTS_AND_TRUTH.md) | Which fields belong to the Agent, runner, report, and evaluator? | One tutorial case plus a clean-room analogue | Field/rule table, legal JSON, leakage-invalid JSON | N03 |
| [N03](nodes/N03_CLEANROOM_SLICE.md) | Can the project reject a bad report without an LLM or third-party data? | Project-authored fixture | Deterministic replay/evaluator result and failing negative case | MS-1 continuation |

## Two-stage use of public data

1. **Orientation now**: inspect one upstream case and use its cached read-only tools. The case is permanently `tutorial/dev-only`; no metric or compatibility claim follows.
2. **Formal smoke after the clean-room slice**: select a different, still-unrevealed case and adapt it through a reviewed data card, project-owned contracts, two separate visibility paths, the same runner, and the independent evaluator. The N00 tutorial case can never become held-out data. Batch benchmarking remains later work.

## Daily entry rule

The daily message contains only the current node, one start command, and the checkpoint to finish. A tracked empty-output starter creates a repository-external working notebook containing the case, explanation, current exercise, self-check, and submission instructions. Later checkpoints are visibly locked and are not additional work for today.

## Content build rule

Long lessons are produced in two passes:

1. Freeze a skeleton: audience, learning outcome, prerequisite, running case, section purpose, input/output handoff, evidence, one exercise, expected behavior, no more than three checks, safety boundary, and previous/next links.
2. Review the skeleton for continuity, then fill the current node as one complete minimum vertical lesson. Run and review the whole node before release; do not publish partially filled sections. A future node remains a skeleton until it is close to being unlocked.

### Definition of Ready for a node

- The running case, input/output handoff, one exercise, expected behavior, three checks, and safety boundary are non-empty.
- The required path can run in a clean notebook kernel without a hidden execution order. Any external credential gate is explicit.
- Only the current node may become a daily task. Passing it unlocks the next node; future skeletons are navigation, not assignments.
