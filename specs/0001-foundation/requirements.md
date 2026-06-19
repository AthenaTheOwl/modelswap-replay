# Spec 0001 — Foundation (ModelSwap Replay)

## R-MSR-001 — repo scaffold
Repo lives at `e:/claude_code/random-apps/modelswap-replay`. MIT
license, copyright Vignesh Gopalakrishnan. README, AGENTS.md,
.gitignore, and `specs/0001-foundation/` exist before any runnable
code lands.

## R-MSR-002 — route registry
`config/routes.yaml` is the single source of truth for which routes are
in scope, which eval suite each route uses, and the per-route LLM-judge
rubric. The registry parses into typed Pydantic models defined by
`schemas/route.schema.json`.

## R-MSR-003 — traffic sampler
`src/sampler/traffic_sampler.py` reads from a trace store (file-backed
in v0) and returns the last N days of sampled requests for a named
route. Sample size and sampling strategy come from the route registry.

## R-MSR-004 — replay runner
`src/replay/replay_runner.py` takes a list of sampled requests and a
candidate model identifier, runs the requests against the candidate,
and returns response objects. The runner is the only module that talks
to a model API.

## R-MSR-005 — score plane
`src/score/eval_runner.py` wraps the route's existing eval suite over
replays. `src/score/llm_judge.py` runs the route's pairwise rubric.
Both emit structured score deltas, not free text.

## R-MSR-006 — verdict author
`src/decide/verdict.py` consumes score deltas plus cost and latency
deltas and emits one of `swap`, `route-split-at-N%`, `hold`, `defer`.
The verdict logic is deterministic given the same input deltas.

## R-MSR-007 — decision record
`src/render/decision_record.py` writes
`decisions/model-swap/<release_id>-<route>.md` containing the verdict,
the deltas, the best three and worst three traces, and an explicit
`revert_threshold:` block. The record validates against
`schemas/decision-record.schema.json`.

## R-MSR-008 — revert threshold required
Every decision record must contain a `revert_threshold:` block with at
least one numeric trigger (quality drop, cost increase, latency
regression). A record without it fails CI.

## R-MSR-009 — gates
Four gates run in CI and locally: `voice_lint.py`, `spec_check.py`,
`validate_schemas.py`, `revert_threshold_present.py`. A PR that fails
any gate does not merge.

## R-MSR-010 — offline fixture
`tests/fixtures/` ships a synthetic route registry, a synthetic trace
store, and a recorded model response for one candidate so the test
suite runs offline with no network and no model key.

## R-MSR-011 — eval-predictive-validity bolt-on (deferred to spec 0003)
A bolt-on report that tracks which evals in the suite have predicted
production outcomes over the last N releases, scoped to spec 0003.
