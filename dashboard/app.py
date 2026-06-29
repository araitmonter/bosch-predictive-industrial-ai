"""Streamlit dashboard for Bosch predictive quality outputs."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS_DIR = ROOT / "artifacts"
SAMPLE_DIR = ROOT / "data" / "sample"


st.set_page_config(
    page_title="Bosch Predictive Quality",
    layout="wide",
)


CSS = """
<style>
.main { background: #ffffff; color: #111111; }
h1, h2, h3 { color: #111111; letter-spacing: 0; }
div[data-testid="stMetric"] {
  background: #ffffff;
  border: 1px solid #d9dde2;
  border-top: 4px solid #e20015;
  padding: 16px;
  border-radius: 6px;
}
.status-band {
  border-left: 5px solid #e20015;
  background: #f7f8fa;
  padding: 14px 18px;
  border-radius: 4px;
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


def demo_outputs() -> tuple[pd.DataFrame, dict[str, float | str], pd.DataFrame, pd.DataFrame, bool]:
    rng = np.random.default_rng(42)
    scores = np.clip(rng.beta(1.4, 14, 1200), 0, 0.98)
    bands = pd.cut(
        scores,
        bins=[0, 0.10, 0.30, 0.60, 1.01],
        labels=[
            "Low risk: pass",
            "Medium risk: monitor",
            "High risk: inspect",
            "Critical risk: escalate",
        ],
        include_lowest=True,
    )
    scored = pd.DataFrame(
        {
            "Id": np.arange(1, len(scores) + 1),
            "risk_score": scores,
            "risk_band": bands,
            "is_actionable": scores >= 0.18,
        },
    )
    metrics = {
        "model_version": "demo",
        "roc_auc": 0.0,
        "pr_auc": 0.0,
        "precision": 0.0,
        "recall": 0.0,
        "f1": 0.0,
        "false_negative_rate": 0.0,
        "decision_threshold": 0.18,
        "data_quality_score": 0.0,
    }
    importance = pd.DataFrame(
        {
            "feature": [f"L{i % 4}_S{i}_F{i * 3}" for i in range(1, 16)],
            "importance": np.linspace(0.18, 0.02, 15),
        },
    )
    monitoring = pd.DataFrame(
        {
            "metric": ["Prediction PSI", "Missing rate delta", "Feature alerts"],
            "current": [0.0, 0.0, 0],
            "alert_level": ["Demo", "Demo", "Demo"],
        },
    )
    return scored, metrics, importance, monitoring, True


@st.cache_data
def load_outputs() -> tuple[pd.DataFrame, dict[str, float | str], pd.DataFrame, pd.DataFrame, bool]:
    try:
        scored = pd.read_csv(SAMPLE_DIR / "scored_components_sample.csv")
        metrics = json.loads((ARTIFACTS_DIR / "metrics.json").read_text(encoding="utf-8"))
        metadata = json.loads((ARTIFACTS_DIR / "model_metadata.json").read_text(encoding="utf-8"))
        importance = pd.read_csv(ARTIFACTS_DIR / "feature_importance.csv")
        monitoring = load_monitoring_table()
        metrics["model_version"] = metadata.get("model_version", "unknown")
        return scored, metrics, importance, monitoring, False
    except Exception:
        return demo_outputs()


def load_monitoring_table() -> pd.DataFrame:
    snapshot_path = ARTIFACTS_DIR / "monitoring_snapshot.json"
    if not snapshot_path.exists():
        return pd.DataFrame(
            {
                "metric": ["Monitoring"],
                "current": ["Run `make monitor`"],
                "alert_level": ["Not available"],
            },
        )

    snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    prediction = snapshot.get("prediction_drift", {})
    missingness = snapshot.get("missingness_drift", {})
    return pd.DataFrame(
        [
            {
                "metric": "Prediction PSI",
                "current": prediction.get("prediction_psi"),
                "alert_level": prediction.get("alert"),
            },
            {
                "metric": "Missing rate delta",
                "current": missingness.get("missing_rate_delta"),
                "alert_level": missingness.get("alert"),
            },
            {
                "metric": "Feature alerts",
                "current": snapshot.get("feature_alert_count"),
                "alert_level": "red" if snapshot.get("retraining_alert") else "green",
            },
        ],
    )


scored, metrics, importance, monitoring, demo_mode = load_outputs()

st.title("Responsible Industrial AI for Bosch Manufacturing Quality")
st.caption("Predictive quality risk scoring, validation, monitoring, and governance controls")

if demo_mode:
    st.warning(
        "Demo mode: synthetic outputs. Run the training pipeline to generate real model outputs."
    )

page = st.sidebar.radio(
    "Dashboard",
    [
        "Executive Overview",
        "Production Risk Intelligence",
        "AI Governance & Monitoring",
        "Strategic Recommendation",
    ],
)
st.sidebar.markdown("---")
st.sidebar.write("Model version")
st.sidebar.markdown(f"**{metrics.get('model_version', 'unknown')}**")
st.sidebar.write("Decision threshold")
st.sidebar.markdown(f"**{float(metrics.get('decision_threshold', 0.0)):.2f}**")


def risk_band_counts() -> pd.DataFrame:
    order = [
        "Low risk: pass",
        "Medium risk: monitor",
        "High risk: inspect",
        "Critical risk: escalate",
    ]
    counts = scored["risk_band"].value_counts().reindex(order, fill_value=0).reset_index()
    counts.columns = ["risk_band", "components"]
    return counts


if page == "Executive Overview":
    high_risk = scored[scored["risk_band"].isin(["High risk: inspect", "Critical risk: escalate"])]
    actionable = int(scored.get("is_actionable", pd.Series(False, index=scored.index)).sum())

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Mean Risk Score", f"{scored['risk_score'].mean():.1%}")
    c2.metric("Actionable Components", f"{actionable:,}")
    c3.metric("High-Risk Components", f"{len(high_risk):,}")
    c4.metric("Recall", f"{float(metrics.get('recall', 0.0)):.0%}")
    c5.metric("False Negative Rate", f"{float(metrics.get('false_negative_rate', 0.0)):.0%}")

    st.markdown(
        '<div class="status-band"><b>Operating status:</b> prototype outputs. '
        "Use as inspection decision support only.</div>",
        unsafe_allow_html=True,
    )
    left, right = st.columns([1.1, 0.9])
    with left:
        fig = px.histogram(scored, x="risk_score", nbins=40, color_discrete_sequence=["#e20015"])
        fig.update_layout(
            title="Risk Score Distribution",
            xaxis_title="Risk score",
            yaxis_title="Components",
            template="plotly_white",
        )
        st.plotly_chart(fig, use_container_width=True)
    with right:
        fig = px.bar(
            risk_band_counts(),
            x="risk_band",
            y="components",
            color="risk_band",
            color_discrete_sequence=["#607987", "#9aa6ad", "#e20015", "#111111"],
        )
        fig.update_layout(
            title="Decision Bands",
            xaxis_title="",
            yaxis_title="Components",
            showlegend=False,
            template="plotly_white",
        )
        st.plotly_chart(fig, use_container_width=True)

elif page == "Production Risk Intelligence":
    st.subheader("Production Risk Intelligence")
    left, right = st.columns([1, 1])
    with left:
        st.dataframe(
            scored.sort_values("risk_score", ascending=False).head(25), use_container_width=True
        )
    with right:
        fig = px.bar(
            importance.head(12),
            x="importance",
            y="feature",
            orientation="h",
            color_discrete_sequence=["#e20015"],
        )
        fig.update_layout(
            title="Top Model Features",
            xaxis_title="Importance",
            yaxis_title="",
            template="plotly_white",
        )
        st.plotly_chart(fig, use_container_width=True)
    st.markdown(
        "The action flag is based on the trained decision threshold. Risk bands remain a separate "
        "communication layer for quality operations."
    )

elif page == "AI Governance & Monitoring":
    st.subheader("AI Governance & Monitoring")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("ROC-AUC", f"{float(metrics.get('roc_auc', 0.0)):.2f}")
    c2.metric("PR-AUC", f"{float(metrics.get('pr_auc', 0.0)):.2f}")
    c3.metric("Precision", f"{float(metrics.get('precision', 0.0)):.0%}")
    c4.metric("F1", f"{float(metrics.get('f1', 0.0)):.2f}")
    st.dataframe(monitoring, use_container_width=True, hide_index=True)
    st.markdown(
        '<div class="status-band"><b>Validation note:</b> the default holdout is lightweight. '
        "Operational validation should use event-time data and decision-point feature availability.</div>",
        unsafe_allow_html=True,
    )

elif page == "Strategic Recommendation":
    st.subheader("Strategic Recommendation")
    st.markdown(
        """
**Recommendation:** use the prototype for shadow scoring and inspection-prioritization analysis.

**Near-term work**

1. Map influential anonymized features to real stations and tests.
2. Replace ID-based holdout with event-time validation.
3. Add inspection capacity and cost assumptions to threshold selection.
4. Monitor missingness, prediction drift, and false-negative rate as labels arrive.

**Do not use this model for autonomous production control.**
"""
    )
