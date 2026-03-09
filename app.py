import streamlit as st
import streamlit.components.v1 as components
import pandas as pd

# -----------------------------
# LOAD CSS
# -----------------------------
def load_css():
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# -----------------------------
# LOAD JS
# -----------------------------
def load_js():
    with open("script.js") as f:
        js = f.read()
        components.html(f"<script>{js}</script>", height=0)

# Load styling
load_css()
load_js()

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Mentor Me Collective Dashboard",
    page_icon="🚀",
    layout="wide"
)

# -----------------------------
# HEADER
# -----------------------------
st.markdown(
"""
<h1 class="main-title">🚀 Mentor Me Collective</h1>
<p class="subtitle">Applicant Selection & Track Management Dashboard</p>
""",
unsafe_allow_html=True
)

st.divider()

# -----------------------------
# TABS
# -----------------------------
tab1, tab2 = st.tabs(["🎓 Applicant Selection", "📊 Track Attendance"])

# =====================================================
# TAB 1 — APPLICANT SELECTION
# =====================================================
with tab1:

    st.subheader("Upload Applicant List")

    file = st.file_uploader("Upload CSV or Excel file", type=["csv","xlsx"])

    if file:

        if file.name.endswith(".csv"):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)

        st.success("File uploaded successfully!")

        st.dataframe(df)

        st.subheader("Track Distribution")

        if "Google Cloud Launchpad Track Preference:" in df.columns:

            track_counts = df["Google Cloud Launchpad Track Preference:"].value_counts()

            st.bar_chart(track_counts)

# =====================================================
# TAB 2 — ATTENDANCE
# =====================================================
with tab2:

    st.subheader("Upload Attendance Sheet")

    file2 = st.file_uploader("Upload attendance sheet", type=["csv","xlsx"], key="attendance")

    if file2:

        if file2.name.endswith(".csv"):
            df2 = pd.read_csv(file2)
        else:
            df2 = pd.read_excel(file2)

        st.success("Attendance sheet loaded!")

        st.dataframe(df2)

        st.info("Next step: strike automation and absence detection can run here.")

st.divider()

st.markdown(
"""
<div class="footer">
Mentor Me Collective • Internal Dashboard
</div>
""",
unsafe_allow_html=True
)
