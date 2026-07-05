from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from cli.main import main


def test_batch_replay_writes_one_decision_per_route(tmp_path: Path) -> None:
    out_dir = tmp_path / "decisions"
    report = tmp_path / "batch.jsonl"
    result = CliRunner().invoke(
        main,
        [
            "batch-replay",
            "--release",
            "fixture-candidate-v1",
            "--since",
            "7d",
            "--routes",
            "tests/fixtures/routes.yaml",
            "--recorded-root",
            "tests/fixtures/recorded_responses",
            "--out-dir",
            str(out_dir),
            "--report",
            str(report),
        ],
    )

    assert result.exit_code == 0, result.output
    records = sorted(path.name for path in out_dir.glob("*.md"))
    assert records == [
        "fixture-candidate-v1-customer-support.md",
        "fixture-candidate-v1-order-triage.md",
    ]
    rows = [json.loads(line) for line in report.read_text(encoding="utf-8").splitlines()]
    assert [row["route"] for row in rows] == ["customer-support", "order-triage"]
    assert all(row["record_type"] == "batch-route" for row in rows)
    assert all(row["verdict"] == "swap" for row in rows)


def test_batch_replay_missing_recorded_response_errors_cleanly(tmp_path: Path) -> None:
    result = CliRunner().invoke(
        main,
        [
            "batch-replay",
            "--release",
            "missing-release",
            "--routes",
            "tests/fixtures/routes.yaml",
            "--recorded-root",
            "tests/fixtures/recorded_responses",
            "--out-dir",
            str(tmp_path / "decisions"),
        ],
    )

    assert result.exit_code != 0
    assert "missing recorded response" in result.output
