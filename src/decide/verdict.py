from __future__ import annotations

from pydantic import BaseModel

from src.models.route_registry import MIN_SAMPLE_FLOOR, RevertThreshold
from src.score.eval_runner import ScoreSummary


class VerdictResult(BaseModel):
    verdict: str
    rationale: list[str]


def choose_verdict(
    summary: ScoreSummary,
    threshold: RevertThreshold,
    min_sample_count: int = MIN_SAMPLE_FLOOR,
) -> VerdictResult:
    """Pick swap / route-split / hold / defer for one scored replay.

    Below `min_sample_count` sampled requests the verdict is defer: no
    quality, judge, cost or latency comparison is trusted on that few
    requests. Callers with a route pass `route.sample.required_sample_count()`;
    the default is the documented floor (MIN_SAMPLE_FLOOR).
    """

    if summary.sample_count == 0:
        return VerdictResult(verdict="defer", rationale=["no sampled requests were available"])

    if summary.sample_count < min_sample_count:
        return VerdictResult(
            verdict="defer",
            rationale=[
                f"insufficient sample: {summary.sample_count} requests, "
                f"below the minimum of {min_sample_count}"
            ],
        )

    if summary.quality_delta < -threshold.quality_drop_max:
        return VerdictResult(
            verdict="hold",
            rationale=[f"quality_delta {summary.quality_delta} is below -{threshold.quality_drop_max}"],
        )

    if summary.judge_candidate_win_rate < 0.5:
        return VerdictResult(
            verdict="hold",
            rationale=[f"judge candidate win rate {summary.judge_candidate_win_rate} is below 0.5"],
        )

    cost_over = summary.cost_delta_ratio > threshold.cost_increase_max
    latency_over = summary.latency_p95_delta_ms > threshold.latency_p95_regression_ms_max
    if cost_over or latency_over:
        return VerdictResult(
            verdict="route-split-at-25%",
            rationale=["candidate passed quality checks but exceeded a cost or latency threshold"],
        )

    return VerdictResult(
        verdict="swap",
        rationale=["candidate passed quality, cost, latency, and judge thresholds"],
    )

