import yaml

from src.render.decision_record import render_decision_record
from tests.support import build_fixture_run


def test_render_includes_schema_fields_and_revert_threshold():
    route, samples, responses, judge, summary, verdict = build_fixture_run()

    record = render_decision_record(
        release_id="fixture-candidate-v1",
        route=route,
        samples=samples,
        responses=responses,
        summary=summary,
        judge=judge,
        verdict=verdict,
    )
    front_matter = yaml.safe_load(record.split("\n---\n", 1)[0].removeprefix("---\n"))

    assert front_matter["verdict"] == "defer"
    assert front_matter["sample_window"]["request_count"] == 6
    assert front_matter["sample_window"]["min_request_count"] == 70
    assert front_matter["judge"]["judged_count"] == 6
    assert front_matter["judge"]["win_rate_ci95_low"] == 0.436
    assert front_matter["judge"]["win_rate_ci95_high"] == 0.97
    assert "judge_candidate_win_rate: 0.833 (5/6, 95% Wilson interval 0.436-0.970)" in record
    assert front_matter["revert_threshold"]["quality_drop_max"] == 0.03
    assert "revert_threshold:" in record
    assert "trace-cs-003" in record

