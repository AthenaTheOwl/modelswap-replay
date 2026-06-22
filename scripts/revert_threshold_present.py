from __future__ import annotations

import sys
from pathlib import Path

import yaml


NUMERIC_KEYS = {
    "quality_drop_max",
    "cost_increase_max",
    "latency_p95_regression_ms_max",
}


def main(argv: list[str] | None = None) -> int:
    targets = [Path(arg) for arg in (argv if argv is not None else sys.argv[1:])]
    if not targets:
        targets = [Path("decisions/model-swap")]

    failures: list[str] = []
    for path in expand_records(targets):
        text = path.read_text(encoding="utf-8")
        data = read_front_matter(text)
        threshold = data.get("revert_threshold")
        if not isinstance(threshold, dict):
            failures.append(f"{path}: missing front matter revert_threshold")
            continue
        numeric_present = [key for key in NUMERIC_KEYS if isinstance(threshold.get(key), (int, float))]
        if not numeric_present:
            failures.append(f"{path}: revert_threshold has no numeric trigger")
        if "revert_threshold:" not in text:
            failures.append(f"{path}: body is missing revert_threshold block")

    if failures:
        print("\n".join(failures))
        return 1
    print("revert_threshold_present: ok")
    return 0


def expand_records(targets: list[Path]) -> list[Path]:
    records: list[Path] = []
    for target in targets:
        if target.is_dir():
            records.extend(sorted(target.glob("*.md")))
        elif target.suffix == ".md":
            records.append(target)
    return records


def read_front_matter(text: str) -> dict:
    if not text.startswith("---\n"):
        return {}
    raw = text.split("\n---\n", 1)[0].removeprefix("---\n")
    data = yaml.safe_load(raw)
    return data if isinstance(data, dict) else {}


if __name__ == "__main__":
    raise SystemExit(main())

