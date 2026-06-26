# modelswap-replay

A new model release lands and someone wants to point production traffic at it
by Friday. modelswap-replay replays six recorded customer-support requests
against the candidate, finds it wins five of six and loses one, and stamps a
verdict: swap. The interesting part is not the number. It's the dated revert
rule it writes next to it, before the swap goes live.

## What it does

Swapping the model behind a router is a one-line config change and a quiet
afternoon of regret. The new model is cheaper, faster on p95, and slightly
worse at the one route nobody was watching. By the time someone notices, the
old release tag is three deploys back and nobody wrote down what "worse" was
supposed to mean.

modelswap-replay makes the swap go through a gate. It samples recent traffic
for one route, replays it against the candidate, scores quality, cost, and
latency against the incumbent, runs a pairwise judge over the qualitative
axes the eval suite misses, and writes the whole thing to a Markdown file with
YAML front matter. That file — the decision record — is the deliverable, not
the verdict it carries. You can review it, validate it against a schema, and
merge it. And it carries a `revert_threshold:` block written before the swap
ships: the quality drop, cost increase, and p95 regression that will pull the
release back, plus the date someone has to look again.

v0.1 is offline only. One route, one checked-in fixture (`customer-support`),
a recorded judge, no live model calls. The gate is the point; the network is
deliberately absent.

## Try it

Read-only, offline. It parses the committed decision record, ranks the
replayed traces by quality delta, and prints the verdict:

```bash
python -m uv run modelswap show
```

```
model swap gate -- fixture-candidate-v1 -> customer-support
========================================================

verdict        : swap
incumbent      : fixture-incumbent-v1
candidate      : fixture-candidate-v1
sample window  : 2026-06-15..2026-06-17 (6 requests)

deltas (candidate vs incumbent)
  metric                       value
  ----------------------------------
  quality                     +0.053
  cost ratio                  -0.105
  latency p95 (ms)               +30
  judge win-rate                83%

traces ranked by quality delta
  rank trace              quality    cost usd   lat ms
  ----------------------------------------------------
  1    trace-cs-002        +0.080     -0.0003      -40
  2    trace-cs-005        +0.080     -0.0004      -30
  3    trace-cs-004        +0.070     -0.0004      -35
  4    trace-cs-001        +0.060     -0.0003      -40
  5    trace-cs-006        +0.060     -0.0003      -30
  6    trace-cs-003        -0.030     -0.0002      +30
```

trace-cs-003 is the one that got worse. It's still in the table, at the
bottom, because a swap that hides its one regression isn't a swap you should
trust.

## Live demo

The card-of-record browser is the same decision record as a page you can poke
— the verdict, the quality / cost / latency deltas, and a trace table ranked
by quality delta with a regressions-only filter. It reads the committed record
directly: no network, no secrets.

```bash
python -m uv run --with streamlit streamlit run streamlit_app.py
```

Deploy on Streamlit Cloud: repo `AthenaTheOwl/modelswap-replay`, branch `main`,
main file `streamlit_app.py`.

<!-- live-url: https://share.streamlit.io/... -->

## How it connects

The decision record borrows its shape from the rest of the portfolio, so a
gate here looks like a gate there:

- [trace-to-eval-harness](https://github.com/AthenaTheOwl/trace-to-eval-harness)
  — turns production traces into the eval suite this gate replays against.
- [procurement-negotiation-lab](https://github.com/AthenaTheOwl/procurement-negotiation-lab)
  — the same written-verdict-with-a-revert-rule discipline, pointed at a
  different decision.

## Run it in full

```bash
python -m pytest -v
python -m cli.main replay \
  --route customer-support \
  --release fixture-candidate-v1 \
  --since 7d \
  --offline \
  --routes tests/fixtures/routes.yaml \
  --recorded-root tests/fixtures/recorded_responses \
  --out decisions/model-swap/fixture-candidate-v1-customer-support.md
python scripts/voice_lint.py
python scripts/spec_check.py
python scripts/validate_schemas.py decisions/model-swap/
python scripts/revert_threshold_present.py decisions/model-swap/
```

With uv:

```bash
python -m uv sync
python -m uv run pytest -v
python -m uv run modelswap replay \
  --route customer-support \
  --release fixture-candidate-v1 \
  --since 7d \
  --offline \
  --out decisions/model-swap/fixture-candidate-v1-customer-support.md
```

`revert_threshold_present.py` fails the record that ships without a revert
rule. The gate refuses to let a swap go out undated.

## Layout

```text
modelswap_replay/   cli, model, scoring, rendering
cli/main.py         the replay entrypoint
src/                sampler, replay, score, decide, render, models
config/routes.yaml  the one fixture route
schemas/            decision-record + route schemas
decisions/model-swap/fixture-candidate-v1-customer-support.md   the checked-in record
reports/            the JSONL report behind it
specs/  tests/
```

## Scope

Offline replay, one route per invocation, fixture-backed judge and recorded
responses. No router changes, no live model calls.

## License

MIT. See `LICENSE`.
