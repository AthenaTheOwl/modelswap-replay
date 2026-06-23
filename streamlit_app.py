from __future__ import annotations

from pathlib import Path

import streamlit as st
import yaml

APP_DIR = Path(__file__).resolve().parent
DECISION_PATH = APP_DIR / "decisions" / "model-swap" / "fixture-candidate-v1-customer-support.md"


def load_front_matter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    _, front, _body = text.split("---", 2)
    data = yaml.safe_load(front)
    return data if isinstance(data, dict) else {}


st.title("modelswap replay")
st.caption(
    "offline release gate for llm model swaps: replay recent route traffic "
    "against a candidate release, score it, and read the decision record."
)

if not DECISION_PATH.exists():
    st.warning(
        "decision record not found at "
        f"{DECISION_PATH.relative_to(APP_DIR)}. run a replay pass to write one."
    )
    st.stop()

record = load_front_matter(DECISION_PATH)
if not record:
    st.warning("decision record has no readable front matter.")
    st.stop()

verdict = str(record.get("verdict", "?"))
route = str(record.get("route", "?"))
candidate = str(record.get("candidate", record.get("release_id", "?")))
incumbent = str(record.get("incumbent", "?"))
window = record.get("sample_window", {}) or {}
deltas = record.get("deltas", {}) or {}
judge = record.get("judge", {}) or {}

quality = float(deltas.get("quality", 0.0))
cost_ratio = float(deltas.get("cost_ratio", 0.0))
latency = int(deltas.get("latency_p95_ms", 0))
win_rate = float(judge.get("candidate_win_rate", 0.0))

col1, col2, col3 = st.columns(3)
col1.metric("verdict", verdict)
col2.metric("quality delta", f"{quality:+.3f}")
col3.metric("judge win-rate", f"{win_rate:.0%}")

col4, col5, col6 = st.columns(3)
col4.metric("cost ratio", f"{cost_ratio:+.3f}")
col5.metric("latency p95 (ms)", f"{latency:+d}")
col6.metric("sampled requests", window.get("request_count", "?"))

best = record.get("best_traces", []) or []
worst = record.get("worst_traces", []) or []
traces = []
for trace in best + worst:
    traces.append(
        {
            "trace": trace.get("trace_id", "?"),
            "quality_delta": float(trace.get("quality_delta", 0.0)),
            "cost_delta_usd": float(trace.get("cost_delta_usd", 0.0)),
            "latency_delta_ms": int(trace.get("latency_delta_ms", 0)),
        }
    )
traces.sort(key=lambda t: t["quality_delta"], reverse=True)

st.subheader("traces ranked by quality delta")
only_regressions = st.checkbox("show only quality regressions (delta < 0)", value=False)
rows = [t for t in traces if t["quality_delta"] < 0] if only_regressions else traces
if rows:
    st.dataframe(rows, use_container_width=True, hide_index=True)
else:
    st.info("no traces match the current filter.")

if verdict == "swap":
    headline = (
        f"swap: {candidate} beats {incumbent} on {route} "
        f"(quality {quality:+.3f}, judge win-rate {win_rate:.0%})."
    )
elif verdict == "revert":
    headline = f"revert: {candidate} regressed past the revert threshold on {route}."
else:
    headline = f"{verdict}: {candidate} on {route}."
st.info(headline)

# ---------------------------------------------------------------------------
# interactive: drive the real release gate
# ---------------------------------------------------------------------------
# the section above reads a committed decision record. the section below calls
# the repo's actual gate engine — src.decide.verdict.choose_verdict — on inputs
# you set yourself. change a delta or a threshold and the verdict recomputes
# live (swap / hold / route-split-at-25% / defer), with the same rationale the
# cli writes into a decision record.

from src.decide.verdict import choose_verdict
from src.models.route_registry import RevertThreshold
from src.score.eval_runner import ScoreSummary

st.divider()
st.header("gate a candidate yourself")
st.caption(
    "set the replay deltas and the route's revert thresholds, then run the real "
    "verdict engine (`choose_verdict`) live. starts pre-filled with the committed "
    "customer-support pass — drop quality below the threshold or win-rate below "
    "0.5 and watch it flip to hold."
)

th_record = record.get("revert_threshold", {}) or {}

st.subheader("replay deltas (candidate vs incumbent)")
ic1, ic2 = st.columns(2)
with ic1:
    in_sample_count = st.number_input(
        "sampled requests", min_value=0, max_value=100000,
        value=int(window.get("request_count", 6)), step=1,
    )
    in_quality = st.slider(
        "quality delta", min_value=-0.50, max_value=0.50,
        value=float(quality), step=0.001, format="%.3f",
    )
    in_win_rate = st.slider(
        "judge candidate win-rate", min_value=0.0, max_value=1.0,
        value=float(win_rate), step=0.01,
    )
with ic2:
    in_cost_ratio = st.slider(
        "cost delta ratio", min_value=-1.0, max_value=2.0,
        value=float(cost_ratio), step=0.005, format="%.3f",
    )
    in_latency = st.slider(
        "latency p95 delta (ms)", min_value=-1000, max_value=2000,
        value=int(latency), step=5,
    )

st.subheader("revert thresholds (from the route registry)")
tc1, tc2, tc3 = st.columns(3)
with tc1:
    th_quality = st.number_input(
        "max quality drop", min_value=0.0, max_value=1.0,
        value=float(th_record.get("quality_drop_max", 0.03)), step=0.005, format="%.3f",
    )
with tc2:
    th_cost = st.number_input(
        "max cost increase ratio", min_value=0.0, max_value=2.0,
        value=float(th_record.get("cost_increase_max", 0.20)), step=0.01, format="%.2f",
    )
with tc3:
    th_latency = st.number_input(
        "max latency p95 regression (ms)", min_value=0, max_value=5000,
        value=int(th_record.get("latency_p95_regression_ms_max", 250)), step=10,
    )

# build the same typed inputs the cli builds, then call the real engine.
live_summary = ScoreSummary(
    sample_count=int(in_sample_count),
    quality_delta=round(float(in_quality), 3),
    cost_delta_usd=0.0,
    cost_delta_ratio=round(float(in_cost_ratio), 3),
    latency_p95_delta_ms=int(in_latency),
    dimension_deltas={},
    trace_scores=[],
    judge_candidate_win_rate=float(in_win_rate),
)
live_threshold = RevertThreshold(
    quality_drop_max=float(th_quality),
    cost_increase_max=float(th_cost),
    latency_p95_regression_ms_max=int(th_latency),
)
result = choose_verdict(live_summary, live_threshold)

st.subheader("live verdict")
verdict_label = {
    "swap": "swap — ship the candidate",
    "hold": "hold — do not swap",
    "route-split-at-25%": "route-split-at-25% — canary, don't full-swap",
    "defer": "defer — not enough signal",
}.get(result.verdict, result.verdict)

if result.verdict == "swap":
    st.success(verdict_label)
elif result.verdict in ("hold", "defer"):
    st.error(verdict_label)
else:
    st.warning(verdict_label)

st.markdown("**rationale (from the engine):**")
for line in result.rationale:
    st.markdown(f"- {line}")

st.caption(
    "this is the same `VerdictResult` the cli serializes into a decision record — "
    "no lookup, the gate logic ran on your inputs."
)
