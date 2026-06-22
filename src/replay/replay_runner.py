from __future__ import annotations

import json
from pathlib import Path
from typing import Protocol

from pydantic import BaseModel, Field

from src.sampler.traffic_sampler import SampledRequest


class ReplayResponse(BaseModel):
    trace_id: str
    response: str
    quality_score: float = Field(ge=0, le=1)
    cost_usd: float = Field(ge=0)
    latency_ms: int = Field(ge=0)
    scores: dict[str, float] = Field(default_factory=dict)
    judge_preference: str = Field(pattern="^(candidate|incumbent|tie)$")
    judge_reason: str


class ReplayAdapter(Protocol):
    def replay(self, request: SampledRequest, release_id: str) -> ReplayResponse:
        ...


class OfflineAdapter:
    def __init__(self, recorded_root: str | Path) -> None:
        self.recorded_root = Path(recorded_root)

    def replay(self, request: SampledRequest, release_id: str) -> ReplayResponse:
        path = self.recorded_root / release_id / f"{request.trace_id}.json"
        if not path.exists():
            raise FileNotFoundError(f"missing recorded response for {request.trace_id}: {path}")
        data = json.loads(path.read_text(encoding="utf-8"))
        return ReplayResponse.model_validate(data)


class ReplayRunner:
    def __init__(self, adapter: ReplayAdapter) -> None:
        self.adapter = adapter

    def run(self, requests: list[SampledRequest], release_id: str) -> list[ReplayResponse]:
        return [self.adapter.replay(request, release_id) for request in requests]

