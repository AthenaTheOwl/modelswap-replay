# Spec 0002 - Runnable Offline Replay

## R-MSR-002 - route registry

`config/routes.yaml` is present and loads into typed Pydantic models.
The route schema lives at `schemas/route.schema.json`.

## R-MSR-003 - traffic sampler

The sampler reads JSONL traces from a file-backed store, filters by
route and lookback window, and samples deterministically from each day.

## R-MSR-004 - replay runner

The replay runner uses an adapter boundary. v0.1 ships the
fixture-backed `OfflineAdapter`; live model adapters are deferred.

## R-MSR-005 - score plane

The eval runner emits structured deltas for quality, cost, latency, and
named dimensions. The offline judge emits a candidate win rate.

## R-MSR-006 - verdict author

The verdict author is deterministic for a fixed score summary and route
threshold.

## R-MSR-007 - decision record

The renderer writes one Markdown record with YAML front matter under
`decisions/model-swap/`.

## R-MSR-008 - revert threshold required

Records must include `revert_threshold:` in front matter and body text.

## R-MSR-009 - gates

The four local gate scripts exist under `scripts/`.

## R-MSR-010 - offline fixture

The test fixture includes a route registry, trace store, recorded
candidate responses, expected record, and tests.

## R-MSR-011 - eval-predictive-validity report

This remains deferred and is listed in `STATUS.md` under
`Next feature queue`.

