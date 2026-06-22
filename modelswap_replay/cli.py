from __future__ import annotations

from pathlib import Path

import click

from modelswap_replay.model import OfflineAdapter, ReplayRunner, load_route_registry, sample_requests
from modelswap_replay.rendering import render_decision_record
from modelswap_replay.scoring import EvalRunner, OfflineJudge, choose_verdict


@click.group()
def main() -> None:
    """ModelSwap Replay command group."""


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
