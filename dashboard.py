import streamlit as st
import pandas as pd
import json
import sqlite3
import plotly.express as px
from pathlib import Path
from datetime import datetime
from src.rasid.database import load_analysis_df, load_reviews_df, save_review_to_db

DB_PATH = Path("logs/rasid.db")
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "rasid123"

st.set_page_config(page_title="RASID Dashboard", page_icon="🛡️", layout="wide")

st.sidebar.markdown("## 🛡️ RASID AI Stack")
st.sidebar.markdown("""
### NLP Models
- AraBERT v2
- BERT-base

### Explainability
- LIME

### Vision
- OCR
- Prototype Deepfake Signal

### Backend
- FastAPI

### Dashboard
- Streamlit

### Database
- SQLite

### Detection Engine
- Hybrid AI + Rules
""")

st.markdown("""
<style>
.stApp { background: #07131f; color: #eaf2f8; font-family: 'Segoe UI', sans-serif; }
.block-container { padding-top: 2rem; padding-left: 3rem; padding-right: 3rem; }
.rasid-header {
    background: linear-gradient(135deg, #0a1a2a, #14283b);
    padding: 32px; border-radius: 24px; margin-bottom: 30px;
    border: 1px solid #24384d; box-shadow: 0 16px 40px rgba(0,0,0,0.25);
}
.rasid-title { color: #ffffff; font-size: 36px; font-weight: 800; }
.rasid-subtitle { color: #9fb0bd; font-size: 15px; }
.card {
    background: #101c29; border-radius: 22px; padding: 24px; margin-bottom: 20px;
    border: 1px solid #24384d; box-shadow: 0 10px 28px rgba(0,0,0,0.22);
}
.metric-title { color: #9fb0bd; font-size: 14px; font-weight: 600; }
.metric-value { font-size: 34px; font-weight: 800; color: #ffffff; }
.safe { color: #5ee0a0; }
.manipulative { color: #e0b85a; }
.fraud { color: #ff6b6b; }
.badge-safe, .badge-manipulative, .badge-fraud {
    padding: 8px 16px; border-radius: 999px; font-weight: 700;
}
.badge-safe {
    background: rgba(94,224,160,0.14); color: #5ee0a0;
    border: 1px solid rgba(94,224,160,0.35);
}
.badge-manipulative {
    background: rgba(224,184,90,0.16); color: #e0b85a;
    border: 1px solid rgba(224,184,90,0.35);
}
.badge-fraud {
    background: rgba(255,107,107,0.14); color: #ff6b6b;
    border: 1px solid rgba(255,107,107,0.35);
}
.stTabs [data-baseweb="tab-list"] { gap: 10px; margin-bottom: 20px; }
.stTabs [data-baseweb="tab"] {
    background: #101c29; color: #9fb0bd; border-radius: 14px;
    padding: 11px 18px; border: 1px solid #24384d; font-weight: 700;
}
.stTabs [aria-selected="true"] {
    background: #e0b85a !important; color: #07131f !important;
    border: 1px solid #e0b85a !important;
}
.stButton > button {
    background: #e0b85a; color: #07131f; border-radius: 14px;
    border: none; padding: 10px 20px; font-weight: 800;
}
.stButton > button:hover { background: #f0c96a; color: #07131f; }
.stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
    background: #101c29 !important; color: #eaf2f8 !important;
    border-radius: 14px !important; border: 1px solid #24384d !important;
}
.stRadio label { color: #eaf2f8 !important; font-weight: 600; }
[data-testid="stDataFrame"] { border-radius: 18px; overflow: hidden; border: 1px solid #24384d; }
p, li, label, div { line-height: 1.65; }
h1, h2, h3, h4 { color: #ffffff; }
.stAlert { border-radius: 16px; }
.login-box {
    max-width: 440px; margin: 90px auto; background: #101c29;
    padding: 38px; border-radius: 28px; border: 1px solid #24384d;
    box-shadow: 0 16px 40px rgba(0,0,0,0.28);
}
</style>
""", unsafe_allow_html=True)


