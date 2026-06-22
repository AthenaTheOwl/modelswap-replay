from __future__ import annotations

from math import ceil

from pydantic import BaseModel

from src.replay.replay_runner import ReplayResponse
from src.sampler.traffic_sampler import SampledRequest
from src.score.llm_judge import JudgeSummary


class TraceScore(BaseModel):
    trace_id: str
    intent: str
    quality_delta: float
    cost_delta_usd: float
    latency_delta_ms: int
    candidate_quality: float
    incumbent_quality: float


class ScoreSummary(BaseModel):
    sample_count: int
    quality_delta: float
    cost_delta_usd: float
    cost_delta_ratio: float
    latency_p95_delta_ms: int
    dimension_deltas: dict[str, float]
    trace_scores: list[TraceScore]
    judge_candidate_win_rate: float


class EvalRunner:
    def evaluate(
        self,
        samples: list[SampledRequest],
        responses: list[ReplayResponse],
        judge: JudgeSummary,
    ) -> ScoreSummary:
        by_trace = {response.trace_id: response for response in responses}
        trace_scores: list[TraceScore] = []
        for sample in samples:
            response = by_trace[sample.trace_id]
            trace_scores.append(
                TraceScore(
                    trace_id=sample.trace_id,
                    intent=sample.intent,
                    quality_delta=round(response.quality_score - sample.incumbent_quality, 3),
                    cost_delta_usd=round(response.cost_usd - sample.incumbent_cost_usd, 4),
                    latency_delta_ms=response.latency_ms - sample.incumbent_latency_ms,
                    candidate_quality=response.quality_score,
                    incumbent_quality=sample.incumbent_quality,
                )
            )

        incumbent_quality = average([sample.incumbent_quality for sample in samples])
        candidate_quality = average([by_trace[sample.trace_id].quality_score for sample in samples])
        incumbent_cost = average([sample.incumbent_cost_usd for sample in samples])
        candidate_cost = average([by_trace[sample.trace_id].cost_usd for sample in samples])
        cost_delta_usd = candidate_cost - incumbent_cost
        cost_delta_ratio = 0.0 if incumbent_cost == 0 else cost_delta_usd / incumbent_cost
        latency_deltas = [score.latency_delta_ms for score in trace_scores]

        return ScoreSummary(
            sample_count=len(samples),
            quality_delta=round(candidate_quality - incumbent_quality, 3),
            cost_delta_usd=round(cost_delta_usd, 4),
            cost_delta_ratio=round(cost_delta_ratio, 3),
            latency_p95_delta_ms=percentile95(latency_deltas),
            dimension_deltas=dimension_deltas(samples, responses),
            trace_scores=trace_scores,
            judge_candidate_win_rate=judge.candidate_win_rate,
        )


def average(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def percentile95(values: list[int]) -> int:
    if not values:
        return 0
    ordered = sorted(values)
    index = max(ceil(0.95 * len(ordered)) - 1, 0)
    return ordered[index]


def dimension_deltas(samples: list[SampledRequest], responses: list[ReplayResponse]) -> dict[str, float]:
    by_trace = {response.trace_id: response for response in responses}
    names = sorted(
        {
            name
            for sample in samples
            for name in sample.incumbent_scores
        }
        | {
            name
            for response in responses
            for name in response.scores
        }
    )
    deltas: dict[str, float] = {}
    for name in names:
        incumbent = average([sample.incumbent_scores.get(name, 0.0) for sample in samples])
        candidate = average([by_trace[sample.trace_id].scores.get(name, 0.0) for sample in samples])
        deltas[name] = round(candidate - incumbent, 3)
    return deltas

