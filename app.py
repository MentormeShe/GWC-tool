import streamlit as st
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import io

# --- PAGE SETUP ---
st.set_page_config(page_title="MMC Track Manager", page_icon="🤖", layout="wide")
st.title("🤖 Mentor Me Collective: Track Manager Bot")

# --- TABS ---
tab1, tab2 = st.tabs(["Applicant Selection", "Track Attendance & Strike Bot"])

# ----------------------------
# TAB 1: APPLICANT SELECTION
# ----------------------------
with tab1:
    st.header("📋 Applicant Selection")
    uploaded_file = st.file_uploader("Upload Applicant Sheet (CSV/Excel)", type=["csv","xlsx"], key="applicants")
    
    if uploaded_file is not None:
        # Read file
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file, engine='openpyxl')
        
        st.success(f"Successfully loaded: {uploaded_file.name}")
        
        # --- CLEAN COLUMNS ---
        df.columns = df.columns.str.strip().str.replace('\xa0','').str.lower().str.replace(':','')
        
        # Map messy headers
        column_map = {
            'first name': 'first name',
            'last name': 'last name',
            'email address': 'email',
            'where are you located?': 'location',
            'google cloud launchpad track preference': 'track_preference'
        }
        df.rename(columns=column_map, inplace=True)
        
        # --- REQUIRED COLUMNS ---
        required_cols = ['first name','email','location','track_preference']
        missing_cols = [c for c in required_cols if c not in df.columns]
        if missing_cols:
            st.error(f"Missing columns: {', '.join(missing_cols)}")
        else:
            # --- SIDEBAR CRITERIA ---
            st.sidebar.header("Selection Criteria")
            total_needed = st.sidebar.number_input("Total Applicants Needed", min_value=1, max_value=10000, value=100)
            region_limits_input = st.sidebar.text_input("Regional Limits (format: AMER=50,EMEA=30,APAC=20)", value="AMER=50,EMEA=30,APAC=20")
            
            # --- MAP LOCATIONS TO REGIONS ---
            region_map = {
                'usa':'AMER', 'canada':'AMER',
                'india':'APAC', 'china':'APAC',
                'germany':'EMEA', 'uk':'EMEA', 'france':'EMEA'
                # extend as needed
            }
            df['region'] = df['location'].str.lower().map(region_map)
            
            # --- APPLY REGIONAL LIMITS ---
            limits = {item.split('=')[0]:int(item.split('=')[1]) for item in region_limits_input.split(',')}
            
            final_selection = pd.DataFrame()
            tracks = df['track_preference'].dropna().unique()
            
            for track in tracks:
                track_df = df[df['track_preference']==track]
                track_df = track_df.sort_values(by='first name')  # optional sorting within track
                
                # Sort by region
                for region in ['AMER','EMEA','APAC']:
                    region_df = track_df[track_df['region']==region]
                    limit = limits.get(region, len(region_df))
                    final_selection = pd.concat([final_selection, region_df.head(limit)])
            
            # --- SORT FINAL OUTPUT BY TRACK → REGION ---
            track_order = {track:i for i, track in enumerate(tracks)}
            region_order = {'AMER':0,'EMEA':1,'APAC':2}
            final_selection['track_order'] = final_selection['track_preference'].map(track_order)
            final_selection['region_order'] = final_selection['region'].map(region_order)
            final_selection = final_selection.sort_values(by=['track_order','region_order']).drop(columns=['track_order','region_order'])
            
            # Limit total number of applicants
            final_selection = final_selection.head(total_needed)
            
            st.success(f"✅ Selected {len(final_selection)} applicants")
            st.dataframe(final_selection, use_container_width=True)
            
            # Download button
            output = io.BytesIO()
            if uploaded_file.name.endswith('.csv'):
                final_selection.to_csv(output,index=False)
                mime_type = "text/csv"
                new_file_name = "SELECTED_" + uploaded_file.name
            else:
                final_selection.to_excel(output,index=False)
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                new_file_name = "SELECTED_" + uploaded_file.name
            output.seek(0)
            st.download_button(label="📥 Download Selected Applicants", data=output.getvalue(), file_name=new_file_name, mime=mime_type)

