from __future__ import annotations

import re
from pathlib import Path


COVERAGE = {
    "R-MSR-001": [
        "README.md",
        "AGENTS.md",
        "specs/0001-foundation/requirements.md",
    ],
    "R-MSR-002": [
        "config/routes.yaml",
        "schemas/route.schema.json",
        "modelswap_replay/model.py",
        "src/models/route_registry.py",
        "tests/test_sampler.py",
    ],
    "R-MSR-003": [
        "modelswap_replay/model.py",
        "src/sampler/traffic_sampler.py",
        "tests/test_sampler.py",
    ],
    "R-MSR-004": [
        "modelswap_replay/model.py",
        "src/replay/replay_runner.py",
        "tests/test_replay.py",
    ],
    "R-MSR-005": [
        "modelswap_replay/scoring.py",
        "src/score/eval_runner.py",
        "src/score/llm_judge.py",
        "tests/test_replay.py",
    ],
    "R-MSR-006": [
        "modelswap_replay/scoring.py",
        "src/decide/verdict.py",
        "tests/test_verdict.py",
    ],
    "R-MSR-007": [
        "modelswap_replay/rendering.py",
        "src/render/decision_record.py",
        "schemas/decision-record.schema.json",
        "tests/test_render.py",
    ],
    "R-MSR-008": [
        "scripts/revert_threshold_present.py",
        "tests/test_render.py",
    ],
    "R-MSR-009": [
        "scripts/voice_lint.py",
        "scripts/spec_check.py",
        "scripts/validate_schemas.py",
        "scripts/revert_threshold_present.py",
    ],
    "R-MSR-010": [
        "modelswap_replay/cli.py",
        "tests/fixtures/routes.yaml",
        "tests/fixtures/trace_store/customer-support/2026-W24.jsonl",
        "tests/fixtures/recorded_responses/fixture-candidate-v1/trace-cs-001.json",
        "tests/test_end_to_end.py",
    ],
    "R-MSR-011": [
        "STATUS.md",
        "specs/0002-design/tasks.md",
    ],
}


def main() -> int:
    ids = sorted(set(re.findall(r"R-MSR-\d{3}", spec_text())))
    missing: list[str] = []
    for requirement_id in ids:
        paths = COVERAGE.get(requirement_id)
        if not paths:
            missing.append(f"{requirement_id}: no coverage mapping")
            continue
        for path in paths:
            if not Path(path).exists():
                missing.append(f"{requirement_id}: missing {path}")

    if missing:
        print("\n".join(missing))
        return 1
    print(f"spec_check: ok ({len(ids)} requirements)")
    return 0


def spec_text() -> str:
    return "\n".join(path.read_text(encoding="utf-8") for path in sorted(Path("specs").glob("**/*.md")))


if __name__ == "__main__":
    raise SystemExit(main())
