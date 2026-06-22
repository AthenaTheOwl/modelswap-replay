from src.replay.replay_runner import OfflineAdapter, ReplayRunner
from tests.support import RECORDED_ROOT, build_fixture_run


def test_offline_replay_loads_recorded_candidate_responses():
    route, samples, _responses, _judge, _summary, _verdict = build_fixture_run()

    responses = ReplayRunner(OfflineAdapter(RECORDED_ROOT)).run(samples, "fixture-candidate-v1")

    assert route.name == "customer-support"
    assert len(responses) == 6
    assert responses[0].trace_id == "trace-cs-001"
    assert responses[0].quality_score == 0.88