# ---------------------------------
# TAB 2: TRACK ATTENDANCE / STRIKE
# ---------------------------------
with tab2:
    st.header("📊 Track Attendance & Strike Bot")
    
    uploaded_file = st.file_uploader("Upload Track Attendance Sheet (CSV/Excel)", type=["csv","xlsx"], key="attendance")
    
    if uploaded_file is not None:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file, engine='openpyxl')
        
        st.success(f"Successfully loaded: {uploaded_file.name}")
        
        # --- CLEAN COLUMNS ---
        df.columns = df.columns.str.strip().str.replace('\xa0','').str.lower().str.replace(':','')
        
        # Ensure strike column exists
        if 'strike_level_sent' not in df.columns:
            df['strike_level_sent'] = 0
        
        # --- AUDIT LOGIC ---
        email_queue = []
        week_cols = [c for c in df.columns if 'week' in c]
        
        for idx,row in df.iterrows():
            first_name = row.get('full name', str(idx))
            email = row.get('email', '')
            last_strike = int(row['strike_level_sent']) if pd.notna(row['strike_level_sent']) else 0
            total_absences = list(row[week_cols].astype(str).str.lower()).count('absent')
            
            if total_absences>0 and total_absences>last_strike and total_absences<=4:
                # Strike emails
                if total_absences==1:
                    subject = "Strike 1: Missed Track Sync"
                    body = f"Hi {first_name}, you missed 1 session."
                elif total_absences==2:
                    subject = "Strike 2: Second Absence"
                    body = f"Hi {first_name}, you missed 2 sessions."
                elif total_absences==3:
                    subject = "Strike 3: FINAL WARNING"
                    body = f"Hi {first_name}, you missed 3 sessions."
                else:
                    subject = "Strike 4: Program Removal"
                    body = f"Hi {first_name}, you missed 4 sessions. You will be removed."
                
                email_queue.append({
                    'Index': idx, 'First Name': first_name, 'Email': email,
                    'Total Absences': total_absences, 'Strike Level': total_absences,
                    'Subject': subject, 'Body': body
                })
        
        if len(email_queue)>0:
            st.warning(f"⚠️ {len(email_queue)} students require strikes")
            st.dataframe(pd.DataFrame(email_queue)[['First Name','Email','Total Absences','Strike Level']], use_container_width=True)
            
            sender_email = st.sidebar.text_input("Sender Email for Attendance Tab", key="email2")
            sender_password = st.sidebar.text_input("App Password", type='password', key="pwd2")
            
            if st.button("🚀 Send Strike Emails"):
                if not sender_email or not sender_password:
                    st.error("Enter email credentials")
                else:
                    try:
                        server = smtplib.SMTP('smtp.gmail.com', 587)
                        server.starttls()
                        server.login(sender_email, sender_password)
                        progress = st.progress(0)
                        for i, task in enumerate(email_queue):
                            msg = MIMEMultipart()
                            msg['From'] = sender_email
                            msg['To'] = task['Email']
                            msg['Subject'] = task['Subject']
                            msg.attach(MIMEText(task['Body'], 'plain'))
                            server.send_message(msg)
                            df.at[task['Index'],'strike_level_sent'] = task['Strike Level']
                            progress.progress((i+1)/len(email_queue))
                        server.quit()
                        st.success("✅ All emails sent!")
                        
                        output = io.BytesIO()
                        if uploaded_file.name.endswith('.csv'):
                            df.to_csv(output,index=False)
                            mime_type="text/csv"
                            new_file_name="UPDATED_"+uploaded_file.name
                        else:
                            df.to_excel(output,index=False)
                            mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            new_file_name="UPDATED_"+uploaded_file.name
                        output.seek(0)
                        st.download_button("📥 Download Updated Attendance Sheet", data=output.getvalue(), file_name=new_file_name, mime=mime_type)
                    except Exception as e:
                        st.error(f"Failed to send emails: {e}")
        else:
            st.success("🎉 No strikes required this week!")
