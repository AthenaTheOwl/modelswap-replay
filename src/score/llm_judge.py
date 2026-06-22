from __future__ import annotations

from pydantic import BaseModel

from src.replay.replay_runner import ReplayResponse
from src.sampler.traffic_sampler import SampledRequest


class JudgeSummary(BaseModel):
    candidate_win_rate: float
    candidate_wins: int
    incumbent_wins: int
    ties: int
    reasons: list[str]


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
        )

