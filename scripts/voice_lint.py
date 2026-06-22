from __future__ import annotations

import re
import sys
from pathlib import Path


BANNED_TERMS = [
    "best-in-class",
    "cutting-edge",
    "delightful",
    "game-changing",
    "mission-critical",
    "revolutionary",
    "seamless",
    "supercharge",
    "transformative",
    "unlock",
    "world-class",
]

BANNED_PATTERNS = [
    re.compile(r"\bnot\s+[^.\n]{1,80}\s+but\b", re.IGNORECASE),
    re.compile(r"\bnot only\b", re.IGNORECASE),
    re.compile(r"\brather than\b", re.IGNORECASE),
]


def main(argv: list[str] | None = None) -> int:
    targets = [Path(arg) for arg in (argv if argv is not None else sys.argv[1:])]
    if not targets:
        targets = [Path("decisions/model-swap")]

    failures: list[str] = []
    for path in expand_markdown(targets):
        text = path.read_text(encoding="utf-8")
        lowered = text.lower()
        for term in BANNED_TERMS:
            if term in lowered:
                failures.append(f"{path}: banned term {term!r}")
        for pattern in BANNED_PATTERNS:
            if pattern.search(text):
                failures.append(f"{path}: banned structural phrase {pattern.pattern!r}")

    if failures:
        print("\n".join(failures))
        return 1
    print("voice_lint: ok")
    return 0


def expand_markdown(targets: list[Path]) -> list[Path]:
    files: list[Path] = []
    for target in targets:
        if target.is_dir():
            files.extend(sorted(target.glob("*.md")))
        elif target.suffix == ".md":
            files.append(target)
    return files


if __name__ == "__main__":
    raise SystemExit(main())

