import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components
import smtplib
from email.message import EmailMessage
import os

st.set_page_config(
    page_title="🚀 Mentor Me Collective",
    page_icon="🚀",
    layout="wide"
)

MAX_STRIKES = 3

# ---------- LOAD CSS ----------
with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ---------- LOAD JS ----------
with open("assets/script.js") as f:
    components.html(f"<script>{f.read()}</script>", height=0)

# ---------- NAVBAR ----------
st.markdown("""
<nav class="navbar fixed w-full top-0 left-0 flex items-center justify-between p-6 z-50">
    <div class="text-white font-bold text-xl">🚀 Mentor Me Collective</div>
    <div class="flex space-x-6">
        <a href="#selection" class="nav-link">Selection</a>
        <a href="#attendance" class="nav-link">Attendance</a>
        <a href="#analytics" class="nav-link">Analytics</a>
    </div>
</nav>
<div class="pt-24"></div>
""", unsafe_allow_html=True)

# ---------- ENV VARIABLES ----------
EMAIL_ADDRESS = os.environ.get("EMAIL_USER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASS")

# ---------- TABS ----------
tab1, tab2 = st.tabs(["🎯 Applicant Selection", "📋 Attendance & Strike Tracker"])

# ---------- TAB 1: Applicant Selection ----------
with tab1:
    st.markdown("<h2 id='selection'>Applicant Selection</h2>", unsafe_allow_html=True)

    max_per_track = st.sidebar.slider(
        "Applicants per Track", 5, 200, 25, key="applicant_slider"
    )

    file = st.file_uploader(
        "Upload Application Spreadsheet",
        type=["csv","xlsx"],
        key="app_file"
    )

    if file:
        # Load file
        if file.name.endswith(".csv"):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)

        st.success("Applicants Loaded Successfully 🎉")
        df.columns = df.columns.str.strip()
        df["AI Score"] = df.fillna("").astype(str).apply(lambda row: sum(len(str(x)) for x in row), axis=1)

        tracks = [
            "UX Design", "Project Management", "Data Analytics",
            "Advanced Data Analytics", "Business Intelligence",
            "Cybersecurity", "Digital Marketing & E-commerce",
            "IT Automation with Python", "IT Support"
        ]

        # Detect track and region columns
        track_column = next((col for col in df.columns if "Track Preference" in col), None)
        region_column = next((col for col in df.columns if "Region" in col or "AMER" in col or "EMEA" in col or "APAC" in col), None)

        if not track_column:
            st.error("No track preference column found in your uploaded file!")
        else:
            track_results = []
            track_colors = {
                "UX Design": "#6EE7B7",
                "Project Management": "#60A5FA",
                "Data Analytics": "#FBBF24",
                "Advanced Data Analytics": "#F472B6",
                "Business Intelligence": "#A78BFA",
                "Cybersecurity": "#F87171",
                "Digital Marketing & E-commerce": "#34D399",
                "IT Automation with Python": "#FCD34D",
                "IT Support": "#38BDF8"
            }

            for track in tracks:
                track_df = df[df[track_column].str.contains(track, na=False)]

                if region_column:
                    for region, region_df in track_df.groupby(region_column):
                        selected = region_df.sort_values("AI Score", ascending=False).head(max_per_track)
                        selected["Track"] = track
                        selected["Region"] = region
                        track_results.append(selected)

                        color = track_colors.get(track, "#9CA3AF")
                        st.markdown(
                            f"<div class='track-card' style='background-color:{color};'><h3>{track} - {region}</h3><p>{len(selected)} selected</p></div>",
                            unsafe_allow_html=True
                        )
                        st.dataframe(selected)
                else:
                    selected = track_df.sort_values("AI Score", ascending=False).head(max_per_track)
                    selected["Track"] = track
                    track_results.append(selected)

                    color = track_colors.get(track, "#9CA3AF")
                    st.markdown(
                        f"<div class='track-card' style='background-color:{color};'><h3>{track}</h3><p>{len(selected)} selected</p></div>",
                        unsafe_allow_html=True
                    )
                    st.dataframe(selected)

            if track_results:
                final_df = pd.concat(track_results)
                st.divider()
                st.markdown("<h2 id='analytics'>Final Selected Cohort</h2>", unsafe_allow_html=True)
                st.dataframe(final_df)

                chart_data = final_df["Track"].value_counts().reset_index()
                chart_data.columns = ["Track","Count"]
                fig = px.bar(chart_data, x="Track", y="Count", title="Selected Applicants per Track")
                st.plotly_chart(fig, use_container_width=True)

                st.download_button(
                    "Download Selected Applicants",
                    final_df.to_csv(index=False),
                    "selected_applicants.csv",
                    "text/csv"
                )

