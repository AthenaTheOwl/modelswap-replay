from tests.support import build_fixture_run


def test_verdict_is_swap_for_fixture_candidate():
    _route, _samples, _responses, _judge, summary, verdict = build_fixture_run()

    assert summary.quality_delta == 0.053
    assert summary.cost_delta_ratio == -0.105
    assert summary.latency_p95_delta_ms == 30
    assert verdict.verdict == "swap"

