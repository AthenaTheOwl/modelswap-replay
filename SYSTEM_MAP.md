# System Map

## Flow

```text
config/routes.yaml
  -> modelswap_replay.cli
  -> sampler
  -> offline replay adapter
  -> eval runner
  -> offline judge
  -> verdict author
  -> decision record renderer
  -> decisions/model-swap/<release>-<route>.md
  -> reports/<release>-<route>.jsonl
```

## Package surface

- `modelswap_replay/cli.py` owns the `modelswap replay` command.
- `modelswap_replay/model.py` exposes route, sample, and replay models.
- `modelswap_replay/scoring.py` exposes eval, judge, and verdict types.

## Data ownership

- `config/routes.yaml` names routes, sampling settings, rubrics, and
  revert thresholds.
- Trace fixtures under `tests/fixtures/trace_store/` are immutable
  sampled request inputs for v0.1.
- Recorded responses under `tests/fixtures/recorded_responses/` are the
  offline candidate outputs for v0.1.
- Decision records under `decisions/model-swap/` are the human review
  artifacts.
- JSONL files under `reports/` are machine-readable run summaries.

## Gates

- `scripts/voice_lint.py` scans emitted records for banned wording.
- `scripts/spec_check.py` confirms each `R-MSR-*` id has an owned
  implementation, test, or deferred queue entry.
- `scripts/validate_schemas.py` validates decision-record front matter.
- `scripts/revert_threshold_present.py` fails records without
  `revert_threshold:`.
