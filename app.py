import threading

import streamlit as st
from src.generate_qr_code import generate_qr_code
from src.update_excel import append_to_sheet
from googleapiclient.errors import HttpError
from src.update_excel import append_to_sheet, service
import urllib.parse
import configparser
from src.update_configuration_sheet import update_configuration_sheet
from src.sheet_management import get_active_sheet_name, get_active_subject
from threading import Lock
import time
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
# New global variables for batch processing
BATCH_SIZE = 2
batch_storage = []
batch_lock = Lock()


def process_and_generate_qr(batch_data):
    # Place your logic here for batch updating Google Sheets with batch_data
    # And for generating QR codes. For example:
    for submission in batch_data:
        # Your existing logic to append to Google Sheets
        # And generate QR codes

        # Placeholder: Replace with actual call to append_to_sheet and generate QR code
        print("Processing submission:", submission)

    # This is where you'd send the QR codes to the users or make them retrievable
    print("Batch processed.")


if 'admin_authenticated' not in st.session_state:
    st.session_state.admin_authenticated = False
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'main'
if 'authentication_failed' not in st.session_state:
    st.session_state['authentication_failed'] = False
# Passcode for TA access
TA_PASSCODE = "1234"
subject_to_spreadsheet_id = {
    'DIC': '17zLyXGck6_1tGc7cf_KWFWDsV5RZzu7o5kHlkWN8JEc',
    'DMQL': '1wxcqkT3EhV_4sXhIFTMTadvDvgmnGSQK6OhvihAigI0',
}
# Streamlit UI
st.title('Quiz Attendance System')

if not st.session_state.admin_authenticated:
    if st.button('Admin Login'):
        st.session_state.current_page = 'admin_login'
        st.experimental_rerun()

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
            submission_data = {
                "first_name": first_name,
                "last_name": last_name,
                "ub_person_number": ub_person_number,
                # Any other data needed for processing
            }
            with batch_lock:
                batch_storage.append(submission_data)

            # Check if the batch size is reached
            process_batch = False
            with batch_lock:
                if len(batch_storage) >= BATCH_SIZE:
                    process_batch = True

            if process_batch:
                # Processing is deferred to not block the Streamlit app
                threading.Thread(target=process_and_generate_qr, args=(batch_storage.copy(),)).start()
                with batch_lock:
                    batch_storage.clear()

            # Display a loading message
            st.info("Please wait while we process your submission...")