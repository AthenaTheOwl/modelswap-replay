from src.render.decision_record import render_decision_record
from tests.support import build_fixture_run


def test_render_is_byte_deterministic():
    route, samples, responses, judge, summary, verdict = build_fixture_run()

    first = render_decision_record("fixture-candidate-v1", route, samples, responses, summary, judge, verdict)
    second = render_decision_record("fixture-candidate-v1", route, samples, responses, summary, judge, verdict)

    assert first == second

