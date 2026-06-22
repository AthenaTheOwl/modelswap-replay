from pathlib import Path
from tempfile import TemporaryDirectory

from click.testing import CliRunner

from cli.main import main


def test_cli_writes_expected_decision_record():
    with TemporaryDirectory(dir=Path.cwd()) as temp_dir:
        out = Path(temp_dir) / "fixture-candidate-v1-customer-support.md"
        result = CliRunner().invoke(
            main,
            [
                "replay",
                "--route",
                "customer-support",
                "--release",
                "fixture-candidate-v1",
                "--since",
                "7d",
                "--offline",
                "--routes",
                "tests/fixtures/routes.yaml",
                "--recorded-root",
                "tests/fixtures/recorded_responses",
                "--out",
                str(out),
            ],
        )

        assert result.exit_code == 0, result.output
        expected = Path("tests/fixtures/expected/fixture-candidate-v1-customer-support.md")
        assert out.read_text(encoding="utf-8") == expected.read_text(encoding="utf-8")
