# ModelSwap Replay

On every frontier model release, ModelSwap Replay auto-replays the last
seven days of sampled production traffic per route, scores the replays
with the existing eval suite plus an LLM judge, and emits a per-route
`swap` / `route-split-at-N%` / `hold` / `defer` decision record with a
pre-declared revert threshold.

## What this is

The release-gate decision plane for an LLM routing layer. Every two to
four weeks a frontier release happens. Most teams either swap on vibes
or wait six weeks for someone to run an offline eval that's already
stale. ModelSwap Replay is the small, opinionated CLI that closes the
loop:

1. Sample the last seven days of production traffic per route
2. Replay every sampled request against the candidate model
3. Score replays with the route's existing eval suite plus an LLM judge
4. Diff cost, latency, and quality versus the incumbent
5. Emit one `decisions/model-swap/<release_id>-<route>.md` per route,
   with the verdict and a revert threshold that is written down before
   the swap goes live

The output is a typed artifact, not a dashboard. The artifact is what a
human reads, signs, and merges.

## Status

v0 scaffold. No implementation yet — only the spec ledger, the AGENTS
contract, and the file layout below. First runnable code lands in
spec 0002.

- [x] Repo scaffold + LICENSE + AGENTS.md
- [x] Spec 0001 (foundation) — requirements, design, tasks, acceptance
- [x] First-PR plan in `docs/first-pr.md`
- [ ] Route registry schema
- [ ] Traffic sampler against a fixture trace store
- [ ] First verdict on the next frontier release for one named route
- [ ] Eval-predictive-validity bolt-on report

## How to run

Placeholder. The runnable CLI lands in spec 0002. Intended shape:

```bash
uv sync
uv run modelswap replay \
    --route customer-support \
    --release claude-opus-4-7 \
    --since 7d \
    --out decisions/model-swap/claude-opus-4-7-customer-support.md
```

Until spec 0002 lands, the only thing in this repo that runs is
`python -c "print('scaffold')"`.

## Layout

```
modelswap-replay/
  README.md
  LICENSE
  AGENTS.md
  .gitignore
  specs/
    0001-foundation/
      requirements.md
      design.md
      tasks.md
      acceptance.md
  docs/
    first-pr.md
```

Planned but not yet present:

```
  cli/
    main.py
  src/
    sampler/
      traffic_sampler.py
    replay/
      replay_runner.py
    score/
      eval_runner.py
      llm_judge.py
    decide/
      verdict.py
    render/
      decision_record.py
  config/
    routes.yaml
  schemas/
    decision-record.schema.json
    route.schema.json
  decisions/
    model-swap/
      .gitkeep
  tests/
    fixtures/
  pyproject.toml
```

## Who this is for

- Platform teams running an LLM router with more than two routes and
  more than one model in production.
- Individual builders who want a written-down revert threshold instead
  of a Slack message saying "looks fine."
- Eval-discipline teams who want a release-gate that consumes their
  existing eval suite instead of replacing it.

## What this is not

- Not a routing layer. ModelSwap reads from your router's traffic; it
  does not route traffic.
- Not a model-eval framework. It runs an eval suite you already own.
- Not a dashboard. The output is a per-route decision record file.

## License

MIT. See `LICENSE`.
