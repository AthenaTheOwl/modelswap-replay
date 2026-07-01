from src.decide.verdict import choose_verdict
from src.models.route_registry import RevertThreshold
from src.score.eval_runner import ScoreSummary
from tests.support import build_fixture_run


def _summary(**overrides) -> ScoreSummary:
    # A passing baseline; each test overrides one field to steer a branch.
    base = dict(
        sample_count=4,
        quality_delta=0.05,
        cost_delta_usd=-0.001,
        cost_delta_ratio=-0.1,
        latency_p95_delta_ms=30,
        dimension_deltas={},
        trace_scores=[],
        judge_candidate_win_rate=0.75,
    )
    base.update(overrides)
    return ScoreSummary(**base)


THRESHOLD = RevertThreshold(
    quality_drop_max=0.03,
    cost_increase_max=0.20,
    latency_p95_regression_ms_max=250,
)


def test_verdict_is_swap_for_fixture_candidate():
    _route, _samples, _responses, _judge, summary, verdict = build_fixture_run()

    assert summary.quality_delta == 0.053
    assert summary.cost_delta_ratio == -0.105
    assert summary.latency_p95_delta_ms == 30
    assert verdict.verdict == "swap"


def test_verdict_defers_when_no_samples():
    result = choose_verdict(_summary(sample_count=0), THRESHOLD)

    assert result.verdict == "defer"
    assert result.rationale == ["no sampled requests were available"]


def test_verdict_holds_on_quality_drop():
    result = choose_verdict(_summary(quality_delta=-0.05), THRESHOLD)

    assert result.verdict == "hold"
    assert result.rationale == ["quality_delta -0.05 is below -0.03"]


def test_verdict_holds_on_low_judge_win_rate():
    result = choose_verdict(_summary(judge_candidate_win_rate=0.4), THRESHOLD)

    assert result.verdict == "hold"
    assert result.rationale == ["judge candidate win rate 0.4 is below 0.5"]


def test_verdict_route_splits_on_cost_over():
    result = choose_verdict(_summary(cost_delta_ratio=0.5), THRESHOLD)

    assert result.verdict == "route-split-at-25%"
    assert result.rationale == [
        "candidate passed quality checks but exceeded a cost or latency threshold"
    ]


def test_verdict_route_splits_on_latency_over():
    result = choose_verdict(_summary(latency_p95_delta_ms=500), THRESHOLD)

    assert result.verdict == "route-split-at-25%"
    assert result.rationale == [
        "candidate passed quality checks but exceeded a cost or latency threshold"
    ]