# ---------- TAB 2: Attendance & Strike Tracker ----------
with tab2:
    st.markdown("<h2 id='attendance'>Attendance & Strike Tracker</h2>", unsafe_allow_html=True)

    attendance_file = st.file_uploader(
        "Upload Attendance Sheet", type=["csv","xlsx"], key="attendance_file"
    )

    if attendance_file:
        if attendance_file.name.endswith(".csv"):
            att_df = pd.read_csv(attendance_file)
        else:
            att_df = pd.read_excel(attendance_file)

        st.success("Attendance Sheet Loaded 🎉")
        week_cols = [col for col in att_df.columns if "Week" in col or "June" in col or "July" in col or "Aug" in col or "Sept" in col]

        if "Strikes" not in att_df.columns:
            att_df["Strikes"] = 0

        edited_df = st.data_editor(att_df, num_rows="dynamic", key="att_editor")

        def calculate_strikes(row):
            return sum(1 for c in week_cols if str(row[c]).strip().lower() == "absent")

        edited_df["Strikes"] = edited_df.apply(calculate_strikes, axis=1)

        def strike_color(val):
            if val >= MAX_STRIKES:
                return 'background-color: #FF4C4C; color:white;'
            elif val == MAX_STRIKES-1:
                return 'background-color: #FFA500; color:white;'
            else:
                return ''

        st.dataframe(edited_df.style.applymap(strike_color, subset=["Strikes"]))

        st.subheader("Send Strike Emails ⚡")
        if st.button("Send Strike Emails", key="send_strikes"):
            if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
                st.error("Set EMAIL_USER & EMAIL_PASS environment variables.")
            else:
                emails_sent = 0
                for idx, row in edited_df.iterrows():
                    if row["Strikes"] >= MAX_STRIKES:
                        email_address = row.get("Email", None)
                        name = row.get("Full Name", "Applicant")
                        track = row.get("Track", "your program")
                        if email_address:
                            try:
                                msg = EmailMessage()
                                msg['Subject'] = "⚠️ Attendance Warning"
                                msg['From'] = EMAIL_ADDRESS
                                msg['To'] = email_address
                                msg.set_content(f"""Hi {name},

You have reached {row['Strikes']} strikes in {track}.
Please take immediate action to avoid further consequences.

- Mentor Me Collective
""")
                                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                                    smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                                    smtp.send_message(msg)
                                emails_sent += 1
                            except Exception as e:
                                st.error(f"Failed to send to {name}: {e}")
                st.success(f"Emails sent: {emails_sent}")

        st.download_button(
            "Download Updated Attendance + Strikes",
            edited_df.to_csv(index=False),
            "updated_attendance.csv",
            "text/csv"
        )

st.markdown("<h6 style='text-align:center;color:gray;'>🚀 Built with ❤️ for Mentor Me Collective</h6>", unsafe_allow_html=True)
# ---------- ENV VARIABLES ----------
EMAIL_ADDRESS = os.environ.get("EMAIL_USER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASS")

# ---------- TABS ----------
tab1, tab2 = st.tabs(["🎯 Applicant Selection", "📋 Attendance & Strike Tracker"])

