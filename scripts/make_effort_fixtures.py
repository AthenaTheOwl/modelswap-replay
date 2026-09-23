#!/usr/bin/env python3
"""Build the effort-setting fixtures for `modelswap curve` from the committed candidate.

fixture-candidate-v1 is treated as the medium setting. Low and high are synthetic
variants of the same six customer-support responses: low trades quality for
cost and latency, high buys a little quality at a large cost and latency premium.
The numbers are illustrative fixture data, not measurements.

    python scripts/make_effort_fixtures.py
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORDED = ROOT / "tests" / "fixtures" / "recorded_responses"
BASE = "fixture-candidate-v1"
TRACES = [f"trace-cs-{i:03d}" for i in range(1, 7)]

SETTINGS = {
    # effort: (quality shift, cost multiplier, latency multiplier, traces the judge gives to the incumbent)
    "low": (-0.09, 0.50, 0.55, {"trace-cs-001", "trace-cs-003", "trace-cs-004", "trace-cs-006"}),
    "medium": (0.0, 1.0, 1.0, set()),
    "high": (0.03, 2.40, 2.20, set()),
}


def clamp(x: float) -> float:
    return round(min(1.0, max(0.0, x)), 3)


def main() -> int:
    for effort, (dq, cost_x, latency_x, incumbent_wins) in SETTINGS.items():
        out_dir = RECORDED / f"{BASE}-effort-{effort}"
        out_dir.mkdir(parents=True, exist_ok=True)
        for trace in TRACES:
            base = json.loads((RECORDED / BASE / f"{trace}.json").read_text(encoding="utf-8"))
            rec = dict(base)
            rec["quality_score"] = clamp(base["quality_score"] + dq)
            rec["scores"] = {k: clamp(v + dq) for k, v in base["scores"].items()}
            rec["cost_usd"] = round(base["cost_usd"] * cost_x, 6)
            rec["latency_ms"] = int(round(base["latency_ms"] * latency_x))
            if trace in incumbent_wins:
                rec["judge_preference"] = "incumbent"
                rec["judge_reason"] = f"{effort}-effort answer skipped a policy step"
            (out_dir / f"{trace}.json").write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(SETTINGS)} effort settings x {len(TRACES)} traces under {RECORDED.relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
