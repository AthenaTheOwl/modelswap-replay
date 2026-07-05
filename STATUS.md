# ModelSwap Replay Status

## Current state

- v0.1 has offline `modelswap replay` and `modelswap batch-replay` commands. Single replay writes one decision record; batch replay writes one record per route plus a JSONL batch report.
- The route registry now carries two routes (`customer-support` and `order-triage`) with separate trace-store and recorded-response fixtures.
- The checked-in report is `decisions/model-swap/fixture-candidate-v1-customer-support.md`.

## Known limits

- Live model adapters are deferred.
- The score plane uses fixture scores and a fixture judge; it does not call a live eval service.

## Next feature queue

- Add a live replay adapter with explicit model API boundaries and no router changes.
- Add a route-diff report that compares two candidate releases across the same batch.
- Add the eval-predictive-validity report from `R-MSR-011`.

- Resolve factory defect: implementation produced no file changes relative to base; refusing to mark a no-op as done
- Resolve factory defect: claude_code review requested patch; inspect defect log
- Resolve factory defect: missing PRODUCT_BRIEF.md,SYSTEM_MAP.md
- Resolve factory defect: missing reports/*.jsonl
- Resolve factory defect: PRODUCT_BRIEF.md is required for active repos
- Resolve factory defect: SYSTEM_MAP.md is required for active repos
- Resolve factory defect: expected file 'PRODUCT_BRIEF.md' is missing
- Resolve factory defect: expected file 'SYSTEM_MAP.md' is missing
- Resolve factory defect: expected file 'modelswap_replay/cli.py' is missing
- Resolve factory defect: expected glob 'reports/*.jsonl' matched no files
- Resolve factory defect: module 'cli' declares source 'modelswap_replay/cli.py', but it is missing
- Resolve factory defect: module 'model' declares source 'modelswap_replay/model.py', but it is missing
- Resolve factory defect: module 'report' declares source 'modelswap_replay/scoring.py', but it is missing
- Resolve factory defect: claude_code review requested patch; inspect defect log
