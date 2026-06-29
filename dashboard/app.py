"""Executive Streamlit dashboard for responsible industrial AI quality risk."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
SAMPLE_DIR = ROOT / "data" / "sample"


st.set_page_config(
    page_title="Responsible Industrial AI | Manufacturing Quality",
    layout="wide",
)


CSS = """
<style>
:root {
  --bosch-red: #e20015;
  --black: #111111;
  --dark-gray: #2d2f33;
  --light-gray: #f3f4f6;
  --steel: #607987;
}
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
.small-note { color: #5c6670; font-size: 0.92rem; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


def synthetic_outputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(42)
    n = 1200
    scores = np.clip(rng.beta(1.4, 14, n), 0, 0.98)
    bands = pd.cut(
        scores,
        bins=[0, 0.10, 0.30, 0.60, 1.01],
        labels=["Low risk: pass", "Medium risk: monitor", "High risk: inspect", "Critical risk: escalate"],
        include_lowest=True,
    )
    scored = pd.DataFrame({"Id": np.arange(1, n + 1), "risk_score": scores, "risk_band": bands})
    metrics = pd.DataFrame(
        [
            {
                "model_version": "v0.1-governed-prototype",
                "roc_auc": 0.71,
                "pr_auc": 0.13,
                "precision": 0.18,
                "recall": 0.76,
                "f1": 0.29,
                "false_negative_rate": 0.24,
                "decision_threshold": 0.18,
                "data_quality_score": 86.0,
            }
        ]
    )
    importance = pd.DataFrame(
        {"feature": [f"L{i % 4}_S{i}_F{i * 3}" for i in range(1, 16)], "importance": np.linspace(0.18, 0.02, 15)}
    )
    monitoring = pd.DataFrame(
        {
            "metric": ["Data quality score", "Missing rate", "Prediction PSI", "Retraining trigger"],
            "baseline": [91.2, 0.088, 0.0, 0],
            "current": [83.4, 0.168, 0.18, 0],
            "alert_level": ["Amber", "Amber", "Amber", "Green"],
        }
    )
    return scored, metrics, importance, monitoring


@st.cache_data
def load_outputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    try:
        scored = pd.read_csv(SAMPLE_DIR / "scored_components_sample.csv")
        metrics = pd.read_csv(SAMPLE_DIR / "model_metrics.csv")
        importance = pd.read_csv(SAMPLE_DIR / "feature_importance.csv")
        monitoring = pd.read_csv(SAMPLE_DIR / "monitoring_snapshot.csv")
        return scored, metrics, importance, monitoring
    except Exception:
        return synthetic_outputs()


scored, metrics, importance, monitoring = load_outputs()
metric = metrics.iloc[0]


st.title("Responsible Industrial AI for Manufacturing Quality")
st.caption("Predictive quality, governed risk scoring, and executive decision intelligence")

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
st.sidebar.markdown(f"**{metric.get('model_version', 'v0.1')}**")
st.sidebar.write("Decision threshold")
st.sidebar.markdown(f"**{metric.get('decision_threshold', 0.18):.2f}**")


def risk_band_counts() -> pd.DataFrame:
    order = ["Low risk: pass", "Medium risk: monitor", "High risk: inspect", "Critical risk: escalate"]
    counts = scored["risk_band"].value_counts().reindex(order, fill_value=0).reset_index()
    counts.columns = ["risk_band", "components"]
    return counts


if page == "Executive Overview":
    high_risk = scored[scored["risk_band"].isin(["High risk: inspect", "Critical risk: escalate"])]
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Predicted Defect Risk", f"{scored['risk_score'].mean():.1%}")
    c2.metric("High-Risk Components", f"{len(high_risk):,}")
    c3.metric("Recall", f"{metric.get('recall', 0.76):.0%}")
    c4.metric("False Negative Risk", f"{metric.get('false_negative_rate', 0.24):.0%}")
    c5.metric("Data Quality Score", f"{metric.get('data_quality_score', 86.0):.0f}/100")

    st.markdown('<div class="status-band"><b>Operational risk level:</b> Amber. Suitable for controlled pilot with human review, not autonomous production release.</div>', unsafe_allow_html=True)
    left, right = st.columns([1.1, 0.9])
    with left:
        fig = px.histogram(scored, x="risk_score", nbins=40, color_discrete_sequence=["#e20015"])
        fig.update_layout(title="Risk Score Distribution", xaxis_title="Risk score", yaxis_title="Components", template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)
    with right:
        fig = px.bar(risk_band_counts(), x="risk_band", y="components", color="risk_band", color_discrete_sequence=["#607987", "#9aa6ad", "#e20015", "#111111"])
        fig.update_layout(title="Decision Bands", xaxis_title="", yaxis_title="Components", showlegend=False, template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

elif page == "Production Risk Intelligence":
    st.subheader("Production Risk Intelligence")
    left, right = st.columns([1, 1])
    with left:
        st.dataframe(
            scored.sort_values("risk_score", ascending=False).head(25),
            use_container_width=True,
            hide_index=True,
        )
    with right:
        fig = px.bar(importance.head(12), x="importance", y="feature", orientation="h", color_discrete_sequence=["#e20015"])
        fig.update_layout(title="Top Risk Drivers", xaxis_title="Relative importance", yaxis_title="", template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)
    st.markdown(
        "**Decision logic:** low-risk components continue normal flow; medium-risk components are monitored; high-risk components route to inspection; critical-risk components escalate to quality leadership."
    )

elif page == "AI Governance & Monitoring":
    st.subheader("AI Governance & Monitoring")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("ROC-AUC", f"{metric.get('roc_auc', 0.71):.2f}")
    c2.metric("PR-AUC", f"{metric.get('pr_auc', 0.13):.2f}")
    c3.metric("Precision", f"{metric.get('precision', 0.18):.0%}")
    c4.metric("F1", f"{metric.get('f1', 0.29):.2f}")
    st.dataframe(monitoring, use_container_width=True, hide_index=True)
    st.markdown(
        '<div class="status-band"><b>Governance status:</b> Controlled prototype. Deployment requires station mapping, model approval, monitoring baseline, and human-in-the-loop workflow sign-off.</div>',
        unsafe_allow_html=True,
    )

elif page == "Strategic Recommendation":
    st.subheader("Strategic Recommendation")
    st.markdown(
        """
**Recommendation:** advance to a 90-day governed pilot focused on inspection prioritization, not autonomous production control.

**90-day roadmap**

1. Weeks 1-3: confirm data lineage, station mapping, target definition, and quality-owner sign-off.
2. Weeks 4-6: build production-grade feature pipelines, validation gates, and model registry workflow.
3. Weeks 7-9: run shadow scoring against live or recent production history.
4. Weeks 10-12: review false-negative risk, inspection capacity, explainability, and operating policy.

**Primary deployment risks**

- Rare failures make false negatives the central risk.
- Anonymized features must be mapped to real stations before actioning explanations.
- Data drift can occur after process or equipment changes.
- Human review is required for high and critical risk decisions.
"""
    )
