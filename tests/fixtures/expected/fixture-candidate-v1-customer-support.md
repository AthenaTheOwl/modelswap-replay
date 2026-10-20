---
release_id: fixture-candidate-v1
route: customer-support
verdict: defer
incumbent: fixture-incumbent-v1
candidate: fixture-candidate-v1
sample_window:
  start: '2026-06-15'
  end: '2026-06-17'
  request_count: 6
  min_request_count: 70
deltas:
  quality: 0.053
  cost_per_request_usd: -0.0003
  cost_ratio: -0.105
  latency_p95_ms: 30
dimensions:
  faithfulness: 0.055
  refusal: 0.013
  task_completion: 0.058
judge:
  candidate_win_rate: 0.833
  candidate_wins: 5
  incumbent_wins: 1
  ties: 0
  judged_count: 6
  win_rate_ci95_low: 0.436
  win_rate_ci95_high: 0.97
best_traces:
  - trace_id: trace-cs-002
    quality_delta: 0.08
    cost_delta_usd: -0.0003
    latency_delta_ms: -40
  - trace_id: trace-cs-005
    quality_delta: 0.08
    cost_delta_usd: -0.0004
    latency_delta_ms: -30
  - trace_id: trace-cs-004
    quality_delta: 0.07
    cost_delta_usd: -0.0004
    latency_delta_ms: -35
worst_traces:
  - trace_id: trace-cs-003
    quality_delta: -0.03
    cost_delta_usd: -0.0002
    latency_delta_ms: 30
  - trace_id: trace-cs-001
    quality_delta: 0.06
    cost_delta_usd: -0.0003
    latency_delta_ms: -40
  - trace_id: trace-cs-006
    quality_delta: 0.06
    cost_delta_usd: -0.0003
    latency_delta_ms: -30
revert_threshold:
  quality_drop_max: 0.03
  cost_increase_max: 0.2
  latency_p95_regression_ms_max: 250
revert_review_date: '2026-07-01'
rationale:
  - 'insufficient sample: 6 requests, below the minimum of 70'
---
# Model Swap - fixture-candidate-v1 -> customer-support

## Verdict
- verdict: defer
- incumbent: fixture-incumbent-v1
- candidate: fixture-candidate-v1
- sample_window: 2026-06-15..2026-06-17 (6 requests)
- minimum_requests_for_verdict: 70

## Deltas
- quality_delta: +0.053
- cost_delta_per_request_usd: -0.0003
- cost_delta_ratio: -0.105
- latency_p95_delta_ms: +30
- judge_candidate_win_rate: 0.833 (5/6, 95% Wilson interval 0.436-0.970)

## Dimensions
- faithfulness: +0.055
- refusal: +0.013
- task_completion: +0.058

## Best traces
- trace-cs-002: quality_delta=+0.080, cost_delta_usd=-0.0003, latency_delta_ms=-40
- trace-cs-005: quality_delta=+0.080, cost_delta_usd=-0.0004, latency_delta_ms=-30
- trace-cs-004: quality_delta=+0.070, cost_delta_usd=-0.0004, latency_delta_ms=-35

## Worst traces
- trace-cs-003: quality_delta=-0.030, cost_delta_usd=-0.0002, latency_delta_ms=+30
- trace-cs-001: quality_delta=+0.060, cost_delta_usd=-0.0003, latency_delta_ms=-40
- trace-cs-006: quality_delta=+0.060, cost_delta_usd=-0.0003, latency_delta_ms=-30

## Revert threshold
revert_threshold:
  quality_drop_max: 0.03
  cost_increase_max: 0.2
  latency_p95_regression_ms_max: 250
- revert_review_date: 2026-07-01

## Rationale
- insufficient sample: 6 requests, below the minimum of 70
