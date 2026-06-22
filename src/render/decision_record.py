from __future__ import annotations

from datetime import timedelta
from typing import Any

import yaml

from src.decide.verdict import VerdictResult
from src.models.route_registry import RouteConfig
from src.replay.replay_runner import ReplayResponse
from src.sampler.traffic_sampler import SampledRequest
from src.score.eval_runner import ScoreSummary, TraceScore
from src.score.llm_judge import JudgeSummary


class IndentDumper(yaml.SafeDumper):
    def increase_indent(self, flow: bool = False, indentless: bool = False) -> Any:
        return super().increase_indent(flow, False)


def render_decision_record(
    release_id: str,
    route: RouteConfig,
    samples: list[SampledRequest],
    responses: list[ReplayResponse],
    summary: ScoreSummary,
    judge: JudgeSummary,
    verdict: VerdictResult,
) -> str:
    if not samples:
        raise ValueError("cannot render decision record without samples")

    start = min(sample.timestamp.date() for sample in samples)
    end = max(sample.timestamp.date() for sample in samples)
    review_date = end + timedelta(days=14)
    best = sorted(summary.trace_scores, key=lambda score: (-score.quality_delta, score.trace_id))[:3]
    worst = sorted(summary.trace_scores, key=lambda score: (score.quality_delta, score.trace_id))[:3]
    front_matter = {
        "release_id": release_id,
        "route": route.name,
        "verdict": verdict.verdict,
        "incumbent": route.incumbent,
        "candidate": release_id,
        "sample_window": {
            "start": start.isoformat(),
            "end": end.isoformat(),
            "request_count": summary.sample_count,
        },
        "deltas": {
            "quality": summary.quality_delta,
            "cost_per_request_usd": summary.cost_delta_usd,
            "cost_ratio": summary.cost_delta_ratio,
            "latency_p95_ms": summary.latency_p95_delta_ms,
        },
        "dimensions": summary.dimension_deltas,
        "judge": {
            "candidate_win_rate": judge.candidate_win_rate,
            "candidate_wins": judge.candidate_wins,
            "incumbent_wins": judge.incumbent_wins,
            "ties": judge.ties,
        },
        "best_traces": [trace_summary(score) for score in best],
        "worst_traces": [trace_summary(score) for score in worst],
        "revert_threshold": route.revert_threshold.model_dump(),
        "revert_review_date": review_date.isoformat(),
        "rationale": verdict.rationale,
    }

    yaml_text = yaml.dump(front_matter, Dumper=IndentDumper, sort_keys=False, allow_unicode=False, width=120)
    lines = [
        "---",
        yaml_text.rstrip(),
        "---",
        f"# Model Swap - {release_id} -> {route.name}",
        "",
        "## Verdict",
        f"- verdict: {verdict.verdict}",
        f"- incumbent: {route.incumbent}",
        f"- candidate: {release_id}",
        f"- sample_window: {start.isoformat()}..{end.isoformat()} ({summary.sample_count} requests)",
        "",
        "## Deltas",
        f"- quality_delta: {summary.quality_delta:+.3f}",
        f"- cost_delta_per_request_usd: {summary.cost_delta_usd:+.4f}",
        f"- cost_delta_ratio: {summary.cost_delta_ratio:+.3f}",
        f"- latency_p95_delta_ms: {summary.latency_p95_delta_ms:+d}",
        f"- judge_candidate_win_rate: {judge.candidate_win_rate:.3f}",
        "",
        "## Dimensions",
        *[f"- {name}: {delta:+.3f}" for name, delta in summary.dimension_deltas.items()],
        "",
        "## Best traces",
        *[trace_line(score) for score in best],
        "",
        "## Worst traces",
        *[trace_line(score) for score in worst],
        "",
        "## Revert threshold",
        "revert_threshold:",
        f"  quality_drop_max: {route.revert_threshold.quality_drop_max}",
        f"  cost_increase_max: {route.revert_threshold.cost_increase_max}",
        f"  latency_p95_regression_ms_max: {route.revert_threshold.latency_p95_regression_ms_max}",
        f"- revert_review_date: {review_date.isoformat()}",
        "",
        "## Rationale",
        *[f"- {item}" for item in verdict.rationale],
        "",
    ]
    return "\n".join(lines)


def trace_summary(score: TraceScore) -> dict[str, float | int | str]:
    return {
        "trace_id": score.trace_id,
        "quality_delta": score.quality_delta,
        "cost_delta_usd": score.cost_delta_usd,
        "latency_delta_ms": score.latency_delta_ms,
    }


def trace_line(score: TraceScore) -> str:
    return (
        f"- {score.trace_id}: quality_delta={score.quality_delta:+.3f}, "
        f"cost_delta_usd={score.cost_delta_usd:+.4f}, "
        f"latency_delta_ms={score.latency_delta_ms:+d}"
    )

