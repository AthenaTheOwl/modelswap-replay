from click.testing import CliRunner

from cli.main import main


COMMON = [
    "--routes",
    "tests/fixtures/routes.yaml",
    "--recorded-root",
    "tests/fixtures/recorded_responses",
]


def test_replay_unknown_route_errors_cleanly(tmp_path):
    out = tmp_path / "o.md"
    result = CliRunner().invoke(
        main,
        ["replay", "--route", "nope", "--release", "r1", "--out", str(out), *COMMON],
    )

    assert result.exit_code != 0
    assert "unknown route 'nope'" in result.output
    assert "known routes: customer-support" in result.output


def test_replay_bad_since_errors_cleanly(tmp_path):
    out = tmp_path / "o.md"
    result = CliRunner().invoke(
        main,
        [
            "replay",
            "--route",
            "customer-support",
            "--release",
            "fixture-candidate-v1",
            "--since",
            "garbage",
            "--out",
            str(out),
            *COMMON,
        ],
    )

    assert result.exit_code != 0
    assert "bad --since" in result.output


def test_replay_missing_routes_errors_cleanly(tmp_path):
    out = tmp_path / "o.md"
    result = CliRunner().invoke(
        main,
        [
            "replay",
            "--route",
            "customer-support",
            "--release",
            "r1",
            "--out",
            str(out),
            "--routes",
            "tests/fixtures/does-not-exist.yaml",
            "--recorded-root",
            "tests/fixtures/recorded_responses",
        ],
    )

    assert result.exit_code != 0
    assert "cannot read route registry" in result.output


def test_replay_missing_recorded_response_errors_cleanly(tmp_path):
    out = tmp_path / "o.md"
    result = CliRunner().invoke(
        main,
        [
            "replay",
            "--route",
            "customer-support",
            "--release",
            "no-such-release",
            "--out",
            str(out),
            *COMMON,
        ],
    )

    assert result.exit_code != 0
    assert "missing recorded response" in result.output
