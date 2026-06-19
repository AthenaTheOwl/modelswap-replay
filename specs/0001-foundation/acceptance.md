# Spec 0001 — Acceptance (ModelSwap Replay)

v0 (this scaffold PR) is done when:

- `README.md`, `LICENSE`, `AGENTS.md`, `.gitignore` exist
- `specs/0001-foundation/{requirements,design,tasks,acceptance}.md` exist
- `docs/first-pr.md` describes the second PR
- README status checkboxes show the scaffold rows checked
- No code beyond what spec 0001 names lives in this repo

Spec 0002 (the next PR) is done when:

```bash
uv sync
uv run pytest                                          # all green
uv run modelswap replay \
    --route customer-support \
    --release fixture-candidate-v1 \
    --since 7d \
    --out decisions/model-swap/fixture-candidate-v1-customer-support.md \
    --offline
uv run python scripts/voice_lint.py
uv run python scripts/spec_check.py
uv run python scripts/validate_schemas.py decisions/model-swap/
uv run python scripts/revert_threshold_present.py decisions/model-swap/
```

And:

- The emitted record contains a verdict, deltas, best/worst traces, a
  `revert_threshold:` block, and validates against
  `schemas/decision-record.schema.json`
- Running the same command twice with the same seed produces
  byte-identical output
- All tests run offline with no network and no model key

Gates: `voice_lint`, `spec_check`, `validate_schemas`,
`revert_threshold_present`. A PR that fails any gate is not merged.
