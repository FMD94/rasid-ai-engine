import streamlit as st

st.set_page_config(
    page_title="RASID Portal",
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
    padding: 28px;
    border-radius: 24px;
    border: 1px solid #24384d;
    margin-bottom: 20px;
    text-align: center;
}
a {
    text-decoration: none;
}
.portal-btn {
    display: block;
    background: #e0b85a;
    color: #07131f !important;
    padding: 16px;
    border-radius: 14px;
    font-weight: 800;
    margin-top: 15px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;'>🛡️ RASID Portal</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#9fb0bd;'>AI Context-Aware Online Safety Engine</p>", unsafe_allow_html=True)

st.markdown("""
<div class="card">
    <h2>User Portal</h2>
    <p>Submit advertisements and track review requests.</p>
    <a class="portal-btn" href="http://localhost:8502" target="_blank">Open User Portal</a>
</div>

<div class="card">
    <h2>Admin Dashboard</h2>
    <p>Review AI decisions, disputes, logs, and analytics.</p>
    <a class="portal-btn" href="http://localhost:8501" target="_blank">Open Admin Dashboard</a>
</div>
""", unsafe_allow_html=True)