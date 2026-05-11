import streamlit as st
import requests
import sqlite3
from pathlib import Path
from datetime import datetime
import json

API_URL = "http://127.0.0.1:8000/analyze/text/auto"
DB_PATH = Path("logs/rasid.db")
DB_PATH.parent.mkdir(exist_ok=True)

st.set_page_config(
    page_title="RASID Submission",
    page_icon="🛡️",
    layout="centered"
)

st.markdown("""
<style>
.stApp {
    background: #07131f;
    color: #eaf2f8;
    font-family: 'Segoe UI', sans-serif;
}

.card {
    background: #101c29;
    padding: 26px;
    border-radius: 24px;
    border: 1px solid #24384d;
    box-shadow: 0 12px 30px rgba(0,0,0,0.25);
    margin-bottom: 20px;
}

.title {
    font-size: 34px;
    font-weight: 800;
    color: #ffffff;
}

.subtitle {
    color: #9fb0bd;
    margin-bottom: 20px;
}

.safe { color: #5ee0a0; font-weight: 800; }
.manipulative { color: #e0b85a; font-weight: 800; }
.fraud { color: #ff6b6b; font-weight: 800; }
.review { color: #4cc9c0; font-weight: 800; }

.stButton > button {
    background: #e0b85a;
    color: #07131f;
    border-radius: 14px;
    border: none;
    padding: 10px 20px;
    font-weight: 800;
}

.stTextArea textarea {
    background: #101c29 !important;
    color: #eaf2f8 !important;
    border-radius: 14px !important;
    border: 1px solid #24384d !important;
}
</style>
""", unsafe_allow_html=True)


def init_disputes_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dispute_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        ad_text TEXT,
        ai_decision TEXT,
        confidence REAL,
        language TEXT,
        reasons TEXT,
        user_note TEXT,
        status TEXT
    )
    """)

    conn.commit()
    conn.close()


def save_dispute(ad_text, result, user_note):
    init_disputes_table()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO dispute_requests (
        timestamp, ad_text, ai_decision, confidence, language,
        reasons, user_note, status
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().isoformat(timespec="seconds"),
        ad_text,
        result.get("decision", "unknown"),
        result.get("confidence", 0),
        result.get("language", "unknown"),
        json.dumps(result.get("reasons", []), ensure_ascii=False),
        user_note,
        "Under Review"
    ))

    conn.commit()
    conn.close()


def label(decision):
    mapping = {
        "approved": "Safe",
        "flagged": "Manipulative",
        "blocked": "Fraud"
    }
    return mapping.get(decision, decision)


st.markdown('<div class="title">🛡️ RASID Ad Submission</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Submit advertisement text for AI safety analysis.</div>', unsafe_allow_html=True)

st.markdown('<div class="card">', unsafe_allow_html=True)

ad_text = st.text_area(
    "Advertisement Text",
    height=160,
    placeholder="Paste the advertisement text here..."
)

if st.button("Run RASID Analysis"):
    if not ad_text.strip():
        st.warning("Please enter advertisement text first.")
    else:
        form_data = {"text": ad_text}

        try:
            response = requests.post(API_URL, data=form_data)
            result = response.json()

            st.session_state["last_text"] = ad_text
            st.session_state["last_result"] = result

        except Exception as e:
            st.error(f"Could not connect to RASID API: {e}")

st.markdown('</div>', unsafe_allow_html=True)


if "last_result" in st.session_state:
    result = st.session_state["last_result"]
    decision = label(result.get("decision", "unknown"))

    css_class = "safe"
    if decision == "Manipulative":
        css_class = "manipulative"
    elif decision == "Fraud":
        css_class = "fraud"

    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.markdown(f"### Result: <span class='{css_class}'>{decision}</span>", unsafe_allow_html=True)
    st.write("**Confidence:**", result.get("confidence", 0))
    st.write("**Language:**", result.get("language", "unknown"))

    st.write("### Explanation")
    reasons = result.get("reasons", [])
    if isinstance(reasons, list):
        for reason in reasons:
            st.write(f"• {reason}")
    else:
        st.write(reasons)

    if "lime_explanation" in result:
        st.write("### LIME Explanation")
        for item in result["lime_explanation"]:
            if "word" in item:
                st.write(f"• **{item['word']}** → weight: {item['weight']}")

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.write("### Disagree with this result?")
    user_note = st.text_area(
        "Request moderator review",
        placeholder="Explain why you disagree with the AI decision..."
    )

    if st.button("Request Review"):
        save_dispute(
            st.session_state["last_text"],
            result,
            user_note
        )
        st.success("Your request has been submitted. Status: Under Review")

    st.markdown('</div>', unsafe_allow_html=True)