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
    # Read the file
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.success(f"Successfully loaded: {uploaded_file.name}")

    # Ensure necessary columns exist
    required_cols = ['First Name', 'Email']
    missing_cols = [col for col in required_cols if col not in df.columns]
    
    if missing_cols:
        st.error(f"Missing required columns: {', '.join(missing_cols)}. Please check your sheet.")
    else:
        # If 'Strike_Level_Sent' doesn't exist, create it
        if 'Strike_Level_Sent' not in df.columns:
            df['Strike_Level_Sent'] = 0
            
        # --- AUDIT LOGIC ---
        email_queue = []

        # Iterate through the sheet
        for index, row in df.iterrows():
            first_name = str(row['First Name'])
            email = str(row['Email'])
            last_strike_sent = int(row['Strike_Level_Sent']) if pd.notna(row['Strike_Level_Sent']) else 0
            
            # Count how many times "Absent" appears in this student's row
            # (This makes it universal, regardless of how dates are formatted!)
            total_absences = list(row.astype(str).str.strip().str.lower()).count('absent')

            # Check if they qualify for a new strike
            if total_absences > 0 and total_absences > last_strike_sent and total_absences <= 4:
                
                # Determine Email Subject and Body
                if total_absences == 1:
                    subject = "Strike 1: Missed Track Sync - Action Required"
                    body = f"Hi {first_name},\n\nWe noticed you missed a weekly track sync. To stay on track with the Grow with Google program, please attend 'Workshop Wednesday' to make up for this absence.\n\nYou can find the Make-up Form link in the YouTube description of the Workshop session.\n\nBest,\nMentor Me Collective Support"
                elif total_absences == 2:
                    subject = "Strike 2: Second Absence Notice"
                    body = f"Hi {first_name},\n\nYou now have 2 absences on record. Per the Code of Conduct (CoC) you signed during onboarding, attendance is mandatory to maintain your spot in the program.\n\nPlease utilize Workshop Wednesday to make up these missed sessions immediately.\n\nBest,\nMentor Me Collective Support"
                elif total_absences == 3:
                    subject = "Strike 3: FINAL WARNING - Imminent Removal"
                    body = f"URGENT: {first_name},\n\nYou have reached 3 absences. This is your final warning. A 4th missed session will result in immediate removal from the Mentor Me Collective program.\n\nIf you are experiencing blockers, please review the FAQ and use the Ticket-to-Talk Escalation Form immediately.\n\nBest,\nMentor Me Collective Support"
                elif total_absences == 4:
                    subject = "Strike 4: Notice of Program Removal"
                    body = f"Hi {first_name},\n\nYou have now reached 4 absences. As outlined in the Code of Conduct, this triggers automatic removal from the current Grow with Google cohort.\n\nYour Coursera and Slack access will be revoked within 24 hours. We wish you the best in your future career endeavors.\n\nBest,\nMentor Me Collective Support"

                # Add to queue
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
            
            # Display summary table
            queue_df = pd.DataFrame(email_queue)[["First Name", "Email", "Total Absences", "Strike Level"]]
            st.dataframe(queue_df, use_container_width=True)

            # Send Emails Button
            if st.button("🚀 Send Warning Emails"):
                if not sender_email or not sender_password:
                    st.error("Please enter your Email Credentials in the sidebar first!")
                else:
                    try:
                        # Connect to Email Server (Assuming Gmail/Google Workspace)
                        server = smtplib.SMTP('smtp.gmail.com', 587)
                        server.starttls()
                        server.login(sender_email, sender_password)

                        progress_bar = st.progress(0)
                        
                        # Send emails
                        for i, task in enumerate(email_queue):
                            msg = MIMEMultipart()
                            msg['From'] = sender_email
                            msg['To'] = task['Email']
                            msg['Subject'] = task['Subject']
                            msg.attach(MIMEText(task['Body'], 'plain'))

                            server.send_message(msg)
                            
                            # Update the dataframe to reflect the strike was sent
                            df.at[task["Index"], 'Strike_Level_Sent'] = task["Strike Level"]
                            
                            # Update progress
                            progress_bar.progress((i + 1) / len(email_queue))

                        server.quit()
                        st.success("✅ All emails sent successfully!")

                        # Provide updated file for download
                        output = io.BytesIO()
                        if uploaded_file.name.endswith('.csv'):
                            df.to_csv(output, index=False)
                            mime_type = "text/csv"
                            new_file_name = "UPDATED_" + uploaded_file.name
                        else:
                            df.to_excel(output, index=False)
                            mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            new_file_name = "UPDATED_" + uploaded_file.name
                            
                        st.download_button(
                            label="📥 Download Updated Attendance Sheet",
                            data=output.getvalue(),
                            file_name=new_file_name,
                            mime=mime_type
                        )
                        st.info("Make sure to upload this updated sheet back to your Google Drive so the bot remembers these strikes for next week!")

                    except Exception as e:
                        st.error(f"Failed to send emails. Error: {e}")
        else:
            st.success("🎉 No scholars require intervention this week! Everyone is up to date.")
