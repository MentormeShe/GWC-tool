import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Mentor Me Collective AI Dashboard",
    page_icon="🚀",
    layout="wide"
)

# ---------- LOAD CSS ----------
def load_css():
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ---------- LOAD JS ----------
def load_js():
    with open("script.js") as f:
        components.html(f"<script>{f.read()}</script>", height=0)

load_css()
load_js()

# ---------- HERO HEADER ----------
st.markdown(
"""
<div class="hero">
<h1>🚀 Mentor Me Collective</h1>
<p>AI Applicant Selection Dashboard</p>
</div>
""",
unsafe_allow_html=True
)

# ---------- SIDEBAR ----------
st.sidebar.title("⚙️ AI Selection Controls")

max_per_track = st.sidebar.slider(
    "Applicants per Track",
    5,
    200,
    25
)

# ---------- FILE UPLOAD ----------
st.header("Upload Applicant File")

file = st.file_uploader(
    "Upload Application Spreadsheet",
    type=["csv","xlsx"]
)

if file:

    if file.name.endswith(".csv"):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)

    st.success("Applicants Loaded Successfully 🎉")

    # ---------- AI SCORE ----------
    df["AI Score"] = (
        df.fillna("")
        .astype(str)
        .apply(lambda row: sum(len(str(x)) for x in row), axis=1)
    )

    # ---------- TRACK DEFINITIONS ----------
    tracks = [
    "UX Design",
    "Project Management",
    "Data Analytics",
    "Advanced Data Analytics",
    "Business Intelligence",
    "Cybersecurity",
    "Digital Marketing & E-commerce",
    "IT Automation with Python",
    "IT Support"
    ]

    track_column = "Google Cloud Launchpad Track Preference:"

    st.divider()
    st.header("🎓 Selected Applicants by Track")

    track_results = []

    for track in tracks:

        track_df = df[df[track_column].str.contains(track, na=False)]

        selected = track_df.sort_values(
            "AI Score",
            ascending=False
        ).head(max_per_track)

        if len(selected) > 0:

            st.markdown(
            f"""
            <div class="track-card">
            <h3>{track}</h3>
            <p>{len(selected)} selected applicants</p>
            </div>
            """,
            unsafe_allow_html=True
            )

            st.dataframe(selected)

            selected["Track"] = track
            track_results.append(selected)

    # ---------- COMBINED OUTPUT ----------
    if track_results:

        final_df = pd.concat(track_results)

        st.divider()
        st.header("🏆 Final Selected Cohort")

        st.dataframe(final_df)

        # ---------- ANALYTICS ----------
        st.divider()
        st.header("📊 Track Distribution")

        chart_data = final_df["Track"].value_counts().reset_index()
        chart_data.columns = ["Track","Count"]

        fig = px.bar(
            chart_data,
            x="Track",
            y="Count",
            title="Selected Applicants per Track"
        )

        st.plotly_chart(fig, use_container_width=True)

        # ---------- DOWNLOAD ----------
        st.download_button(
            "Download Selected Applicants",
            final_df.to_csv(index=False),
            "selected_applicants.csv",
            "text/csv"
        )
