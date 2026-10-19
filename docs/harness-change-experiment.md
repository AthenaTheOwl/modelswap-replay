# Compare the harness as part of the release

Changing only the model label misses several ways a route changes behavior: tool
definitions, retrieval, context compaction, effort settings and reviewer prompts.
Treat a harness change as a candidate configuration with its own replay record.
Keep the incumbent record intact and state exactly which inputs changed.

This repository already has useful pieces for the experiment: route fixtures,
recorded responses, effort curves, written verdicts, revert thresholds and signed
digests on result cards. The recorded effort responses are synthetic variants,
so the bundled curve demonstrates selection mechanics. It does not measure a
provider's current quality, latency or price.

For one real route, freeze task IDs and source snapshots before comparing. Run
the incumbent and candidate on the same cases. Record the full model identifier,
effort, prompt digest, tool schema digest, retrieval settings, environment limits,
attempt budget and raw result refs in an external experiment manifest. The current
decision schema does not enforce all of these fields; keep the manifest alongside
the record rather than adding undocumented keys to a validated file.

Review which individual tasks changed outcome. An unchanged average can hide a
newly failing customer path. Count retries, reviewer corrections and elapsed time
when estimating cost per accepted task. Re-run a judge on a fixed human-labeled
subset before attributing a small difference to the candidate; `judge-kappa` can
check the saved labels without making model calls.

Set the adoption and revert criteria before inspecting the candidate. AIP's
[model-comparison workflow](https://github.com/3orionkings/ai-product-team/blob/main/workflows/compare-models.md)
can organize that review. The local runner remains the execution evidence. An
author's summary, a second agent's agreement and a result-card digest each answer
a different question; none alone establishes that the measured conditions match
the proposed deployment.

The smallest useful pilot is one route and one changed harness component. Keep
other settings fixed, inspect every changed task, and hold the release when an
important failure lacks an explanation. Scaling to many specialist roles should
follow evidence that the first comparison changed a decision.
