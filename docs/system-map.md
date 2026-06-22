# System Map

## Flow

```text
config/routes.yaml
  -> sampler
  -> offline replay adapter
  -> eval runner
  -> offline judge
  -> verdict author
  -> decision record renderer
  -> decisions/model-swap/<release>-<route>.md
```

## Ownership

- `config/routes.yaml` names routes, sampling settings, rubrics, and
  revert thresholds.
- `src/sampler/traffic_sampler.py` reads immutable JSONL trace files.
- `src/replay/replay_runner.py` is the model-adapter boundary.
- `src/score/eval_runner.py` computes score, cost, and latency deltas.
- `src/score/llm_judge.py` reads fixture judge choices in v0.1.
- `src/decide/verdict.py` selects `swap`, `route-split-at-25%`,
  `hold`, or `defer`.
- `src/render/decision_record.py` writes the Markdown artifact.

## Gates

- `scripts/voice_lint.py` scans emitted records for banned wording.
- `scripts/spec_check.py` confirms each `R-MSR-*` id has an owned
  implementation, test, or deferred queue entry.
- `scripts/validate_schemas.py` validates decision-record front matter.
- `scripts/revert_threshold_present.py` fails records without
  `revert_threshold:`.

