from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field, PositiveInt


class RevertThreshold(BaseModel):
    quality_drop_max: float = Field(ge=0)
    cost_increase_max: float = Field(ge=0)
    latency_p95_regression_ms_max: int = Field(ge=0)


# Smallest default sample a verdict may rest on. At n=30 an observed 70%
# judge win rate has a 95% Wilson interval of about 0.52-0.83, which clears
# a coin; at n=20 the same rate's interval reaches below 0.5. See
# decisions/DEC-MSR-001-minimum-sample-guard.md.
MIN_SAMPLE_FLOOR = 30


class SampleConfig(BaseModel):
    window_days: PositiveInt = 7
    per_day_n: PositiveInt = 200
    strategy: Literal["all", "stratified-by-intent"] = "stratified-by-intent"
    seed: int = 17
    # Fewest sampled requests a non-defer verdict needs. When unset, the
    # route's own sample design (window_days x per_day_n) is the minimum,
    # and never less than MIN_SAMPLE_FLOOR.
    min_sample_count: PositiveInt | None = None

    def required_sample_count(self) -> int:
        if self.min_sample_count is not None:
            return self.min_sample_count
        return max(self.window_days * self.per_day_n, MIN_SAMPLE_FLOOR)


class RouteConfig(BaseModel):
    name: str
    incumbent: str
    trace_store: str
    sample: SampleConfig
    eval_suite: str
    llm_judge_rubric: str
    revert_threshold: RevertThreshold


class RouteRegistry(BaseModel):
    routes: list[RouteConfig]

    def get(self, name: str) -> RouteConfig:
        for route in self.routes:
            if route.name == name:
                return route
        known = ", ".join(sorted(route.name for route in self.routes))
        raise KeyError(f"unknown route {name!r}; known routes: {known}")


def load_route_registry(path: str | Path) -> RouteRegistry:
    route_path = Path(path)
    data = yaml.safe_load(route_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"route registry must be a mapping: {route_path}")
    return RouteRegistry.model_validate(data)

