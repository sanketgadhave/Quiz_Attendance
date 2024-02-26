import streamlit as st
from src.generate_qr_code import generate_qr_code
from src.update_excel import append_to_sheet
from googleapiclient.errors import HttpError
from src.update_excel import append_to_sheet, service
import urllib.parse
import configparser
from src.update_configuration_sheet import update_configuration_sheet
from src.sheet_management import get_active_sheet_name, get_active_subject
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import datetime
import requests

if 'admin_authenticated' not in st.session_state:
    st.session_state.admin_authenticated = False
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'main'
if 'authentication_failed' not in st.session_state:
    st.session_state['authentication_failed'] = False
if 'qr_code_authenticated' not in st.session_state:
    st.session_state.qr_code_authenticated = False
if 'qr_session_start_time' not in st.session_state:
    st.session_state.qr_session_start_time = None
# Passcode for TA access
TA_PASSCODE = "1234"
subject_to_spreadsheet_id = {
    'DIC': '17zLyXGck6_1tGc7cf_KWFWDsV5RZzu7o5kHlkWN8JEc',
    'DMQL': '1wxcqkT3EhV_4sXhIFTMTadvDvgmnGSQK6OhvihAigI0',
}

# Function to check if the TA's QR session is still valid
def is_qr_session_valid():
    if st.session_state['qr_session_start_time'] and datetime.datetime.now() - st.session_state['qr_session_start_time'] < datetime.timedelta(hours=4):  # 4 hours for example
        return True
    return False

# Function to process QR code content and mark attendance
def mark_attendance(ub_person_number, sheet_name, url):
    script_url = url  # Replace with your actual Apps Script URL
    params = {
        "ubPersonNumber": ub_person_number,
        "sheetName": sheet_name
    }
    response = requests.get(script_url, params=params)
    if response.ok:
        st.success("Attendance marked successfully.")
    else:
        st.error("Failed to mark attendance.")

# Streamlit UI
st.title('Quiz Attendance System')

if not st.session_state.admin_authenticated:
    if st.button('Admin Login'):
        st.session_state.current_page = 'admin_login'
        st.experimental_rerun()

# QR Code Login Button and Logic
if st.button('QR Code Login'):
    st.session_state.current_page = 'qr_code_login'
    st.experimental_rerun()

# Handling QR Code Login
if st.session_state.current_page == 'qr_code_login':
    qr_passcode_input = st.text_input("Enter TA passcode for QR code scan sessions:", type="password")
    if qr_passcode_input:
        if qr_passcode_input == TA_PASSCODE:
            st.success("QR Code Scan Session Authenticated Successfully!")
            st.session_state.qr_code_authenticated = True
            st.session_state.qr_session_start_time = datetime.datetime.now()
            st.session_state.current_page = 'main'  # Redirecting back to the main page
            st.experimental_rerun()
        else:
            st.error("Incorrect passcode. Please try again.")

# Admin Login "Page"
if st.session_state.current_page == 'admin_login':
    passcode_input = st.text_input("Enter TA passcode for administrative actions:", type="password")
    if passcode_input:
        if passcode_input == TA_PASSCODE:
            st.success("Authenticated successfully!")
            st.session_state.admin_authenticated = True
            st.session_state.current_page = 'admin_page'
            st.experimental_rerun()  # Navigate to admin page
        else:
            st.error("Incorrect passcode. Please try again.")
            st.session_state['authentication_failed'] = True


