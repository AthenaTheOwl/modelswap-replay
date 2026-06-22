from __future__ import annotations

from pydantic import BaseModel

from src.models.route_registry import RevertThreshold
from src.score.eval_runner import ScoreSummary


class VerdictResult(BaseModel):
    verdict: str
    rationale: list[str]


def choose_verdict(summary: ScoreSummary, threshold: RevertThreshold) -> VerdictResult:
    if summary.sample_count == 0:
        return VerdictResult(verdict="defer", rationale=["no sampled requests were available"])

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

