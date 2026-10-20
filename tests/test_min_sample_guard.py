"""A verdict needs a minimum sample; the record reports n and a binomial interval."""

import pytest

from src.decide.verdict import choose_verdict
from src.models.route_registry import MIN_SAMPLE_FLOOR, RevertThreshold, SampleConfig
from src.score.eval_runner import ScoreSummary
from src.score.llm_judge import wilson_interval

THRESHOLD = RevertThreshold(
    quality_drop_max=0.03,
    cost_increase_max=0.20,
    latency_p95_regression_ms_max=250,
)


def _summary(sample_count: int, win_rate: float = 1.0, quality: float = 0.05) -> ScoreSummary:
    return ScoreSummary(
        sample_count=sample_count,
        quality_delta=quality,
        cost_delta_usd=0.0,
        cost_delta_ratio=0.0,
        latency_p95_delta_ms=0,
        dimension_deltas={},
        trace_scores=[],
        judge_candidate_win_rate=win_rate,
    )


def test_one_winning_request_no_longer_swaps():
    result = choose_verdict(_summary(1), THRESHOLD)
    assert result.verdict == "defer"
    assert result.rationale == [
        f"insufficient sample: 1 requests, below the minimum of {MIN_SAMPLE_FLOOR}"
    ]


def test_split_pair_with_quality_drop_no_longer_swaps():
    assert choose_verdict(_summary(2, win_rate=0.5, quality=-0.02), THRESHOLD).verdict == "defer"


def test_guard_boundary_is_the_configured_minimum():
    assert choose_verdict(_summary(69), THRESHOLD, min_sample_count=70).verdict == "defer"
    assert choose_verdict(_summary(70), THRESHOLD, min_sample_count=70).verdict == "swap"


def test_default_minimum_is_the_route_sample_design():
    assert SampleConfig(window_days=7, per_day_n=10).required_sample_count() == 70
    assert SampleConfig().required_sample_count() == 7 * 200


def test_default_minimum_never_drops_below_the_floor():
    assert SampleConfig(window_days=2, per_day_n=3).required_sample_count() == MIN_SAMPLE_FLOOR


def test_explicit_minimum_overrides_the_design():
    assert SampleConfig(window_days=7, per_day_n=10, min_sample_count=12).required_sample_count() == 12


@pytest.mark.parametrize(
    ("wins", "n", "expected"),
    [
        (5, 6, (0.436, 0.97)),
        (4, 4, (0.51, 1.0)),
        (21, 30, (0.521, 0.833)),
        (14, 20, (0.481, 0.855)),
        (0, 0, (0.0, 1.0)),
    ],
)
def test_wilson_interval(wins, n, expected):
    assert wilson_interval(wins, n) == expected
