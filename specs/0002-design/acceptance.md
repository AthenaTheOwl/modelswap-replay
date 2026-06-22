# Spec 0002 - Acceptance

v0.1 is accepted when these commands pass:

```bash
python -m pytest -v
python -m cli.main replay \
  --route customer-support \
  --release fixture-candidate-v1 \
  --since 7d \
  --offline \
  --out decisions/model-swap/fixture-candidate-v1-customer-support.md
python scripts/voice_lint.py
python scripts/spec_check.py
python scripts/validate_schemas.py decisions/model-swap/
python scripts/revert_threshold_present.py decisions/model-swap/
```

The package is also configured for uv:

```bash
python -m uv sync
python -m uv run pytest -v
```

