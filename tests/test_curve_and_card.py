import json
from pathlib import Path

import yaml

from click.testing import CliRunner

from cli.main import main
from modelswap_replay.cli import DEFAULT_DECISION, build_card

REPO = Path(__file__).resolve().parents[1]


def _routes_with_min_sample(tmp_path, minimum):
    # The six-request fixture is below the committed routes' 70-request
    # minimum, so the curve mechanism is exercised with an explicit override.
    routes = yaml.safe_load((REPO / "config" / "routes.yaml").read_text(encoding="utf-8"))
    for route in routes["routes"]:
        route["trace_store"] = str(REPO / route["trace_store"])
        route["sample"]["min_sample_count"] = minimum
    path = tmp_path / "routes.yaml"
    path.write_text(yaml.safe_dump(routes), encoding="utf-8")
    return path


def test_curve_defers_every_setting_on_the_committed_routes():
    result = CliRunner().invoke(main, ["curve", "--route", "customer-support", "--release", "fixture-candidate-v1", "--json"])
    assert result.exit_code == 1, result.output
    data = json.loads(result.output)
    assert [(r["effort"], r["verdict"], r["request_count"]) for r in data["curve"]] == [
        ("low", "defer", 6),
        ("medium", "defer", 6),
        ("high", "defer", 6),
    ]
    assert data["cheapest_clearing"] is None


def test_curve_picks_cheapest_setting_that_clears_thresholds(tmp_path):
    routes = _routes_with_min_sample(tmp_path, 6)
    result = CliRunner().invoke(main, ["curve", "--route", "customer-support", "--release", "fixture-candidate-v1",
                                       "--routes", str(routes), "--json"])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert [(r["effort"], r["verdict"]) for r in data["curve"]] == [
        ("low", "hold"),
        ("medium", "swap"),
        ("high", "route-split-at-25%"),
    ]
    assert data["cheapest_clearing"] == "medium"


def test_curve_exits_1_when_no_setting_clears():
    result = CliRunner().invoke(main, ["curve", "--route", "customer-support", "--release", "fixture-candidate-v1",
                                       "--efforts", "low,high"])
    assert result.exit_code == 1
    assert "none" in result.output


def test_curve_unknown_setting_errors_cleanly():
    result = CliRunner().invoke(main, ["curve", "--route", "customer-support", "--release", "fixture-candidate-v1",
                                       "--efforts", "turbo"])
    assert result.exit_code != 0
    assert "no recorded responses" in result.output


def test_card_is_stable_and_tracks_its_input(tmp_path):
    first, second = build_card(Path(DEFAULT_DECISION)), build_card(Path(DEFAULT_DECISION))
    assert first == second
    assert first["verdict"] == "defer" and first["route"] == "customer-support"
    assert first["sample_window"]["min_request_count"] == 70
    assert first["judge"]["judged_count"] == 6

    edited = tmp_path / Path(DEFAULT_DECISION).name
    edited.write_bytes(Path(DEFAULT_DECISION).read_bytes() + b" ")
    changed = build_card(edited)
    assert changed["inputs"]["decision_record"]["sha256"] != first["inputs"]["decision_record"]["sha256"]
    assert changed["card_sha256"] != first["card_sha256"]


def test_card_verify_catches_tampering(tmp_path):
    out = tmp_path / "card.json"
    runner = CliRunner()
    assert runner.invoke(main, ["card", "--out", str(out)]).exit_code == 0
    assert runner.invoke(main, ["card", "--verify", str(out)]).exit_code == 0
    card = json.loads(out.read_text(encoding="utf-8"))
    card["verdict"] = "hold"
    out.write_text(json.dumps(card), encoding="utf-8")
    result = runner.invoke(main, ["card", "--verify", str(out)])
    assert result.exit_code == 1
    assert "digest mismatch" in result.output


def test_committed_card_matches_the_committed_record():
    committed = json.loads((REPO / "reports" / "cards" / "fixture-candidate-v1-customer-support.json").read_text(encoding="utf-8"))
    assert committed == json.loads(json.dumps(build_card(Path(DEFAULT_DECISION)), default=str))