# Admin Page
if st.session_state.admin_authenticated and st.session_state.current_page == 'admin_page':
    subject = st.selectbox('Select Subject', ['DIC', 'DMQL'])
    if 'selected_sheet_name' not in st.session_state or st.session_state.selected_sheet_name is None:
        st.session_state.selected_sheet_name = 'Sheet1'  # Default sheet name
    new_sheet_name = st.text_input('Name for New Quiz Sheet', value=st.session_state.selected_sheet_name)
    if st.button('Create New Sheet') and new_sheet_name:
        active_sheet_name  = update_configuration_sheet(service, subject, new_sheet_name, subject_to_spreadsheet_id)
        if active_sheet_name is None:
            st.error(f"Sheet name '{new_sheet_name}' already exists. Please choose a different name.")
        spreadsheet_id = subject_to_spreadsheet_id[subject]
        # Code to create a new sheet within the selected Google Sheet
        batch_update_request_body = {
            "requests": [{"addSheet": {"properties": {"title": new_sheet_name}}}]
        }
        try:
            # Create the new sheet
            service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=batch_update_request_body).execute()

            # Prepare the headers
            headers = [["First Name", "Last Name", "UB Person", "Attendance"]]
            value_range_body = {
                "values": headers
            }

            # Update the newly created sheet with headers
            update_range = f"{new_sheet_name}!A1:D1"  # Adjust the range if necessary
            service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=update_range,
                valueInputOption="RAW",
                body=value_range_body
            ).execute()

            st.success(f"Active sheet set to '{active_sheet_name}' for {subject}.")
        except HttpError as error:
            st.error(f"Failed to create new sheet: {error}")
        st.session_state['active_sheet_name'] = active_sheet_name

    if st.button('Log Out'):
        st.session_state.admin_authenticated = False
        st.session_state.current_page = 'main'  # Optionally reset the current page to 'main'
        st.experimental_rerun()  # Refresh the app to reflect the logout state

    if st.session_state['authentication_failed']:
        st.error("Incorrect passcode. Please try again.")

if st.session_state.current_page == 'main':
    with st.form("student_info", clear_on_submit=True):
        first_name = st.text_input("First Name")
        last_name = st.text_input("Last Name")
        ub_person_number = st.text_input("UB Person Number")
        submitted = st.form_submit_button("Submit")

        if submitted:
            active_subject = get_active_subject(service, subject_to_spreadsheet_id['DIC'])
            active_sheet_name = get_active_sheet_name(service, active_subject, subject_to_spreadsheet_id)
            # Prepare data for Google Sheets
            if active_sheet_name:
                data = [first_name, last_name, ub_person_number, ""]  # Leave "Custom" column empty for now
                append_to_sheet(spreadsheet_id=subject_to_spreadsheet_id[active_subject], data=data, range_name=active_sheet_name)  # Use dynamic range_name based on sheet_name

                encoded_sheet_name = urllib.parse.quote(active_sheet_name)

                # Generate QR code with URL
                # Assuming you have a web service endpoint or script ready to handle the query and mark attendance
                #active_subject = get_active_subject(service, subject_to_spreadsheet_id['DIC'])
                print(active_subject)
                base_url = "https://quizattendanceub.streamlit.app/"
                #base_url = "https://script.google.com/macros/s/AKfycbzYdiYkY8ceFPQmlSJ_3pThrm8oOAatJ_af7v5ALIRGX7qlGVEDLUULpoosV1mOBC4wJQ/exec"
                qr_data = f"{base_url}/?UBPersonNumber={urllib.parse.quote(ub_person_number)}&SheetName={urllib.parse.quote(encoded_sheet_name)}"
                qr_code_image = generate_qr_code(qr_data)

                # Display QR Code
                st.image(qr_code_image.getvalue(), caption='Your QR Code', use_column_width=True)
            else:
                st.error("Failed to fetch the active sheet name. Please check the configuration.")

        config = configparser.ConfigParser()
        config.read('data_files/google_sheet_url.properties')
        active_subject = get_active_subject(service, subject_to_spreadsheet_id['DIC'])
        base_url = config.get('URLs', active_subject)
        if st.session_state.qr_code_authenticated and is_qr_session_valid():
            st.header("TA QR Code Processing")
            qr_code_content = st.text_area("Paste QR code content here:")
            process_button = st.button("Process QR Code")

            if process_button and qr_code_content:
                # Assuming the QR code content is a URL with parameters
                parsed_content = urllib.parse.parse_qs(urllib.parse.urlparse(qr_code_content).query)
                ub_person_number = parsed_content.get('UBPersonNumber', [None])[0]
                sheet_name = parsed_content.get('SheetName', [None])[0]

                if ub_person_number and sheet_name:
                    # Function to mark attendance; Implement as needed
                    # For example, redirecting or making a request to your Google Apps Script
                    mark_attendance(ub_person_number, sheet_name, base_url)
                else:
                    st.error("Invalid QR code content. Please check and try again.")
        elif st.session_state.qr_code_authenticated:
            # If the session exists but is not valid, prompt for re-authentication
            st.error("QR code session has expired. Please login again.")