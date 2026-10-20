from __future__ import annotations

from math import sqrt

from pydantic import BaseModel

from src.replay.replay_runner import ReplayResponse
from src.sampler.traffic_sampler import SampledRequest


Z_95 = 1.959964


def wilson_interval(successes: int, n: int, z: float = Z_95) -> tuple[float, float]:
    """Two-sided Wilson score interval for a binomial proportion."""

    if n <= 0:
        return (0.0, 1.0)
    p = successes / n
    denominator = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denominator
    half = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denominator
    return (round(max(0.0, center - half), 3), round(min(1.0, center + half), 3))


class JudgeSummary(BaseModel):
    candidate_win_rate: float
    candidate_wins: int
    incumbent_wins: int
    ties: int
    reasons: list[str]
    judged_count: int = 0
    win_rate_ci95: tuple[float, float] = (0.0, 1.0)


class OfflineJudge:
    def score(self, samples: list[SampledRequest], responses: list[ReplayResponse]) -> JudgeSummary:
        by_trace = {response.trace_id: response for response in responses}
        candidate_wins = 0
        incumbent_wins = 0
        ties = 0
        reasons: list[str] = []
        for sample in samples:
            response = by_trace[sample.trace_id]
            if response.judge_preference == "candidate":
                candidate_wins += 1
            elif response.judge_preference == "incumbent":
                incumbent_wins += 1
            else:
                ties += 1
            reasons.append(f"{sample.trace_id}: {response.judge_reason}")

        total = max(len(samples), 1)
        return JudgeSummary(
            candidate_win_rate=round(candidate_wins / total, 3),
            candidate_wins=candidate_wins,
            incumbent_wins=incumbent_wins,
            ties=ties,
            reasons=reasons,
            judged_count=len(samples),
            win_rate_ci95=wilson_interval(candidate_wins, len(samples)),
        )

