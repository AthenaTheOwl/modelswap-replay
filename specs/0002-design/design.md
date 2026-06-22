# Spec 0002 - Design

## CLI

```text
modelswap replay --route customer-support --release fixture-candidate-v1 --since 7d --offline --out decisions/model-swap/fixture-candidate-v1-customer-support.md
```

The command performs one route/release replay pass and writes one
decision record.

## Data contracts

- Route registry: YAML validated by Pydantic models and
  `schemas/route.schema.json`.
- Trace store: JSONL records with incumbent response, quality, cost,
  latency, and dimension scores.
- Recorded responses: one JSON file per trace id under
  `tests/fixtures/recorded_responses/<release>/`.
- Decision record: Markdown body plus YAML front matter validated by
  `schemas/decision-record.schema.json`.

## Determinism

- The sampler uses stable hashing from route seed and trace id.
- The offline adapter reads fixed response files.
- The judge reads fixed fixture preferences.
- The renderer computes review date from the sampled trace window, not
  wall-clock time.