def login_page():
    st.markdown("""
    <div class="login-box">
        <h1 style="text-align:center;">🛡️ RASID</h1>
        <p style="text-align:center; color:#9fb0bd;">
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


def decision_badge(decision):
    if decision == "Safe":
        return '<span class="badge-safe">Safe</span>'
    if decision == "Manipulative":
        return '<span class="badge-manipulative">Manipulative</span>'
    if decision == "Fraud":
        return '<span class="badge-fraud">Fraud</span>'
    return decision


def load_disputes():
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query("SELECT * FROM dispute_requests ORDER BY id DESC", conn)
    except Exception:
        df = pd.DataFrame()
    conn.close()
    return df


def themed_pie(dataframe, names_col, values_col, color_col, color_map):
    fig = px.pie(
        dataframe,
        values=values_col,
        names=names_col,
        hole=0.45,
        color=color_col,
        color_discrete_map=color_map
    )

    fig.update_layout(
        paper_bgcolor="#101c29",
        plot_bgcolor="#101c29",
        font_color="#eaf2f8",
        margin=dict(t=30, b=20, l=20, r=20),
        legend=dict(bgcolor="#101c29", font=dict(color="#eaf2f8"))
    )

    fig.update_traces(
        textfont_color="#eaf2f8",
        marker=dict(line=dict(color="#07131f", width=2))
    )

    return fig


def parse_json_field(value, default=None):
    if default is None:
        default = []

    if isinstance(value, list):
        return value

    if isinstance(value, str):
        try:
            return json.loads(value)
        except Exception:
            return default

    return default


def display_explanation_block(latest):
    st.markdown("#### Explanation")

    deepfake_risk = latest.get("deepfake_risk", "")

    if deepfake_risk == "high":
        st.error("Potential synthetic or manipulated media detected.")
    elif deepfake_risk == "medium":
        st.warning("Moderate visual manipulation risk detected.")
    elif deepfake_risk == "low":
        st.success("No major visual manipulation indicators detected.")

    extension_explanation = latest.get("explanation", "")

    if extension_explanation and str(extension_explanation).strip() not in ["", "None", "nan"]:
        st.write(extension_explanation)
    else:
        reasons = parse_json_field(latest.get("reasons", []), [])

        if isinstance(reasons, list) and reasons:
            for reason in reasons:
                st.write(f"• {reason}")
        else:
            st.info("No general explanation available.")


def display_lime_explanation(latest):
    st.markdown("#### Why RASID Classified This Advertisement")

    lime_data = parse_json_field(latest.get("lime_explanation", []), [])

    suspicious_keywords = [
        "offer", "limited", "exclusive", "guaranteed", "urgent", "free",
        "win", "discount", "buy", "sale", "now", "today", "profit",
        "investment", "reward", "cash", "promo", "click", "register",
        "risk", "money", "income", "detox", "cure",

        "عرض", "حصري", "مجانا", "اربح", "خصم", "اشتر", "تخفيض",
        "الآن", "فوري", "مضمون", "استثمار", "ربح", "سجل", "اضغط",
        "استرداد", "جائزة", "فرصة", "حصريا", "دخل", "أرباح", "علاج"
    ]

    shown = 0

    if lime_data:
        for item in lime_data:
            if not isinstance(item, dict):
                continue

            if "word" not in item or "weight" not in item:
                continue

            word = str(item["word"]).strip().lower()
            weight = float(item["weight"])

            if len(word) <= 2:
                continue

            if abs(weight) < 0.02:
                continue

            if word not in suspicious_keywords:
                continue

            shown += 1

            if weight > 0:
                st.warning(
                    f'This advertisement contains persuasive or manipulative wording such as "{word}".'
                )
            else:
                st.info(
                    f'The term "{word}" slightly reduced the manipulation probability.'
                )

    if shown == 0:
        reasons = parse_json_field(latest.get("reasons", []), [])
        found_reason = False

        if isinstance(reasons, list):
            for reason in reasons:
                lowered = str(reason).lower()

                if (
                    "promo" in lowered or
                    "advertisement" in lowered or
                    "marketing" in lowered or
                    "persuasive" in lowered or
                    "manipulative" in lowered or
                    "blocked phrase" in lowered or
                    "flagged phrase" in lowered or
                    "high-risk" in lowered or
                    "عرض" in lowered or
                    "خصم" in lowered or
                    "ترويج" in lowered or
                    "إعلان" in lowered
                ):
                    st.warning(reason)
                    found_reason = True

        if not found_reason:
            st.info(
                "RASID detected contextual advertisement risk patterns, but no strong keyword-level manipulation signal was isolated."
            )


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

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview",
    "👤 Moderator Review",
    "🌍 Region Policy Check",
    "🗂 Logs",
    "⚠️ Dispute Requests"
])


with tab1:
    st.markdown("## Live Detection Analytics")

    safe_count = len(df[df["decision"] == "approved"])
    manipulative_count = len(df[df["decision"] == "flagged"])
    fraud_count = len(df[df["decision"] == "blocked"])
    avg_confidence = round(df["confidence"].mean(), 2)

    col1, col2, col3, col4 = st.columns(4)

    metrics = [
        ("Total Scans", len(df), ""),
        ("Safe", safe_count, "safe"),
        ("Manipulative", manipulative_count, "manipulative"),
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

        risk_counts = df["decision_label"].value_counts().reset_index()
        risk_counts.columns = ["Decision", "Count"]

        fig = themed_pie(
            risk_counts,
            "Decision",
            "Count",
            "Decision",
            {
                "Safe": "#5ee0a0",
                "Manipulative": "#e0b85a",
                "Fraud": "#ff6b6b"
            }
        )

        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Language Distribution")

        lang_counts = df["language"].value_counts().reset_index()
        lang_counts.columns = ["Language", "Count"]

        fig_lang = themed_pie(
            lang_counts,
            "Language",
            "Count",
            "Language",
            {
                "ar": "#4cc9c0",
                "en": "#5b6cff",
                "unknown": "#9fb0bd"
            }
        )

        st.plotly_chart(fig_lang, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Input Type Distribution")

        input_counts = df["input_type"].value_counts().reset_index()
        input_counts.columns = ["Input", "Count"]

        fig_input = themed_pie(
            input_counts,
            "Input",
            "Count",
            "Input",
            {
                "text": "#5b6cff",
                "image": "#4cc9c0",
                "image_url": "#4cc9c0",
                "video": "#e0b85a",
                "video_url": "#e0b85a",
                "unknown": "#9fb0bd"
            }
        )

        st.plotly_chart(fig_input, use_container_width=True)
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
        deepfake_risk = latest.get("deepfake_risk", "unknown")
        deepfake_score = latest.get("deepfake_score", "N/A")

        if deepfake_risk in ["unknown", "", None]:
            st.write("**Deepfake Analysis:** No deepfake indicators detected")
        else:
            st.write(f"**Deepfake Analysis:** {deepfake_risk}")

        if deepfake_score not in ["N/A", "", None]:
            st.write(f"**Deepfake Confidence:** {deepfake_score}")

        display_explanation_block(latest)
        display_lime_explanation(latest)

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("System Status")
        st.success("RASID Engine Online")
        st.write(f"Average confidence: **{avg_confidence}**")
        st.markdown('</div>', unsafe_allow_html=True)


with tab2:
    st.subheader("Human-in-the-Loop Moderator Review")

    def make_review_label(i):
        row = df.iloc[i]

        timestamp = row.get("timestamp", "No time")
        decision = row.get("decision_label", "Unknown")
        input_type = row.get("input_type", "unknown")
        confidence = row.get("confidence", 0)

        reasons = parse_json_field(row.get("reasons", []), [])
        preview = ""

        if isinstance(reasons, list) and reasons:
            preview = str(reasons[0])
        else:
            preview = str(row.get("explanation", ""))

        preview = preview.replace("\n", " ").strip()

        if len(preview) > 55:
            preview = preview[:55] + "..."

        return (
            f"{timestamp} | "
            f"{decision} | "
            f"{input_type} | "
            f"conf={confidence} | "
            f"{preview}"
        )

    review_index = st.selectbox(
    "Select scan to review",
    options=list(reversed(range(len(df)))),
    format_func=make_review_label
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
        st.write("**Source URL:**", selected.get("source_url", "Not available"))
        st.write("**Timestamp:**", selected.get("timestamp", "unknown"))
        deepfake_risk = selected.get("deepfake_risk", "unknown")
        deepfake_score = selected.get("deepfake_score", "N/A")

        if deepfake_risk in ["unknown", "", None]:
            st.write("**Deepfake Analysis:** No deepfake indicators detected")
        else:
            st.write(f"**Deepfake Analysis:** {deepfake_risk}")

        if deepfake_score not in ["N/A", "", None]:
            st.write(f"**Deepfake Confidence:** {deepfake_score}")

        st.write("### Reasons")
        reasons = parse_json_field(selected.get("reasons", []), [])

        if isinstance(reasons, list) and reasons:
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

    if policy_area == "Finance" and current_decision in ["Manipulative", "Fraud"]:
        policy_warning = "Financial advertisements require human review when they contain profit guarantees, fixed income claims, or risk-free investment language."
    elif policy_area == "Health" and current_decision in ["Manipulative", "Fraud"]:
        policy_warning = "Health advertisements require strict review when they contain cure claims, guaranteed results, or medical treatment promises."
    elif region == "Saudi Arabia" and policy_area in ["Finance", "Health"]:
        policy_warning = "Regional policy check recommends moderator review for sensitive finance or health advertisement claims."
    elif current_decision == "Fraud":
        policy_warning = "High-risk content should be escalated for human moderation."
    elif current_decision == "Manipulative":
        policy_warning = "Potentially manipulative content should be reviewed before approval."

    st.warning(policy_warning)
    st.write("**Selected Region:**", region)
    st.write("**Policy Area:**", policy_area)
    st.write("**Decision:**", current_decision)
    st.markdown('</div>', unsafe_allow_html=True)


with tab4:
    st.subheader("System Logs")

    display_columns = [
        "timestamp",
        "source",
        "input_type",
        "decision_label",
        "language",
        "confidence",
        "deepfake_risk",
        "deepfake_score",
        "reasons"
    ]

    available_columns = [col for col in display_columns if col in df.columns]

    display_df = df.tail(50)[available_columns].rename(columns={
        "timestamp": "Time",
        "source": "Source",
        "input_type": "Input Type",
        "decision_label": "Decision",
        "language": "Language",
        "confidence": "Confidence",
        "deepfake_risk": "Deepfake Risk",
        "deepfake_score": "Deepfake Score",
        "reasons": "Reasons"
    })

    st.dataframe(display_df, use_container_width=True)

    reviews_df = load_reviews_df()

    st.subheader("Moderator Review History")
    if reviews_df.empty:
        st.info("No moderator reviews saved yet.")
    else:
        st.dataframe(reviews_df.tail(30), use_container_width=True)


with tab5:
    st.markdown("## User Dispute Requests")

    disputes_df = load_disputes()

    if disputes_df.empty:
        st.info("No dispute requests found.")
    else:
        pending_df = disputes_df[disputes_df["status"] != "Resolved"]
        resolved_df = disputes_df[disputes_df["status"] == "Resolved"]

        pending_tab, resolved_tab = st.tabs([
            "Pending Requests",
            "Resolved Requests"
        ])

        with pending_tab:
            if pending_df.empty:
                st.success("No pending dispute requests.")
            else:
                for idx, row in pending_df.iterrows():
                    st.markdown("---")

                    decision = row["ai_decision"]

                    display_decision = {
                        "approved": "Safe",
                        "flagged": "Manipulative",
                        "blocked": "Fraud"
                    }.get(decision, decision)

                    st.markdown(f"### Submission #{row['id']}")
                    st.write("**Status:**", row["status"])
                    st.write("**User:**", row.get("username", "unknown"))
                    st.write("**AI Decision:**", display_decision)
                    st.write("**Confidence:**", row["confidence"])
                    st.write("**Language:**", row["language"])

                    st.write("### Advertisement Text")
                    st.code(row["ad_text"])
                    image_path = row.get("image_path", "")

                    if image_path and Path(image_path).exists():
                        st.write("### Submitted Advertisement Image")
                        st.image(image_path, use_container_width=True)

                    st.write("### AI Reasons")
                    try:
                        reasons = json.loads(row["reasons"])
                        for reason in reasons:
                            st.write(f"• {reason}")
                    except Exception:
                        st.write(row["reasons"])

                    st.write("### User Appeal")
                    st.write(row["user_note"])

                    moderator_action = st.selectbox(
                        f"Moderator Action #{row['id']}",
                        [
                            "Keep AI Decision",
                            "Override to Safe",
                            "Override to Manipulative",
                            "Override to Fraud"
                        ],
                        key=f"mod_action_{row['id']}"
                    )

                    moderator_note = st.text_area(
                        "Moderator Note",
                        key=f"mod_note_{row['id']}"
                    )

                    if st.button(
                        f"Resolve Request #{row['id']}",
                        key=f"resolve_{row['id']}"
                    ):
                        conn = sqlite3.connect(DB_PATH)
                        cursor = conn.cursor()

                        cursor.execute("""
                        UPDATE dispute_requests
                        SET status = ?
                        WHERE id = ?
                        """, ("Resolved", row["id"]))

                        conn.commit()
                        conn.close()

                        st.success("Request resolved successfully.")
                        st.rerun()

        with resolved_tab:
            if resolved_df.empty:
                st.info("No resolved requests yet.")
            else:
                display_resolved = resolved_df[[
                    "id",
                    "timestamp",
                    "username",
                    "ai_decision",
                    "confidence",
                    "language",
                    "status",
                    "user_note"
                ]].copy()

                display_resolved["ai_decision"] = display_resolved["ai_decision"].map({
                    "approved": "Safe",
                    "flagged": "Manipulative",
                    "blocked": "Fraud"
                }).fillna(display_resolved["ai_decision"])

                display_resolved = display_resolved.rename(columns={
                    "id": "ID",
                    "timestamp": "Time",
                    "username": "User",
                    "ai_decision": "AI Decision",
                    "confidence": "Confidence",
                    "language": "Language",
                    "status": "Status",
                    "user_note": "User Appeal"
                })

                st.dataframe(display_resolved, use_container_width=True)