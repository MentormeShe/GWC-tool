import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components
import smtplib
from email.message import EmailMessage

# ---------- CONFIG ----------
st.set_page_config(
    page_title="🚀 Mentor Me Collective AI Dashboard",
    page_icon="🚀",
    layout="wide"
)

MAX_STRIKES = 3  # Max strikes before sending email

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
<p>AI Applicant Selection & Attendance Dashboard</p>
</div>
""",
unsafe_allow_html=True
)

# ---------- TABS ----------
tab1, tab2 = st.tabs(["🎯 Applicant Selection", "📋 Attendance & Strike Tracker"])

# ---------- TAB 1: Applicant Selection ----------
with tab1:

    st.sidebar.title("⚙️ AI Selection Controls")
    max_per_track = st.sidebar.slider(
        "Applicants per Track", 5, 200, 25
    )

    st.header("Upload Applicant File")
    file = st.file_uploader("Upload Application Spreadsheet", type=["csv","xlsx"])

    if file:

        if file.name.endswith(".csv"):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)

        st.success("Applicants Loaded Successfully 🎉")

        # AI Score (fun example: length of data in row)
        df["AI Score"] = df.fillna("").astype(str).apply(lambda row: sum(len(str(x)) for x in row), axis=1)

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
            selected = track_df.sort_values("AI Score", ascending=False).head(max_per_track)

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

        if track_results:
            final_df = pd.concat(track_results)
            st.divider()
            st.header("🏆 Final Selected Cohort")
            st.dataframe(final_df)

            # Track Distribution Chart
            chart_data = final_df["Track"].value_counts().reset_index()
            chart_data.columns = ["Track","Count"]
            fig = px.bar(chart_data, x="Track", y="Count", title="Selected Applicants per Track")
            st.plotly_chart(fig, use_container_width=True)

            # Download Button
            st.download_button(
                "Download Selected Applicants",
                final_df.to_csv(index=False),
                "selected_applicants.csv",
                "text/csv"
            )

# ---------- TAB 2: Attendance & Strike Tracker ----------
with tab2:

    st.header("Upload Weekly Attendance Sheet")
    attendance_file = st.file_uploader("Upload Attendance CSV/XLSX", type=["csv","xlsx"], key="attend")

    if attendance_file:
        if attendance_file.name.endswith(".csv"):
            att_df = pd.read_csv(attendance_file)
        else:
            att_df = pd.read_excel(attendance_file)

        st.success("Attendance Sheet Loaded 🎉")

        # Identify week columns dynamically
        week_cols = [col for col in att_df.columns if "Week" in col or "June" in col or "July" in col or "Aug" in col or "Sept" in col]

        # Initialize Strikes column if not exists
        if "Strikes" not in att_df.columns:
            att_df["Strikes"] = 0

        # Editable table for attendance
        st.subheader("Mark Attendance / Update Make-Up Sessions")
        edited_df = st.data_editor(att_df, num_rows="dynamic")

        # Calculate strikes automatically
        def calculate_strikes(row):
            absent_count = sum(1 for c in week_cols if str(row[c]).strip().lower() == "absent")
            return absent_count

        edited_df["Strikes"] = edited_df.apply(calculate_strikes, axis=1)

        # Highlight people reaching strike limit
        def strike_color(val):
            if val >= MAX_STRIKES:
                return 'background-color: #FF4C4C; color:white;'  # Red for alert
            elif val == MAX_STRIKES-1:
                return 'background-color: #FFA500; color:white;'  # Orange for warning
            else:
                return ''

        st.subheader("Strike Status")
        st.dataframe(edited_df.style.applymap(strike_color, subset=["Strikes"]))

        # ---------- EMAIL ALERTS ----------
        st.subheader("Send Strike Emails ⚡")
        st.write("Emails will be sent to anyone with strikes >= 3")

        if st.button("Send Strike Emails"):
            emails_sent = 0
            for idx, row in edited_df.iterrows():
                if row["Strikes"] >= MAX_STRIKES:
                    try:
                        # Placeholder email code
                        email_address = row.get("Email", None)
                        name = row.get("Full Name", "Applicant")
                        if email_address:
                            # Email template
                            msg = EmailMessage()
                            msg['Subject'] = "Attendance Warning ⚠️"
                            msg['From'] = "YOUR_EMAIL@gmail.com"
                            msg['To'] = email_address
                            msg.set_content(f"Hi {name},\n\nYou have reached {row['Strikes']} strikes due to missed attendance. Please take immediate action.\n\n- Mentor Me Collective")

                            # Uncomment below and add SMTP credentials to actually send
                            """
                            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                                smtp.login("YOUR_EMAIL@gmail.com", "YOUR_PASSWORD")
                                smtp.send_message(msg)
                            """
                            emails_sent += 1
                    except Exception as e:
                        st.error(f"Failed to send to {name}: {e}")

            st.success(f"Emails prepared/sent: {emails_sent}")

        # ---------- DOWNLOAD UPDATED ATTENDANCE ----------
        st.download_button(
            "Download Updated Attendance + Strikes",
            edited_df.to_csv(index=False),
            "updated_attendance.csv",
            "text/csv"
        )

st.markdown("<h6 style='text-align:center;color:gray;'>🚀 Built with ❤️ for Mentor Me Collective</h6>", unsafe_allow_html=True)