# ---------- TAB 1: Applicant Selection ----------
with tab1:
    st.markdown("<h2 id='selection'>Applicant Selection</h2>", unsafe_allow_html=True)
    max_per_track = st.sidebar.slider("Applicants per Track", 5, 200, 25)
    file = st.file_uploader("Upload Application Spreadsheet", type=["csv","xlsx"])

    if file:
        if file.name.endswith(".csv"):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)

        st.success("Applicants Loaded Successfully 🎉")
        df.columns = df.columns.str.strip()
        df["AI Score"] = df.fillna("").astype(str).apply(lambda row: sum(len(str(x)) for x in row), axis=1)

        tracks = [
            "UX Design", "Project Management", "Data Analytics",
            "Advanced Data Analytics", "Business Intelligence",
            "Cybersecurity", "Digital Marketing & E-commerce",
            "IT Automation with Python", "IT Support"
        ]

        # Detect track and region columns
        track_column = next((col for col in df.columns if "Track Preference" in col), None)
        region_column = next((col for col in df.columns if "Region" in col or "AMER" in col or "EMEA" in col or "APAC" in col), None)

        if not track_column:
            st.error("No track preference column found in your uploaded file!")
        else:
            track_results = []
            track_colors = {
                "UX Design": "#6EE7B7",
                "Project Management": "#60A5FA",
                "Data Analytics": "#FBBF24",
                "Advanced Data Analytics": "#F472B6",
                "Business Intelligence": "#A78BFA",
                "Cybersecurity": "#F87171",
                "Digital Marketing & E-commerce": "#34D399",
                "IT Automation with Python": "#FCD34D",
                "IT Support": "#38BDF8"
            }

            for track in tracks:
                track_df = df[df[track_column].str.contains(track, na=False)]
                
                # ---------- REGION-AWARE ----------
                if region_column:
                    for region, region_df in track_df.groupby(region_column):
                        selected = region_df.sort_values("AI Score", ascending=False).head(max_per_track)
                        selected["Track"] = track
                        selected["Region"] = region
                        track_results.append(selected)

                        color = track_colors.get(track, "#9CA3AF")
                        st.markdown(
                            f"<div class='track-card' style='background-color:{color};'><h3>{track} - {region}</h3><p>{len(selected)} selected</p></div>",
                            unsafe_allow_html=True
                        )
                        st.dataframe(selected)
                else:
                    selected = track_df.sort_values("AI Score", ascending=False).head(max_per_track)
                    selected["Track"] = track
                    track_results.append(selected)

                    color = track_colors.get(track, "#9CA3AF")
                    st.markdown(
                        f"<div class='track-card' style='background-color:{color};'><h3>{track}</h3><p>{len(selected)} selected</p></div>",
                        unsafe_allow_html=True
                    )
                    st.dataframe(selected)

            if track_results:
                final_df = pd.concat(track_results)
                st.divider()
                st.markdown("<h2 id='analytics'>Final Selected Cohort</h2>", unsafe_allow_html=True)
                st.dataframe(final_df)

                chart_data = final_df["Track"].value_counts().reset_index()
                chart_data.columns = ["Track","Count"]
                fig = px.bar(chart_data, x="Track", y="Count", title="Selected Applicants per Track")
                st.plotly_chart(fig, use_container_width=True)

                st.download_button(
                    "Download Selected Applicants",
                    final_df.to_csv(index=False),
                    "selected_applicants.csv",
                    "text/csv"
                )

