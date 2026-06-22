from __future__ import annotations

from pathlib import Path

from src.decide.verdict import choose_verdict
from src.models.route_registry import load_route_registry
from src.replay.replay_runner import OfflineAdapter, ReplayRunner
from src.sampler.traffic_sampler import sample_requests
from src.score.eval_runner import EvalRunner
from src.score.llm_judge import OfflineJudge


FIXTURE_ROOT = Path("tests/fixtures")
ROUTES_PATH = FIXTURE_ROOT / "routes.yaml"
RECORDED_ROOT = FIXTURE_ROOT / "recorded_responses"


def build_fixture_run():
    registry = load_route_registry(ROUTES_PATH)
    route = registry.get("customer-support")
    samples = sample_requests(route, ROUTES_PATH, "7d")
    responses = ReplayRunner(OfflineAdapter(RECORDED_ROOT)).run(samples, "fixture-candidate-v1")
    judge = OfflineJudge().score(samples, responses)
    summary = EvalRunner().evaluate(samples, responses, judge)
    verdict = choose_verdict(summary, route.revert_threshold)
    return route, samples, responses, judge, summary, verdict

