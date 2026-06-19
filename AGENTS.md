# AGENTS.md — modelswap-replay

Operating contract for AI agents (Claude, Codex, Cursor) working in this
repo. Conventions match the rest of the AthenaTheOwl portfolio so an
agent already trained on trace-to-eval-harness or
procurement-negotiation-lab recognizes the shape.

## What this repo is

A release-gate decision plane for an LLM routing layer. Each frontier
model release triggers a per-route replay-and-score pass and emits a
written verdict with a pre-declared revert threshold. The artifact, not
the score, is the deliverable.

## Roles you may see in tasks

| Role | What they do |
|---|---|
| `traffic-sampler` | Pulls last-N-day production traffic per route from the trace store |
| `replay-runner` | Re-runs sampled requests against the candidate model |
| `eval-runner` | Wraps the route's existing eval suite over replays |
| `llm-judge` | Pairwise scoring on the qualitative axes the suite doesn't cover |
| `verdict-author` | Combines deltas into swap / route-split / hold / defer |
| `revert-threshold-author` | Writes the explicit revert rule before swap goes live |
| `record-renderer` | Writes `decisions/model-swap/<release_id>-<route>.md` |

These roles exist in the spec ledger; v0 does not implement them.

## Voice constraints

- No marketing words.
- No antithetical reversals as a structural device.
- Plain assertions. The decision record is structured data with a
  human-readable wrapper. Skip the adjectives.

## Gates (will land in spec 0002)

- `voice_lint.py` mirrored from athena-site, run on every emitted
  decision record
- `spec_check.py` — every `R-MSR-*` ID in `specs/` is implemented or
  tested by the time its parent PR merges
- `validate_schemas.py` — `decision-record.schema.json` validates every
  file under `decisions/model-swap/`
- `revert_threshold_present.py` — fails if a decision record has no
  `revert_threshold:` block

## Out of scope

- Routing requests. The router stays where it is. ModelSwap is a
  pre-flight gate.
- Online learning. The replay set is sampled and immutable per release.
- Cross-org telemetry. Each deployment runs against its own routes; no
  shared scoreboard.
