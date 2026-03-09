import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Mentor Me Collective AI Dashboard",
    page_icon="🚀",
    layout="wide"
)

# -----------------------------
# HERO HEADER
# -----------------------------
st.markdown("""
<style>
.hero {
    background: linear-gradient(90deg,#6a5acd,#ff7f50);
    padding: 30px;
    border-radius: 12px;
    color:white;
    text-align:center;
    margin-bottom:25px;
}

.card {
    padding:20px;
    border-radius:12px;
    background:white;
    box-shadow:0px 4px 10px rgba(0,0,0,0.08);
}

.metric-card {
    padding:20px;
    border-radius:12px;
    background:#f8f9ff;
    text-align:center;
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
<h1>🚀 Mentor Me Collective</h1>
<h3>AI Applicant Selection & Track Management</h3>
<p>Smart filtering, ranking and analytics for Grow With Google cohorts</p>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# SIDEBAR AI FILTERS
# -----------------------------
st.sidebar.title("⚙️ AI Selection Controls")

max_applicants = st.sidebar.slider(
    "Applicants to Select",
    10,
    500,
    100
)

preferred_tracks = st.sidebar.multiselect(
    "Track Preference",
    ["Cloud Foundations","Data Engineering","Cloud Engineering"]
)

region_filter = st.sidebar.multiselect(
    "Regions",
    ["AMER","EMEA","APAC"]
)

# -----------------------------
# TABS
# -----------------------------
tab1, tab2 = st.tabs(["🎓 Applicant AI Selection","📊 Attendance Analytics"])

# ==================================================
# TAB 1
# ==================================================
with tab1:

    st.subheader("Upload Applicant Data")

    file = st.file_uploader(
        "Upload applicant spreadsheet",
        type=["csv","xlsx"]
    )

    if file:

        if file.name.endswith(".csv"):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)

        st.success("Applicants loaded")

        # -----------------------------
        # AI SCORING SYSTEM
        # -----------------------------
        df["AI Score"] = (
            df.fillna("").astype(str)
            .apply(lambda row: sum(len(str(x)) for x in row), axis=1)
        )

        df = df.sort_values("AI Score", ascending=False)

        selected = df.head(max_applicants)

        # -----------------------------
        # METRICS
        # -----------------------------
        col1,col2,col3,col4 = st.columns(4)

        col1.metric("Total Applicants",len(df))
        col2.metric("Selected Applicants",len(selected))
        col3.metric("Average AI Score",int(selected["AI Score"].mean()))
        col4.metric("Selection Rate",f"{round(len(selected)/len(df)*100,1)}%")

        st.divider()

        st.subheader("🏆 Top AI Ranked Applicants")

        st.dataframe(selected)

        # -----------------------------
        # TRACK ANALYTICS
        # -----------------------------
        if "Google Cloud Launchpad Track Preference:" in df.columns:

            track_counts = (
                selected["Google Cloud Launchpad Track Preference:"]
                .value_counts()
                .reset_index()
            )

            fig = px.bar(
                track_counts,
                x="count",
                y="Google Cloud Launchpad Track Preference:",
                orientation="h",
                title="Selected Applicants per Track"
            )

            st.plotly_chart(fig,use_container_width=True)

# ==================================================
# TAB 2
# ==================================================
with tab2:

    st.subheader("Upload Attendance Data")

    file2 = st.file_uploader(
        "Upload attendance sheet",
        type=["csv","xlsx"],
        key="attendance"
    )

    if file2:

        if file2.name.endswith(".csv"):
            df2 = pd.read_csv(file2)
        else:
            df2 = pd.read_excel(file2)

        st.success("Attendance loaded")

        attendance_counts = (
            df2.apply(lambda row: list(row.astype(str)).count("Present"),axis=1)
        )

        df2["Attendance Score"] = attendance_counts

        st.dataframe(df2)

        fig = px.histogram(
            df2,
            x="Attendance Score",
            nbins=15,
            title="Attendance Distribution"
        )

        st.plotly_chart(fig,use_container_width=True)

st.divider()

st.markdown(
"""
<center>
Mentor Me Collective • AI Program Management Dashboard
</center>
""",
unsafe_allow_html=True
)
