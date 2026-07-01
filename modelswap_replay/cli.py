from __future__ import annotations

from pathlib import Path

import click
import yaml

from modelswap_replay.model import OfflineAdapter, ReplayRunner, load_route_registry, sample_requests
from modelswap_replay.rendering import render_decision_record
from modelswap_replay.scoring import EvalRunner, OfflineJudge, choose_verdict


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ROUTES = REPO_ROOT / "config" / "routes.yaml"
DEFAULT_RECORDED_ROOT = REPO_ROOT / "tests" / "fixtures" / "recorded_responses"
DEFAULT_DECISION = (
    REPO_ROOT / "decisions" / "model-swap" / "fixture-candidate-v1-customer-support.md"
)


def load_decision_front_matter(path: Path) -> dict:
    """Parse the YAML front matter from a decision-record markdown file."""

    try:
        text = path.read_text(encoding="utf-8")
    except OSError as err:
        # A directory or unreadable path lands here; name it instead of crashing.
        raise click.ClickException(f"cannot read decision record {path}: {err}")
    if not text.startswith("---"):
        raise click.ClickException(f"no YAML front matter in {path}")
    _, front, _body = text.split("---", 2)
    try:
        data = yaml.safe_load(front)
    except yaml.YAMLError as err:
        raise click.ClickException(f"malformed YAML front matter in {path}: {err}")
    if not isinstance(data, dict):
        raise click.ClickException(f"front matter is not a mapping in {path}")
    return data


def _fmt_signed(value: float, places: int) -> str:
    return f"{value:+.{places}f}"


def render_show(record: dict) -> str:
    """Build a ranked, readable summary of a decision record."""

    verdict = str(record.get("verdict", "?"))
    route = str(record.get("route", "?"))
    candidate = str(record.get("candidate", record.get("release_id", "?")))
    incumbent = str(record.get("incumbent", "?"))
    window = record.get("sample_window", {}) or {}
    count = window.get("request_count", "?")
    deltas = record.get("deltas", {}) or {}
    judge = record.get("judge", {}) or {}
    win_rate = judge.get("candidate_win_rate", 0.0)

    quality = deltas.get("quality", 0.0)
    cost_ratio = deltas.get("cost_ratio", 0.0)
    latency = deltas.get("latency_p95_ms", 0)

    headline = {
        "swap": f"SWAP: {candidate} beats {incumbent} on {route} "
        f"(quality {_fmt_signed(quality, 3)}, judge win-rate {win_rate:.0%}).",
        "hold": f"HOLD: {candidate} did not clear the gate on {route}.",
        "revert": f"REVERT: {candidate} regressed past the revert threshold on {route}.",
    }.get(verdict, f"{verdict.upper()}: {candidate} on {route}.")

    lines: list[str] = []
    lines.append(f"model swap gate -- {candidate} -> {route}")
    lines.append("=" * 56)
    lines.append("")
    lines.append(f"verdict        : {verdict}")
    lines.append(f"incumbent      : {incumbent}")
    lines.append(f"candidate      : {candidate}")
    lines.append(
        f"sample window  : {window.get('start', '?')}..{window.get('end', '?')} "
        f"({count} requests)"
    )
    lines.append("")
    lines.append("deltas (candidate vs incumbent)")
    lines.append(f"  {'metric':<22}{'value':>12}")
    lines.append(f"  {'-' * 22}{'-' * 12:>12}")
    lines.append(f"  {'quality':<22}{_fmt_signed(quality, 3):>12}")
    lines.append(f"  {'cost ratio':<22}{_fmt_signed(cost_ratio, 3):>12}")
    lines.append(f"  {'latency p95 (ms)':<22}{f'{latency:+d}':>12}")
    lines.append(f"  {'judge win-rate':<22}{win_rate:>11.0%}")
    lines.append("")

    best = record.get("best_traces", []) or []
    worst = record.get("worst_traces", []) or []
    ranked = sorted(
        best + worst,
        key=lambda t: t.get("quality_delta", 0.0),
        reverse=True,
    )
    lines.append("traces ranked by quality delta")
    lines.append(f"  {'rank':<5}{'trace':<16}{'quality':>10}{'cost usd':>12}{'lat ms':>9}")
    lines.append(f"  {'-' * 5}{'-' * 16}{'-' * 10:>10}{'-' * 12:>12}{'-' * 9:>9}")
    for rank, trace in enumerate(ranked, start=1):
        lines.append(
            f"  {rank:<5}{trace.get('trace_id', '?'):<16}"
            f"{_fmt_signed(trace.get('quality_delta', 0.0), 3):>10}"
            f"{_fmt_signed(trace.get('cost_delta_usd', 0.0), 4):>12}"
            f"{trace.get('latency_delta_ms', 0):>+9d}"
        )
    lines.append("")
    lines.append(headline)
    return "\n".join(lines)


