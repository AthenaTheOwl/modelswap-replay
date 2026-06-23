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
