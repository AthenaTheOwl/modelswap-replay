from pathlib import Path

from src.models.route_registry import load_route_registry
from src.sampler.traffic_sampler import sample_requests


def test_sampler_loads_fixture_route_and_is_deterministic():
    routes_path = Path("tests/fixtures/routes.yaml")
    route = load_route_registry(routes_path).get("customer-support")

    first = sample_requests(route, routes_path, "7d")
    second = sample_requests(route, routes_path, "7d")

    assert [record.trace_id for record in first] == [
        "trace-cs-001",
        "trace-cs-002",
        "trace-cs-003",
        "trace-cs-004",
        "trace-cs-005",
        "trace-cs-006",
    ]
    assert [record.model_dump() for record in first] == [record.model_dump() for record in second]

