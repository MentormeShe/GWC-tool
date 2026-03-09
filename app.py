import streamlit as st
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import io

# --- PAGE SETUP ---
st.set_page_config(page_title="MMC Strike Bot", page_icon="🤖", layout="wide")
st.title("🤖 Mentor Me Collective: Strike Bot")
st.markdown("Upload your track's attendance sheet to auto-audit absences and trigger Strike emails.")

# --- SIDEBAR: EMAIL SETTINGS ---
st.sidebar.header("Email Configuration")
sender_email = st.sidebar.text_input("Sender Email (e.g., GWG@mentormecollective.com)")
sender_password = st.sidebar.text_input("Email App Password", type="password")
st.sidebar.caption("Note: Use an App Password if using Gmail/Google Workspace.")

# --- MAIN APP ---
uploaded_file = st.file_uploader("Upload Attendance Sheet (CSV or Excel)", type=["csv", "xlsx"])

if uploaded_file is not None:
    # --- READ FILE ---
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file, engine='openpyxl')

    st.success(f"Successfully loaded: {uploaded_file.name}")

    # --- CLEAN & NORMALIZE COLUMNS ---
    df.columns = df.columns.str.strip()              # remove leading/trailing spaces
    df.columns = df.columns.str.replace('\xa0','')   # remove hidden non-breaking spaces
    df.columns = df.columns.str.lower()              # lowercase all headers
    df.columns = df.columns.str.replace(':','')      # remove trailing colons

    # Map messy headers to expected columns
    column_map = {
        'first name': 'first name',
        'email address': 'email'
    }
    df.rename(columns=column_map, inplace=True)

    # --- CHECK REQUIRED COLUMNS ---
    required_cols = ['first name','email']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        st.error(f"Missing required columns: {', '.join(missing_cols)}. Please check your sheet.")
    else:
        # Ensure strike column exists
        if 'strike_level_sent' not in df.columns:
            df['strike_level_sent'] = 0

        # --- AUDIT LOGIC ---
        email_queue = []

        for index, row in df.iterrows():
            first_name = str(row['first name'])
            email = str(row['email'])
            last_strike_sent = int(row['strike_level_sent']) if pd.notna(row['strike_level_sent']) else 0

            # Count absences
            total_absences = list(row.astype(str).str.strip().str.lower()).count('absent')

            # Check if a new strike is needed
            if total_absences > 0 and total_absences > last_strike_sent and total_absences <= 4:
                # --- Email Templates ---
                if total_absences == 1:
                    subject = "Strike 1: Missed Track Sync - Action Required"
                    body = f"Hi {first_name},\n\nWe noticed you missed a weekly track sync. Please attend 'Workshop Wednesday' to make up for this absence.\n\nMake-up Form link is in the YouTube description of the Workshop session.\n\nBest,\nMentor Me Collective Support"
                elif total_absences == 2:
                    subject = "Strike 2: Second Absence Notice"
                    body = f"Hi {first_name},\n\nYou now have 2 absences. Per the Code of Conduct, attendance is mandatory to maintain your spot in the program.\n\nPlease utilize Workshop Wednesday to make up missed sessions.\n\nBest,\nMentor Me Collective Support"
                elif total_absences == 3:
                    subject = "Strike 3: FINAL WARNING - Imminent Removal"
                    body = f"URGENT: {first_name},\n\nYou have reached 3 absences. This is your final warning. A 4th missed session will result in removal from the program.\n\nIf experiencing blockers, review the FAQ and use the Ticket-to-Talk Escalation Form immediately.\n\nBest,\nMentor Me Collective Support"
                elif total_absences == 4:
                    subject = "Strike 4: Notice of Program Removal"
                    body = f"Hi {first_name},\n\nYou have reached 4 absences. This triggers automatic removal from the program.\n\nCoursera and Slack access will be revoked within 24 hours.\n\nBest,\nMentor Me Collective Support"

                email_queue.append({
                    "Index": index,
                    "First Name": first_name,
                    "Email": email,
                    "Total Absences": total_absences,
                    "Strike Level": total_absences,
                    "Subject": subject,
                    "Body": body
                })

        # --- PREVIEW DASHBOARD ---
        if len(email_queue) > 0:
            st.warning(f"⚠️ Found {len(email_queue)} scholars who require Strike Emails.")

            queue_df = pd.DataFrame(email_queue)[["First Name","Email","Total Absences","Strike Level"]]
            st.dataframe(queue_df, use_container_width=True)

            if st.button("🚀 Send Warning Emails"):
                if not sender_email or not sender_password:
                    st.error("Please enter your Email Credentials in the sidebar first!")
                else:
                    try:
                        server = smtplib.SMTP('smtp.gmail.com', 587)
                        server.starttls()
                        server.login(sender_email, sender_password)

                        progress_bar = st.progress(0)

                        for i, task in enumerate(email_queue):
                            msg = MIMEMultipart()
                            msg['From'] = sender_email
                            msg['To'] = task['Email']
                            msg['Subject'] = task['Subject']
                            msg.attach(MIMEText(task['Body'], 'plain'))

                            server.send_message(msg)
                            df.at[task["Index"], 'strike_level_sent'] = task["Strike Level"]
                            progress_bar.progress((i + 1) / len(email_queue))

                        server.quit()
                        st.success("✅ All emails sent successfully!")

                        # --- DOWNLOAD UPDATED FILE ---
                        output = io.BytesIO()
                        if uploaded_file.name.endswith('.csv'):
                            df.to_csv(output, index=False)
                            mime_type = "text/csv"
                            new_file_name = "UPDATED_" + uploaded_file.name
                        else:
                            df.to_excel(output, index=False)
                            mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            new_file_name = "UPDATED_" + uploaded_file.name
                        output.seek(0)

                        st.download_button(
                            label="📥 Download Updated Attendance Sheet",
                            data=output.getvalue(),
                            file_name=new_file_name,
                            mime=mime_type
                        )
                        st.info("Upload this updated sheet back to Google Drive so strikes are tracked next week!")

                    except Exception as e:
                        st.error(f"Failed to send emails. Error: {e}")
        else:
            st.success("🎉 No scholars require intervention this week! Everyone is up to date.")
