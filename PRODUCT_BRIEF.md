# Product Brief

## Product

ModelSwap Replay is a local release gate for teams that swap LLM
models behind an existing router. It samples recent route traffic,
replays that traffic against a candidate release, scores the replay,
and writes a decision record with a revert threshold.

## User

- Platform owner responsible for model release changes.
- Eval owner responsible for route-level quality checks.
- Reviewer responsible for approving or rejecting a model swap record.

## v0.1 scope

- Offline replay only.
- One route per command invocation.
- One checked-in fixture route named `customer-support`.
- One Markdown decision record under `decisions/model-swap/`.
- One JSONL report artifact under `reports/`.

## Non-goals

- No live routing.
- No live model calls.
- No shared cross-organization telemetry.

## Artifact

The decision record is the review surface. It contains the verdict,
sample window, quality delta, cost delta, latency delta, best traces,
worst traces, and `revert_threshold:` block.
