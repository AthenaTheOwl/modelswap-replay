# First PR after the scaffold

This file describes the literal next PR after the v0 scaffold lands.
Spec 0002 is the work plan; this file is the file-level changeset.

## Goal

A `modelswap replay` command that, given a route name, a candidate
release id, and a time window, reads sampled traffic from an offline
fixture trace store, replays each request against a fixture-recorded
candidate model, scores the replays, emits a verdict, and writes one
schema-valid decision record under `decisions/model-swap/`.

No live model API call in this PR. The replay adapter has two
implementations: a real one (deferred) and an `OfflineAdapter` that
reads pre-recorded responses from `tests/fixtures/`.

## Files changed

New:

- `pyproject.toml` — Python 3.11, `uv`, `pydantic`, `jsonschema`, `click`
- `cli/main.py` — `click` group with `replay`
- `config/routes.yaml` — one example route (`customer-support`)
- `src/__init__.py`
- `src/sampler/traffic_sampler.py`
- `src/replay/replay_runner.py` + offline adapter
- `src/score/eval_runner.py`
- `src/score/llm_judge.py` + offline judge
- `src/decide/verdict.py`
- `src/render/decision_record.py`
- `schemas/route.schema.json`
- `schemas/decision-record.schema.json`
- `tests/fixtures/routes.yaml`
- `tests/fixtures/trace_store/customer-support/2026-W24.jsonl`
- `tests/fixtures/recorded_responses/fixture-candidate-v1/*.json`
- `tests/fixtures/expected/fixture-candidate-v1-customer-support.md`
- `tests/test_sampler.py`
- `tests/test_replay.py`
- `tests/test_verdict.py`
- `tests/test_render.py`
- `tests/test_end_to_end.py`
- `tests/test_determinism.py`
- `scripts/voice_lint.py`
- `scripts/spec_check.py`
- `scripts/validate_schemas.py`
- `scripts/revert_threshold_present.py`
- `decisions/model-swap/.gitkeep`

Modified:

- `README.md` — replace placeholder "How to run" with the real command
- `specs/0001-foundation/tasks.md` — check off the spec-0002 rows
- `AGENTS.md` — point Gates section at real scripts

## Verification

```bash
uv sync
uv run pytest -v
uv run modelswap replay \
    --route customer-support \
    --release fixture-candidate-v1 \
    --since 7d \
    --offline \
    --out decisions/model-swap/fixture-candidate-v1-customer-support.md
diff decisions/model-swap/fixture-candidate-v1-customer-support.md \
     tests/fixtures/expected/fixture-candidate-v1-customer-support.md
uv run python scripts/voice_lint.py
uv run python scripts/spec_check.py
uv run python scripts/validate_schemas.py decisions/model-swap/
uv run python scripts/revert_threshold_present.py decisions/model-swap/
```

## Out of scope for this PR

- The real (non-offline) model adapter
- The eval-predictive-validity bolt-on report (spec 0003)
- Multiple-route batch invocation (spec 0003)
- The first real decision record on a real frontier release
