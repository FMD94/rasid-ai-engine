import streamlit as st
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
from src.rasid.database import load_analysis_df, load_reviews_df, save_review_to_db

LOG_FILE = Path("logs/analysis_log.jsonl")
REVIEW_FILE = Path("logs/moderator_reviews.jsonl")

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "rasid123"

st.set_page_config(
    page_title="RASID Dashboard",
    page_icon="🛡️",
    layout="wide"
)

st.markdown("""
<style>

/* Main App */
.stApp {
    background: #07131f;
    color: #eaf2f8;
    font-family: 'Segoe UI', sans-serif;
}

.block-container {
    padding-top: 2rem;
    padding-left: 3rem;
    padding-right: 3rem;
}

/* Header */
.rasid-header {
    background: linear-gradient(135deg, #0a1a2a, #14283b);
    padding: 32px;
    border-radius: 24px;
    margin-bottom: 30px;
    border: 1px solid #24384d;
    box-shadow: 0 16px 40px rgba(0, 0, 0, 0.25);
}

.rasid-title {
    color: #ffffff;
    font-size: 36px;
    font-weight: 800;
}

.rasid-subtitle {
    color: #9fb0bd;
    font-size: 15px;
}

/* Cards */
.card {
    background: #101c29;
    border-radius: 22px;
    padding: 24px;
    margin-bottom: 20px;
    border: 1px solid #24384d;
    box-shadow: 0 10px 28px rgba(0,0,0,0.22);
}

/* Metrics */
.metric-title {
    color: #9fb0bd;
    font-size: 14px;
    font-weight: 600;
}

.metric-value {
    font-size: 34px;
    font-weight: 800;
    color: #ffffff;
}

/* Status Colors */
.safe {
    color: #5ee0a0;
}

.manipulative {
    color: #e0b85a;
}

.fraud {
    color: #ff6b6b;
}

/* Badges */
.badge-safe {
    background: rgba(94, 224, 160, 0.14);
    color: #5ee0a0;
    padding: 8px 16px;
    border-radius: 999px;
    font-weight: 700;
    border: 1px solid rgba(94, 224, 160, 0.35);
}

.badge-manipulative {
    background: rgba(224, 184, 90, 0.16);
    color: #e0b85a;
    padding: 8px 16px;
    border-radius: 999px;
    font-weight: 700;
    border: 1px solid rgba(224, 184, 90, 0.35);
}

.badge-fraud {
    background: rgba(255, 107, 107, 0.14);
    color: #ff6b6b;
    padding: 8px 16px;
    border-radius: 999px;
    font-weight: 700;
    border: 1px solid rgba(255, 107, 107, 0.35);
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 10px;
    margin-bottom: 20px;
}

.stTabs [data-baseweb="tab"] {
    background: #101c29;
    color: #9fb0bd;
    border-radius: 14px;
    padding: 11px 18px;
    border: 1px solid #24384d;
    font-weight: 700;
}

.stTabs [aria-selected="true"] {
    background: #e0b85a !important;
    color: #07131f !important;
    border: 1px solid #e0b85a !important;
}

/* Buttons */
.stButton > button {
    background: #e0b85a;
    color: #07131f;
    border-radius: 14px;
    border: none;
    padding: 10px 20px;
    font-weight: 800;
}

.stButton > button:hover {
    background: #f0c96a;
    color: #07131f;
}

/* Selectbox */
.stSelectbox div[data-baseweb="select"] {
    background: #101c29 !important;
    color: #eaf2f8 !important;
    border-radius: 14px !important;
    border: 1px solid #24384d !important;
}

.stSelectbox * {
    color: #eaf2f8 !important;
}

/* Text inputs and textarea */
.stTextInput input,
.stTextArea textarea {
    background: #101c29 !important;
    color: #eaf2f8 !important;
    border-radius: 14px !important;
    border: 1px solid #24384d !important;
}

.stTextArea textarea::placeholder {
    color: #7f91a3 !important;
}

/* Radio buttons */
.stRadio label {
    color: #eaf2f8 !important;
    font-weight: 600;
}

/* Tables */
[data-testid="stDataFrame"] {
    border-radius: 18px;
    overflow: hidden;
    border: 1px solid #24384d;
}

/* Charts */
[data-testid="stVegaLiteChart"] {
    background: #101c29;
    border-radius: 18px;
    padding: 12px;
    border: 1px solid #24384d;
}

/* General text readability */
p, li, label, div {
    line-height: 1.65;
}

h1, h2, h3, h4 {
    color: #ffffff;
}

/* Alerts */
.stAlert {
    border-radius: 16px;
    background: #162536;
    color: #eaf2f8;
}

/* Login Box */
.login-box {
    max-width: 440px;
    margin: 90px auto;
    background: #101c29;
    padding: 38px;
    border-radius: 28px;
    border: 1px solid #24384d;
    box-shadow: 0 16px 40px rgba(0,0,0,0.28);
}

/* Small white empty cards fix */
div[data-testid="stHorizontalBlock"] > div {
    background: transparent;
}

/* Expander/dropdown readability */
[data-baseweb="popover"] {
    background: #101c29 !important;
    color: #eaf2f8 !important;
}

</style>
""", unsafe_allow_html=True)


