from pathlib import Path

from click.testing import CliRunner

from cli.main import main


def test_show_prints_ranked_readable_summary():
    result = CliRunner().invoke(main, ["show"])

    assert result.exit_code == 0, result.output
    out = result.output
    # headline verdict
    assert "SWAP: fixture-candidate-v1 beats fixture-incumbent-v1" in out
    # ranked trace table, best quality delta first
    assert "traces ranked by quality delta" in out
    lines = [line for line in out.splitlines() if line.strip().startswith("1 ")]
    assert lines and "trace-cs-002" in lines[0]
    # the worst trace ranks last
    worst_index = out.index("trace-cs-003")
    best_index = out.index("trace-cs-002")
    assert best_index < worst_index
    # deltas surfaced
    assert "quality" in out
    assert "judge win-rate" in out


def test_show_missing_record_errors_cleanly():
    result = CliRunner().invoke(main, ["show", "--decision", "does-not-exist.md"])

    assert result.exit_code != 0
    assert "decision record not found" in result.output
