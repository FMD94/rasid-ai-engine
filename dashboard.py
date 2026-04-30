import streamlit as st
import pandas as pd
import json
from pathlib import Path

LOG_FILE = Path("logs/analysis_log.jsonl")

st.set_page_config(
    page_title="RASID Dashboard",
    page_icon="🛡️",
    layout="wide"
)

st.markdown("""
<style>
body {
    background-color: #f6f8fb;
}

.main {
    background-color: #f6f8fb;
}

.rasid-title {
    font-size: 32px;
    font-weight: 800;
    margin-bottom: 20px;
}

.card {
    background: white;
    padding: 22px;
    border-radius: 22px;
    box-shadow: 0 8px 28px rgba(0,0,0,0.06);
    margin-bottom: 18px;
}

.metric-title {
    color: #6b7280;
    font-size: 14px;
}

.metric-value {
    font-size: 30px;
    font-weight: 800;
    margin-top: 6px;
}

.safe {
    color: #16a34a;
    font-weight: 700;
}

.misleading {
    color: #f59e0b;
    font-weight: 700;
}

.fraud {
    color: #dc2626;
    font-weight: 700;
}

.risk-box {
    background: #fee2e2;
    border-radius: 20px;
    padding: 22px;
}

.sidebar-box {
    background: white;
    padding: 20px;
    border-radius: 22px;
    box-shadow: 0 8px 28px rgba(0,0,0,0.05);
}
</style>
""", unsafe_allow_html=True)


def load_logs():
    if not LOG_FILE.exists():
        return pd.DataFrame()

    rows = []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))

    return pd.DataFrame(rows)


df = load_logs()

label_map = {
    "approved": "Safe",
    "flagged": "Misleading",
    "blocked": "Fraud"
}

if df.empty:
    st.warning("No RASID logs found yet. Run the extension or API first.")
    st.stop()

df["decision_label"] = df["decision"].map(label_map).fillna(df["decision"])
df["confidence"] = pd.to_numeric(df["confidence"], errors="coerce").fillna(0)

total_scans = len(df)
misleading_count = (df["decision"] == "flagged").sum()
fraud_count = (df["decision"] == "blocked").sum()
safe_count = (df["decision"] == "approved").sum()
avg_confidence = round(df["confidence"].mean(), 2)

# Header
st.markdown('<div class="rasid-title">🛡️ RASID Dashboard</div>', unsafe_allow_html=True)

# Metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="card">
        <div class="metric-title">Ads Reviewed</div>
        <div class="metric-value">{total_scans}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="card">
        <div class="metric-title">Misleading</div>
        <div class="metric-value misleading">{misleading_count}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="card">
        <div class="metric-title">Fraud</div>
        <div class="metric-value fraud">{fraud_count}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="card">
        <div class="metric-title">Average Confidence</div>
        <div class="metric-value">{avg_confidence}</div>
    </div>
    """, unsafe_allow_html=True)

# Layout
left, right = st.columns([2.2, 1])

with left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Risk Distribution")
    st.bar_chart(df["decision_label"].value_counts())
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Language Distribution")
    st.bar_chart(df["language"].value_counts())
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Recent Scans")

    display_df = df.tail(10)[[
        "timestamp",
        "input_type",
        "decision_label",
        "language",
        "confidence",
        "source"
    ]].rename(columns={
        "timestamp": "Time",
        "input_type": "Input Type",
        "decision_label": "Decision",
        "language": "Language",
        "confidence": "Confidence",
        "source": "Source"
    })

    st.dataframe(display_df, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with right:
    latest = df.iloc[-1]

    latest_decision = latest.get("decision", "unknown")
    latest_label = label_map.get(latest_decision, latest_decision)
    latest_conf = latest.get("confidence", 0)
    latest_lang = latest.get("language", "unknown")
    latest_type = latest.get("input_type", "unknown")
    latest_reasons = latest.get("reasons", [])

    risk_class = "safe"
    if latest_decision == "flagged":
        risk_class = "misleading"
    elif latest_decision == "blocked":
        risk_class = "fraud"

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Latest Analysis")

    st.markdown(f"""
    <div class="risk-box">
        <h3 class="{risk_class}">{latest_label}</h3>
        <p><b>Confidence:</b> {latest_conf}</p>
        <p><b>Language:</b> {latest_lang}</p>
        <p><b>Input Type:</b> {latest_type}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### XAI Explanation")
    if isinstance(latest_reasons, list):
        for reason in latest_reasons:
            st.write(f"• {reason}")
    else:
        st.write(latest_reasons)

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("System Status")
    st.success("System Online")
    st.write("All systems operational.")
    st.markdown('</div>', unsafe_allow_html=True)