def login_page():
    st.markdown("""
    <div class="login-box">
        <h1 style="text-align:center;">🛡️ RASID</h1>
        <p style="text-align:center; color:#6b7280;">
            Admin access for moderation and system supervision
        </p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_button = st.form_submit_button("Login")

        if login_button:
            if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                st.session_state["logged_in"] = True
                st.rerun()
            else:
                st.error("Invalid username or password.")


def load_jsonl(path):
    if not path.exists():
        return pd.DataFrame()

    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))

    return pd.DataFrame(rows)


def save_review(entry):
    REVIEW_FILE.parent.mkdir(exist_ok=True)
    with open(REVIEW_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def decision_badge(decision):
    if decision == "Safe":
        return '<span class="badge-safe">Safe</span>'
    if decision == "Manipulative":
        return '<span class="badge-manipulative">Manipulative</span>'
    if decision == "Fraud":
        return '<span class="badge-fraud">Fraud</span>'
    return decision


if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    login_page()
    st.stop()


df = load_analysis_df()

label_map = {
    "approved": "Safe",
    "flagged": "Manipulative",
    "blocked": "Fraud"
}

st.markdown("""
<div class="rasid-header">
    <div class="rasid-title">🛡️ RASID Dashboard</div>
    <div class="rasid-subtitle">
        AI Context-Aware Online Safety Engine for multilingual advertisement monitoring
    </div>
</div>
""", unsafe_allow_html=True)

top_col1, top_col2 = st.columns([6, 1])
with top_col2:
    if st.button("Logout"):
        st.session_state["logged_in"] = False
        st.rerun()

if df.empty:
    st.warning("No RASID logs found yet. Run the extension or API first.")
    st.stop()

df["decision_label"] = df["decision"].map(label_map).fillna(df["decision"])
df["confidence"] = pd.to_numeric(df["confidence"], errors="coerce").fillna(0)

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Overview",
    "👤 Moderator Review",
    "🌍 Region Policy Check",
    "🗂 Logs"
])


with tab1:
    total_scans = len(df)
    safe_count = (df["decision"] == "approved").sum()
    misleading_count = (df["decision"] == "flagged").sum()
    fraud_count = (df["decision"] == "blocked").sum()
    avg_confidence = round(df["confidence"].mean(), 2)

    col1, col2, col3, col4 = st.columns(4)

    metrics = [
        ("Total Scans", total_scans, ""),
        ("Safe", safe_count, "safe"),
        ("Manipulative", misleading_count, "manipulative"),
        ("Fraud", fraud_count, "fraud")
    ]

    for col, (title, value, cls) in zip([col1, col2, col3, col4], metrics):
        with col:
            st.markdown(f"""
            <div class="card">
                <div class="metric-title">{title}</div>
                <div class="metric-value {cls}">{value}</div>
            </div>
            """, unsafe_allow_html=True)

    left, right = st.columns([2, 1])

    with left:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Risk Distribution")
        st.bar_chart(df["decision_label"].value_counts())
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Input Type Distribution")
        st.bar_chart(df["input_type"].value_counts())
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        latest = df.iloc[-1]
        latest_decision = latest.get("decision_label", "Unknown")

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Latest Analysis")

        st.markdown(decision_badge(latest_decision), unsafe_allow_html=True)
        st.write("")
        st.write("**Confidence:**", latest.get("confidence", 0))
        st.write("**Language:**", latest.get("language", "unknown"))
        st.write("**Input Type:**", latest.get("input_type", "unknown"))
        st.write("**Source:**", latest.get("source", "unknown"))

        st.markdown("#### Explanation")
        reasons = latest.get("reasons", [])
        if isinstance(reasons, list):
            for reason in reasons:
                st.write(f"• {reason}")
        else:
            st.write(reasons)

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("System Status")
        st.success("RASID Engine Online")
        st.write(f"Average confidence: **{avg_confidence}**")
        st.markdown('</div>', unsafe_allow_html=True)


with tab2:
    st.subheader("Human-in-the-Loop Moderator Review")

    review_index = st.selectbox(
        "Select scan to review",
        options=list(range(len(df))),
        format_func=lambda i: f"{df.iloc[i].get('timestamp', 'No time')} | {df.iloc[i].get('decision_label', 'Unknown')} | {df.iloc[i].get('input_type', 'unknown')}"
    )

    selected = df.iloc[review_index]

    col_a, col_b = st.columns([1.1, 1])

    with col_a:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.write("### AI Analysis")

        st.markdown(decision_badge(selected.get("decision_label", "Unknown")), unsafe_allow_html=True)
        st.write("")
        st.write("**Confidence:**", selected.get("confidence", 0))
        st.write("**Language:**", selected.get("language", "unknown"))
        st.write("**Input Type:**", selected.get("input_type", "unknown"))
        st.write("**Timestamp:**", selected.get("timestamp", "unknown"))

        st.write("### Reasons")
        reasons = selected.get("reasons", [])
        if isinstance(reasons, list):
            for reason in reasons:
                st.write(f"• {reason}")
        else:
            st.write(reasons)

        st.markdown('</div>', unsafe_allow_html=True)

    with col_b:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.write("### Moderator Decision")

        moderator_decision = st.radio(
            "Final Decision",
            ["Accept AI Decision", "Safe", "Manipulative", "Fraud"],
            horizontal=False
        )

        reviewer_note = st.text_area(
            "Moderator Note",
            placeholder="Explain why you accepted or changed the AI decision..."
        )

        if st.button("Save Moderator Review"):
            final_decision = selected.get("decision_label", "Unknown")

            if moderator_decision != "Accept AI Decision":
                final_decision = moderator_decision

            review_entry = {
                "review_timestamp": datetime.now().isoformat(timespec="seconds"),
                "original_timestamp": selected.get("timestamp", ""),
                "ai_decision": selected.get("decision_label", "Unknown"),
                "final_decision": final_decision,
                "language": selected.get("language", "unknown"),
                "input_type": selected.get("input_type", "unknown"),
                "confidence": float(selected.get("confidence", 0)),
                "note": reviewer_note
            }

            save_review_to_db(review_entry)
            st.success("Review saved successfully.")

        st.markdown('</div>', unsafe_allow_html=True)


with tab3:
    st.subheader("Region Policy Check")

    col1, col2, col3 = st.columns(3)

    with col1:
        region = st.selectbox(
            "Region",
            ["Saudi Arabia", "GCC", "European Union", "United States", "General"]
        )

    with col2:
        policy_area = st.selectbox(
            "Policy Area",
            ["General", "Finance", "Health", "Education", "Retail", "Technology"]
        )

    with col3:
        current_decision = st.selectbox(
            "RASID Decision",
            ["Safe", "Manipulative", "Fraud"]
        )

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.write("### Policy Interpretation")

    policy_warning = "No additional policy warning detected."

    if policy_area == "Finance" and current_decision in ["Misleading", "Fraud"]:
        policy_warning = "Financial advertisements require human review when they contain profit guarantees, fixed income claims, or risk-free investment language."

    elif policy_area == "Health" and current_decision in ["Misleading", "Fraud"]:
        policy_warning = "Health advertisements require strict review when they contain cure claims, guaranteed results, or medical treatment promises."

    elif region == "Saudi Arabia" and policy_area in ["Finance", "Health"]:
        policy_warning = "Regional policy check recommends moderator review for sensitive finance or health advertisement claims."

    elif current_decision == "Fraud":
        policy_warning = "High-risk content should be escalated for human moderation."

    elif current_decision == "Manipulative":
        policy_warning = "Potentially misleading content should be reviewed before approval."

    st.warning(policy_warning)
    st.write("**Selected Region:**", region)
    st.write("**Policy Area:**", policy_area)
    st.write("**Decision:**", current_decision)
    st.markdown('</div>', unsafe_allow_html=True)


with tab4:
    st.subheader("System Logs")

    display_df = df.tail(50)[[
        "timestamp",
        "source",
        "input_type",
        "decision_label",
        "language",
        "confidence",
        "reasons"
    ]].rename(columns={
        "timestamp": "Time",
        "source": "Source",
        "input_type": "Input Type",
        "decision_label": "Decision",
        "language": "Language",
        "confidence": "Confidence",
        "reasons": "Reasons"
    })

    st.dataframe(display_df, use_container_width=True)

    reviews_df = load_reviews_df()

    st.subheader("Moderator Review History")
    if reviews_df.empty:
        st.info("No moderator reviews saved yet.")
    else:
        st.dataframe(reviews_df.tail(30), use_container_width=True)