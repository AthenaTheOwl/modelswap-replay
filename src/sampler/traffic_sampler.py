from __future__ import annotations

from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
from hashlib import sha256
import json
from pathlib import Path

from pydantic import BaseModel, Field

from src.models.route_registry import RouteConfig


class SampledRequest(BaseModel):
    trace_id: str
    route: str
    timestamp: datetime
    intent: str
    prompt: str
    incumbent_response: str
    incumbent_quality: float = Field(ge=0, le=1)
    incumbent_cost_usd: float = Field(ge=0)
    incumbent_latency_ms: int = Field(ge=0)
    incumbent_scores: dict[str, float] = Field(default_factory=dict)


def parse_since_days(since: str) -> int:
    if not since.endswith("d"):
        raise ValueError("since must use day syntax, for example 7d")
    days = int(since[:-1])
    if days <= 0:
        raise ValueError("since must be positive")
    return days


def sample_requests(route: RouteConfig, registry_path: str | Path, since: str = "7d") -> list[SampledRequest]:
    trace_store = resolve_trace_store(route.trace_store, Path(registry_path))
    records = [record for record in load_trace_store(trace_store) if record.route == route.name]
    if not records:
        return []

    days = parse_since_days(since)
    end = max(record.timestamp for record in records)
    start = end - timedelta(days=days)
    windowed = [record for record in records if start <= record.timestamp <= end]
    grouped: dict[str, list[SampledRequest]] = defaultdict(list)
    for record in windowed:
        grouped[record.timestamp.date().isoformat()].append(record)

    sampled: list[SampledRequest] = []
    for day in sorted(grouped):
        sampled.extend(sample_one_day(grouped[day], route.sample.per_day_n, route.sample.seed, route.sample.strategy))
    return sorted(sampled, key=lambda record: (record.timestamp, record.trace_id))


def resolve_trace_store(trace_store: str, registry_path: Path) -> Path:
    raw = Path(trace_store)
    if raw.is_absolute():
        return raw

    candidates = [
        registry_path.parent / raw,
        registry_path.parent.parent / raw,
        Path.cwd() / raw,
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve()
    return candidates[0].resolve()


def load_trace_store(trace_store: Path) -> list[SampledRequest]:
    files = sorted(trace_store.glob("*.jsonl")) if trace_store.is_dir() else [trace_store]
    records: list[SampledRequest] = []
    for path in files:
        with path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                try:
                    records.append(SampledRequest.model_validate(json.loads(line)))
                except Exception as exc:  # pragma: no cover - error path preserves source context.
                    raise ValueError(f"invalid trace record {path}:{line_number}: {exc}") from exc
    return records


def sample_one_day(
    records: list[SampledRequest],
    per_day_n: int,
    seed: int,
    strategy: str,
) -> list[SampledRequest]:
    if len(records) <= per_day_n:
        return sorted(records, key=lambda record: (record.timestamp, record.trace_id))
    if strategy == "stratified-by-intent":
        return stratified(records, per_day_n, seed)
    return sorted(records, key=lambda record: stable_sample_key(record.trace_id, seed))[:per_day_n]


def stratified(records: list[SampledRequest], per_day_n: int, seed: int) -> list[SampledRequest]:
    by_intent: dict[str, deque[SampledRequest]] = {}
    for intent in sorted({record.intent for record in records}):
        ordered = sorted(
            [record for record in records if record.intent == intent],
            key=lambda record: stable_sample_key(record.trace_id, seed),
        )
        by_intent[intent] = deque(ordered)

    picked: list[SampledRequest] = []
    while len(picked) < per_day_n and any(by_intent.values()):
        for intent in sorted(by_intent):
            if by_intent[intent] and len(picked) < per_day_n:
                picked.append(by_intent[intent].popleft())
    return sorted(picked, key=lambda record: (record.timestamp, record.trace_id))


def stable_sample_key(trace_id: str, seed: int) -> str:
    return sha256(f"{seed}:{trace_id}".encode("utf-8")).hexdigest()

