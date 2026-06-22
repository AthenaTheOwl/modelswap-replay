from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator


def main(argv: list[str] | None = None) -> int:
    targets = [Path(arg) for arg in (argv if argv is not None else sys.argv[1:])]
    if not targets:
        targets = [Path("decisions/model-swap")]

    schema = json.loads(Path("schemas/decision-record.schema.json").read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    failures: list[str] = []
    for path in expand_records(targets):
        data = read_front_matter(path)
        errors = sorted(validator.iter_errors(data), key=lambda error: list(error.path))
        for error in errors:
            location = ".".join(str(part) for part in error.path) or "<root>"
            failures.append(f"{path}: {location}: {error.message}")

    if failures:
        print("\n".join(failures))
        return 1
    print("validate_schemas: ok")
    return 0


def expand_records(targets: list[Path]) -> list[Path]:
    records: list[Path] = []
    for target in targets:
        if target.is_dir():
            records.extend(sorted(target.glob("*.md")))
        elif target.suffix == ".md":
            records.append(target)
    return records


def read_front_matter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"{path}: missing YAML front matter")
    try:
        raw = text.split("\n---\n", 1)[0].removeprefix("---\n")
    except ValueError as exc:
        raise ValueError(f"{path}: unterminated YAML front matter") from exc
    data = yaml.safe_load(raw)
    if not isinstance(data, dict):
        raise ValueError(f"{path}: front matter must be a mapping")
    return data


if __name__ == "__main__":
    raise SystemExit(main())

