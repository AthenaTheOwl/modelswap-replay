# Spec 0001 — Tasks (ModelSwap Replay)

First PR (the scaffold — this commit):

- [x] R-MSR-001 scaffold: README + LICENSE + AGENTS.md + .gitignore
- [x] R-MSR-001 specs/0001-foundation/{requirements,design,tasks,acceptance}.md
- [x] R-MSR-001 docs/first-pr.md

Second PR (foundation runnable code):

- [ ] R-MSR-002 `config/routes.yaml` + `schemas/route.schema.json`
- [ ] R-MSR-002 typed Pydantic models that load the route registry
- [ ] R-MSR-003 `src/sampler/traffic_sampler.py` against fixture trace
      store, seeded deterministic
- [ ] R-MSR-004 `src/replay/replay_runner.py` with one model adapter +
      one fixture-backed adapter for offline tests
- [ ] R-MSR-005 `src/score/eval_runner.py` wrapper + one example suite
- [ ] R-MSR-005 `src/score/llm_judge.py` with offline judge for tests
- [ ] R-MSR-006 `src/decide/verdict.py` deterministic verdict logic
- [ ] R-MSR-007 `src/render/decision_record.py` writer
- [ ] R-MSR-007 `schemas/decision-record.schema.json`
- [ ] R-MSR-008 enforce `revert_threshold:` block presence at render
- [ ] R-MSR-010 fixtures: routes, trace store, recorded responses
- [ ] R-MSR-009 `scripts/voice_lint.py`, `scripts/spec_check.py`,
      `scripts/validate_schemas.py`,
      `scripts/revert_threshold_present.py`
- [ ] CLI: `cli/main.py` with `replay` subcommand

Third PR (first real verdict):

- [ ] First decision record committed for one named route on the next
      frontier release
- [ ] Release notes referencing the record
