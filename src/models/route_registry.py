from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field, PositiveInt


class RevertThreshold(BaseModel):
    quality_drop_max: float = Field(ge=0)
    cost_increase_max: float = Field(ge=0)
    latency_p95_regression_ms_max: int = Field(ge=0)


class SampleConfig(BaseModel):
    window_days: PositiveInt = 7
    per_day_n: PositiveInt = 200
    strategy: Literal["all", "stratified-by-intent"] = "stratified-by-intent"
    seed: int = 17


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