# ---------- TAB 2: Attendance & Strike Tracker ----------
with tab2:
    st.markdown("<h2 id='attendance'>Attendance & Strike Tracker</h2>", unsafe_allow_html=True)
    attendance_file = st.file_uploader("Upload Attendance Sheet", type=["csv","xlsx"], key="attend")

    if attendance_file:
        if attendance_file.name.endswith(".csv"):
            att_df = pd.read_csv(attendance_file)
        else:
            att_df = pd.read_excel(attendance_file)

        st.success("Attendance Sheet Loaded 🎉")
        week_cols = [col for col in att_df.columns if "Week" in col or "June" in col or "July" in col or "Aug" in col or "Sept" in col]

        if "Strikes" not in att_df.columns:
            att_df["Strikes"] = 0

        edited_df = st.data_editor(att_df, num_rows="dynamic")

        def calculate_strikes(row):
            return sum(1 for c in week_cols if str(row[c]).strip().lower() == "absent")

        edited_df["Strikes"] = edited_df.apply(calculate_strikes, axis=1)

        def strike_color(val):
            if val >= MAX_STRIKES:
                return 'background-color: #FF4C4C; color:white;'
            elif val == MAX_STRIKES-1:
                return 'background-color: #FFA500; color:white;'
            else:
                return ''

        st.dataframe(edited_df.style.applymap(strike_color, subset=["Strikes"]))

        st.subheader("Send Strike Emails ⚡")
        if st.button("Send Strike Emails"):
            if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
                st.error("Set EMAIL_USER & EMAIL_PASS environment variables.")
            else:
                emails_sent = 0
                for idx, row in edited_df.iterrows():
                    if row["Strikes"] >= MAX_STRIKES:
                        email_address = row.get("Email", None)
                        name = row.get("Full Name", "Applicant")
                        track = row.get("Track", "your program")
                        if email_address:
                            try:
                                msg = EmailMessage()
                                msg['Subject'] = "⚠️ Attendance Warning"
                                msg['From'] = EMAIL_ADDRESS
                                msg['To'] = email_address
                                msg.set_content(f"""Hi {name},

You have reached {row['Strikes']} strikes in {track}.
Please take immediate action to avoid further consequences.

- Mentor Me Collective
""")
                                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                                    smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                                    smtp.send_message(msg)
                                emails_sent += 1
                            except Exception as e:
                                st.error(f"Failed to send to {name}: {e}")
                st.success(f"Emails sent: {emails_sent}")

        st.download_button(
            "Download Updated Attendance + Strikes",
            edited_df.to_csv(index=False),
            "updated_attendance.csv",
            "text/csv"
        )

st.markdown("<h6 style='text-align:center;color:gray;'>🚀 Built with ❤️ for Mentor Me Collective</h6>", unsafe_allow_html=True)
# ---------- ENV VARIABLES ----------
EMAIL_ADDRESS = os.environ.get("EMAIL_USER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASS")

# ---------- TABS ----------
tab1, tab2 = st.tabs(["🎯 Applicant Selection", "📋 Attendance & Strike Tracker"])

# ---------- TAB 1: Applicant Selection ----------
with tab1:
    st.markdown("<h2 id='selection'>Applicant Selection</h2>", unsafe_allow_html=True)
    max_per_track = st.sidebar.slider("Applicants per Track", 5, 200, 25)
    file = st.file_uploader("Upload Application Spreadsheet", type=["csv","xlsx"])

    if file:
        if file.name.endswith(".csv"):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)

        st.success("Applicants Loaded Successfully 🎉")
        df.columns = df.columns.str.strip()
        df["AI Score"] = df.fillna("").astype(str).apply(lambda row: sum(len(str(x)) for x in row), axis=1)

        tracks = [
            "UX Design", "Project Management", "Data Analytics",
            "Advanced Data Analytics", "Business Intelligence",
            "Cybersecurity", "Digital Marketing & E-commerce",
            "IT Automation with Python", "IT Support"
        ]

        track_column = next((col for col in df.columns if "Track Preference" in col), None)
        region_column = next((col for col in df.columns if "Region" in col), None)

        if not track_column:
            st.error("No track preference column found in your uploaded file!")
        else:
            track_results = []
            track_colors = {
                "UX Design": "#6EE7B7",
                "Project Management": "#60A5FA",
                "Data Analytics": "#FBBF24",
                "Advanced Data Analytics": "#F472B6",
                "Business Intelligence": "#A78BFA",
                "Cybersecurity": "#F87171",
                "Digital Marketing & E-commerce": "#34D399",
                "IT Automation with Python": "#FCD34D",
                "IT Support": "#38BDF8"
            }

            for track in tracks:
                track_df = df[df[track_column].str.contains(track, na=False)]
                
                # ---------- REGION-AWARE ----------
                if region_column:
                    for region, region_df in track_df.groupby(region_column):
                        selected = region_df.sort_values("AI Score", ascending=False).head(max_per_track)
                        color = track_colors.get(track, "#9CA3AF")
                        st.markdown(
                            f"<div class='track-card' style='background-color:{color};'><h3>{track} - {region}</h3><p>{len(selected)} selected</p></div>",
                            unsafe_allow_html=True
                        )
                        st.dataframe(selected)
                        selected["Track"] = track
                        selected["Region"] = region
                        track_results.append(selected)
                else:
                    selected = track_df.sort_values("AI Score", ascending=False).head(max_per_track)
                    color = track_colors.get(track, "#9CA3AF")
                    st.markdown(
                        f"<div class='track-card' style='background-color:{color};'><h3>{track}</h3><p>{len(selected)} selected</p></div>",
                        unsafe_allow_html=True
                    )
                    st.dataframe(selected)
                    selected["Track"] = track
                    track_results.append(selected)

            if track_results:
                final_df = pd.concat(track_results)
                st.divider()
                st.markdown("<h2 id='analytics'>Final Selected Cohort</h2>", unsafe_allow_html=True)
                st.dataframe(final_df)

                chart_data = final_df["Track"].value_counts().reset_index()
                chart_data.columns = ["Track","Count"]
                fig = px.bar(chart_data, x="Track", y="Count", title="Selected Applicants per Track")
                st.plotly_chart(fig, use_container_width=True)

                st.download_button(
                    "Download Selected Applicants",
                    final_df.to_csv(index=False),
                    "selected_applicants.csv",
                    "text/csv"
                )

