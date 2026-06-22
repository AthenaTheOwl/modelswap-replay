from __future__ import annotations

from pathlib import Path

import click

from modelswap_replay.model import OfflineAdapter, ReplayRunner, load_route_registry, sample_requests
from modelswap_replay.rendering import render_decision_record
from modelswap_replay.scoring import EvalRunner, OfflineJudge, choose_verdict


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ROUTES = REPO_ROOT / "config" / "routes.yaml"
DEFAULT_RECORDED_ROOT = REPO_ROOT / "tests" / "fixtures" / "recorded_responses"


@click.group()
def main() -> None:
    """ModelSwap Replay command group."""


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

    registry = load_route_registry(routes_path)
    route = registry.get(route_name)
    samples = sample_requests(route=route, registry_path=routes_path, since=since)
    responses = ReplayRunner(adapter=OfflineAdapter(recorded_root)).run(samples, release_id)
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
