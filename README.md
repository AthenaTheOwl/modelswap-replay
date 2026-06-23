# ModelSwap Replay

ModelSwap Replay is a local release gate for LLM model swaps. It samples
recent route traffic, replays the sampled requests against a candidate
release, scores the replay, and writes a decision record with a
pre-declared revert threshold.

The decision record is the deliverable. It is a Markdown file with YAML
front matter that can be reviewed, validated, and merged.

## Current state

- v0.1 ships a runnable Python CLI: `modelswap replay`.
- The package surface is `modelswap_replay/`.
- The fixture route is `customer-support`.
- The checked-in decision record is
  `decisions/model-swap/fixture-candidate-v1-customer-support.md`.
- The checked-in JSONL report is
  `reports/fixture-candidate-v1-customer-support.jsonl`.

## Run

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

## show

Print a ranked, readable summary of the committed decision record (read-only,
offline):

```bash
python -m uv run modelswap show
```

It parses the decision record's YAML front matter, ranks the replayed traces by
quality delta, and prints a headline verdict.

## live demo

Run the card-of-record browser locally:

```bash
python -m uv run --with streamlit streamlit run streamlit_app.py
```

The app reads the committed decision record
(`decisions/model-swap/fixture-candidate-v1-customer-support.md`) directly: no
network, no secrets. It shows the verdict, quality / cost / latency deltas, and
a trace table ranked by quality delta with a regressions-only filter.

Deploy on Streamlit Cloud: repo `AthenaTheOwl/modelswap-replay`, branch `main`,
main file `streamlit_app.py`.

<!-- live-url: https://share.streamlit.io/... -->

## Layout

```text
modelswap-replay/
  PRODUCT_BRIEF.md
  SYSTEM_MAP.md
  STATUS.md
  pyproject.toml
  modelswap_replay/
    cli.py
    model.py
    scoring.py
    rendering.py
  cli/
    main.py
  src/
    sampler/
    replay/
    score/
    decide/
    render/
    models/
  config/
    routes.yaml
  schemas/
    decision-record.schema.json
    route.schema.json
  decisions/model-swap/
    fixture-candidate-v1-customer-support.md
  reports/
    fixture-candidate-v1-customer-support.jsonl
  specs/
    0001-foundation/
    0002-design/
  tests/
```

## Scope

- Offline replay only.
- One route per command invocation.
- Fixture-backed judge and recorded responses.
- No router changes.
- No live model calls.

## License

MIT. See `LICENSE`.