# ---------- TAB 2: Attendance & Strike Tracker ----------
with tab2:
    st.markdown("<h2 id='attendance'>Attendance & Strike Tracker</h2>", unsafe_allow_html=True)
    attendance_file = st.file_uploader("Upload Attendance Sheet", type=["csv","xlsx"], key="attend")

    if attendance_file:
        if attendance_file.name.endswith(".csv"):
            att_df = pd.read_csv(attendance_file)
        else:
            att_df = pd.read_excel(attendance_file)

        st.success("Attendance Sheet Loaded 🎉")
        week_cols = [col for col in att_df.columns if "Week" in col or "June" in col or "July" in col or "Aug" in col or "Sept" in col]

        if "Strikes" not in att_df.columns:
            att_df["Strikes"] = 0

        edited_df = st.data_editor(att_df, num_rows="dynamic")

        def calculate_strikes(row):
            return sum(1 for c in week_cols if str(row[c]).strip().lower() == "absent")

        edited_df["Strikes"] = edited_df.apply(calculate_strikes, axis=1)

        def strike_color(val):
            if val >= MAX_STRIKES:
                return 'background-color: #FF4C4C; color:white;'
            elif val == MAX_STRIKES-1:
                return 'background-color: #FFA500; color:white;'
            else:
                return ''

        st.dataframe(edited_df.style.applymap(strike_color, subset=["Strikes"]))

        st.subheader("Send Strike Emails ⚡")
        if st.button("Send Strike Emails"):
            if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
                st.error("Set EMAIL_USER & EMAIL_PASS environment variables.")
            else:
                emails_sent = 0
                for idx, row in edited_df.iterrows():
                    if row["Strikes"] >= MAX_STRIKES:
                        email_address = row.get("Email", None)
                        name = row.get("Full Name", "Applicant")
                        track = row.get("Track", "your program")
                        if email_address:
                            try:
                                msg = EmailMessage()
                                msg['Subject'] = "⚠️ Attendance Warning"
                                msg['From'] = EMAIL_ADDRESS
                                msg['To'] = email_address
                                msg.set_content(f"""Hi {name},

You have reached {row['Strikes']} strikes in {track}.
Please take immediate action to avoid further consequences.

- Mentor Me Collective
""")
                                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                                    smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                                    smtp.send_message(msg)
                                emails_sent += 1
                            except Exception as e:
                                st.error(f"Failed to send to {name}: {e}")
                st.success(f"Emails sent: {emails_sent}")

        st.download_button(
            "Download Updated Attendance + Strikes",
            edited_df.to_csv(index=False),
            "updated_attendance.csv",
            "text/csv"
        )

st.markdown("<h6 style='text-align:center;color:gray;'>🚀 Built with ❤️ for Mentor Me Collective</h6>", unsafe_allow_html=True)