@click.group()
def main() -> None:
    """ModelSwap Replay command group."""


@main.command()
@click.option(
    "--decision",
    "decision_path",
    default=DEFAULT_DECISION,
    show_default=True,
    type=click.Path(path_type=Path),
    help="Decision record to summarize.",
)
def show(decision_path: Path) -> None:
    """Print a ranked, readable summary of the committed decision record.

    Read-only and offline: parses the decision record's YAML front matter,
    ranks the replayed traces by quality delta, and prints a headline verdict.
    """

    if not decision_path.exists():
        raise click.ClickException(f"decision record not found: {decision_path}")
    record = load_decision_front_matter(decision_path)
    click.echo(render_show(record))


@main.command()
@click.option(
    "--routes",
    "routes_path",
    default=DEFAULT_ROUTES,
    show_default=True,
    type=click.Path(path_type=Path),
    help="Route registry to typed-validate.",
)
@click.option(
    "--recorded-root",
    default=DEFAULT_RECORDED_ROOT,
    show_default=True,
    type=click.Path(path_type=Path),
    help="Recorded-response root that must exist.",
)
def validate(routes_path: Path, recorded_root: Path) -> None:
    """Typed-validate the bundled route registry and recorded fixtures.

    Read-only first user action: loads config/routes.yaml through the
    pydantic models and confirms the recorded-response root is present.
    """

    if not routes_path.exists():
        raise click.ClickException(f"route registry not found: {routes_path}")
    registry = load_route_registry(routes_path)
    if not registry.routes:
        raise click.ClickException(f"route registry has no routes: {routes_path}")
    if not recorded_root.exists():
        raise click.ClickException(f"recorded-response root not found: {recorded_root}")
    names = ", ".join(route.name for route in registry.routes)
    click.echo(f"validate: ok ({len(registry.routes)} route(s): {names})")


@main.command()
@click.option("--route", "route_name", required=True, help="Route name from the route registry.")
@click.option("--release", "release_id", required=True, help="Candidate release identifier.")
@click.option("--since", default="7d", show_default=True, help="Lookback window, for example 7d.")
@click.option("--out", "out_path", required=True, type=click.Path(path_type=Path), help="Decision record output path.")
@click.option(
    "--routes",
    "routes_path",
    default=Path("config/routes.yaml"),
    show_default=True,
    type=click.Path(path_type=Path),
    help="Route registry path.",
)
@click.option(
    "--recorded-root",
    default=Path("tests/fixtures/recorded_responses"),
    show_default=True,
    type=click.Path(path_type=Path),
    help="Offline recorded response root.",
)
@click.option("--offline/--live", default=True, show_default=True, help="Use fixture-backed responses.")
def replay(
    route_name: str,
    release_id: str,
    since: str,
    out_path: Path,
    routes_path: Path,
    recorded_root: Path,
    offline: bool,
) -> None:
    """Run one offline replay pass and write one decision record."""

    if not offline:
        raise click.ClickException("live model adapters are deferred to a later spec")

    try:
        registry = load_route_registry(routes_path)
    except OSError as err:
        raise click.ClickException(f"cannot read route registry {routes_path}: {err}")
    try:
        route = registry.get(route_name)
    except KeyError as err:
        # KeyError already carries "unknown route ...; known routes: ..."; unwrap it
        # so ClickException prints the message without KeyError's extra quoting.
        raise click.ClickException(str(err.args[0]))
    try:
        samples = sample_requests(route=route, registry_path=routes_path, since=since)
    except ValueError as err:
        raise click.ClickException(f"bad --since {since!r}: {err}")
    try:
        responses = ReplayRunner(adapter=OfflineAdapter(recorded_root)).run(samples, release_id)
    except FileNotFoundError as err:
        raise click.ClickException(str(err))
    judge = OfflineJudge().score(samples, responses)
    summary = EvalRunner().evaluate(samples, responses, judge)
    verdict = choose_verdict(summary, route.revert_threshold)
    record = render_decision_record(
        release_id=release_id,
        route=route,
        samples=samples,
        responses=responses,
        summary=summary,
        judge=judge,
        verdict=verdict,
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(record, encoding="utf-8")
    click.echo(str(out_path))


if __name__ == "__main__":
    main()
