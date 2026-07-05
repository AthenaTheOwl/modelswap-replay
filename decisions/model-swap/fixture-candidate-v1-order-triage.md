---
release_id: fixture-candidate-v1
route: order-triage
verdict: swap
incumbent: fixture-incumbent-v1
candidate: fixture-candidate-v1
sample_window:
  start: '2026-06-15'
  end: '2026-06-17'
  request_count: 4
deltas:
  quality: 0.087
  cost_per_request_usd: -0.0002
  cost_ratio: -0.08
  latency_p95_ms: -25
dimensions:
  actionability: 0.125
  faithfulness: 0.095
  risk_flagging: 0.1
judge:
  candidate_win_rate: 1.0
  candidate_wins: 4
  incumbent_wins: 0
  ties: 0
best_traces:
  - trace_id: trace-ot-001
    quality_delta: 0.1
    cost_delta_usd: -0.0002
    latency_delta_ms: -30
  - trace_id: trace-ot-002
    quality_delta: 0.09
    cost_delta_usd: -0.0002
    latency_delta_ms: -25
  - trace_id: trace-ot-003
    quality_delta: 0.08
    cost_delta_usd: -0.0002
    latency_delta_ms: -35
worst_traces:
  - trace_id: trace-ot-003
    quality_delta: 0.08
    cost_delta_usd: -0.0002
    latency_delta_ms: -35
  - trace_id: trace-ot-004
    quality_delta: 0.08
    cost_delta_usd: -0.0002
    latency_delta_ms: -30
  - trace_id: trace-ot-002
    quality_delta: 0.09
    cost_delta_usd: -0.0002
    latency_delta_ms: -25
revert_threshold:
  quality_drop_max: 0.03
  cost_increase_max: 0.2
  latency_p95_regression_ms_max: 250
revert_review_date: '2026-07-01'
rationale:
  - candidate passed quality, cost, latency, and judge thresholds
---
# Model Swap - fixture-candidate-v1 -> order-triage

## Verdict
- verdict: swap
- incumbent: fixture-incumbent-v1
- candidate: fixture-candidate-v1
- sample_window: 2026-06-15..2026-06-17 (4 requests)

## Deltas
- quality_delta: +0.087
- cost_delta_per_request_usd: -0.0002
- cost_delta_ratio: -0.080
- latency_p95_delta_ms: -25
- judge_candidate_win_rate: 1.000

## Dimensions
- actionability: +0.125
- faithfulness: +0.095
- risk_flagging: +0.100

## Best traces
- trace-ot-001: quality_delta=+0.100, cost_delta_usd=-0.0002, latency_delta_ms=-30
- trace-ot-002: quality_delta=+0.090, cost_delta_usd=-0.0002, latency_delta_ms=-25
- trace-ot-003: quality_delta=+0.080, cost_delta_usd=-0.0002, latency_delta_ms=-35

## Worst traces
- trace-ot-003: quality_delta=+0.080, cost_delta_usd=-0.0002, latency_delta_ms=-35
- trace-ot-004: quality_delta=+0.080, cost_delta_usd=-0.0002, latency_delta_ms=-30
- trace-ot-002: quality_delta=+0.090, cost_delta_usd=-0.0002, latency_delta_ms=-25

## Revert threshold
revert_threshold:
  quality_drop_max: 0.03
  cost_increase_max: 0.2
  latency_p95_regression_ms_max: 250
- revert_review_date: 2026-07-01

## Rationale
- candidate passed quality, cost, latency, and judge thresholds
