---
id: DEC-MSR-001-minimum-sample-guard
spec: specs/0002-design/
requirement: R-MSR-006
date: 2026-10-20
status: approved
reversible: true
decision: |
  choose_verdict defers with "insufficient sample" when a replay has fewer
  sampled requests than the route's minimum. The minimum is
  sample.min_sample_count when a route sets it, and otherwise the route's own
  sample design (window_days x per_day_n), never below a floor of 30. Every
  decision record, batch row, curve row and card reports n, the minimum, and
  a 95% Wilson interval around the judge win rate.
alternatives:
  - label: keep deferring only at zero samples
    rejected_because: |
      One winning request was enough for "swap", and so was a 1-1 judge split
      with a -0.02 quality delta. The committed customer-support record said
      swap on 6 requests and the order-triage record on 4. Five wins in six
      happen with probability 0.109 under a coin-flip judge.
  - label: a fixed floor for every route
    rejected_because: |
      Routes already state how much traffic a decision should see
      (window_days x per_day_n). A fixed floor would let a route designed
      for 1,400 requests swap on 30.
  - label: gate on the interval's lower bound instead of the 0.5 point rate
    rejected_because: |
      It changes what "the candidate wins" means for every route. This record
      only adds the sample guard and reports the interval; tightening the
      win-rate test is a separate decision.
rationale: |
  A verdict should rest on at least the sample the route was designed to
  collect. The floor of 30 is the smallest n at which an observed 70% judge
  win rate has a 95% Wilson interval that excludes 0.5 (21 of 30 gives
  0.521-0.833; 14 of 20 gives 0.481-0.855). A route can set a lower
  min_sample_count, but has to write it down in the registry to do so.
evidence:
  - kind: test
    ref: tests/test_min_sample_guard.py
  - kind: record
    ref: decisions/model-swap/fixture-candidate-v1-customer-support.md
  - kind: record
    ref: decisions/model-swap/fixture-candidate-v1-order-triage.md
rollback: |
  Set sample.min_sample_count on a route to the sample size it should accept,
  or revert this change to restore the zero-sample-only check.
---

# DEC-MSR-001: defer below a minimum sample

## Effect on committed records

Both committed fixture records were regenerated with the README's
`batch-replay` and `replay` commands, and the customer-support card with
`modelswap card`. Both verdicts changed from `swap` to `defer`:

| route | requests | minimum | judge | 95% Wilson interval | before | after |
|---|---:|---:|---:|---|---|---|
| customer-support | 6 | 70 | 5 of 6 (0.833) | 0.436-0.970 | swap | defer |
| order-triage | 4 | 70 | 4 of 4 (1.000) | 0.510-1.000 | swap | defer |

The quality, cost and latency deltas are unchanged. Every setting in the
effort curve now defers too, so `curve` on the committed routes exits 1 with
no cheapest clearing setting. The curve tests exercise the selection
mechanism with an explicit `min_sample_count: 6` override.

`reports/fixture-candidate-v1-customer-support.jsonl` came from the v0.1
factory commit, and no command in this repo writes it. It still says `swap`
and is superseded by the decision record above.

## Still open

The swap test still compares the point win rate with 0.5. At the minimum of
70, a 35-of-70 judge split passes it.
