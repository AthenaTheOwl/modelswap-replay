# Spec 0001 — Design (ModelSwap Replay)

## Pipeline shape

```
config/routes.yaml
        │
        ▼
sampler ──► replay ──► score (eval suite + LLM judge) ──► verdict ──► record
        │                                                                  │
        ▼                                                                  ▼
trace store                                          decisions/model-swap/<release>-<route>.md
```

One CLI invocation per (release, route) pair. The router stays where it
is; ModelSwap reads sampled traffic out of the trace store and writes
exactly one decision record.

## Module map

```
cli/
  main.py                      # click group; one command, `replay`
src/
  sampler/
    traffic_sampler.py         # reads trace store, returns SampledRequest list
  replay/
    replay_runner.py           # only module that calls a model API
  score/
    eval_runner.py             # wraps the route's existing eval suite
    llm_judge.py               # pairwise rubric per route
  decide/
    verdict.py                 # deterministic on the same score deltas
  render/
    decision_record.py         # writes the .md + validates schema
config/
  routes.yaml
schemas/
  route.schema.json
  decision-record.schema.json
```

## Route registry shape

```yaml
# config/routes.yaml
routes:
  - name: customer-support
    incumbent: claude-sonnet-4-5
    trace_store: ops/traces/customer-support
    sample:
      window_days: 7
      per_day_n: 200
      strategy: stratified-by-intent
    eval_suite: evals/customer_support_v3
    llm_judge_rubric: rubrics/customer_support.md
    revert_threshold:
      quality_drop_max: 0.03
      cost_increase_max: 0.20
      latency_p95_regression_ms_max: 250
```

## Decision-record shape

```markdown
# Model Swap — claude-opus-4-7 → customer-support
- Verdict: route-split-at-25%
- Incumbent: claude-sonnet-4-5
- Candidate: claude-opus-4-7
- Sample window: 2026-06-10..2026-06-17 (1,402 requests)
- Quality delta: +0.04 (citation faithfulness +0.06; refusal -0.01)
- Cost delta: +0.18 per request
- Latency p95 delta: +180 ms
- Best traces: …
- Worst traces: …
- Revert threshold:
  - quality_drop_max: 0.03
  - cost_increase_max: 0.20
  - latency_p95_regression_ms_max: 250
- Revert review date: 2026-07-01
```

The record is the artifact. The dashboard is the file system.

## Determinism

- Sampler uses a seed pinned in the route registry. Same window + same
  store + same seed = same sample.
- Verdict logic is pure: same deltas in, same verdict out.
- LLM-judge pairwise scoring runs at `temperature=0` and stores the
  judge model version in the decision record.

## Test discipline

- One unit test per `R-MSR-*` requirement.
- One integration test that runs the full pipeline against the offline
  fixture and diffs the emitted record against `tests/fixtures/expected/`.
- No test hits a live model API.
